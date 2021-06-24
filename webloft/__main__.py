import logging
import argparse
import os

import webloft


def main():
    try:
        args = setup_argparse()
        webloft.log.logger.setLevel(args.log_level)

        logging.debug(f'given arguments: {args}')

        if args.delete:
            webloft.delete(base_dir=args.path)
        else:
            webloft.build(base_dir=args.path, template_name=args.template)
    except Exception as e:
        logging.exception(e)


def setup_argparse():
    """Setup the command line arguments."""
    parser = argparse.ArgumentParser(description='Generate a static website.')
    parser.add_argument('path', type=str, nargs='?', default=os.curdir,
                        help='a path to the directory containing the '
                             'configuration files '
                             '(default: current directory)')
    parser.add_argument('-t', '--template', type=str, default='aquarius',
                        help='the name of the template to be used')
    parser.add_argument('-d', '--delete', action='store_true',
                        help='remove the build directory and exit.')
    parser.add_argument('-v', '--verbose', action='store_const',
                        default=logging.ERROR, const=logging.DEBUG,
                        dest='log_level',
                        help='show more descriptive and verbose log '
                             'messages.')
    parser.add_argument('-q', '--quiet', action='store_const',
                        default=logging.ERROR, const=logging.CRITICAL + 1,
                        dest='log_level',
                        help='suppress any log messages.')

    return parser.parse_args()


if __name__ == "__main__":
    main()
