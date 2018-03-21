""" Unit tests for the `main` module. """

from as_dataframe.main import as_dataframe, _DataFrameableDict
from pandas import DataFrame
from unittest import TestCase
from unittest.mock import patch


class TestAsDataframeFunction(TestCase):

    @patch('as_dataframe.main._DataFrameableDict', new=lambda x: x[0])
    def test_as_dataframe(self):
        dataframeable_dict = [{'a': [1], ('b', 'a'): [4]}, {'a': [2, 3], ('b', 'b'): [5, 6]}]
        expected = DataFrame({'a': [1, 2, 3], 'b.a': [4, None, None], 'b.b': [None, 5, 6]})
        actual = as_dataframe(dataframeable_dict)
        self.assertTrue(expected.equals(actual))


class TestDataFrameableDict(TestCase):

    @patch('as_dataframe.main._DataFrameableDict.flattened', new=lambda x: x)
    @patch('as_dataframe.main._DataFrameableDict.impute_locf', new=lambda x: None)
    @patch('as_dataframe.main._DataFrameableDict.drop_redundant_keys', new=lambda x: None)
    def test_init(self):
        self.assertEqual(_DataFrameableDict([{'a': 1}]), _DataFrameableDict([{'a': 1}]))
        self.assertRaises(TypeError, _DataFrameableDict, 'foo')
        self.assertEqual({}, _DataFrameableDict({}))

        d = {'a': 1, 'b': [1, 2, 3]}
        expected = {'a': [1], 'b': [1, 2, 3]}
        actual = _DataFrameableDict([d])
        self.assertEqual(expected, actual)

    def test_drop_redundant_keys(self):
        actual = {('a',): [1, 2, 3], ('b',): [None] * 3, ('b', 'a'): [4, 5, 6]}
        expected = {('a',): [1, 2, 3], ('b', 'a'): [4, 5, 6]}

        # noinspection PyCallByClass,PyTypeChecker
        _DataFrameableDict.drop_redundant_keys(actual)
        self.assertEqual(expected, actual)

    def test_impute_locf(self):
        actual = {('a',): [1, 2, 3], ('b',): [1, 2, 3, 4 ,5]}
        expected = {('a',): [1, 2, 3, 3, 3], ('b',): [1, 2, 3, 4, 5]}

        # noinspection PyCallByClass,PyTypeChecker
        _DataFrameableDict.impute_locf(actual)
        self.assertEqual(expected, actual)

    def test_flattened(self):
        d = {
            'a': 1,
            ('b',): 2,
            'c': {'d': 1},
            'e': [{'f': 1}, {'f': 2}]
        }

        actual = _DataFrameableDict.flattened(d)
        expected = {('a',): 1, (('b',),): 2, ('c', 'd'): 1, ('e', 'f'): [1, 2]}
        self.assertEqual(expected, actual)

        d['g'] = [{'h': 1}, {'h': 2}, {'h': 3}]
        self.assertRaises(ValueError, _DataFrameableDict.flattened, d)
