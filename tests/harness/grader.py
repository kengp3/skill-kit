"""Development-only qualification and fixed-product grading; no model execution."""
import hashlib
from pathlib import Path


def case_inputs(files, *, dependencies, environment, command=None):
    """Fingerprint relevant files/versions and a stable checker command prefix."""
    fingerprints = {}
    for name, value in sorted(files.items()):
        path = Path(value)
        if path.is_symlink() or not path.is_file():
            raise ValueError('Qualification input must be an existing regular file')
        fingerprints[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    if command:
        executable = Path(command[0])
        if not executable.is_absolute() or not executable.is_file():
            raise ValueError('Checker command needs an absolute executable path')
        fingerprints['executable'] = hashlib.sha256(executable.resolve().read_bytes()).hexdigest()
    if not {'requirement', 'checker', 'fixture'} <= fingerprints.keys():
        raise ValueError('Requirement, checker and fixture inputs are required')
    return {'files': fingerprints, 'dependencies': dict(dependencies),
            'environment': dict(environment), 'command': list(command) if command else None}


def qualification_status(case, evidence):
    if not evidence or evidence.get('status') != 'qualified':
        return 'unverified'
    if any(evidence.get(key) != case.get(key) for key in ('case_id', 'kind', 'inputs')):
        return 'stale'
    return 'qualified'


def _supported(receipt):
    counts = receipt.get('test_counts')
    if (receipt.get('status') != 'graded'
            or type(receipt.get('product_passed')) is not bool
            or receipt.get('execution', {}).get('status') != 'completed'
            or not receipt.get('source_before')
            or receipt.get('source_before') != receipt.get('source_after')
            or receipt.get('source_before') != receipt.get('product_fingerprint')
            or not isinstance(counts, dict) or not counts):
        return False
    values = list(counts.values())
    for value in values:
        if (not isinstance(value, dict)
                or any(type(value.get(key)) is not int
                       for key in ('tests', 'failures', 'errors', 'skipped'))
                or value['tests'] <= 0 or not 0 <= value['failures'] <= value['tests']
                or value['errors'] != 0 or value['skipped'] != 0):
            return False
    failed = any(value['failures'] for value in values)
    return receipt['product_passed'] is (not failed)


def qualify(case, observations):
    roles = {'bug': {'defect': False, 'correct': True},
             'feature': {'missing_feature': False, 'implemented': True},
             'refactor': {'before': True, 'after': True, 'structure': True}}
    if case.get('kind') not in roles:
        raise ValueError('Unknown case kind')
    valid = all(
        _supported(observations.get(role, {}))
        and observations[role].get('case_id') == case['case_id']
        and observations[role].get('kind') == case['kind']
        and observations[role].get('product_passed') is expected
        and observations[role].get('inputs') == case['inputs']
        for role, expected in roles[case['kind']].items())
    return {key: case[key] for key in ('case_id', 'kind', 'inputs')} | {
        'status': 'qualified' if valid else 'unverified',
        'observations': observations}


def select_regrades(cases, products, receipts):
    """Select every fixed product lacking a current, terminal grading receipt."""
    selected = []
    for case in cases:
        for product in products:
            if case['case_id'] not in product['case_ids']:
                continue
            current = any(
                _supported(receipt)
                and receipt.get('kind') == case['kind']
                and receipt.get('case_id') == case['case_id']
                and receipt.get('inputs') == case['inputs']
                and receipt.get('product_id') == product['product_id']
                and receipt.get('product_fingerprint') == product['fingerprint']
                for receipt in receipts)
            if not current:
                selected.append((case['case_id'], product['product_id']))
    return selected


def product_fingerprint(root):
    """Identify the immutable delivered files, including dirty content."""
    import json
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('Fixed product must be a regular directory')
    files = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('Fixed product must not contain symbolic links')
        if path.is_file():
            files[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    if not files:
        raise ValueError('Fixed product is empty')
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def regrade(case, *, product_id, product_root, input_files, workspace, argv,
            reports, receipt, limits, env=None):
    """Run an external checker in the P0 boundary and retain a new receipt."""
    import json
    import xml.etree.ElementTree as ET
    from .boundary import run

    product_root, workspace, receipt = map(Path, (product_root, workspace, receipt))
    if receipt.exists() or receipt.is_symlink():
        raise FileExistsError('A grading receipt cannot be overwritten')
    if workspace.absolute() != workspace.resolve() or product_root.is_symlink():
        raise ValueError('Workspace and product aliases must be resolved explicitly')
    product_root, workspace = product_root.resolve(), workspace.resolve()
    if product_root == workspace or product_root in workspace.parents or workspace in product_root.parents:
        raise ValueError('Execution workspace and immutable product must be separate')
    if any(workspace == Path(path).resolve() or workspace in Path(path).resolve().parents
           for path in input_files.values()):
        raise ValueError('Grader inputs must be outside the writable workspace')
    if workspace in receipt.resolve().parents or product_root in receipt.resolve().parents:
        raise ValueError('Receipt must be outside checker write scope and fixed product')
    expected_reports = {}
    if not reports:
        raise ValueError('At least one expected test report is required')
    for filename, count in reports.items():
        path = workspace / filename
        if count <= 0 or path.resolve() == workspace or workspace not in path.resolve().parents:
            raise ValueError('Expected reports need a positive count and workspace path')
        if path.exists() or path.is_symlink():
            raise FileExistsError('Old test report must not be reused: ' + str(path))
        expected_reports[path] = count
    before = product_fingerprint(product_root)
    prefix = case['inputs'].get('command')
    if not prefix or list(argv[:len(prefix)]) != prefix:
        raise ValueError('Checker command is not bound to case inputs')
    if any(case['inputs']['environment'].get(key) != value for key, value in (env or {}).items()):
        raise ValueError('Execution environment is not bound to case inputs')
    current_inputs = case_inputs(input_files, dependencies=case['inputs']['dependencies'],
                                environment=case['inputs']['environment'], command=argv)
    if current_inputs != case['inputs']:
        raise ValueError('Grader inputs changed since case qualification')
    record = {'case_id': case['case_id'], 'kind': case['kind'],
              'inputs': case['inputs'], 'product_id': product_id,
              'product_fingerprint': before, 'source_before': before,
              'argv': list(argv), 'status': 'running', 'product_passed': None,
              'test_counts': {}}
    with receipt.open('x') as output:
        output.write(json.dumps(record, indent=2) + '\n')
        output.flush()
        try:
            result = run(argv, workspace=workspace, limits=limits, env=env)
            record['execution'] = {'status': result.status, 'returncode': result.returncode,
                'stdout': result.stdout, 'stderr': result.stderr,
                'remaining_pids': result.remaining_pids}
            counts = {}
            for path, expected in expected_reports.items():
                if path.is_symlink() or not path.is_file():
                    raise ValueError('Expected test report missing or linked: ' + str(path))
                suite = ET.parse(path).getroot()
                if suite.tag.rsplit('}', 1)[-1] != 'testsuite':
                    raise ValueError('Expected a testsuite report')
                values = {name: int(suite.attrib.get(name, '0'))
                          for name in ('tests', 'failures', 'errors', 'skipped')}
                counts[str(path.relative_to(workspace))] = values
                if values['tests'] != expected or min(values.values()) < 0:
                    raise ValueError('Expected test count was not executed')
                if values['errors'] or values['skipped']:
                    raise ValueError('Qualification report has errors or skipped tests')
                if values['failures'] > values['tests']:
                    raise ValueError('Inconsistent test counts')
            record['test_counts'] = counts
            failed = any(value['failures'] for value in counts.values())
            if result.status != 'completed' or result.remaining_pids or result.returncode is None:
                raise ValueError('Checker execution has no reconciled terminal outcome')
            if (result.returncode == 0) == failed:
                raise ValueError('Checker exit and test assertions disagree')
            record['status'] = 'graded'
            record['product_passed'] = not failed
        except Exception as error:
            record['status'] = 'unverified'
            record['error'] = str(error)
        try:
            record['source_after'] = product_fingerprint(product_root)
            after_inputs = case_inputs(input_files, dependencies=case['inputs']['dependencies'],
                                      environment=case['inputs']['environment'], command=argv)
            if record['source_after'] != before or after_inputs != current_inputs:
                raise ValueError('Immutable product or checker input changed during grading')
        except Exception as error:
            record['status'] = 'unverified'
            record['product_passed'] = None
            record['error'] = str(error)
        output.seek(0)
        output.write(json.dumps(record, indent=2) + '\n')
        output.truncate()
    return record
