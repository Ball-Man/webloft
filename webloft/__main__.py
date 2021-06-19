import logging
import argparse
import os

import webloft


LOGGING_FILE = 'webloft.log'
LOGGING_LEVEL = logging.DEBUG


def main():
    try:
        setup_logging()
        args = setup_argparse()

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
    parser.add_argument('-t', '--template', type=str, default='null',
                        help='the name of the template to be used')

    args = parser.parse_args()
    logging.debug(f'given arguments: {args}')
    return args


def setup_logging():
    """Setup the loggers and log level for mile.
    See LOGGING_LEVEL and LOGGING_FILE.
    """
    if __debug__:
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s',
                                      '%Y-%m-%d %H:%M:%S')

        logger = logging.getLogger()
        logger.setLevel(LOGGING_LEVEL)

        file_handler = logging.FileHandler(LOGGING_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        logging.debug('logging enabled')
    else:
        logging.disable()


if __name__ == "__main__":
    main()
