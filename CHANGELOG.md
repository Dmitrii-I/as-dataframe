# CHANGELOG

## 0.1.1
* Bug fix: could not convert nested dictionary with inner dictionary having a list as value, e.g. `{'a': {'b': [1, 2]}}`, because `num_rows` was derived from nested dictionary, but must be derived from flattened one. 

## 0.1.0
* Initial release