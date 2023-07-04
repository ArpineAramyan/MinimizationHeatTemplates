import json


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True


def parameter_type_checker(parameter_value, parameter_type):
    if parameter_type == 'json' and is_json(str(parameter_value)):
        return True
    if parameter_type == 'comma_delimited_list' and isinstance(parameter_value, list):
        return True
    if parameter_type == 'string' and isinstance(parameter_value, str):
        return True
    if parameter_type == 'number' and isinstance(parameter_value, int):
        return True
    if parameter_type == 'boolean' and isinstance(parameter_value, bool):
        return True
    return False

