"""E6 证据完整性：重跑必须使用全新的空输出目录。"""
import os
import tempfile
import unittest
from pathlib import Path

from draft.autobuild import auto_build

BROKEN = (
    "FROM python:3.13-slim\n"
    "WORKDIR /work\n"
    "COPY main.c Makefile ./\n"
    "RUN make\n"
    'CMD ["./hello"]\n'
)
CANDIDATE = (
    "FROM python:3.13-slim@sha256:" + "a" * 64 + "\n"
    "WORKDIR /work\n"
    "COPY main.c Makefile ./\n"
    "RUN apt-get update && apt-get install -y build-essential\n"
    "RUN make\n"
    'CMD ["./hello"]\n'
)


class OutputDirectoryGuardTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "posix", "auto_build requires the Linux service container")
    def test_non_empty_output_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = root / "fixture"
            fixture.mkdir()
            (fixture / "Dockerfile.broken").write_text(BROKEN, encoding="utf-8")
            candidate = root / "candidate.Dockerfile"
            candidate.write_text(CANDIDATE, encoding="utf-8")

            output = root / "out"
            output.mkdir()
            (output / "stale-result.json").write_text("{}", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Use a fresh empty output directory"):
                auto_build(fixture, candidate, output, "hello E3")


if __name__ == "__main__":
    unittest.main()
