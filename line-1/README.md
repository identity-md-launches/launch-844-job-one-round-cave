# Step 01 — Listening to the Signal

Line 1 starts with RPC Health: a dependency-free, read-only Ethereum endpoint probe. Its goal, usage, real-chain observations and limits are recorded alongside the tool. No coin is needed for this capability.

## Wall result and review

Output: `artifacts/line-1/wall.png`, PNG, 1254 × 1254 pixels, square and matching the supplied cave dimensions. Record: `dist/line-1/01.json`; its image URL contains the SHA-256 of the delivered PNG bytes. All PNG chunk CRCs passed, the record shape was checked, and delivered non-image files are below 100 KB.

Visually inspected the final image: recognizable wide-mouthed, heavy-lidded Pepe in charcoal and ochre, with a hollow reed and signal ripples, uneven worn pigment on warm rock. Counted five digits on each of the two open hands (four fingers and a thumb). No letters, numbers, signatures, logos, frames, real people or prohibited symbols observed. Cave size, framing, major cracks and warm lighting retained. No known unmet visual requirement; generative editing does not guarantee pixel-identical rock microtexture. No predecessor paintings existed.

The installed image editor was used directly to save only the requested wall PNG. Initial edit prompt: preserve the bare cave's dimensions, rock, cracks, lighting and framing; add a modest prehistoric Pepe listening through a hollow reed toward ripples, with five digits per hand, only earth pigments, and no text. A second targeted edit opened the reed-side hand to make its five digits countable while preserving the rest. The source needed a `.png` filename for the editor, so it was copied to the final wall path before editing.

## Checks

Offline demo and mocked transport rejection checks passed. Two live runs against both public endpoints returned fresh mainnet blocks. Details and a repeatable offline command are in `tools/rpc-health/README.md`. No transaction was signed, submitted or prepared, and no wallet, secret, configuration or environment variable was read by the tool. All deliverables were left untracked for the upload daemon.
