import json
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pipeline
import server

class Contracts(unittest.TestCase):
    def report(self):return {'schema_version':'e11e12-1','kind':'incremental-check','commit':'a'*40,'status':'SUCCEEDED'}
    def test_accept_current_report(self):pipeline.check_envelope(self.report(),'a'*40,'incremental-check')
    def test_reject_old_commit(self):
        with self.assertRaisesRegex(pipeline.Failure,'another commit'):pipeline.check_envelope(self.report(),'b'*40)
    def test_reject_schema(self):
        r=self.report();r['schema_version']='old'
        with self.assertRaises(pipeline.Failure):pipeline.check_envelope(r,'a'*40)
    def test_reject_failed_upstream(self):
        r=self.report();r['status']='FAILED'
        with self.assertRaises(pipeline.Failure):pipeline.check_envelope(r,'a'*40)
    def test_reject_wrong_artifact_kind(self):
        with self.assertRaises(pipeline.Failure):pipeline.check_envelope(self.report(),'a'*40,'fixed-md')
    def test_artifact_uses_relative_uri_and_content_hash(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'x.json';p.write_text('{}')
            a=pipeline.artifact(p,root,'job-1');self.assertEqual(a['uri'],'artifact://job-1/x.json');self.assertEqual(len(a['sha256']),64)
    def test_existing_evidence_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'keep').write_text('keep')
            with self.assertRaises(pipeline.Failure):pipeline.execute({},root)
            self.assertEqual((root/'keep').read_text(),'keep')
    def test_changed_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'r.json';p.write_text('{}')
            with self.assertRaises(pipeline.Failure):pipeline.load_artifact(p,'0'*64)
    def test_same_key_same_request_same_job(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);store=server.Store(root/'jobs')
            request={'mode':'e11-a','repo':str(pipeline.ROOT/'data/p'),'base':'a','target':'b'}
            with patch.object(store.pool,'submit'):
                one=store.submit(request,'same');two=store.submit(request,'same')
                self.assertEqual(one['job_id'],two['job_id'])
                changed=dict(request,target='c')
                with self.assertRaisesRegex(ValueError,'IDEMPOTENCY_CONFLICT'):store.submit(changed,'same')
            store.pool.shutdown()
    def test_api_rejects_repo_outside_data(self):
        with tempfile.TemporaryDirectory() as d:
            store=server.Store(Path(d)/'jobs')
            with self.assertRaises(ValueError):store.submit({'mode':'e11-a','repo':str(Path(d)),'base':'a','target':'b'},'k')
            store.pool.shutdown()

class Adaptation(unittest.TestCase):
    """E11 自主适配：项目描述、子目录与 macro 风格补丁位置。"""

    MAKEFILE = (
        "DEPS = main.c\n"
        "CFLAGS = -I.\n"
        "main: main.o\n"
        "\tgcc -o main main.o\n"
        "main.o: $(DEPS)\n"
        "\tgcc $(CFLAGS) -c main.c -o main.o\n"
        ".PHONY: clean\n"
        "clean:\n"
        "\trm -f main.o main\n"
    )

    def project(self, directory):
        import lab
        p = Path(directory) / 'proj'
        p.mkdir()
        (p / 'main.c').write_text('#include "extra.h"\n#include <stdio.h>\n#include "config.h"\n'
                                  'int main(void){printf("%s\\n",MESSAGE);return 0;}\n')
        (p / 'config.h').write_text('#define MESSAGE "v1"\n')
        (p / 'extra.h').write_text('#define EXTRA 0\n')
        (p / 'Makefile').write_text(self.MAKEFILE)
        (p / '.lab-project.json').write_text(
            '{"targets":[{"object":"main.o","source":"main.c"}],'
            '"program":"main","build_target":"main","allowed_flags":["-I."],'
            '"header":"config.h","expected_output":"v1",'
            '"header_edit":{"from":"#define MESSAGE \\"v1\\"","to":"#define MESSAGE \\"v2\\""},'
            '"header_output":"v2"}')
        lab.run(['git', 'init', '-b', 'main'], p)
        lab.run(['git', 'config', 'user.name', 'AdaptationTest'], p)
        lab.run(['git', 'config', 'user.email', 'fixture@localhost'], p)
        lab.run(['git', 'add', '-A'], p)
        lab.run(['git', 'commit', '-m', 'C1'], p)
        return p

    def test_default_profile_matches_e8e10(self):
        import lab
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(lab.target_pairs(d), [('main.o', 'main.c'), ('helper.o', 'helper.c')])
            self.assertEqual(lab.profile(d)['program'], 'app')

    def test_descriptor_overrides_targets_and_program(self):
        import lab
        with tempfile.TemporaryDirectory() as d:
            p = self.project(d)
            self.assertEqual(lab.target_pairs(p), [('main.o', 'main.c')])
            prof = lab.profile(p)
            self.assertEqual(prof['program'], 'main')
            self.assertEqual(prof['expected_output'], 'v1')
            self.assertEqual(prof['allowed_flags'], ['-I.'])

    def test_scan_uses_descriptor_targets(self):
        import lab
        with tempfile.TemporaryDirectory() as d:
            p = self.project(d)
            r = lab.scan(p)
            self.assertEqual(sorted(r['actual']), ['main.o'])
            kinds = sorted((f['type'], f['dependency']) for f in r['findings'])
            self.assertEqual(kinds, [('MISSING', 'config.h'), ('MISSING', 'extra.h')])

    def test_macro_style_patch_updates_definition_not_target_line(self):
        import lab
        with tempfile.TemporaryDirectory() as d:
            p = self.project(d)
            diff, edits = lab.patch(p, lab.scan(p))
            self.assertEqual(len(edits), 2)
            self.assertTrue(all(e['style'] == 'macro' for e in edits), edits)
            self.assertIn('-DEPS = main.c', diff)
            self.assertIn('+DEPS = main.c config.h extra.h', diff)
            self.assertNotIn('+main.o:', diff)
            self.assertIn('main.o: $(DEPS)', (p / 'Makefile').read_text())

    def test_subdir_escape_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / 'repo'
            repo.mkdir()
            import lab
            lab.run(['git', 'init', '-b', 'main'], repo)
            lab.run(['git', 'config', 'user.name', 't'], repo)
            lab.run(['git', 'config', 'user.email', 't@e'], repo)
            (repo / 'x.txt').write_text('x')
            lab.run(['git', 'add', '-A'], repo)
            lab.run(['git', 'commit', '-m', 'c'], repo)
            sha = lab.run(['git', 'rev-parse', 'HEAD'], repo).strip()
            out = Path(d) / 'snap'
            logs = Path(d) / 'logs'
            with self.assertRaises(pipeline.Failure):
                pipeline.snapshot(repo, sha, out, logs, subdir='../outside')

    def test_stale_report_carries_error_code(self):
        r = {'schema_version': 'e11e12-1', 'kind': 'incremental-check', 'commit': 'a' * 40,
             'status': 'SUCCEEDED'}
        with self.assertRaises(pipeline.Failure) as ctx:
            pipeline.check_envelope(r, 'c' * 40)
        self.assertEqual(ctx.exception.code, 'STALE_REPORT')


class Student241880171(unittest.TestCase):
    def test_macro_patch_lands_on_definition_line(self):
        """自主任务：macro 风格补丁落在 DEPS 定义行，main.o: $(DEPS) 一字不变。"""
        import lab
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'sample'
            lab.fixture(p, 'macro')
            makefile = p / 'Makefile'
            before = makefile.read_text()
            target_before = [ln for ln in before.splitlines() if ln.startswith('main.o:')]
            report = lab.scan(p)
            diff, edits = lab.patch(p, report)
            # 唯一 MISSING 是 config.h，风格为 macro
            self.assertEqual(edits, [{'target': 'main.o', 'dependency': 'config.h', 'style': 'macro'}])
            # 补丁落在 DEPS 定义行，而非目标行
            self.assertIn('-DEPS = main.c unused.h', diff)
            self.assertIn('+DEPS = main.c unused.h config.h', diff)
            self.assertNotIn('-main.o:', diff)
            self.assertNotIn('+main.o:', diff)
            # 源文件未被修改
            self.assertEqual(makefile.read_text(), before)
            # 应用补丁后，目标行字节级一字不变
            candidate = Path(d) / 'candidate.patch'
            candidate.write_text(diff)
            lab.run(['git', 'apply', str(candidate.resolve())], p)
            after = makefile.read_text()
            target_after = [ln for ln in after.splitlines() if ln.startswith('main.o:')]
            self.assertEqual(target_before, target_after)
            self.assertEqual(target_after, ['main.o: $(DEPS)'])
            # 重检无 MISSING（RD unused.h 允许保留）
            self.assertFalse(any(f['type'] == 'MISSING' for f in lab.scan(p)['findings']))


class Student241880214(unittest.TestCase):
    def test_mixed_style_patch_appends_to_target_line(self):
        import lab
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            lab.fixture(p,'mixed')
            diff,edits=lab.patch(p,lab.scan(p))
            self.assertEqual([e['style'] for e in edits],['mixed'])
            self.assertIn('+main.o: main.c $(HEADERS) config.h',diff)
            self.assertIn('HEADERS = unused.h', (p/'Makefile').read_text())
            self.assertNotIn('HEADERS = unused.h config.h', (p/'Makefile').read_text())
            self.assertEqual(diff.count('+main.o:'),1)

    def _fake_autobuild(self, target, candidate, draft_dir, expected, timeout=600):
        draft_dir.mkdir(parents=True, exist_ok=True)
        (draft_dir / 'result.json').write_text('{"status": "SUCCEEDED"}', encoding='utf-8')
        return {'status': 'SUCCEEDED'}

    def test_fixed_report_sha256_missing_is_backward_compatible(self):
        req = json.loads((pipeline.ROOT / 'data/integration-sample/e11-b.json').read_text(encoding='utf-8'))
        req.pop('fixed_report_sha256', None)
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'out'
            with patch('draft.autobuild.auto_build', side_effect=self._fake_autobuild):
                res = pipeline.execute(req, out)
                self.assertEqual(res['status'], 'SUCCEEDED')
                self.assertNotIn('error', res)

    def test_fixed_report_sha256_mismatch_fails_with_artifact_hash_mismatch(self):
        req = json.loads((pipeline.ROOT / 'data/integration-sample/e11-b.json').read_text(encoding='utf-8'))
        bad_req = dict(req, fixed_report_sha256='0' * 64)
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'out'
            with patch('draft.autobuild.auto_build', side_effect=self._fake_autobuild):
                res = pipeline.execute(bad_req, out)
                self.assertEqual(res['status'], 'FAILED')
                self.assertEqual(res['error']['code'], 'ARTIFACT_HASH_MISMATCH')

    def test_fixed_report_file_missing_fails_explicitly_not_keyerror(self):
        req = json.loads((pipeline.ROOT / 'data/integration-sample/e11-b.json').read_text(encoding='utf-8'))
        missing_req = dict(req, fixed_report='/nonexistent/fixed_report.json')
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'out'
            with patch('draft.autobuild.auto_build', side_effect=self._fake_autobuild):
                res = pipeline.execute(missing_req, out)
                self.assertEqual(res['status'], 'FAILED')
                self.assertNotEqual(res['error']['code'], 'KeyError')
                self.assertIn('No such file or directory', res['error']['message'])

class Student241880237(unittest.TestCase):
    """自主任务：同一目标两条 MISSING 的计划顺序与单行合并。

    项目里 main.c 故意把 #include "extra.h" 写在 #include "config.h" 之前，
    gcc -MM 的原始输出顺序因此是 extra.h、config.h。
    若实现只是照抄 gcc 顺序追加依赖，下面的顺序断言就会失败；
    通过则说明计划顺序由依赖名稳定决定，而不取决于编译器输出顺序。
    """

    MAKEFILE = (
        "CFLAGS = -I.\n"
        "main: main.o\n"
        "\tgcc -o main main.o\n"
        "main.o: main.c\n"
        "\tgcc $(CFLAGS) -c main.c -o main.o\n"
        ".PHONY: clean\n"
        "clean:\n"
        "\trm -f main.o main\n"
    )

    def project(self, directory):
        import lab
        p = Path(directory) / 'proj'
        p.mkdir()
        (p / 'main.c').write_text('#include "extra.h"\n#include "config.h"\n#include <stdio.h>\n'
                                  'int main(void){printf("%s\\n",MESSAGE);return 0;}\n')
        (p / 'config.h').write_text('#define MESSAGE "v1"\n')
        (p / 'extra.h').write_text('#define EXTRA 0\n')
        (p / 'Makefile').write_text(self.MAKEFILE)
        (p / '.lab-project.json').write_text(
            '{"targets":[{"object":"main.o","source":"main.c"}],'
            '"program":"main","build_target":"main","allowed_flags":["-I."],'
            '"header":"config.h","expected_output":"v1",'
            '"header_edit":{"from":"#define MESSAGE \\"v1\\"","to":"#define MESSAGE \\"v2\\""},'
            '"header_output":"v2"}')
        lab.run(['git', 'init', '-b', 'main'], p)
        lab.run(['git', 'config', 'user.name', 'Student241880237'], p)
        lab.run(['git', 'config', 'user.email', 'student@localhost'], p)
        lab.run(['git', 'add', '-A'], p)
        lab.run(['git', 'commit', '-m', 'C1'], p)
        return p

    def test_two_missing_for_same_target_are_ordered_and_merged(self):
        import lab
        with tempfile.TemporaryDirectory() as directory:
            p = self.project(directory)
            report = lab.scan(p)
            # 独立预期：main.o 同时缺两个头文件，而不是一条
            self.assertEqual(sorted((f['type'], f['target'], f['dependency']) for f in report['findings']),
                             [('MISSING', 'main.o', 'config.h'), ('MISSING', 'main.o', 'extra.h')])
            diff, plan = lab.patch(p, report)
            # 1) 计划两项，目标相同、依赖各一条
            self.assertEqual([(e['target'], e['dependency']) for e in plan],
                             [('main.o', 'config.h'), ('main.o', 'extra.h')])
            # 2) 顺序固定：config.h 先、extra.h 后（不随 gcc -MM 的 include 顺序）
            self.assertEqual([e['dependency'] for e in plan], ['config.h', 'extra.h'])
            # 3) 两条依赖合进同一行：diff 只有一行 -main.o: 和一行 +main.o:
            self.assertEqual(diff.count('+main.o:'), 1)
            self.assertEqual(diff.count('-main.o:'), 1)
            self.assertIn('+main.o: main.c config.h extra.h', diff)
            # 4) direct 风格，且 patch() 不写回源文件
            self.assertEqual({e['style'] for e in plan}, {'direct'})
            self.assertEqual((p / 'Makefile').read_text(), self.MAKEFILE)
            # 5) 补丁可应用，落地后依赖顺序稳定且无重复
            candidate = Path(directory) / 'candidate.patch'
            candidate.write_text(diff)
            lab.run(['git', 'apply', str(candidate.resolve())], p)
            line = [ln for ln in (p / 'Makefile').read_text().splitlines() if ln.startswith('main.o:')]
            self.assertEqual(line, ['main.o: main.c config.h extra.h'])
            # 6) 重检不再有 MISSING
            self.assertFalse(any(f['type'] == 'MISSING' for f in lab.scan(p)['findings']))


if __name__=='__main__':unittest.main()
