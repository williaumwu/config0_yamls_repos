# Supported run modes, CON-50

Prepared fixtures, not a live acceptance result. No AWS resource is created by
these stacks. They emit `echo` or `exit 1` orders and write QHost resource rows.

The public repo contains one Class Helper asset,
`williaumwu:::config0_yamls_repos::run_modes_test`. Its jobs are:

```
produce, writes a durable vars_set and emits a shell order
+-- on_success -> consume, reads that vars_set and records run_output
`-- on_failure -> handle_failure, records failure_handled and emits echo
```

`vars_set` is persistent by its explicit name. `run_output` is scoped to each
run. Stage replay can therefore read the skipped producer's stored value without
copying the old run's private `run_store`. Across stacks, `dependency_name`
uses the existing `dependency_run_ids` and `get_run_output` machinery.

## Before the later live run

1. Land the CON-49 browser assertion on code main. Publish this public test
   repo commit when the requester authorizes the push. These files were not
   pushed during preparation.
2. Have the test tenant onboarded in `ap-northeast-1` with current runtime
   packages, SaaS API, QHost, hub, worker and coordinator.
3. Scan `williaumwu/config0_yamls_repos`, branch `main`, through the existing
   Assets scan UI. Wait for stack assembly. Confirm the `run_modes_test` asset
   has a versioned `doc.json` and `run.py`. A config folder alone does not
   publish an authored stack.
4. Export `SAAS_API_LAMBDA_URL`, `QHOST_URL`, and `RECORD_DIR`. Keep the
   authenticated test user's Clerk JWT in `CLERK_JWT_FILE` and a current,
   tenant-scoped QHost JWT in `QHOST_JWT_FILE`, both under the existing excluded
   credentials directory. Renew those files through the existing token issuer
   when they expire. No token belongs in a fixture or retained response.
5. Use new project names below, or explicitly remove an earlier campaign's
   projects first. The output names are deliberately fixed and distinct by
   scenario. Do not run two copies of the same scenario concurrently.

## Local preparation check

```bash
task -d ~/project/williaumwu/config0_yamls_repos/run-modes check \
  CODE_ROOT=/home/gary/project/repos/jiffy-rewrite-2026
```

This runs real v2 parsing, scan declaration introspection and SaaS schedule
capture, not the live jobs. It checks the only start gate, both trigger edges,
explicit timeouts and the four configs' dependencies.

## Create the four projects through the existing wizard

Run these serially on main. Each command uses the existing Story 06 spec's
config-path and project-name inputs. It proves submission and the Convex entry's
`adding` to `active` transition. It does not prove that the jobs have settled.
Retain the task output, Playwright report and screenshots for each command.

```bash
STORY06_PROJECT_NAME=con50-on-failure \
STORY06_CONFIG_PATH=run-modes-on-failure/config0.yaml \
task -d ~/project/repos/jiffy-rewrite-2026-ops e2e:williaumwu:run-spec \
  SPEC=e2e/add-story06-longbuild-e2e.spec.ts

STORY06_PROJECT_NAME=con50-stage-replay \
STORY06_CONFIG_PATH=run-modes-stage-replay/config0.yaml \
task -d ~/project/repos/jiffy-rewrite-2026-ops e2e:williaumwu:run-spec \
  SPEC=e2e/add-story06-longbuild-e2e.spec.ts

STORY06_PROJECT_NAME=con50-stack-replay \
STORY06_CONFIG_PATH=run-modes-stack-replay/config0.yaml \
task -d ~/project/repos/jiffy-rewrite-2026-ops e2e:williaumwu:run-spec \
  SPEC=e2e/add-story06-longbuild-e2e.spec.ts

STORY06_PROJECT_NAME=con50-schedule-chain \
STORY06_CONFIG_PATH=run-modes-schedule-chain/config0.yaml \
task -d ~/project/repos/jiffy-rewrite-2026-ops e2e:williaumwu:run-spec \
  SPEC=e2e/add-story06-longbuild-e2e.spec.ts
```

## Retain a project snapshot

For each project, set `PROJECT_ID` from its create response, and `LABEL` to the
scenario and observation, for example `stage-before` or `stage-after`.
Run all three reads before and after replay. During dependency chaining, repeat
with a new `LABEL` to retain the order in which the stacks start and settle.
Each request fails on HTTP errors and writes only the returned JSON. There is no
retry, token minting or hidden mutation in this test helper.

```bash
task -d ~/project/williaumwu/config0_yamls_repos/run-modes request \
  URL="$QHOST_URL/api/v1/schedules?project_id=$PROJECT_ID" \
  TOKEN_FILE="$QHOST_JWT_FILE" RECORD="$RECORD_DIR/$LABEL-schedules.json"
task -d ~/project/williaumwu/config0_yamls_repos/run-modes request \
  URL="$QHOST_URL/api/v1/runs?project_id=$PROJECT_ID" \
  TOKEN_FILE="$QHOST_JWT_FILE" RECORD="$RECORD_DIR/$LABEL-runs.json"
task -d ~/project/williaumwu/config0_yamls_repos/run-modes request \
  URL="$QHOST_URL/api/v1/resources?project_id=$PROJECT_ID" \
  TOKEN_FILE="$QHOST_JWT_FILE" RECORD="$RECORD_DIR/$LABEL-resources.json"
```

Keep the worker's job/order logs with these snapshots. The snapshots name the
fresh run ids, producer ids and stored values. A submit response alone is not
acceptance evidence.

## On failure

For `con50-on-failure`, require `produce=failed`, `handle_failure=completed`,
and `consume` dormant. The handler's run_output must contain
`failure_handled=true`. The overall run must finish `failed`, not `completed`.
The deliberate shell command is `exit 1`, not an injected infrastructure fault.

## Stage replay with reused output

Wait for `con50-stage-replay` to complete. Retain `stage-before` snapshots.
Set `PROJECT_ID` to that project and `SCHEDULE_ID` to its `staged` schedule.

```bash
task -d ~/project/williaumwu/config0_yamls_repos/run-modes request \
  METHOD=POST \
  URL="$SAAS_API_LAMBDA_URL/api/v1/projects/$PROJECT_ID/schedules/$SCHEDULE_ID/replay" \
  TOKEN_FILE="$CLERK_JWT_FILE" BODY=stage-replay.json \
  RECORD="$RECORD_DIR/stage-replay-dispatch.json"
```

Use the SaaS replay route directly. The existing BFF schedule-replay route sends
`{}` and does not forward `replay_from_stage`.

Wait for the fresh run to complete. Retain `stage-after` snapshots. Require only
`consume` to execute. `produce` and `handle_failure` must be skipped by replay.
The vars_set's `producer_run_id` and value must be unchanged. The new run_output
must have a new `consumer_run_id` and the old `producer_run_id`. This proves
reuse rather than recomputation.

## Stack replay

Wait for all three `con50-stack-replay` stacks to complete. Retain
`stack-before` snapshots. Set `PROJECT_ID` to that project and `SCHEDULE_ID`
to its `middle` schedule.

```bash
task -d ~/project/williaumwu/config0_yamls_repos/run-modes request \
  METHOD=POST \
  URL="$SAAS_API_LAMBDA_URL/api/v1/projects/$PROJECT_ID/schedules/$SCHEDULE_ID/replay" \
  TOKEN_FILE="$CLERK_JWT_FILE" BODY=stack-replay.json \
  RECORD="$RECORD_DIR/stack-replay-dispatch.json"
```

Require no new `upstream` run. Require a fresh `middle` run followed by a fresh
`downstream` run, never a concurrent downstream dispatch before middle settles.
The new middle output must carry the old upstream output. The new downstream
output must carry the NEW middle run's output. Retain `stack-after` snapshots
and the dispatch and worker logs that show this order.

## Schedule dependency chaining

For `con50-schedule-chain`, require first and second to have distinct run ids.
Second must not start before first completes. Second's recorded
`value.upstream.consumer_run_id` must equal first's run id. Both runs must end
`completed`. Retain snapshots during the chain and after it settles.

## Explicit cleanup

Remove these four projects through the existing project removal UI. Wait for
removal to complete. Require the four Convex entries and their QHost schedules
and vars_set/run_output rows to be absent. Run rows stay: they are history
and have no delete route (run lifecycle contract). No offboard or AWS cleanup is
needed for these fixture stacks themselves, because they create no AWS resources.
