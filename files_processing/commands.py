import argparse
import sys
import files_processing.FilesProcessing


def get_parser():
    parser = argparse.ArgumentParser(prog='Minimization')
    parser.add_argument('-th', '--templates_home',
                        metavar='<directory>',
                        type=str,
                        default='./',
                        help='Path to templates home directory')
    parser.add_argument('-m', '--minimized',
                        metavar='<directory>',
                        type=str,
                        default='../minimized-heat-templates',
                        help='Path to directory with minimized templates')
    parser.add_argument('-rd', '--roles_data',
                        metavar='<filename>',
                        type=str,
                        default='roles_data.yaml',
                        help='Path from templates home to roles_data file')
    parser.add_argument('-pe', '--plan_env',
                        metavar='<filename>',
                        type=str,
                        default='plan-environment.yaml',
                        help='Path from templates home to plan-environment file')
    return parser


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = get_parser()
    arguments = vars(parser.parse_args(args))
    files_processing.FilesProcessing.main(arguments['templates_home'], arguments['minimized'], arguments['roles_data'],
                                          arguments['plan_env'])
