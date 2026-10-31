k# Structure Outline: resume-all

## ✅ Phase 1: parse --all flag and list all plans
Files: scripts/factory.sh
Validation: `test "$(scripts/factory.sh resume --all | grep -c 'all gates approved')" -ge 5` AND `test "$(scripts/factory.sh resume | grep -c 'next ->')" -eq 0`
- [x] resume --all lists all plans
- [x] resume without --all unchanged

## Phase 2: verify the three cases
Files: scripts/factory.sh (read-only; verify, don't modify)
Validation: `test "$(scripts/factory.sh resume --all | grep -c 'all gates approved')" -ge 5` AND `test "$(scripts/factory.sh resume | grep -c 'next ->')" -eq 0`
- [x] case a: all approved (≥5 plans listed)
- [x] case b: one open (create scratch plan, verify next ->, delete)
- [x] case c: no plans (verify no crash)
