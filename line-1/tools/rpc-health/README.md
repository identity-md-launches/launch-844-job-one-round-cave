# RPC Health

Checks whether public Ethereum RPC endpoints provide a well-formed mainnet identity and a recent latest block. Reports block number/hash, age against the local clock, and total latency for two sequential read-only requests. Uses Python 3 and only the standard library. No installation is needed.

Run this from the workspace root to see it working without network access:

```sh
python3 line-1/tools/rpc-health/probe.py --demo
```

For real public chain reads:

```sh
python3 line-1/tools/rpc-health/probe.py
```

Override endpoints with repeated `--endpoint https://...` flags. `--timeout` controls each HTTP request (default 12 seconds); `--max-age` sets the freshness threshold (default 120 seconds). Exit status is 0 when all endpoints are fresh, 1 for stale/error observations, and 2 for invalid arguments. The demo returns 0 when its assertions pass. Requests carry `Pepeolithic-RPC-Health/1.0` as their User-Agent.

## What happened when tried

On 2026-10-07, the offline demo passed fresh/stale, wrong-chain, missing-block, and malformed-hash cases. Live calls to PublicNode and dRPC both reported Ethereum mainnet block 26135456 with hash `0x19c7f4582190e51de73c0692151c418b38ada78641240e05a90e8efb741b831f`. Ages were 10.32 and 10.56 seconds; total latencies were 264.34 and 237.41 ms. Both observations were fresh.

After disabling automatic environment-based proxy discovery, a second live run also passed: both endpoints returned block 26135462 at ages 7.41/7.71 seconds. Mocked transport checks passed for the custom User-Agent, valid results, malformed envelopes, mismatched IDs, RPC errors, and the response-size limit. The demo also rejected six malformed quantities.

## Limits

This is a single observation, not a guarantee of availability or truthful chain data. Providers may agree while sharing infrastructure. Freshness depends on the local clock. Chain identity and plausible block fields do not establish consensus or verify a block cryptographically. Sequential identity/block requests can race with endpoint changes. This first piece does not yet compare repeated samples or calculate availability over time. It never signs or sends transactions, reads credentials, or posts to the swarm. HTTP POST is used only to transport the two read-only JSON-RPC methods.
