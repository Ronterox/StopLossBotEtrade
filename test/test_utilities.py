import unittest

from utilites.utilities import is_float


class TestUtils(unittest.TestCase):
    def test_is_float(self):
        self.assertTrue(is_float("2.5"))
        self.assertTrue(is_float("2"))

        self.assertFalse(is_float(""))
        self.assertFalse(is_float("h"))

    def test_os(self):
        import os
        self.assertTrue(os.name != 'nt')


if __name__ == '__main__':
    unittest.main()
