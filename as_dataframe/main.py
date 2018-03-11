
from collections import defaultdict
from pandas import DataFrame
from typing import Dict, List, NewType, Any


TypeDataFrame = NewType('TypeDataFrame', DataFrame)


def as_dataframe(obj: Dict or List[Dict]) -> TypeDataFrame:
    """ Returns dataframe built from dictionary or list of dictionaries.

    :param obj: Dictionary or list of dictionaries.
    :returns: Dataframe.
    """

    if isinstance(obj, dict):
        obj = [obj]

    combined_df = DataFrame()
    for d in obj:
        flat = _flattened_2(d)
        num_rows = max([1] + [len(flat[k]) for k in flat if isinstance(flat[k], list)])
        df = DataFrame(flat, index=range(num_rows))
        combined_df = combined_df.append(df, ignore_index=False, verify_integrity=False)

    combined_df = combined_df.reset_index(drop=True)
    #combined_df = combined_df.dropna(axis='columns', how='all')
    return combined_df


def _flattened(nested_dict: dict) -> dict:
    """ Returns flattened dictionary

    :param nested_dict: Nested dictionary. A nested dictionary is a dictionary with at least one value being a
    dictionary that itself may be nested, ad infinitum. E.g.: `{'a': 1, 'b': {'c': 2, 'd': 3}}`.
    :returns: Flattened dictionary.
    """

    flat = dict()

    for k, v in nested_dict.items():

        if isinstance(v, list) and len(v) == 1:
            v = v[0]

        if isinstance(v, dict):
            flattened = _flattened(v)
            flattened = {str(k) + '.' + k_flattened: flattened[k_flattened] for k_flattened in flattened}
            flat.update(flattened)
        elif isinstance(v, list):
            if all([isinstance(el, dict) for el in v]):
                new = _gathered(v)
                flat.update({str(k) + '.' + kk: new[kk] for kk in new})
            else:
                flat.update({k: v})
        else:
            flat.update({k: v})

    return flat


def _flattened_2(dictionary: dict) -> dict:

    tree = TreeNode()

    for k, v in dictionary.items():

        node = TreeNode(name=k)

        if isinstance(v, list) and len(v) == 1:
            v = v[0]

        if isinstance(v, dict):
            v = _flattened_2(v)
            for k_flattened, v_flattened in v.items():
                sub_node = TreeNode(name=k_flattened, data=v_flattened)
                node.add_child(sub_node)
        elif isinstance(v, list):
            if all([isinstance(el, dict) for el in v]):
                v = [_flattened_2(d) for d in v]  ## replace by as_tree
                v = _gathered(v)
                for k_flattened, v_flattened in v.items():
                    sub_node = TreeNode(name=k_flattened, data=v_flattened)
                    node.add_child(sub_node)
            else:
                node.data = v
        else:
            node.data = v

        tree.add_child(node)

    flattened = {leaf.full_name: leaf.data for leaf in tree.leaf_nodes()}

    return flattened


def _as_tree(d: dict):
    pass

def _gathered(dictionaries: list, missing_value: str=None) -> dict:
    """ Returns a single dictionary built from a list of dictionaries

    :param dictionaries: List of non-nested dictionaries. The dictionaries are allowed to be heterogeneous.
    :param missing_value: How to represent missing values when the dictionaries are heterogeneous.
    :returns: A single dictionary.
    """

    all_keys = set([key for d in dictionaries for key in list(d.keys())])
    dictionary = dict(zip(all_keys, [list() for _ in range(len(all_keys))]))

    for d in dictionaries:
        d = defaultdict(lambda: missing_value, **d)
        for k in all_keys:
            dictionary[k].append(d[k])

    return dictionary


class TreeNode:
    def __init__(self, name: str=None, data: Any=None):
        self.name = name
        self.data = data
        self.children = []
        self.parents = []
        self.delimiter = '.'

    def add_child(self, node):

        if self.data:
            raise ValueError('Cannot add children because the node contains data')

        node.parents = self.parents + [self]
        self.children.append(node)

    def leaf_nodes(self):
        leaves = []

        for node in self.children:
            if not node.children:
                leaves.append(node)
            else:
                leaves.extend(node.leaf_nodes())
        return leaves

    @property
    def full_name(self):
        return self.delimiter.join([p.name for p in self.parents if p.parents] + [self.name])

    def __str__(self):
        return str(self.name)
