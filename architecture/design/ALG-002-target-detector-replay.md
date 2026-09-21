# ALG-002: Exact target-type detector replay

Status: approved by confirmed SPEC-0001

## Purpose and owner

`learning_qualification` owns replay and qualification. Replay evaluates every supplied speed and collision-offset tuple using the selected `float32` or `float64` representation chosen before Start Learning.

## Arithmetic and detector state

Samples and frozen constants enter the target representation before replay. Each FIR output starts from its bias and accumulates output X/Y/Z, input X/Y/Z, then lag zero/current to oldest. Every multiply and add rounds separately in the selected type; fused multiply-add and reassociation are forbidden.

Residual axes are normalized with immutable centers/scales. `MAX_ABS` compares X, Y, then Z. `L2_NORM` rounds three squares, then `x² + y²`, then `+ z²`, then uses correctly rounded selected-type IEEE square root. No temporal RMS exists.

The ARMED detector applies exactly one confirmation rule: first sample, two consecutive valid samples, or two of the current/previous three valid samples at `score > threshold`. Equality does not fill confirmation history. Invalid input, Ignore, discontinuity, and reset clear confirmation history. A trigger enters LATCHED. Re-arming requires score below `0.5 * threshold` for 50 ms; latched samples do not build a new confirmation.

## Qualification gates

For an in-range supplied condition, every Normal Robot Motion, Pick, and Put interval that occurs must produce zero false collisions; a class with zero intervals is neutral. At least one Fork Collision interval must exist, and every Fork Collision must trigger no later than 150 ms after its annotation interval start. The 150 ms deadline is qualification-only and does not affect annotation. A condition with no Collision evidence is a Coverage Gap, not a pass.

## Evidence

Required evidence includes target-type bit vectors, strict threshold-neighbor cases, FMA-sensitive vectors, axis/lag impulse tests, detector transition tests, 150 ms boundary tests, and compiled C99/C++17 semantic-contract checks for exported profiles.
