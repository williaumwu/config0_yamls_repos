"""Test stack for CON-131 phase 4 acceptance: submit calls to one per-run agent server,
then read each call's agent_result row in the same run, then remove the server.

Built only from shipped stacks, with agent_submit_per_run's arguments:
  1. config0-hub:::aws::agent_server, jobs [server], lifetime per_run, the exact grants
     (the artifact prefix, the calls' key sets and the repository credential set);
  2. one config0-hub:::aws::agent_submit per call, all to that server's hostname;
  3. one config0-hub:::config0_core::empty_stack per call whose description is
     selector:::<result_selector>::result_ref: the next deterministic order reads the
     call's agent_result row (filter.resource_type agent_result, keys.name the call
     name, must_be_one, scoped to this run) when it fires, as agent_attempts does;
  4. config0-hub:::config0_core::delete_resource of the server row, must_exists.

phase 4's agent_submit_per_run removes the server right after the submit order and
inserts no reader, and a dependent config0.yaml stack runs in a new run, where the
run-scoped row is filtered out; this stack supplies the in-run reader.

calls: a JSON list of {"call_name", "adapter", "model", "key_set_name",
"result_selector"}, each optionally with its own "task" (else the stack's task);
result_selector names a selector in config0.yaml listed on this stack. A call name
used twice fails at the second call's finalize pass (step 8). max_concurrent, when
set, is the server's daemon slot count (agent_server's tfvar), for the cancel check.
"""

import json

SUBMIT_SHARED = (
    "task", "task_schema", "repository_url", "branch", "repository_credential_set_name",
    "max_turns", "max_budget_usd", "artifact_prefix", "phase2complete_timeout",
)
CALL_KEYS = {"call_name", "adapter", "model", "key_set_name", "result_selector"}
CALL_OPTIONAL = {"task"}


def run(stackargs):

    stack = newStack(stackargs)

    stack.parse.add_required(key="subnet_id", types="str")
    stack.parse.add_required(key="aws_default_region", types="str")
    stack.parse.add_optional(key="public_subnet", default=False, types="bool")
    stack.parse.add_required(key="calls", types="str")
    stack.parse.add_required(key="task", types="str")
    stack.parse.add_required(key="task_schema", types="str")
    stack.parse.add_required(key="repository_url", types="str")
    stack.parse.add_optional(key="branch", default="", types="str")
    stack.parse.add_optional(key="repository_credential_set_name", types="str")
    stack.parse.add_required(key="max_turns", types="int")
    stack.parse.add_required(key="max_budget_usd", types="float")
    stack.parse.add_required(key="artifact_prefix", types="str")
    stack.parse.add_optional(key="phase2complete_timeout", default=1800, types="int")
    stack.parse.add_optional(key="run_timeout", default=7200, types="int")
    stack.parse.add_optional(key="max_concurrent", types="int")

    stack.add_substack("config0-hub:::aws::agent_server")
    stack.add_substack("config0-hub:::aws::agent_submit")
    stack.add_substack("config0-hub:::config0_core::empty_stack")
    stack.add_substack("config0-hub:::config0_core::delete_resource")

    stack.init_variables()
    stack.init_substacks()

    calls = json.loads(stack.calls)
    if not isinstance(calls, list) or not calls:
        raise ValueError("calls must be a non-empty JSON list")
    for call in calls:
        if not CALL_KEYS <= set(call) <= CALL_KEYS | CALL_OPTIONAL:
            raise ValueError(f"each call has {sorted(CALL_KEYS)}, optionally {sorted(CALL_OPTIONAL)}; got {sorted(call)}")

    hostname = f"ai-{stack.run_id.replace('_', '-')}"

    key_set_names = sorted({call["key_set_name"] for call in calls})
    if stack.get_attr("repository_credential_set_name"):
        key_set_names.append(stack.repository_credential_set_name)

    server_arguments = {"jobs": ["server"],
                        "hostname": hostname,
                        "subnet_id": stack.subnet_id,
                        "public_subnet": stack.public_subnet,
                        "aws_default_region": stack.aws_default_region,
                        "artifact_prefix": stack.artifact_prefix,
                        "key_set_names": ",".join(key_set_names),
                        "lifetime": "per_run"}
    if stack.get_attr("max_concurrent"):
        server_arguments["max_concurrent"] = stack.max_concurrent
    stack.agent_server.insert(display=True,
                              arguments=server_arguments,
                              human_description=f"Create the per-run agent server {hostname}")
    stack.wait_all()

    shared = {key: stack.get_attr(key) for key in SUBMIT_SHARED if stack.get_attr(key) is not None}
    for call in calls:
        arguments = dict(shared, hostname=hostname, call_name=call["call_name"],
                         adapter=call["adapter"], key_set_name=call["key_set_name"])
        if call["model"]:
            arguments["model"] = call["model"]
        if call.get("task"):
            arguments["task"] = call["task"]
        stack.agent_submit.insert(display=True,
                                  arguments=arguments,
                                  human_description=f'Submit "{call["call_name"]}" to {hostname}')
    stack.wait_all()

    for call in calls:
        stack.empty_stack.insert(display=True,
                                 arguments={"description": f"selector:::{call['result_selector']}::result_ref"},
                                 human_description=f'Read the result of "{call["call_name"]}"')
    stack.wait_all()

    stack.delete_resource.insert(display=True,
                                 arguments={"resource_type": "server",
                                            "hostname": hostname,
                                            "must_exists": "true"},
                                 human_description=f"Remove the per-run agent server {hostname}")

    return stack.get_results()
