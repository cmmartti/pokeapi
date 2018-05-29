import unittest

from .loader_util import (
    divide_by_key,
    group_by_batch,
    get_relations,
    get_relations_via_map
)
from .loader_key import LoaderKey


class TestObject(object):
    """An object used for mocking models in tests."""
    def __init__(self, id, other_id):
        self.id = id
        self.other_id = other_id
        self.some_map = TestMap()

    def __eq__(self, other):
        return self.id == other.id

class TestMap(object):
    def all(self):
        return [TestObject(7, 99), TestObject(8, 99), TestObject(9, 99)]


class UtilTestCase(unittest.TestCase):

    def test_loader_key(self):
        key1 = LoaderKey(id=1, arg1="x")
        key2 = LoaderKey(id=1, arg1="x")
        key3 = LoaderKey(id=1, arg1="y")
        key4 = LoaderKey(id=4, arg1="x")

        self.assertEqual(key1, key2, "LoaderKeys with same ids and same args should be equal")
        self.assertNotEqual(key1, key3)
        self.assertNotEqual(key1, key4)
        self.assertNotEqual(key3, key4)

        self.assertEqual(key1.id, 1)
        self.assertEqual(key1.args, ("x",))
        self.assertEqual(key1.args.arg1, "x")

    def test_divide_by_key(self):
        values = [(1, "x"), (2, "x"), (3, "y")]
        compare_fn = lambda key, obj: key == obj[0]
        list1 = divide_by_key([1, 2, 1], values, compare_fn)
        list2 = [(1, "x"), (2, "x"), (1, "x")]
        self.assertEqual(list1, list2)

        empty_list = divide_by_key([], [], lambda key, obj: True)
        self.assertEqual(empty_list, [])

    def test_group_by_batch(self):
        keys = [
            LoaderKey(id=1, arg1="x"),
            LoaderKey(id=2, arg1="x"),
            LoaderKey(id=3, arg1="z"),
            LoaderKey(id=1, arg1="z"),
        ]
        should_be = {
            ("x", ): [1, 2],
            ("z", ): [3, 1],
        }
        self.assertEqual(group_by_batch(keys), should_be)

    def test_get_relations(self):
        keys = [
            LoaderKey(id=56, qty=3),
            LoaderKey(id=23, qty=1),
            LoaderKey(id=332, qty=0),
        ]
        relations = get_relations(keys, UtilTestCase.get_query_set, "other_id")
        should_be = [
            [TestObject(1, 56), TestObject(2, 56), TestObject(3, 56)],
            [TestObject(1, 23)],
            []
        ]

        self.assertEqual(relations, should_be)

    def test_get_relations_via_map(self):
        keys = [
            LoaderKey(id=9, qty=3),
            LoaderKey(id=8, qty=1),
            LoaderKey(id=7, qty=0),
        ]
        relations = get_relations_via_map(
            keys, UtilTestCase.get_query_set, "other_id", "some_map"
        )

    @staticmethod
    def get_query_set(ids, qty):
        results = []
        for id in ids:
            for i in range(qty):
                results.append(TestObject(id=i + 1, other_id=id))
        return results
