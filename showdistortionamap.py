#!/usr/bin/env python
"""
Display how the undistorter converts coordinates visibly.

(C) 2016-2018 1024jp
"""

import os
import sys

from modules import argsparser
from modules.datafile import Data
from modules.undistortion import Undistorter


class ArgsParser(argsparser.Parser):
    description = 'Display how the undistorter converts coordinates visibly.'
    datafile_name = 'location'


def main(data, size):
    """Display potential map for given location file.

    Arguments:
    data (Data) -- Data source instance.
    size (int, int) -- Width and height of source image.
    """
    undistorter = Undistorter.init(data.image_points, data.dest_points, size)
    undistorter.show_map()


def test():
    """Show potential map with test data.
    """
    from modules.datafile import LOC_FILENAME
    path = os.path.join(os.path.dirname(__file__), 'test', LOC_FILENAME)
    location_file = open(path, 'r')

    data = Data(open(path, 'r'))
    main(data, (3840, 2160))


if __name__ == "__main__":
    parser = ArgsParser()
    args = parser.parse_args()

    if args.test:
        test()
        sys.exit()

    data = Data(args.file, in_cols=args.in_cols)
    main(data, args.size)
