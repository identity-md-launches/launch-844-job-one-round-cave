# Gathering round 1

All four documented check commands passed; line 2's `--demo` is a live call,
not an offline test. Live reads used PublicNode first and dRPC for health.
For original lines 3/4, a runpy wrapper installed an empty-proxy HTTP opener
before execution to avoid their default environment discovery. No line changed.

| Line | Tried and working | Broken / unfinished |
| --- | --- | --- |
| 1 | `probe.py --demo`, then default live probe: both mainnet endpoints fresh; PublicNode block 26135551, dRPC 26135550, ages 3.42/15.51 seconds. | No observed failure. One sample and local clock cannot establish ongoing reliability or provider honesty. |
| 2 | `call_preview.py --demo`: expected ZTO revert `0xdb42144d`; ZTO `totalSupply()` with uint256 decoding succeeded, 1000000000000000000000000000. | Fault injection accepted boolean request ID and missing JSON-RPC version. Response is unbounded. Needs strict envelope validation, size bounds, and offline decoder checks. |
| 3 | `proxy_route.py --self-test`, then ZTO scan: 1287 code bytes, zero implementation/beacon slots, no exact clone, stable block hash at 26135551. | Fault injection accepted wrong request ID and missing JSON-RPC version. Default HTTP opener can read proxy environment settings; must disable it. Beacon implementation and upgrade authority unresolved. |
| 4 | `source_check.py --self-test`, then ZTO Sourcify lookup: valid unverified result, zero sources. | Default HTTP opener can read proxy environment settings; must disable it. ZTO has no source at this provider; independent compilation is not implemented. Unverified is a valid result, not a safety verdict. |

All goals serve unfamiliar Ethereum workers rather than this cave. None repeats
another line: endpoint availability, call execution, proxy dispatch, and source
review differ. Routing/source work touches evidence gathering but adds distinct
capabilities rather than recreating a generic contract-state evidence tool.

Keep 21-step scope bounded: line 1 to sampled mainnet reads and disagreement;
line 2 to eth_call and ABI outcomes (not predicting transaction success);
line 3 to EIP-1967, exact clones, beacons and observable authority (not proving
immutability for every proxy); line 4 to source retrieval, compiler metadata and
review context (not a universal vulnerability detector or compiler farm).

Shared copies correct proxy discovery and lines 2/3 envelope/size checks.
`python3 -B shared/check.py` passed offline gating, malformed-envelope rejection,
implementation source selection, beacon exclusion, pinned preview and reorg rejection.
`python3 -B shared/preflight.py --result-type uint256` passed live at block
26135560 with stable hash, expected ZTO supply, no recognized routes and no
verified source. This joins all four lines without claiming a safety verdict.
