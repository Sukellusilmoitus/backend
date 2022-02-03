import ast


def parse_mongo_to_jsonable(item):
    if item.get('_id'):
        item['id'] = str(item['_id'])
        del item['_id']
    if 'created_at' in item:
        item['created_at'] = _datetime_to_valid_string(item['created_at'])
    return item


def _datetime_to_valid_string(date):
    return str(date).split(' ')[0]


def parse_byte_string_to_dict(value):
    dict_str = value.decode('UTF-8')
    dict_str = dict_str.replace('true', 'True')
    dict_str = dict_str.replace('false', 'False')
    data = ast.literal_eval(dict_str)
    return data
