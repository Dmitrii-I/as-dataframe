""" Unit tests for the `main` module. """

from as_dataframe import as_dataframe
from pandas import DataFrame
from unittest import TestCase
from copy import deepcopy


class TestAsDataframeFunction(TestCase):

    def setUp(self):
        self.nested_dict_with_list_value = {
            'Company': 'Kramerica Inc.',
            'Department': {'ID': 4, 'Name': 'Sales'},
            'Employees': [
                {'ID': 1, 'Names': {'First': 'Alice'}},
                {'ID': 2, 'Names': {'First': 'Bob', 'Last': 'Johnson'}},
                {'ID': 3, 'Names': {'Last': 'McLOVIN'}},
                {'ID': 4},
                {'ID': 5, 'Names': None}
            ],
            'Financial': {'Profit': {'Before Tax': 100, 'After Tax': 80}}
        }

        self.flat_dict_with_simple_values = {'a': 1, 'b': 2, 'c': 'foo'}

    def test_with_nested_dict_with_list_value(self):

        nested_dict = deepcopy(self.nested_dict_with_list_value)

        expected_df = DataFrame({
            'Company': 'Kramerica Inc.',
            'Department.ID': 4,
            'Department.Name': 'Sales',
            'Employees.ID': [1, 2, 3, 4, 5],
            'Employees.Names.First': ['Alice', 'Bob', None, None, None],
            'Employees.Names.Last': [None, 'Johnson', 'McLOVIN', None, None],
            'Financial.Profit.Before Tax': 100,
            'Financial.Profit.After Tax': 80,
        })

        self.assertTrue(expected_df.equals(as_dataframe(nested_dict)))

    def test_with_list_of_nested_dicts_with_list_value(self):

        nested_dict = deepcopy(self.nested_dict_with_list_value)

        expected_df = DataFrame({
            'Company': 'Kramerica Inc.',
            'Department.ID': 4,
            'Department.Name': 'Sales',
            'Employees.ID': [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
            'Employees.Names.First': ['Alice', 'Bob', None, None, None, 'Alice', 'Bob', None, None, None],
            'Employees.Names.Last': [None, 'Johnson', 'McLOVIN', None, None, None, 'Johnson', 'McLOVIN', None, None],
            'Financial.Profit.Before Tax': 100,
            'Financial.Profit.After Tax': 80,
        })

        self.assertTrue(expected_df.equals(as_dataframe([nested_dict]*2)))

    def test_argument_is_not_modifed(self):

        dict_1 = deepcopy(self.nested_dict_with_list_value)
        dict_2 = deepcopy(self.nested_dict_with_list_value)

        _ = as_dataframe(dict_1)

        self.assertEqual(dict_1, dict_2)

    def test_with_flat_dict_with_simple_values(self):
        expected_df = DataFrame({'a': [1], 'b': [2], 'c': ['foo']})
        self.assertTrue(expected_df.equals(as_dataframe(self.flat_dict_with_simple_values)))
