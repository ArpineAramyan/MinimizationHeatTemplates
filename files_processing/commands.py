import argparse
import sys
import files_processing.FilesProcessing


def get_parser():
    parser = argparse.ArgumentParser(prog='Minimization')
    parser.add_argument('-th', '--templates_home',
                        metavar='<directory>',
                        type=str,
                        default='./',
                        help='Path to templates home directory. '
                             'Default value: "./"')
    parser.add_argument('-m', '--minimized',
                        metavar='<directory>',
                        type=str,
                        default='../minimized-heat-templates',
                        help='Path to directory with minimized templates. '
                             'Default value: "../minimized-heat-templates"')
    parser.add_argument('-rd', '--roles_data',
                        metavar='<filename>',
                        type=str,
                        default='roles_data.yaml',
                        help='Path from templates home to roles_data file. '
                             'Default value: "roles_data.yaml"')
    parser.add_argument('-pe', '--plan_env',
                        metavar='<filename>',
                        type=str,
                        default='plan-environment.yaml',
                        help='Path from templates home to plan-environment file. '
                             'Default value: "plan-environment.yaml"')
    parser.add_argument('-nd', '--network_data',
                        metavar='<filename>',
                        default='network_data.yaml',
                        help='Path from templates home to network_data file. '
                             'Default value: "network_data.yaml"')
    parser.add_argument('--parameters',
                        action='store_true',
                        help='Add this flag for printing parameters.')
    parser.add_argument('--services',
                        action='store_true',
                        help='Add this flag for printing services.')
    parser.add_argument('--resources',
                        action='store_true',
                        help='Add this flag for printing resources.')
    parser.add_argument('--param_only',
                        action='store_true',
                        help='Add this flag for printing parameters in minimized set.')
    return parser


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = get_parser()
    arguments = vars(parser.parse_args(args))
    files_processing.FilesProcessing.main(arguments['templates_home'], arguments['minimized'], arguments['roles_data'],
                                          arguments['plan_env'], arguments['network_data'], arguments['parameters'],
                                          arguments['services'], arguments['resources'], arguments['param_only'])
