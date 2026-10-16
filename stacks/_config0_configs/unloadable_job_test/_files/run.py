"""CON-91 live repro fixture. No AWS resources, only shell orders.

Job ``bad`` declares a ``conditions.frequency`` the schedule worker cannot
parse. Add-project stores the string as written; nothing upstream checks it.
The schedule worker finds it when it builds the run's jobs, and fails ``bad``
once, when ``ok``'s on_success edge arms it, with the reason on the run
pipeline document. ``bad``'s on_failure edge then arms ``handle``, which runs
like any other job.
"""

from typing import Any


class Main(newSchedStack):
    def __init__(self, stackargs: dict[str, Any]) -> None:
        newSchedStack.__init__(self, stackargs)

    def run_ok(self) -> None:
        stack = self.stack
        stack.init_variables()
        stack.add_external_cmd(cmd="echo ok", role="external/cli/execute")

    def run_bad(self) -> None:
        stack = self.stack
        stack.init_variables()
        stack.add_external_cmd(cmd="echo bad-never-runs", role="external/cli/execute")

    def run_handle(self) -> None:
        stack = self.stack
        stack.init_variables()
        stack.add_external_cmd(cmd="echo handled", role="external/cli/execute")

    def run(self) -> Any:
        self.add_job("ok")
        self.add_job("bad")
        self.add_job("handle")
        return self.finalize_jobs()

    def schedule(self) -> Any:
        sched = self.new_schedule()
        sched.job = "ok"
        sched.archive.timeout = 180
        sched.archive.timewait = 1
        sched.on_success = ["bad"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "bad"
        sched.archive.timeout = 180
        sched.archive.timewait = 1
        sched.conditions.frequency = "every 5 minutes"
        sched.on_failure = ["handle"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "handle"
        sched.archive.timeout = 180
        sched.archive.timewait = 1
        self.add_schedule()
        return self.get_schedules()
