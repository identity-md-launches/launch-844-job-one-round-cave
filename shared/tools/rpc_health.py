"""Read-only Ethereum RPC health probe; Python standard library only."""
import argparse
import json
import math
import time
import urllib.error
import urllib.request

DEFAULTS = ["https://ethereum-rpc.publicnode.com", "https://eth.drpc.org"]


def quantity(value):
    if not isinstance(value, str) or not value.startswith("0x") or len(value) < 3:
        raise ValueError("invalid RPC quantity")
    if len(value) > 3 and value[2] == "0":
        raise ValueError("noncanonical RPC quantity")
    if any(c not in "0123456789abcdefABCDEF" for c in value[2:]):
        raise ValueError("invalid RPC quantity digits")
    return int(value, 16)


def rpc(endpoint, method, params, request_id, timeout):
    request = urllib.request.Request(
        endpoint,
        data=json.dumps({"jsonrpc": "2.0", "id": request_id,
                         "method": method, "params": params}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "Pepeolithic-RPC-Health/1.0"},
    )
    # Disable automatic proxy discovery so the probe never consults environment variables.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=timeout) as response:
        raw = response.read(1_048_577)
    if len(raw) > 1_048_576:
        raise ValueError("RPC response exceeds 1 MiB")
    obj = json.loads(raw)
    if not isinstance(obj, dict) or obj.get("jsonrpc") != "2.0" or type(obj.get("id")) is not int or obj["id"] != request_id:
        raise ValueError("invalid JSON-RPC envelope")
    if "error" in obj:
        raise ValueError("RPC error: " + json.dumps(obj["error"]))
    if "result" not in obj:
        raise ValueError("missing RPC result")
    return obj["result"]


def assess(chain, block, now, max_age):
    if quantity(chain) != 1:
        raise ValueError("endpoint is not Ethereum mainnet")
    if not isinstance(block, dict):
        raise ValueError("latest block is missing")
    number, timestamp = quantity(block.get("number")), quantity(block.get("timestamp"))
    block_hash = block.get("hash")
    if not isinstance(block_hash, str) or len(block_hash) != 66 or not block_hash.startswith("0x"):
        raise ValueError("invalid block hash")
    if any(c not in "0123456789abcdefABCDEF" for c in block_hash[2:]):
        raise ValueError("invalid block hash digits")
    age = now - timestamp
    if age < -30:
        raise ValueError("block timestamp is in the future relative to local clock")
    return {"status": "fresh" if age <= max_age else "stale", "chain_id": 1,
            "block_number": number, "block_hash": block_hash, "age_seconds": round(age, 2)}


def probe(endpoint, timeout, max_age):
    start = time.monotonic()
    try:
        chain = rpc(endpoint, "eth_chainId", [], 1, timeout)
        block = rpc(endpoint, "eth_getBlockByNumber", ["latest", False], 2, timeout)
        result = assess(chain, block, time.time(), max_age)
    except (ValueError, TypeError, OSError, urllib.error.URLError) as exc:
        result = {"status": "error", "error": str(exc)}
    return {"endpoint": endpoint, "latency_ms": round((time.monotonic() - start) * 1000, 2), **result}


def demo():
    block = {"number": "0x10", "timestamp": "0x3e8", "hash": "0x" + "ab" * 32}
    assert assess("0x1", block, 1012, 120)["status"] == "fresh"
    assert assess("0x1", block, 1200, 120)["status"] == "stale"
    for chain, candidate in [("0x2", block), ("0x1", None), ("0x1", {**block, "hash": "0xzz"})]:
        try:
            assess(chain, candidate, 1012, 120)
        except ValueError:
            continue
        raise AssertionError("invalid response was accepted")
    for malformed in [None, 1, "0x", "0x01", "0x-1", "0xgg"]:
        try:
            quantity(malformed)
        except ValueError:
            continue
        raise AssertionError("malformed quantity was accepted")
    print(json.dumps({"demo": "passed", "checks": ["fresh", "stale", "wrong chain", "missing block", "bad hash"]}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="deterministic offline checks; no network")
    parser.add_argument("--endpoint", action="append", help="HTTPS RPC URL; repeat for multiple endpoints")
    parser.add_argument("--timeout", type=float, default=12)
    parser.add_argument("--max-age", type=float, default=120)
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or not math.isfinite(args.max_age) or args.timeout <= 0 or args.max_age < 0:
        parser.error("timeout must be positive and max-age nonnegative")
    if args.demo:
        demo()
        return 0
    endpoints = args.endpoint or DEFAULTS
    if any(not url.startswith("https://") for url in endpoints):
        parser.error("endpoints must use HTTPS")
    results = [probe(url, args.timeout, args.max_age) for url in endpoints]
    print(json.dumps({"observations": results}, indent=2))
    return 0 if all(r["status"] == "fresh" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
