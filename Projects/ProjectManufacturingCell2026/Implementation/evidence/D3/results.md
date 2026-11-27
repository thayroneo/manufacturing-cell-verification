# D3 — PObserve CLI results

Status: VERIFIED

| Case | Monitor | Expected | Observed | Exit |
|---|---|---|---|---|
| original_twophase | RegimentationSafety | PASS | PASS | 0 |
| original_twophase | NoStaleAdmission | PASS | PASS | 0 |
| original_twophase | NoDoubleOutcome | PASS | PASS | 0 |
| original_twophase | ObligationDeadlineRespected | PASS | PASS | 0 |
| original_twophase | AdaptationBoundedTime | PASS | PASS | 0 |
| original_twophase | LockoutBeforeEntry | PASS | PASS | 0 |
| original_twophase | NoOpeningWhileHumanInside | PASS | PASS | 0 |
| original_naive | RegimentationSafety | VIOLATION | VIOLATION | 2 |
| original_naive | NoStaleAdmission | VIOLATION | VIOLATION | 2 |
| two_technicians_fixed | RegimentationSafety | PASS | PASS | 0 |
| two_technicians_fixed | NoStaleAdmission | PASS | PASS | 0 |
| two_technicians_fixed | NoDoubleOutcome | PASS | PASS | 0 |
| two_technicians_fixed | ObligationDeadlineRespected | PASS | PASS | 0 |
| two_technicians_fixed | AdaptationBoundedTime | PASS | PASS | 0 |
| two_technicians_fixed | LockoutBeforeEntry | PASS | PASS | 0 |
| two_technicians_fixed | NoOpeningWhileHumanInside | PASS | PASS | 0 |
| two_technicians_prefix | NoOpeningWhileHumanInside | VIOLATION | VIOLATION | 2 |
| seed64_default_bound | AdaptationBoundedTime | VIOLATION | VIOLATION | 2 |
| seed64_calibrated | RegimentationSafety | PASS | PASS | 0 |
| seed64_calibrated | NoStaleAdmission | PASS | PASS | 0 |
| seed64_calibrated | NoDoubleOutcome | PASS | PASS | 0 |
| seed64_calibrated | ObligationDeadlineRespected | PASS | PASS | 0 |
| seed64_calibrated | AdaptationBoundedTime | PASS | PASS | 0 |
| seed64_calibrated | LockoutBeforeEntry | PASS | PASS | 0 |
| seed64_calibrated | NoOpeningWhileHumanInside | PASS | PASS | 0 |
| seed299_calibrated | RegimentationSafety | PASS | PASS | 0 |
| seed299_calibrated | NoStaleAdmission | PASS | PASS | 0 |
| seed299_calibrated | NoDoubleOutcome | PASS | PASS | 0 |
| seed299_calibrated | ObligationDeadlineRespected | PASS | PASS | 0 |
| seed299_calibrated | AdaptationBoundedTime | PASS | PASS | 0 |
| seed299_calibrated | LockoutBeforeEntry | PASS | PASS | 0 |
| seed299_calibrated | NoOpeningWhileHumanInside | PASS | PASS | 0 |
| system_sanction_suppressed | ObligationDeadlineRespected | VIOLATION | VIOLATION | 2 |
| system_commit_delayed | AdaptationBoundedTime | VIOLATION | VIOLATION | 2 |
| log_missing_leave | RegimentationSafety | VIOLATION | VIOLATION | 2 |
| log_deleted_sanction | ObligationDeadlineRespected | VIOLATION | VIOLATION | 2 |
| log_duplicate_commit | NoStaleAdmission | VIOLATION | VIOLATION | 2 |
| log_duplicate_outcome | NoDoubleOutcome | VIOLATION | VIOLATION | 2 |
| human_bypasses_lockout | LockoutBeforeEntry | VIOLATION | VIOLATION | 2 |
| abort_valid | AdaptationBoundedTime | PASS | PASS | 0 |
| abort_wrong_version | AdaptationBoundedTime | VIOLATION | VIOLATION | 2 |

These are real PObserve CLI invocations on synthetic logs.
A passing finite log does not prove liveness or physical safety.
