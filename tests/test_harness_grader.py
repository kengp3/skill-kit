"""Exercise grader qualification and fixed-product evidence, without model calls."""
import copy
import json
import sys
import tempfile
from pathlib import Path
import unittest

from harness.grader import case_inputs, qualification_status, qualify, select_regrades, regrade


class QualificationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.files = {}
        for name in ('requirement', 'checker', 'fixture'):
            path = self.root / name
            path.write_text(name)
            self.files[name] = path
        self.inputs = case_inputs(self.files, dependencies={'spring': '7'},
                                  environment={'jdk': '25'}, reports={'known': 1})
        self.case = {'case_id': 'lifecycle', 'kind': 'bug', 'inputs': self.inputs}

    def result(self, passed, kind='bug'):
        return {'status': 'graded', 'case_id': 'lifecycle', 'kind': kind, 'product_passed': passed,
                'inputs': copy.deepcopy(self.inputs), 'execution': {'status': 'completed',
                'returncode': 0 if passed else 1, 'remaining_pids': []},
                'product_fingerprint': 'fixed', 'source_before': 'fixed',
                'source_after': 'fixed', 'test_counts': {'known': {'tests': 1,
                'failures': 0 if passed else 1, 'errors': 0, 'skipped': 0}}}

    def test_changed_related_inputs_invalidate_qualified_evidence(self):
        evidence = qualify(self.case, {'defect': self.result(False),
                                      'correct': self.result(True)})
        self.assertEqual(qualification_status(self.case, evidence), 'qualified')
        for field in ('requirement', 'checker', 'fixture'):
            with self.subTest(field=field):
                self.files[field].write_text('new ' + field)
                changed = dict(self.case, inputs=case_inputs(self.files,
                    dependencies={'spring': '7'}, environment={'jdk': '25'}, reports={'known': 1}))
                self.assertEqual(qualification_status(changed, evidence), 'stale')
                self.files[field].write_text(field)
        changed_dependency = dict(self.case, inputs=case_inputs(self.files,
            dependencies={'spring': '8'}, environment={'jdk': '25'}, reports={'known': 1}))
        changed_environment = dict(self.case, inputs=case_inputs(self.files,
            dependencies={'spring': '7'}, environment={'jdk': '26'}, reports={'known': 1}))
        for changed in (changed_dependency, changed_environment):
            self.assertEqual(qualification_status(changed, evidence), 'stale')
        self.assertEqual(qualification_status(self.case, None), 'unverified')
        self.assertEqual(qualification_status(self.case, dict(self.case, status='qualified')),
                         'unverified')

    def test_feature_and_refactor_qualification_do_not_require_historical_bug(self):
        feature = dict(self.case, kind='feature')
        refactor = dict(self.case, kind='refactor')
        self.assertEqual(qualify(feature, {'missing_feature': self.result(False, 'feature'),
            'implemented': self.result(True, 'feature')})['status'], 'qualified')
        self.assertEqual(qualify(refactor, {'before': self.result(True, 'refactor'),
            'after': self.result(True, 'refactor'), 'structure': self.result(True, 'refactor')})['status'],
            'qualified')
        self.assertEqual(qualify(refactor, {'before': self.result(False, 'refactor'),
            'after': self.result(True, 'refactor'), 'structure': self.result(True, 'refactor')})['status'],
            'unverified')
        unknown = self.result(False)
        unknown['status'] = 'unverified'
        self.assertEqual(qualify(self.case, {'defect': unknown,
            'correct': self.result(True)})['status'], 'unverified')
        stale = self.result(False)
        stale['inputs']['environment']['jdk'] = '24'
        self.assertEqual(qualify(self.case, {'defect': stale,
            'correct': self.result(True)})['status'], 'unverified')


    def test_unsubstantiated_flags_do_not_qualify_a_checker(self):
        self.assertEqual(qualify(self.case, {
            'defect': {'status': 'graded', 'product_passed': False, 'inputs': self.inputs},
            'correct': {'status': 'graded', 'product_passed': True, 'inputs': self.inputs}})['status'],
            'unverified')


    def test_checker_revision_regrades_all_affected_products_including_failures(self):
        products = [{'product_id': name, 'case_ids': ['lifecycle'],
                     'fingerprint': 'fixed-' + name} for name in ('A', 'B', 'C')]
        unrelated = {'case_id': 'unrelated', 'kind': 'refactor', 'inputs': {'v': 1, 'reports': {'known': 1}}}
        products.append({'product_id': 'D', 'case_ids': ['unrelated'],
                         'fingerprint': 'fixed-D'})
        receipts = [dict(self.result(name != 'B'), case_id='lifecycle',
                         product_id=name, product_fingerprint='fixed-' + name,
                         source_before='fixed-' + name, source_after='fixed-' + name)
                    for name in ('A', 'B', 'C')]
        receipts.append(dict(self.result(True), case_id='unrelated', kind='refactor',
            product_id='D', product_fingerprint='fixed-D', source_before='fixed-D',
            source_after='fixed-D', inputs={'v': 1, 'reports': {'known': 1}}))
        self.assertEqual(select_regrades([self.case, unrelated], products, receipts), [])
        changed = copy.deepcopy(self.case)
        changed['inputs']['files']['checker'] = 'new-checker'
        self.assertEqual(select_regrades([changed, unrelated], products, receipts),
                         [('lifecycle', 'A'), ('lifecycle', 'B'), ('lifecycle', 'C')])
        self.assertEqual(receipts[1]['product_passed'], False)
        products[0]['fingerprint'] = 'changed-A'
        self.assertEqual(select_regrades([self.case, unrelated], products, receipts),
                         [('lifecycle', 'A')])


    def test_malformed_or_missing_terminal_receipt_is_selected_again(self):
        product = {'product_id': 'A', 'case_ids': ['lifecycle'], 'fingerprint': 'fixed'}
        valid = dict(self.result(True), product_id='A')
        for field, value in [('status', 'unverified'), ('product_passed', None),
                             ('kind', 'refactor'), ('test_counts', {}),
                             ('source_after', 'changed')]:
            with self.subTest(field=field):
                malformed = dict(valid, **{field: value})
                self.assertEqual(select_regrades([self.case], [product], [malformed]),
                                 [('lifecycle', 'A')])
        self.assertEqual(select_regrades([self.case], [product], []),
                         [('lifecycle', 'A')])


    def test_malformed_execution_is_unverified_in_public_qualification_and_selection(self):
        product = {'product_id': 'A', 'case_ids': ['lifecycle'], 'fingerprint': 'fixed'}
        for execution in (None, [], 'completed',
                          {'status': 'completed', 'returncode': 0},
                          {'status': 'completed', 'returncode': 0, 'remaining_pids': None}):
            with self.subTest(execution=execution):
                malformed = dict(self.result(True), product_id='A', execution=execution)
                self.assertEqual(select_regrades([self.case], [product], [malformed]),
                                 [('lifecycle', 'A')])
                self.assertEqual(qualify(self.case, {'defect': self.result(False),
                    'correct': malformed})['status'], 'unverified')
        unsupported = dict(self.case, status='qualified', observations=None)
        self.assertEqual(qualification_status(self.case, unsupported), 'unverified')


    def test_recorded_receipt_report_contract_is_checked_when_reusing_evidence(self):
        evidence = Path(__file__).resolve().parents[1] / 'docs/research/codex-harness-p0-20261024-evidence/fixed-grading'
        correct = json.loads((evidence / 'A-HarnessLifecycleTest.json').read_text())
        defect = json.loads((evidence / 'parent-HarnessLifecycleTest.json').read_text())
        case = {key: correct[key] for key in ('case_id', 'kind', 'inputs')}
        product = {'product_id': 'A', 'case_ids': [case['case_id']],
                   'fingerprint': correct['product_fingerprint']}
        self.assertEqual(qualify(case, {'defect': defect, 'correct': correct})['status'], 'qualified')
        report = next(iter(correct['test_counts']))
        for mode in ('wrong_count', 'missing_report', 'extra_report'):
            with self.subTest(mode=mode):
                bad, bad_defect, changed = map(copy.deepcopy, (correct, defect, case))
                if mode == 'wrong_count':
                    bad['test_counts'][report]['tests'] = 1
                elif mode == 'missing_report':
                    for value in (bad, bad_defect, changed):
                        value['inputs']['reports']['required-extra.xml'] = 1
                else:
                    bad['test_counts']['unexpected.xml'] = {'tests': 1, 'failures': 0, 'errors': 0, 'skipped': 0}
                self.assertEqual(select_regrades([changed], [product], [bad]),
                                 [(case['case_id'], 'A')])
                self.assertEqual(qualify(changed, {'defect': bad_defect,
                    'correct': bad})['status'], 'unverified')


class FixedProductTest(unittest.TestCase):
    def test_fixed_products_are_immutable_and_grading_receipts_are_not_overwritten(self):
        from harness.boundary import Limits
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            product = root / 'product'
            product.mkdir()
            source = product / 'source.txt'
            source.write_text('fixed delivery')
            requirement = root / 'requirement.txt'
            requirement.write_text('source unchanged; checker reports behavior')
            checker = root / 'checker.py'
            checker.write_text("""from pathlib import Path
import sys
source = Path(sys.argv[1])
try:
    source.write_text('forbidden mutation')
except PermissionError:
    pass
else:
    raise SystemExit('boundary failed')
Path('TEST-result.xml').write_text('<testsuite name="behavior" tests="1" failures="0" errors="0" skipped="0"/>')
""")
            files = {'requirement': requirement, 'checker': checker, 'fixture': source}
            case = {'case_id': 'immutable', 'kind': 'refactor',
                    'inputs': case_inputs(files, dependencies={}, environment={},
                    command=[sys.executable, '-B', str(checker)], reports={'TEST-result.xml': 1})}
            workspace = root / 'execution'
            workspace.mkdir()
            receipt = root / 'receipt.json'
            result = regrade(case, product_id='fixed', product_root=product,
                input_files=files, workspace=workspace,
                argv=[sys.executable, '-B', str(checker), str(source)],
                reports={'TEST-result.xml': 1}, receipt=receipt,
                limits=Limits(wall_seconds=5, cpu_seconds=3, memory_mb=256,
                              max_processes=2))
            self.assertEqual(result['status'], 'graded', result)
            self.assertTrue(result['product_passed'])
            self.assertEqual(source.read_text(), 'fixed delivery')
            self.assertEqual(json.loads(receipt.read_text()), result)
            saved = receipt.read_bytes()
            with self.assertRaises(FileExistsError):
                regrade(case, product_id='fixed', product_root=product,
                    input_files=files, workspace=workspace, argv=['must-not-run'],
                    reports={'TEST-result.xml': 1}, receipt=receipt,
                    limits=Limits(wall_seconds=5, cpu_seconds=3, memory_mb=256,
                                  max_processes=2))
            self.assertEqual(receipt.read_bytes(), saved)

    def test_product_failure_is_distinct_from_missing_skipped_or_interrupted_checks(self):
        from harness.boundary import Limits
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            product = root / 'product'
            product.mkdir()
            source = product / 'source.txt'
            source.write_text('fixed')
            requirement = root / 'requirement'
            requirement.write_text('one complete behavioral check')
            checker = root / 'checker.py'
            checker.write_text("""from pathlib import Path
import sys, time
mode = sys.argv[1]
if mode != 'missing':
    tests = 0 if mode == 'zero' else 2 if mode == 'count' else 1
    failures = 1 if mode == 'assertion' else 0
    skipped = 1 if mode == 'skipped' else 0
    Path('TEST-result.xml').write_text(f'<testsuite tests="{tests}" failures="{failures}" errors="0" skipped="{skipped}"/>')
if mode == 'timeout':
    time.sleep(2)
raise SystemExit(1 if mode in ('assertion', 'wrong_exit') else 0)
""")
            files = {'requirement': requirement, 'checker': checker, 'fixture': source}
            prefix = [sys.executable, '-B', str(checker)]
            case = {'case_id': 'behavior', 'kind': 'bug',
                    'inputs': case_inputs(files, dependencies={}, environment={}, command=prefix, reports={'TEST-result.xml': 1})}
            outcomes = [('pass', 'graded', True), ('assertion', 'graded', False),
                        ('missing', 'unverified', None), ('zero', 'unverified', None),
                        ('count', 'unverified', None), ('skipped', 'unverified', None),
                        ('wrong_exit', 'unverified', None), ('timeout', 'unverified', None)]
            for mode, status, passed in outcomes:
                with self.subTest(mode=mode):
                    workspace = root / mode
                    workspace.mkdir()
                    result = regrade(case, product_id=mode, product_root=product,
                        input_files=files, workspace=workspace, argv=prefix + [mode],
                        reports={'TEST-result.xml': 1}, receipt=root / (mode + '.json'),
                        limits=Limits(wall_seconds=.25 if mode == 'timeout' else 5,
                                      cpu_seconds=3, memory_mb=256, max_processes=2))
                    self.assertEqual(result['status'], status, result)
                    self.assertIs(result['product_passed'], passed)
                    self.assertIn('execution', result)
                    if mode == 'timeout':
                        self.assertEqual(result['execution']['status'], 'timeout')
                    self.assertEqual(result['source_before'], result['source_after'])


if __name__ == '__main__':
    unittest.main()
