# ALG-003: Offset and speed fallback with retained round winners

Status: refined by SPEC-0008 revision 5; see ALG-0004 for the current complete record.

## Purpose and owner

`learning_qualification` owns deterministic one-based rounds. Qualification always replays every supplied offset and speed; the pooled eligible non-collision evidence admitted to fitting changes. The user chooses which qualified retained winners to export; failed winners remain diagnostic only.

## Round construction

The outer loop starts with all supplied collision offsets. After the current inner speed search passes or exhausts, exclude exactly the smallest active offset and reset the inner speed loop to all supplied speeds for the remaining offsets, even after success. Excluded offsets remain in Qualification evidence and visible in results.

Within one outer round, Round 1 fits all eligible Normal/Pick/Put evidence for all supplied speeds. If its winner does not qualify its complete Training speed interval, the next inner round removes exactly the current lowest speed and refits the same active-offset pool, including when an offset is wholly undetectable. Qualification still evaluates all supplied speeds and offsets. Only the inner search stops on a full-range pass or final-speed exhaustion; the outer search continues.

Every completed round retains exactly one winner even when its qualified range is narrower than its Training interval. This mismatch remains diagnostic and does not erase the kernel.

## Ranking

Within a round, compare candidates in this exact order:

1. Widest observed contiguous high-speed qualified suffix.
2. More active offsets (equal for all candidates within one round).
3. Shorter kernel depth/tap count.
4. Lower worst in-range collision latency; every passing latency is already no greater than 20 ms.
5. Larger combined robustness margin.
6. Stable declared candidate order.

Across rounds, only nonempty full Training/Qualification range matches enter the qualified view. The same ordering prefers more supplied speed strata, then more active offsets before technical ties. Retained result order and all-supplied diagnostic ranking remain independent from qualified display ordering.

## Evidence

Required evidence includes data-driven suffix generation, all-offset/all-speed replay facts, whole-offset exclusion, speed-loop reset, range-match stopping, retained mismatch cases, stable tie breaks, coverage gaps, and exact condition denominators.
