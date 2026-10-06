"""Offline contract checks. Uses the same schedule capture as SaaS dispatch."""

from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
CODE = Path(os.environ["CODE_ROOT"])
for package in sorted((CODE / "src/packages").iterdir(), reverse=True):
    if package.is_dir():
        source = package / "src"
        sys.path.insert(0, str(source if source.is_dir() else package))
sys.path.insert(0, str(CODE / "src/services/aws/config0-saas-api"))

from config0_saas_api.projectlib.execution.runner import execute_stack_schedule  # noqa: E402
from config0_saas_api.projectlib.models.schedule_rows import born_retries_by_job  # noqa: E402
from config0_saas_api.projectlib.yaml_parser_v2 import parse_config0_yaml  # noqa: E402
from scan_stacks.stack_parser import introspect_stack  # noqa: E402

RUN_PY = ROOT / "stacks/_config0_configs/run_modes_test/_files/run.py"
FQN = "williaumwu:::config0_yamls_repos::run_modes_test"


class TestRunModeFixtures(unittest.TestCase):
    def test_scan_captures_fixture_arguments(self) -> None:
        result = introspect_stack(RUN_PY.read_text(), {}, "run_modes_test")
        self.assertTrue(result.success, result.error_message)
        self.assertEqual([var.key for var in result.required_vars], ["output_name"])
        self.assertEqual([var.key for var in result.optional_vars], ["fail", "dependency_name"])
        self.assertEqual(result.dependencies, [])

    def test_three_jobs_and_failure_only_handler(self) -> None:
        captured = execute_stack_schedule(RUN_PY, {"asset_name": "run_modes_test"})
        self.assertIsNone(captured["error"])
        self.assertEqual(captured["stack_type"], "class")
        by_job = {row["job"]: row for row in captured["schedules"]}
        self.assertEqual(list(by_job), ["produce", "consume", "handle_failure"])
        self.assertEqual(by_job["produce"]["on_success"], ["consume"])
        self.assertEqual(by_job["produce"]["on_failure"], ["handle_failure"])
        self.assertEqual(
            born_retries_by_job(captured["schedules"]),
            {"produce": 1, "consume": 0, "handle_failure": 0},
        )
        for row in captured["schedules"]:
            self.assertEqual(row["archive"], {"timeout": 180, "timewait": 1})

    def test_v2_scenarios(self) -> None:
        expected = {
            "on-failure": [("failure", [], True, None)],
            "stage-replay": [("staged", [], False, None)],
            "stack-replay": [
                ("upstream", [], False, None),
                ("middle", ["upstream"], False, "upstream"),
                ("downstream", ["middle"], False, "middle"),
            ],
            "schedule-chain": [
                ("first", [], False, None),
                ("second", ["first"], False, "first"),
            ],
        }
        names = set()
        for scenario, schedules in expected.items():
            path = ROOT / f"run-modes-{scenario}/config0.yaml"
            with self.subTest(scenario=scenario):
                parsed = parse_config0_yaml(path.read_text())
                rows = parsed["schedules"]
                self.assertEqual(len(rows), len(schedules))
                for row, (name, dependencies, fail, dependency_name) in zip(rows, schedules, strict=True):
                    self.assertEqual(row["sched_name"], name)
                    content = row["sched_content"]
                    self.assertEqual(content["stack_name"], FQN)
                    self.assertEqual(row["dependencies"], dependencies)
                    self.assertEqual(content["arguments"].get("fail", False), fail)
                    self.assertEqual(content["arguments"].get("dependency_name"), dependency_name)
                    output_name = content["arguments"]["output_name"]
                    self.assertNotIn(output_name, names)
                    names.add(output_name)


if __name__ == "__main__":
    unittest.main()
