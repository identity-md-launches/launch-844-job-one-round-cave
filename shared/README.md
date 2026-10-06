# Read-only contract preflight

Reusable Python standard-library copies of RPC Health (line 1), Call Preview
(line 2), Proxy Route (line 3), and Source Check (line 4) are in `tools/`.
Original line files remain untouched. Copies of lines 3 and 4 explicitly disable
environment-based HTTP proxy discovery, matching lines 1 and 2.
Shared copies of lines 2 and 3 also require JSON-RPC 2.0, an integer matching
request ID, exactly one result/error field, and a response of at most 1 MiB.

From the workspace root:

```sh
python3 -B shared/preflight.py --result-type uint256
python3 -B shared/check.py
```

The first command uses real ZTO: choose a fresh mainnet endpoint, inspect routing,
retrieve Sourcify status for the contract and any implementation/clone leads,
and preview `totalSupply()` at the routing scan's block. Recheck that block's
number and hash after the call. The second command checks the composition offline.
No network or dependencies are needed for the offline checks.

`--address`, `--data`, `--result-type`, and repeated `--endpoint` customize the
lookup. This narrow workflow previews zero-value calls without a sender.
Source failures are explicit per-address observations and do not prevent calls;
no fresh endpoint prevents all subsequent work. Contract-call RPC failures make
the command fail. An observed revert is a completed preview, not approval to send.

Source is not extracted, compiled, or executed. Beacon addresses are not treated
as implementations. This reports review leads rather than safety, upgrade
authorization, or independent source verification. Provider honesty, transient
availability and changes between reads remain limitations. It never signs,
sends transactions, discovers credentials, or accesses environment settings.

Live validation returned ZTO supply `1000000000000000000000000000`, zero
recognized proxy routes, and unverified Sourcify status. No new coin is needed.
