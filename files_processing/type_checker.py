import json


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True


def type_checker(parameter_value, parameter_type):
    bools = ['t', 'true', 'on', 'y', 'yes', '1', 'f', 'false', 'off', 'n', 'no', '0']
    # dict?
    if parameter_type == 'json' and is_json(str(parameter_value)):
        return True
    if parameter_type == 'comma_delimited_list':
        if isinstance(parameter_value, str) and len(parameter_value.split(',')) > 1:
            return True
        if isinstance(parameter_value, list):
            return True
    if parameter_type == 'string' and isinstance(parameter_value, str):
        return True
    if parameter_type == 'number' and (isinstance(parameter_value, int) or isinstance(parameter_value, float)):
        return True
    if parameter_type == 'boolean' and (isinstance(parameter_value, bool) or parameter_value in bools):
        return True
    return False


def parameters_type_checker(parameters_defaults, heat_parameters):
    for parameter, value_param in heat_parameters.items():
        if parameter not in parameters_defaults.keys() and value_param['default'] != '':
            parameters_defaults.update({parameter: value_param['default']})
        if parameter in parameters_defaults.keys():
            if not type_checker(parameters_defaults[parameter], value_param['type']):
                print('Value does not match the type. Check this parameter - ', parameter)
