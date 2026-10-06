"""Run-mode acceptance fixture. No AWS resources, only shell orders and QHost rows."""

from typing import Any


class Main(newSchedStack):
    def __init__(self, stackargs: dict[str, Any]) -> None:
        newSchedStack.__init__(self, stackargs)
        self.parse.add_required(key="output_name", types="str")
        self.parse.add_optional(key="fail", default=False, types="bool")
        self.parse.add_optional(key="dependency_name", default=None, types="str")

    def run_produce(self) -> None:
        stack = self.stack
        stack.init_variables()
        value = {"producer_run_id": stack.run_id}
        if stack.dependency_name:
            value["upstream"] = stack.get_run_output(stack.dependency_name)
        stack.record_vars_set(values={
            "name": stack.output_name,
            "producer_run_id": stack.run_id,
            "value": value,
        })
        stack.add_external_cmd(
            cmd="exit 1" if stack.fail else "echo produced",
            role="external/cli/execute",
        )

    def run_consume(self) -> None:
        stack = self.stack
        stack.init_variables()
        rows = stack.get_resource(
            name=stack.output_name,
            resource_type="vars_set",
            ref_schedule_id=stack.schedule_id,
            must_be_one=True,
        )
        stack.record_run_output(value={
            "consumer_run_id": stack.run_id,
            "producer_run_id": rows[0]["producer_run_id"],
            "value": rows[0]["value"],
        })
        stack.add_external_cmd(cmd="echo consumed", role="external/cli/execute")

    def run_handle_failure(self) -> None:
        stack = self.stack
        stack.init_variables()
        stack.record_run_output(value={"failure_handled": True, "run_id": stack.run_id})
        stack.add_external_cmd(cmd="echo failure-handled", role="external/cli/execute")

    def run(self) -> Any:
        self.stack.unset_parallel(sched_init=True)
        self.add_job("produce")
        self.add_job("consume")
        self.add_job("handle_failure")
        return self.finalize_jobs()

    def schedule(self) -> Any:
        sched = self.new_schedule()
        sched.job = "produce"
        sched.archive.timeout = 180
        sched.archive.timewait = 1
        sched.on_success = ["consume"]
        sched.on_failure = ["handle_failure"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "consume"
        sched.archive.timeout = 180
        sched.archive.timewait = 1
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "handle_failure"
        sched.archive.timeout = 180
        sched.archive.timewait = 1
        self.add_schedule()
        return self.get_schedules()
