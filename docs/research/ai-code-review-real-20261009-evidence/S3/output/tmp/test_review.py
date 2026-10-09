import importlib
import pathlib
import sys
import unittest

snapshot = pathlib.Path(sys.argv.pop(1)).resolve()
sys.path.insert(0, str(snapshot))
page = importlib.import_module('api').page

class PaginationContract(unittest.TestCase):
    def check_page(self, ids, cursor, limit, expected):
        before = ids.copy()
        actual = page(ids, cursor, limit)
        print(f'ids={ids!r} cursor={cursor!r} limit={limit!r} expected={expected!r} actual={actual!r}', flush=True)
        self.assertEqual(ids, before)
        self.assertEqual(actual, expected)
        self.assertLessEqual(len(actual), limit)
        self.assertTrue(all(i > cursor for i in actual))
    def test_exact_boundary(self):
        self.check_page([1, 2, 3], 2, 2, [3])
    def test_empty(self):
        self.check_page([], 0, 1, [])
    def test_before_first_cap(self):
        self.check_page([1, 2, 3], 0, 1, [1])
    def test_after_last(self):
        self.check_page([1, 2, 3], 4, 1, [])
    def test_last_cursor(self):
        self.check_page([1, 2, 3], 3, 1, [])
    def test_between_ids_cap(self):
        self.check_page([1, 3, 5, 7], 2, 2, [3, 5])
    def test_large_limit_order(self):
        self.check_page([-3, -1, 2, 5], -2, 10, [-1, 2, 5])
    def test_invalid_limits(self):
        for limit in [0, -1, True, False, 1.0, '1', None]:
            with self.subTest(limit=repr(limit)):
                with self.assertRaisesRegex(ValueError, '^limit$'):
                    page([1, 2, 3], 0, limit)
                print(f'invalid limit={limit!r}: ValueError(limit)', flush=True)

unittest.main(verbosity=2)
