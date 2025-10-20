# This file is placed in the Public Domain.


import unittest


from objz import Object, dumps, loads


class TestTypes(unittest.TestCase):

    def test_integer(self):
        obj = loads(dumps(1))
        self.assertEqual(obj, 1)
