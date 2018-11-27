#!/usr/bin/env python
"""
Undistort image.

(C) 2016-2018 1024jp
"""

import math
import os
import sys

import cv2
import numpy as np

from modules import argsparser
from modules.datafile import Data
from modules.undistortion import Undistorter
from modules.projection import Projector

# constants
SUFFIX = "_calib"


class ArgsParser(argsparser.Parser):
    description = 'Undistort image based on a location file.'
    datafile_name = 'image'

    def init_arguments(self):
        super(ArgsParser, self).init_arguments()

        script = self.add_argument_group('script options')
        script.add_argument('--save',
                            action='store_true',
                            default=False,
                            help="save result in a file instead displaying it"
                                 " (default: %(default)s)"
                            )
        script.add_argument('--perspective',
                            action='store_true',
                            default=False,
                            help="also remove perspective"
                                 " (default: %(default)s)"
                            )
        script.add_argument('--stats',
                            action='store_true',
                            default=False,
                            help="display stats"
                                 " (default: %(default)s)"
                            )


def add_suffix_to_path(path, suffix):
    """Append suffix  to file name before file extension.

    Arguments:
    path (str) -- File path.
    suffix (str) -- Suffix string to append.
    """
    root, extension = os.path.splitext(path)
    return root + suffix + extension


def show_image(image, scale=1.0, window_title='Image'):
    """Display given image in a window.

    Arguments:
    image () -- Image to display.
    scale (float) -- Magnification of image.
    window_title (str) -- Title of window.
    """
    scaled_image = scale_image(image, scale)

    cv2.imshow(window_title, scaled_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def scale_image(image, scale=1.0):
    """Scale up/down given image.

    Arguments:
    image () -- Image to process.
    scale (float) -- Magnification of image.
    """
    height, width = [int(scale * length) for length in image.shape[:2]]
    return cv2.resize(image, (width, height))


def plot_points(image, points, color=(0, 0, 255)):
    """Draw circles at given locations on image.

    Arguments:
    image -- Image to draw on.
    points -- x,y pairs of points to plot.
    """
    # find best radius for image
    image_width = image.shape[1]
    radius = int(image_width / 400)

    # draw
    for point in points:
        point = tuple(map(int, point))
        cv2.circle(image, point, color=color, radius=radius,
                   thickness=radius/2)


def estimate_clipping_rect(projector, size):
    """
    Return:
    rect -- NSRect style 2d-tuple.
    flipped (bool) -- Whether y-axis is flipped.
    """
    # lt -> rt -> lb -> rb
    image_corners = [(0, 0), (size[0], 0), (0, size[1]), size]
    x_points = []
    y_points = []
    for corner in image_corners:
        x, y = map(int, projector.project_point(*corner))
        x_points.append(x)
        y_points.append(y)
    min_x = min(x_points)
    min_y = min(y_points)
    max_x = max(x_points)
    max_y = max(y_points)

    rect = ((min_x, min_y), (max_x - min_x, max_y - min_y))
    flipped = y_points[3] < 0

    return rect, flipped


def main(data, saves_file=False, removes_perspective=True, shows_stats=False):
    imgpath = data.datafile.name
    image = cv2.imread(imgpath)
    size = image.shape[::-1][1:3]

    undistorter = Undistorter(data.image_points, data.dest_points, size)

    image = undistorter.undistort_image(image)
    undistorted_points = undistorter.calibrate_points(data.image_points)

    plot_points(image, undistorted_points)

    if shows_stats:
        print('[stats]')
        print('number of points: {}'.format(len(undistorted_points)))

    if removes_perspective:
        projector = Projector(undistorted_points, data.dest_points)

        # show stats if needed
        if shows_stats:
            diffs = []
            for point, (dest_x, dest_y) in zip(undistorted_points,
                                               data.dest_points):
                x, y = projector.project_point(*point)
                diffs.append([x - dest_x, y - dest_y])
            abs_diffs = [(abs(x), abs(y)) for x, y in diffs]
            print('mean: {:.2f}, {:.2f}'.format(*np.mean(abs_diffs, axis=0)))
            print(' std: {:.2f}, {:.2f}'.format(*np.std(abs_diffs, axis=0)))
            print(' max: {:.2f}, {:.2f}'.format(*np.max(abs_diffs, axis=0)))
            print('diff:')
            for x, y in diffs:
                print('     {:6.1f},{:6.1f}'.format(x, y))

        # transform image by removing perspective
        rect, is_flipped = estimate_clipping_rect(projector, size)

        image = projector.project_image(image, rect[1], rect[0])

        scale = float(size[0]) / image.shape[1]
        image = scale_image(image, scale)

        for point in data.dest_points:
            point = [scale * (l - origin) for l, origin in zip(point, rect[0])]
            plot_points(image, [point], color=(255, 128, 0))

        # flip image if needed
        if is_flipped:
            image = cv2.flip(image, 0)

    if saves_file:
        outpath = add_suffix_to_path(imgpath, SUFFIX)
        cv2.imwrite(outpath, image)
    else:
        show_image(image, scale=1.0/2, window_title='Undistorted Image')


if __name__ == "__main__":
    parser = ArgsParser()
    args = parser.parse_args()

    if args.test:
        print("This script doesn't have test.")
        sys.exit()

    data = Data(args.file, in_cols=args.in_cols)
    main(data, saves_file=args.save,
         removes_perspective=args.perspective, shows_stats=args.stats)
