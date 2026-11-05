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

class StudentE8B(unittest.TestCase):
    # 参考测试（来自 08_个人测试编写示例.md 2B）：补丁只改依赖行，TAB 配方逐字节保持。
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

class StudentE8BExtra(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'sample';fixture(self.p)

    # 独立测试：报告引用未知目标（ghost.o）时必须明确拒绝 UNSUPPORTED_TARGET，
    # 且源 Makefile 逐字节保持不变（拒绝动作不得触碰源文件）。
    def test_unknown_target_rejected(self):
        r=scan(self.p)
        r['findings']=[{'type':'MISSING','target':'ghost.o','dependency':'config.h'}]
        before=(self.p/'Makefile').read_bytes()
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_TARGET'):
            patch(self.p,r)
        self.assertEqual((self.p/'Makefile').read_bytes(),before)
        # 源工作区仍干净，拒绝未产生任何副作用。
        from lab import run
        self.assertEqual(run(['git','status','--porcelain'],self.p).strip(),'')


class StudentE9BExtra(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'sample';fixture(self.p,'macro')

    # 独立测试（E9-B，共享变量方向）：macro 风格补丁必须只修改 DEPS 定义行，
    # main.o 的目标行（main.o: $(DEPS)）在 diff 中不得出现增删——
    # 目标引用保持原样才能保证未分析的共享变量语义不被悄悄扩大。
    def test_macro_patch_touches_only_deps_definition(self):
        r=scan(self.p);diff,plan=patch(self.p,r)
        self.assertEqual(plan[0]['style'],'macro')
        self.assertIn('-DEPS = main.c unused.h',diff)
        self.assertIn('+DEPS = main.c unused.h config.h',diff)
        self.assertNotIn('-main.o:',diff)
        self.assertNotIn('+main.o:',diff)
        # 补丁未写回源文件
        self.assertNotIn('config.h',(self.p/'Makefile').read_text())

class StudentE10BExtra(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'sample';fixture(self.p)

    # 独立测试（E10-B，"能构建但仍存在MD"方向）：构造错误候选——
    # 把依赖加成确实存在、可参与构建的 extra.h 而非 config.h。
    # 预期：patch 可应用、构建通过、功能测试通过，但增量重检仍报 MISSING config.h
    # （no_missing=False），因此 accepted=False 且源 Makefile 逐字节不变。
    def test_buildable_but_still_missing_rejected(self):
        from lab import validate
        r=scan(self.p)
        r['findings']=[{'type':'MISSING','target':'main.o','dependency':'extra.h'}]
        diff,plan=patch(self.p,r)
        candidate=self.p.parent/'wrong.patch'
        candidate.write_text(diff)
        before=(self.p/'Makefile').read_bytes()
        result=validate(self.p,candidate,self.p.parent/'validation-wrong')
        self.assertTrue(result['checks']['patch_applies'])
        self.assertTrue(result['checks']['build'])
        self.assertFalse(result['checks']['no_missing'])
        self.assertFalse(result['accepted'])
        self.assertTrue(result['rollback'])
        self.assertTrue(result['source_unchanged'])
        self.assertEqual((self.p/'Makefile').read_bytes(),before)

if __name__=='__main__':unittest.main()
