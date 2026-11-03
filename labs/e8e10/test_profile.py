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

if __name__=='__main__':unittest.main()
