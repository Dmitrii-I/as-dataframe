""" Unit tests for the `main` module. """

from as_dataframe.main import as_dataframe, _flattened, TreeNode, _flattened_2, _gathered
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

        actual_df = as_dataframe(nested_dict)
        self.assertTrue(expected_df.equals(actual_df))

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

    def test_all_nulls_column_is_kept(self):
        """ Test that a column with all NULLs is kept. """
        dict_with_all_nones_for_a_key = {
            'c': [
                {'e': 1, 'f': {'g': 1, 'h': 1}},
                {'e': 1, 'f': None}
            ]
        }
        expected = DataFrame({
            'c.e': [1, 1],
            'c.f.g': [1, None],
            'c.f.h': [1, None]
        })
        actual = as_dataframe(dict_with_all_nones_for_a_key)
        print(actual)
        self.assertTrue(expected.equals(actual))

#
# class TestFlattenedFunction(TestCase):
#     def test_with_3_levels_of_list_of_dicts(self):
#
#         nested = {
#             'a': [
#                 {
#                     'b': [
#                         {
#                             'c': [
#                                 {'x': 1, 'y': 2, 'z': 3},
#                                 {'x': 4, 'y': 5, 'z': 6},
#                                 {'x': 7, 'y': 8, 'z': 9}
#                             ]
#                         }
#                     ]
#                 }
#             ]
#         }
#
#         expected_flattened = {
#             'a.b.c.x': [1, 4, 7],
#             'a.b.c.y': [2, 5, 8],
#             'a.b.c.z': [3, 6, 9]
#         }
#
#         self.assertEqual(_flattened(nested), expected_flattened)


class TestTreeNode(TestCase):
    def test_leaf_nodes(self):
        tree = TreeNode('root', None)

        node_a = TreeNode('a')
        node_aa = TreeNode('aa')
        node_a.add_child(node_aa)

        node_aa.add_child(TreeNode('aaa', data=3))

        tree.add_child(node_a)

        print({node.full_name: node.data for node in tree.leaf_nodes()})


class TestFlattened2Function(TestCase):
    def test_with_3_levels_of_list_of_dicts(self):

        nested = {
            'a': [
                {
                    'b': [
                        {
                            'c': [
                                {'x': 1, 'y': 2, 'z': 3},
                                {'x': 4, 'y': 5, 'z': 6},
                                {'x': 7, 'y': 8, 'z': 9}
                            ]
                        }
                    ]
                }
            ]
        }

        expected_flattened = {
            'a.b.c.x': [1, 4, 7],
            'a.b.c.y': [2, 5, 8],
            'a.b.c.z': [3, 6, 9]
        }

        self.assertEqual(_flattened_2(nested), expected_flattened)

    def test_with_simple_dict(self):
        simple = {'a': 1, 'b': 2, 'c': 'foo'}

        self.assertEqual(_flattened_2(simple), simple)

    def test_with_list_of_nested_dicts(self):
        list_of_nested_dicts = {
            'a': [
                {'c': 1, 'd': {'e': 2}},
                {'c': 1, 'd': None}
            ]
        }

        expected = {'a.c': [1, 1], 'a.d.e': [2, None]}

        print(_flattened_2(list_of_nested_dicts))
        self.assertEqual(_flattened_2(list_of_nested_dicts), expected)


class TestGatheredFunction(TestCase):

    def test_with_mixed_values(self):
        mixed = [
            {'c': 1, 'd.e': 2},
            {'c': 1}
        ]

        print(_gathered(mixed))
