#!/usr/bin/env python

"""Command line arguments parser.

(C) 2016-2018 1024jp
"""

import argparse
import io
import logging
import os
import sys

try:
    from . import __version__ as version
except ImportError:
    version = 'n/a'


class Parser(argparse.ArgumentParser):
    description = 'Translate coordinates in a picture to the real world.'
    datafile_name = 'source'

    def __init__(self):
        argparse.ArgumentParser.__init__(self, description=self.description)
        self.init_arguments()

    def init_arguments(self):
        """Setup arguments of command.
        """
        # argument
        self.add_argument('file',
                          type=argparse.FileType('rb'),
                          metavar='FILE',
                          nargs='?',
                          help="path to source file"
                          )

        # define options
        self.add_argument('--version',
                          action='version',
                          version=version
                          )
        self.add_argument('-t', '--test',
                          action='store_true',
                          default=False,
                          help="test the program"
                          )
        self.add_argument('-v', '--verbose',
                          action='store_true',
                          default=False,
                          help="display debug info to standard output"
                               " (default: %(default)s)"
                          )

        output = self.add_argument_group('output options')
        output.add_argument('--out',
                            type=argparse.FileType('w'),
                            default=sys.stdout,
                            metavar='FILE',
                            help="path to output file"
                                 " (default: display to standard output)"
                            )

        input_ = self.add_argument_group('input options')
        input_.add_argument('--location',
                            type=str,
                            default=None,
                            metavar='FILE',
                            help="path to location file"
                                 " (default: Localiton.csv in the same"
                                 " directory of source fil)"
                            )
        input_.add_argument('--camera',
                            type=argparse.FileType('rb'),
                            default=None,
                            metavar='FILE',
                            help="path to camera model file for undistortion"
                                 " (default: points in source file are used)"
                            )

        # format values
        fileformat = self.add_argument_group('format options')
        fileformat.add_argument('--size',
                                type=int,
                                nargs=2,
                                default=(3840, 2160),
                                metavar=('WIDTH', 'HEIGHT'),
                                help=("dimension of the image"
                                      " (default: %(default)s)")
                                )
        fileformat.add_argument('--in_cols',
                                type=int,
                                nargs=2,
                                default=[2, 3],
                                metavar='INDEX',
                                help=("column positions of x, y in file "
                                      " (default: %(default)s)")
                                )
        fileformat.add_argument('--z_col',
                                type=int,
                                default=None,
                                metavar='INDEX',
                                help=("column position of z in file "
                                      " (default: %(default)s)")
                                )
        fileformat.add_argument('--out_cols',
                                type=int,
                                nargs=2,
                                default=None,
                                metavar='INDEX',
                                help=("column positions of x, y in file for"
                                      " calibrated data"
                                      " (default: same as in_cols")
                                )

    @property
    def datafile(self):
        """Path to data file.

        Return:
        datafile (file) -- File to process, given as a command argument.
        """
        args = super(Parser, self).parse_args()
        return args.file

    def parse_args(self, **kwargs):
        """Parse command arguments and return.

        Return:
        args (namespace) -- a simple object holding command arguments.
        """
        args = super(Parser, self).parse_args(**kwargs)

        if len(kwargs) > 0:
            return args

        if not args.test and not args.file:
            self.error('This script requires a path to a {} file.\n'.format(
                    self.datafile_name))

        # size to tuple instead of list
        args.size = tuple(args.size)

        # set logging level
        if args.verbose:
            logging.basicConfig(level=logging.DEBUG,
                                format='[%(levelname)s] %(module)s -'
                                       '%(message)s (%(relativeCreated)4dms)')
            display(args)

        return args


def display(args):
    """Display input arguments for test use.
    """
    print('[arguments]')
    for key, arg in vars(args).items():
        if isinstance(arg, io.IOBase):
            arg = arg.name
        print('    {:10s} {}'.format(key + ':', arg))


if __name__ == "__main__":
    parser = Parser()
    display(parser.parse_args())
