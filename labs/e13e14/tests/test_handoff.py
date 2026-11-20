import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from handoff_a_to_b import make_handoff


def artifact(path, root, job_id):
    data = path.read_bytes()
    return {
        "uri": f"artifact://{job_id}/{path.relative_to(root).as_posix()}",
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sha = "a" * 40
        self.job = "job-example"
        self.trace = "trace-example"
        inner = self.root / "incremental-report.json"
        inner.write_text('{"findings": []}\n')
        stage = {
            "schema_version": "e11e12-1",
            "kind": "incremental-check",
            "status": "SUCCEEDED",
            "commit": self.sha,
            "job_id": self.job,
            "trace_id": self.trace,
            "data": {"commit": self.sha, "findings": []},
            "artifacts": [artifact(inner, self.root, self.job)],
        }
        stage_path = self.root / "incremental-check.json"
        stage_path.write_text(json.dumps(stage) + "\n")
        result = {
            "schema_version": "e11e12-1",
            "status": "SUCCEEDED",
            "target_commit": self.sha,
            "job_id": self.job,
            "trace_id": self.trace,
            "stages": [
                {"name": "incremental-check", "artifact": artifact(stage_path, self.root, self.job)}
            ],
        }
        self.result_path = self.root / "result.json"
        self.result_path.write_text(json.dumps(result) + "\n")

    def test_live_a_report_becomes_b_input_with_provenance(self):
        handoff = make_handoff(self.result_path, self.sha)
        self.assertEqual(handoff["kind"], "fixed-md")
        self.assertEqual(handoff["data"]["commit"], self.sha)
        self.assertEqual(handoff["source_report"]["job_id"], self.job)

    def test_changed_inner_artifact_is_rejected(self):
        (self.root / "incremental-report.json").write_text('{"findings": ["changed"]}\n')
        with self.assertRaisesRegex(ValueError, "hash or size mismatch"):
            make_handoff(self.result_path, self.sha)

    def test_other_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "another target commit"):
            make_handoff(self.result_path, "b" * 40)

    def test_multiple_incremental_check_stages_are_rejected(self):
        # A 的结果目录混入多轮报告时，stages 里会出现不止一个 incremental-check，
        # make_handoff 必须拒绝，而不是默默取第一个。
        result = json.loads(self.result_path.read_text())
        result["stages"].append(dict(result["stages"][0]))
        self.result_path.write_text(json.dumps(result) + "\n")
        with self.assertRaisesRegex(ValueError, "one incremental-check stage"):
            make_handoff(self.result_path, self.sha)

    def test_changed_stage_artifact_is_rejected(self):
        stage_path = self.root / "incremental-check.json"
        data = bytearray(stage_path.read_bytes())
        data[0] ^= 0x01
        stage_path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "hash or size mismatch"):
            make_handoff(self.result_path, self.sha)

    def test_artifact_uri_from_other_job_is_rejected(self):
        result = json.loads(self.result_path.read_text())
        uri = result["stages"][0]["artifact"]["uri"]
        result["stages"][0]["artifact"]["uri"] = uri.replace(
            "artifact://job-example/", "artifact://job-other/", 1
        )
        self.result_path.write_text(json.dumps(result) + "\n")
        with self.assertRaisesRegex(ValueError, "another job"):
            make_handoff(self.result_path, self.sha)


if __name__ == "__main__":
    unittest.main()
