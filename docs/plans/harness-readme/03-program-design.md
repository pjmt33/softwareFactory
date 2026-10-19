# Program Design: README.md prose update

## Files
- `README.md`: Updated to document the harness workflow, including `harness.py`, gate references, status files, and `--answer-file` usage.

## Types & signatures

## Call stack

## Test plan

## Least confident decisions

1. **Decision**: Document the harness workflow in `README.md` vs. a separate `HARNESS.md`.
   - **Alternative rejected**: Split into `HARNESS.md`.
   - **Switch condition**: If `README.md` grows too long.

2. **Decision**: Keep `MANUAL.md` as-is vs. merge its content into `README.md`.
   - **Alternative rejected**: Merge `MANUAL.md` into `README.md`.
   - **Switch condition**: If `MANUAL.md` and `README.md` diverge.

3. **Decision**: Include the `--answer-file` example inline vs. link to `MANUAL.md`.
   - **Alternative rejected**: Link to `MANUAL.md`.
   - **Switch condition**: If the example needs updating in two places.
