# wait-tests

Eight wait-row scenarios, one folder each, all running
`config0-hub:::config0_core::wait_test` (scenarios e and h also pull in
`config0-hub:::config0_core::wait_test_child`). Orders are `echo ok` / `exit 1` /
`sleep 20`; no cloud resource is created. Both stacks must be scanned before use.

Run one: `/config0-add-project test` pointed at `wait-tests/<scenario>/config0.yaml`.

Verify, read-only, never a browser:

- orders: `/config0-order-queue show <run_id>` (Query by `run_id` on `config0-orders-queue`,
  SaaS account 025988853303)
- job status: QHost `GET /api/v1/runs` for the run_id

`E` = the wait stack's exec order wt. WAIT = the `check-wait::api` row
(`dependencies.prior_all == true`, `retries == -1`).

| scenario | run.py | pass condition |
|---|---|---|
| a | `set_parallel(); ok; ok; ok; wait_all(); ok` | WAIT row exists; `E.025.dependencies.queue_ids == [WAIT]`; `E.020.started_at` later than every `completed_at` of `E.005..E.015`; `E.025.started_at` later than `E.020.completed_at`; job `completed` |
| b | `set_parallel(); ok; bad; ok; wait_all(); ok` | `E.010` settles `failed` with `retries == 0`; job `failed`; WAIT and `E.025` never `completed`; `E.025.started_at` absent |
| c | as b, `bad` has `must_succeed=false` | `E.010` `failed`; WAIT `completed`; `E.025` `completed`; job `completed` |
| d1 | `set_parallel(); bad; bad; slow; wait_all(must_complete=True); ok` | the job's failure is decided only after `E.015` (slow) `completed_at`; job `failed`; `E.025` never starts |
| d2 | as d1, both `bad` `must_succeed=false` | WAIT `completed` after `E.015`; `E.025` `completed`; job `completed` |
| e | `set_parallel(); wait_test_child(slow); wait_all(); ok` | `E.010.started_at` (WAIT) later than `E.005.005.completed_at` (the grandchild slow order) |
| g | `slow; set_parallel(); ok; ok; wait_all(); ok` | `E.020.started_at` later than `E.005.completed_at` |
| h | `set_parallel(); child(fast) as B; child(slow) as C; wait_all(); ok` | `E.005.020.started_at` (WAIT-B) earlier than `E.010.005.completed_at` (C's slow); `E.015.started_at` (WAIT-A) not earlier than every `E.*.completed_at` (compare full-precision timestamps); job `completed`. B's post-wait order finishing before C's slow is a race, not a pass condition. WAIT-B later than C's slow = scope leaked = FAIL |
