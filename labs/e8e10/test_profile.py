import json, tempfile, unittest
from pathlib import Path
from lab import fixture,scan,patch,commit

class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'sample';fixture(self.p)

    def test_independent_known_edges(self):
        r=scan(self.p)
        self.assertEqual(r['actual']['main.o'],['config.h','main.c'])
        self.assertEqual({(f['type'],f['dependency']) for f in r['findings']},{('MISSING','config.h'),('REDUNDANT','unused.h')})

    def test_unchanged_reuses_both_targets(self):
        r=scan(self.p,scan(self.p));self.assertEqual(r['reused'],['main.o','helper.o']);self.assertEqual(r['refreshed'],[])

    def test_include_added_invalidates_cache(self):
        old=scan(self.p)
        (self.p/'main.c').write_text('#include "extra.h"\n'+(self.p/'main.c').read_text());commit(self.p,'new include')
        r=scan(self.p,old)
        self.assertIn(['MISSING','main.o','extra.h'],r['added']);self.assertEqual(len(r['refreshed']),2)

    def test_patch_preserves_redundant_dependency(self):
        r=scan(self.p);diff,plan=patch(self.p,r)
        self.assertIn('+main.o: main.c unused.h config.h',diff)
        self.assertNotIn('-\tgcc',diff)
        self.assertNotIn('config.h',(self.p/'Makefile').read_text())

    def test_old_report_rejected(self):
        r=scan(self.p);r['commit']='0'*40
        with self.assertRaisesRegex(ValueError,'STALE_REPORT'):patch(self.p,r)

    def test_unsafe_dependency_rejected(self):
        r=scan(self.p);r['findings']=[{'type':'MISSING','target':'main.o','dependency':'../outside.h'}]
        with self.assertRaisesRegex(ValueError,'UNSAFE_PATH'):patch(self.p,r)

    def test_unsupported_configuration_rejected(self):
        (self.p/'Makefile').write_text((self.p/'Makefile').read_text().replace('-O0','-include unknown.h'))
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_FLAGS'):scan(self.p)

    def test_redundant_only_report_makes_no_change(self):
        # 独立预期：报告里只有 REDUNDANT 时，补丁器不应有任何动作—
        # 不生成 diff、不产生修改计划、源文件逐字节不变、RD 不被删除。
        r=scan(self.p);r['findings']=[f for f in r['findings'] if f['type']=='REDUNDANT']
        self.assertEqual([f['type'] for f in r['findings']],['REDUNDANT'])
        before=(self.p/'Makefile').read_bytes();diff,plan=patch(self.p,r)
        self.assertEqual(diff,'');self.assertEqual(plan,[])
        self.assertEqual((self.p/'Makefile').read_bytes(),before)
        self.assertIn('unused.h',(self.p/'Makefile').read_text())

    def test_duplicate_missing_entries_added_once(self):
        # 独立预期：同一条 MISSING 在报告里出现两次时，补丁只能追加一次；
        # 且对同一个报告重复应用补丁不应产生 config.h config.h。
        r=scan(self.p)
        md=[f for f in r['findings'] if f['type']=='MISSING']
        self.assertEqual([f['dependency'] for f in md],['config.h'])
        r['findings']=md+md
        before=(self.p/'Makefile').read_bytes();diff,plan=patch(self.p,r)
        self.assertEqual((self.p/'Makefile').read_bytes(),before)
        self.assertEqual(len(plan),1)
        self.assertEqual(diff.count('config.h'),1)
        self.assertEqual(diff.count('+main.o:'),1)
class StudentE8B(unittest.TestCase):
    def test_patch_keeps_recipe_bytes(self):
        from lab import run
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            before=(p/'Makefile').read_bytes()
            diff,plan=patch(p,scan(p))
            candidate=Path(directory)/'candidate.patch'
            candidate.write_text(diff)
            run(['git','apply',str(candidate.resolve())],p)
            after=(p/'Makefile').read_bytes()
            recipes=lambda data:[line for line in data.splitlines() if line.startswith(b'\t')]
            self.assertEqual(recipes(before),recipes(after))
            self.assertIn(b'main.o: main.c unused.h config.h',after)
            self.assertEqual(plan[0]['style'],'direct')
class StudentE9B(unittest.TestCase):
    def test_macro_style_patch_updates_definition(self):
        from lab import run
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p,'macro')
            diff,plan=patch(p,scan(p))
            candidate=Path(directory)/'candidate.patch'
            candidate.write_text(diff)
            run(['git','apply',str(candidate.resolve())],p)
            text=(p/'Makefile').read_text()
            self.assertIn('DEPS = main.c unused.h config.h',text)
            self.assertIn('main.o: $(DEPS)',text)
            self.assertEqual(plan[0]['style'],'macro')
            self.assertFalse(any(x['type']=='MISSING' for x in scan(p)['findings']))
class StudentE10B(unittest.TestCase):
    def test_build_failure_keeps_original_makefile(self):
        from lab import validate
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            p=root/'sample'
            fixture(p)
            diff,plan=patch(p,scan(p))
            candidate=root/'candidate.patch'
            candidate.write_text(diff)
            before=(p/'Makefile').read_bytes()
            (p/'main.c').write_text('this is invalid C;\n')
            result=validate(p,candidate,root/'validation')
            self.assertTrue(result['checks']['patch_applies'])
            self.assertFalse(result['checks'].get('build',False))
            self.assertIn('COMMAND_FAILED',result['error'])
            self.assertFalse(result['accepted'])
            self.assertTrue(result['rollback'])
            self.assertTrue(result['source_unchanged'])
            self.assertEqual((p/'Makefile').read_bytes(),before)
class Student241880214(unittest.TestCase):
    def test_macro_plus_direct_dependency_is_mixed(self):
        from lab import run
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p,'macro')
            makefile=p/'Makefile'
            makefile.write_text(makefile.read_text().replace('main.o: $(DEPS)','main.o: $(DEPS) extra.h'))
            commit(p,'student: macro plus direct dependency')
            diff,plan=patch(p,scan(p))
            self.assertEqual(plan,[{'target':'main.o','dependency':'config.h','style':'mixed'}])
            self.assertIn('+main.o: $(DEPS) extra.h config.h',diff)
            self.assertIn('DEPS = main.c unused.h\n',makefile.read_text())
            candidate=Path(directory)/'candidate.patch'
            candidate.write_text(diff)
            run(['git','apply',str(candidate.resolve())],p)
            self.assertFalse(any(f['type']=='MISSING' for f in scan(p)['findings']))


class Student241880171(unittest.TestCase):
    def test_two_missing_for_same_target(self):
        """独立预期：同一个 target 有两条 MISSING（config.h 和 extra.h）时，
        补丁计划有两项，目标行两个依赖都加上，顺序稳定为 config.h 再 extra.h。"""
        from lab import run
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            # main.c 同时包含 config.h 和 extra.h，但 Makefile 都没有声明
            (p/'main.c').write_text(
                '#include <stdio.h>\n'
                '#include "config.h"\n'
                '#include "extra.h"\n'
                'int helper(void);\n'
                'int main(void){printf("%d\n",VALUE+helper());return 0;}\n'
            )
            commit(p,'student: two undeclared headers')
            report=scan(p)
            missing=[f for f in report['findings'] if f['type']=='MISSING']
            self.assertEqual([f['dependency'] for f in missing],['config.h','extra.h'])
            before=(p/'Makefile').read_bytes()
            diff,plan=patch(p,report)
            self.assertEqual((p/'Makefile').read_bytes(),before)
            self.assertEqual(len(plan),2)
            self.assertEqual(plan,[
                {'target':'main.o','dependency':'config.h','style':'direct'},
                {'target':'main.o','dependency':'extra.h','style':'direct'},
            ])
            self.assertIn('+main.o: main.c unused.h config.h extra.h',diff)
            candidate=Path(directory)/'candidate.patch'
            candidate.write_text(diff)
            run(['git','apply',str(candidate.resolve())],p)
            self.assertFalse(any(f['type']=='MISSING' for f in scan(p)['findings']))

if __name__=='__main__':unittest.main()
