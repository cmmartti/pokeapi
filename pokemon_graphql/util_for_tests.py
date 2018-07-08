import collections

## Use this code before assertEqual:
#         from ..util_for_tests import to_dict, to_unicode
#         self.maxDiff = None
#         expected = to_unicode(expected)
#         executed = to_unicode(to_dict(executed))


def to_dict(ordered_dict):
    """
    Recursively convert an OrderedDict to a regular dict. Not strictly necessary, but makes deciphering error messages loads easier, especially since a line-by-line comparison is shown if actual and expected values are the same type. Use only if needed.
    """
    simple_dict = {}
    for key, value in ordered_dict.items():
        if isinstance(value, collections.OrderedDict):
            simple_dict[key] = to_dict(value)
        elif isinstance(value, list):
            simple_list = []
            for item in value:
                if isinstance(item, collections.OrderedDict):
                    simple_list.append(to_dict(item))
                else:
                    simple_list.append(item)
            simple_dict[key] = simple_list
        else:
            simple_dict[key] = value
    return simple_dict


def to_unicode(data):
    if isinstance(data, basestring):
        # return data.decode('utf8')
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(to_unicode, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(to_unicode, data))
    else:
        return data
