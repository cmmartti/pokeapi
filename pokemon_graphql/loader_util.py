from loader_key import LoaderKey

'''
Some utility functions for loaders.
'''


def divide_by_key(keys, values, compare_fn):
    '''
    Given a list of `keys` and a list of `values`, return a list of values with the same length and order as `keys`. Each value in the returned list shall be a value from `values` that passes the test implemented by the provided `compare_fn` function. Used to de-batch a results list.
    '''

    results = []
    for key in keys:
        value = None
        for obj in values:
            if compare_fn(key, obj):
                value = obj
                break
        results.append(value)
    return results


def group_by_batch(keys):
    '''
    Given a list of `keys` (instances of LoaderKey), return a dictionary that groups each key `id` value under its `args` value in a dictionary. Each unique `args` object from `keys` forms the dictionary's keys while the dict's values are a list of corresponding key `id`s for values.

    Example `keys` argument = [
        LoaderKey(id=1, arg1='x'),
        LoaderKey(id=2, arg1='x'),
        LoaderKey(id=3, arg1='z'),
        LoaderKey(id=1, arg1='z')
    ]
    Example return value = {
        Args(arg1='x',): [1, 2],
        Args(arg1='z',): [3, 1]
    }
    '''

    batches = {}
    for key in keys:
        assert isinstance(key, LoaderKey)
        if key.args in batches:
            batches[key.args].append(key.id)
        else:
            batches[key.args] = [key.id]
    return batches


def get_relations(keys, get_query_set_fn, id_attr):
    '''
    Given a list of `keys` (instances of LoaderKey), return a list of results the same length as `keys`, with each result corresponding to the correct key. Each result is a list of values that match up to the key.
    The values are batch-fetched with the provided `get_query_set_fn(ids, **args)`, and each value is matched up to the key by comparing the `id_attr` of the value to the key's id.
    '''

    # Create a new query set for each set of args using `get_query_set_fn`
    batched_items = {}
    for args, ids in group_by_batch(keys).iteritems():
        batched_items[args] = get_query_set_fn(ids, **args._asdict()) # TODO: Should ids be de-duplicated?

    # Iterate through each item in each batch and match it to the keys
    # to create a results list
    results = []
    for key in keys:
        values = []
        for args, batch in batched_items.iteritems():

            # Don't bother going down the rabbit hole if this one doesn't have
            # the right `args`
            if key.args == args:
                for item in batch:
                    if not hasattr(item, id_attr):
                        raise ValueError('%s has no id_attr %s' % (item, id_attr))

                    # Does it match?
                    if key.id == getattr(item, id_attr):
                        values.append(item)

        results.append(values)
    return results


def add_filters(query_set, args, **map):
    '''Return query_set with applicable filters applied.
     - query_set: Django query set
     - args: a dictionary containing filter values
     - map: keyword arguments mapping the filter name to the ORM filter name
    '''
    for sql_name, name in map.iteritems():
        if name in args and args[name] is not None:
            query_set = query_set.filter(**{sql_name: args[name]})
    return query_set
