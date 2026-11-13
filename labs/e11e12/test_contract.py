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


if __name__=='__main__':unittest.main()
