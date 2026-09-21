# ADR-0002: Use independent Windows spawn workers per History

- Status: proposed
- Date: 2026-08-26
- Approver: pending
- Approval reference: SPEC-0003 revision 11 records the user's selected behavior; formal ADR acceptance remains pending.

## Context

Training evaluates four independent requested History candidates before deterministic round ranking. The current single Python process leaves most logical processors idle and repeatedly builds identical FIR matrices for every model rule.

## Decision

Introduce a Learning-owned History execution port implemented by an L3 adapter. The adapter launches exactly four independent Windows `spawn` processes, one per requested History, and merges immutable results in declaration order. Each worker owns a bounded per-History/fold raw FIR matrix cache.

Independent processes are selected instead of one shared process pool because a single abnormal worker exit must not invalidate healthy workers. Explicit `MemoryError` is terminal and cancels all workers; startup failure or abnormal process exit retries once in a fresh process; semantic, numerical, product-code, and cancellation failures never retry.

## Consequences

The application gains an execution adapter, IPC channel, process-tree resource evidence, and Windows-spawn integration tests. Dataset payloads are copied by Windows spawn, so aggregate Peak RSS is governed at 85% of launch-time available RAM. Results remain deterministic because completion order is never ranking order.

## Alternatives considered

- A shared `ProcessPoolExecutor`: rejected because a broken pool can invalidate healthy jobs.
- Threads: rejected because Python-level FIR preparation does not reliably scale under the GIL.
- Unix `fork`: out of scope for the Windows product target.
- Adaptive worker count: rejected by the confirmed fixed-four policy.

## Validation

Development architecture gate, spawn integration and failure-injection tests, exact sequential/parallel differential tests, process-tree RSS evidence, per-round duration evidence, and bounded Windows application validation are required before release.
