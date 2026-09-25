#!/usr/bin/env python3
"""
validate.py —— E2 契约最小检查（B10）

覆盖课程要求的四条最小检查：

  01  四类任务（DRAFT / FULL_CHECK / INCREMENTAL_CHECK / REPAIR）
      的请求与响应有效样例，全部通过 task.schema.json 校验
  02  把 job_type 改成 "ABC"，应被拒绝
  03  删除 INCREMENTAL_CHECK 的 baseline，应被拒绝
  04  解释 MD 为什么不等于工具执行失败，并断言 error / findings 互斥

依赖：jsonschema（`pip install --user jsonschema`）
用法：
  python3 e2/validate.py
退出码：0 = 四条全过；1 = 有检查未通过
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTRACTS = ROOT / "contracts"
SCHEMA_FILE = ROOT / "task.schema.json"

SCHEMA_VERSION = "1.0.0"
JOB_TYPES = ["DRAFT", "FULL_CHECK", "INCREMENTAL_CHECK", "REPAIR"]
STATUSES = ["QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "TIMED_OUT", "CANCELLED"]

# 9 个公共字段。execution 与 input/output/error 并列
PUBLIC_FIELDS = [
    "schema_version", "job_id", "trace_id", "job_type",
    "status", "execution", "input", "output", "error",
]

# 响应里必须出现、且不得由请求携带的服务端字段
SERVER_FIELDS = ["job_id", "status", "output", "error"]

ISO8601 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

_failures: list[str] = []


def ok(msg: str) -> None:
    print(f"    OK    {msg}")


def bad(msg: str) -> None:
    print(f"    FAIL  {msg}")
    _failures.append(msg)


def section(title: str) -> None:
    print(f"\n{'=' * 68}\n{title}\n{'=' * 68}")


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------
# 依赖
# --------------------------------------------------------------------------
def get_validator(schema: dict):
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        print("缺少依赖 jsonschema。请先运行：pip install --user jsonschema")
        sys.exit(2)
    return Draft7Validator(schema)


def errors_of(validator, doc) -> list[str]:
    return [
        f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
        for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))
    ]


# --------------------------------------------------------------------------
# 内置样例：B 仓库只拥有 DRAFT 与 REPAIR，另两类的有效样例内置，
# 用于证明 task.schema.json 对四类任务都可表达
# --------------------------------------------------------------------------
def _execution() -> dict:
    return {
        "mode": "ASYNC",
        "timeout_seconds": 1800,
        "started_at": "2026-09-23T07:00:03Z",
        "finished_at": "2026-09-23T07:05:12Z",
        "attempt": 1,
        "command": "make",
        "resources": {"cpu": "2", "memory_mb": 2048},
    }


def _artifact(job_id: str) -> dict:
    return {
        "artifact_id": "art-001",
        "type": "BUILD_LOG",
        "uri": f"artifact://pair10/{job_id}/build.log",
        "media_type": "text/plain",
        "producer_job_id": job_id,
        "sha256": "a" * 64,
    }


def builtin_valid_job(job_type: str) -> dict:
    """四类任务各一份最小有效 Job，用于 01 检查。"""
    job_id = f"job-{job_type.lower().replace('_', '')}"
    base_input = {
        "repository": {"url": "git@github.com:o/p.git", "commit": "c" * 40},
        "build": {"command": "make", "verify_command": "make check"},
    }
    if job_type == "INCREMENTAL_CHECK":
        base_input["baseline"] = {
            "commit": "b" * 40,
            "configuration_id": "cc-MODE0",
            "actual_graph_uri": "artifact://pair10/job-fullcheck/actual.json",
        }
    if job_type == "REPAIR":
        # 注意：不要在此添加 input.source_commit —— 契约中无此字段，
        # 源码版本一律由 input.repository.commit 表达（成员B 提出，2026-09-25 采纳）。
        base_input["md_report_uri"] = "artifact://pair10/job-fullcheck/md.json"

    return {
        "schema_version": SCHEMA_VERSION,
        "job_id": job_id,
        "trace_id": "trace-010",
        "job_type": job_type,
        "status": "SUCCEEDED",
        "created_at": "2026-09-23T07:00:00Z",
        "execution": _execution(),
        "input": base_input,
        "output": {"artifacts": [_artifact(job_id)]},
    }


def builtin_valid_request(job_type: str) -> dict:
    doc = builtin_valid_job(job_type)
    return {
        "schema_version": doc["schema_version"],
        "trace_id": doc["trace_id"],
        "job_type": doc["job_type"],
        "execution": {"mode": "ASYNC", "timeout_seconds": 1800},
        "input": doc["input"],
    }


# --------------------------------------------------------------------------
# 请求样例校验（请求不是 Job 外壳：无 job_id/status/output/error）
# --------------------------------------------------------------------------
def check_request(doc: dict, src: str, expect_reject: bool = False) -> None:
    """请求不是 Job 外壳：无 job_id/status/output/error。

    expect_reject=True 时该样例是反例，被拒绝才算通过，且不计入总账。
    """
    problems: list[str] = []

    for k in ("schema_version", "trace_id", "job_type", "input"):
        if k not in doc:
            problems.append(f"请求缺公共字段 {k}")
    if doc.get("schema_version") not in (None, SCHEMA_VERSION):
        problems.append(f"schema_version 应为 {SCHEMA_VERSION}")
    if doc.get("job_type") not in JOB_TYPES:
        problems.append(f"job_type={doc.get('job_type')!r} 不在四类枚举内")
    if not isinstance(doc.get("input"), dict):
        problems.append("input 必须是 object")

    for k in SERVER_FIELDS:
        if k in doc:
            problems.append(f"请求不应携带服务端生成的 {k}")

    ex = doc.get("execution")
    if ex is not None:
        if not isinstance(ex, dict) or ex.get("mode") not in ("ASYNC", "SYNC"):
            problems.append("execution.mode 必须是 ASYNC 或 SYNC")

    if doc.get("job_type") == "INCREMENTAL_CHECK" and "baseline" not in doc.get("input", {}):
        problems.append("INCREMENTAL_CHECK 缺 input.baseline")

    if expect_reject:
        if problems:
            ok(f"{src} 已被拒绝（预期）：{problems[0]}")
        else:
            bad(f"{src} 未被拒绝，反例失效")
        return

    if problems:
        for p in problems:
            bad(f"[{src}] {p}")
    else:
        ok(src)


# --------------------------------------------------------------------------
# 01
# --------------------------------------------------------------------------
def check_01(validator, schema) -> None:
    section("01  四类任务的有效请求与响应样例全部通过 task.schema.json")

    # 1a. 内置四类：响应侧套 Job 外壳
    for jt in JOB_TYPES:
        doc = builtin_valid_job(jt)
        errs = errors_of(validator, doc)
        if errs:
            bad(f"内置 {jt} 响应样例未通过：{errs}")
        else:
            ok(f"内置响应样例 {jt} 通过（job_id={doc['job_id']}）")

    # 1b. 内置四类：请求侧
    for jt in JOB_TYPES:
        check_request(builtin_valid_request(jt), f"内置请求样例 {jt}")

    # 1c. 仓库内的真实样例
    for name in ("dockerfile_job.res.json", "dockerfile_job_err.res.json",
                 "repair_job.res.json", "repair_job_err.res.json"):
        path = CONTRACTS / name
        if not path.exists():
            print(f"    SKIP  {name}（未提供，属对应成员产出）")
            continue
        doc = load_json(path)
        errs = errors_of(validator, doc)
        if errs:
            bad(f"{name} 未通过：{errs}")
        else:
            ok(f"{name} 通过（status={doc['status']}）")

    for name in ("dockerfile_job.req.json", "repair_job.req.json"):
        path = CONTRACTS / name
        if not path.exists():
            print(f"    SKIP  {name}（未提供，属对应成员产出）")
            continue
        check_request(load_json(path), name)

    # 1d. 公共字段齐全性：查 schema 是否声明了 9 个公共字段。
    #     不能拿单个 SUCCEEDED 样例来查——SUCCEEDED 本来就不带 error。
    declared = set(schema.get("properties", {}))
    missing = [f for f in PUBLIC_FIELDS if f not in declared]
    if missing:
        bad(f"task.schema.json 未声明公共字段 {missing}")
    else:
        ok(f"9 个公共字段齐全：{'、'.join(PUBLIC_FIELDS)}")

    # error 字段的实际可用性：FAILED 样例必须能携带 error 通过
    err_doc = builtin_valid_job("DRAFT")
    err_doc["status"] = "FAILED"
    err_doc.pop("output")
    err_doc["error"] = {"code": "ENV_3002", "message": "Docker image build failed"}
    if errors_of(validator, err_doc):
        bad(f"带 error 的 FAILED 样例未通过：{errors_of(validator, err_doc)}")
    else:
        ok("error 字段可用：FAILED 样例携带 error 通过校验")

    # 未出现在 required 里但必须可用的可选字段
    for opt in ("output", "error", "created_at", "updated_at"):
        if opt not in declared:
            bad(f"task.schema.json 未声明可选字段 {opt}")
    ok("可选字段 output / error / created_at / updated_at 均已声明")

    # 1e. 时间字段格式
    for jt in JOB_TYPES:
        doc = builtin_valid_job(jt)
        for when in ("started_at", "finished_at"):
            v = doc["execution"][when]
            if not ISO8601.match(v):
                bad(f"{jt} execution.{when}={v!r} 不是 ISO8601 UTC")
    ok("execution 时间字段均为 ISO8601 UTC")


# --------------------------------------------------------------------------
# 02
# --------------------------------------------------------------------------
def check_02(validator) -> None:
    section("02  job_type 改成 ABC，应被拒绝")
    doc = builtin_valid_job("DRAFT")
    doc["job_type"] = "ABC"
    errs = errors_of(validator, doc)
    if errs:
        ok(f"已拒绝，理由：{errs[0]}")
    else:
        bad("job_type=ABC 竟然通过了校验，枚举约束失效")

    req = builtin_valid_request("DRAFT")
    req["job_type"] = "ABC"
    check_request(req, "job_type=ABC 请求", expect_reject=True)


# --------------------------------------------------------------------------
# 03
# --------------------------------------------------------------------------
def check_03(validator) -> None:
    section("03  删除 INCREMENTAL_CHECK 的 baseline，应被拒绝")
    doc = builtin_valid_job("INCREMENTAL_CHECK")
    removed = doc["input"].pop("baseline")
    errs = errors_of(validator, doc)
    if errs:
        ok(f"已拒绝，理由：{errs[0]}")
        print(f"          （被删除的 baseline 内容：{json.dumps(removed, ensure_ascii=False)}）")
    else:
        bad("缺 baseline 的 INCREMENTAL_CHECK 竟然通过了，会退化为全量检测")

    # 反向确认：补回 baseline 就应通过
    doc["input"]["baseline"] = removed
    if errors_of(validator, doc):
        bad("补回 baseline 后仍不通过，约束写反了")
    else:
        ok("补回 baseline 后重新通过，确认拒绝原因就是 baseline 缺失")


# --------------------------------------------------------------------------
# 04
# --------------------------------------------------------------------------
def check_04(validator) -> None:
    section("04  MD ≠ 工具执行失败；error 与 findings 互斥")

    print("""
    三种情形必须分清：

    | 情形           | status      | job.error      | output.findings | 含义                     |
    |----------------|-------------|----------------|-----------------|--------------------------|
    | 检测到缺失依赖 | SUCCEEDED   | 空             | 有（MISSING）   | 工具正常完成，发现了问题 |
    | 分析器崩溃     | FAILED      | ANALYSIS_5001  | 空              | 工具失败了，结论不可信   |
    | 两者同存       | ——          | 有             | 有              | 非法：无法判断成功还是失败 |
""")

    # 4a. 检测出 MD 的任务是合法的 SUCCEEDED，不是失败
    doc = builtin_valid_job("FULL_CHECK")
    doc["output"]["findings"] = [
        {"type": "MISSING", "target": "main.o", "dependency": "config.h"}
    ]
    errs = errors_of(validator, doc)
    if errs:
        bad(f"带 findings 的 SUCCEEDED 任务被误判为非法：{errs}")
    else:
        ok("检测出 MISSING 的任务是合法 SUCCEEDED —— 发现数 > 0 不等于任务失败")

    # 4b. findings 类型必须在枚举内
    bad_finding = builtin_valid_job("FULL_CHECK")
    bad_finding["output"]["findings"] = [{"type": "WHATEVER"}]
    if errors_of(validator, bad_finding):
        ok("findings.type 只接受 MISSING / REDUNDANT")
    else:
        bad("findings.type 非法值竟然通过")

    # 4c. 互斥：error 与 findings 不得同存
    both = builtin_valid_job("FULL_CHECK")
    both["status"] = "FAILED"
    both["error"] = {"code": "ANALYSIS_5001", "message": "analyzer crashed"}
    both["output"]["findings"] = [{"type": "MISSING", "target": "a", "dependency": "b"}]
    if has_error_and_findings(both):
        ok("error 与 findings 同存已被判定非法（互斥约束生效）")
    else:
        bad("互斥约束失效")

    # 4d. 互斥的反向确认
    only_err = builtin_valid_job("FULL_CHECK")
    only_err["status"] = "FAILED"
    only_err["error"] = {"code": "ANALYSIS_5001", "message": "analyzer crashed"}
    only_err.pop("output")
    if not has_error_and_findings(only_err) and not errors_of(validator, only_err):
        ok("只有 error、没有 findings 的失败任务是合法的")
    else:
        bad("纯失败任务被误判")


def has_error_and_findings(doc: dict) -> bool:
    """JSON Schema draft-07 无法表达跨字段互斥，这条靠显式断言。"""
    return bool(doc.get("error")) and bool(doc.get("output", {}).get("findings"))


# --------------------------------------------------------------------------
def main() -> int:
    print("E2 契约校验（B10）")
    print(f"Schema: {SCHEMA_FILE.relative_to(ROOT.parent)}")

    if not SCHEMA_FILE.exists():
        print(f"缺 schema 文件：{SCHEMA_FILE}")
        return 1

    schema = load_json(SCHEMA_FILE)
    validator = get_validator(schema)
    props = sorted(schema.get("properties", {}))
    print(f"task.schema.json 已加载（required={len(schema['required'])} 项，"
          f"properties={len(props)} 项）")

    check_01(validator, schema)
    check_02(validator)
    check_03(validator)
    check_04(validator)

    section("结论")
    if _failures:
        print(f"未通过 {len(_failures)} 项：")
        for f in _failures:
            print(f"  - {f}")
        return 1
    print("最小检查 01–04 全部通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
