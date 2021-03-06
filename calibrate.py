#!/usr/bin/env python
"""
Remove distortion of camera lens and project to the real world coordinates.

(C) 2016-2019 1024jp
"""

import io
import os
import unittest
import sys

import numpy as np

from modules import argsparser
from modules.datafile import Data
from modules.undistortion import Undistorter
from modules.projection import Projector

# constants
DEFAULT_IMAGE_SIZE = (3840, 2160)


def main(data, outfile, camerafile=None, size=DEFAULT_IMAGE_SIZE):
    if camerafile:
        undistorter = Undistorter.load(camerafile)
    else:
        undistorter = Undistorter.init(data.image_points, data.dest_points,
                                       size)
    undistorded_refpoints = undistorter.calibrate_points(data.image_points)
    projector = Projector(undistorded_refpoints.tolist(),
                          data.dest_points)

    # process data file
    def processor_handler(x, y, z):
        x, y = undistorter.calibrate_points([(x, y)])
        return projector.project_point(x, y, z)
    data.process_coordinates(processor_handler, outfile)


def undistort(data, outfile, camerafile=None, size=DEFAULT_IMAGE_SIZE):
    if camerafile:
        undistorter = Undistorter.load(camerafile)
    else:
        undistorter = Undistorter.init(data.image_points, data.dest_points,
                                       size)

    # process data file
    def processor_handler(x, y, z):
        return undistorter.calibrate_points([(x, y)])
    data.process_coordinates(processor_handler, outfile)


def project(data, outfile):
    projector = Projector(data.image_points, data.dest_points)

    # process data file
    def processor_handler(x, y, z):
        return projector.project_point(x, y, z)
    data.process_coordinates(processor_handler, outfile)


class TestCase(unittest.TestCase):
    dirname = 'test'

    def test_projection(self):
        result_filename = 'result_projection.tsv'
        test_dir = os.path.join(os.path.dirname(__file__), self.dirname)
        filepath = os.path.join(test_dir, 'tracklog.tsv')
        resultpath = os.path.join(test_dir, result_filename)

        out = io.StringIO()
        with open(filepath, 'r') as f:
            data = Data(f)
        project(data, out)
        result = out.getvalue()

        with open(resultpath) as f:
            expected_result = f.read()

        for line, expected_line in zip(result.splitlines(),
                                       expected_result.splitlines()):
            self.assertEqual(line, expected_line)

    def test_undistortion(self):
        result_filename = 'result_undistortion.tsv'
        test_dir = os.path.join(os.path.dirname(__file__), self.dirname)
        filepath = os.path.join(test_dir, 'tracklog.tsv')
        resultpath = os.path.join(test_dir,  result_filename)

        out = io.StringIO()
        with open(filepath, 'r') as f:
            data = Data(f)
        undistort(data, out, size=(3840, 2160))

        result = out.getvalue()
        with open(resultpath) as f:
            expected_result = f.read()

        for line, expected_line in zip(result.splitlines(),
                                       expected_result.splitlines()):
            self.assertEqual(line, expected_line)


if __name__ == "__main__":
    parser = argsparser.Parser()
    args = parser.parse_args()

    if args.test:
        suite = unittest.TestLoader().loadTestsFromTestCase(TestCase)
        unittest.TextTestRunner().run(suite)
        sys.exit()

    data = Data(args.file, loc_path=args.location, in_cols=args.in_cols,
                z_col=args.z_col)
    main(data, args.out, args.camera, args.size)
#     undistort(data, args.out, args.size)
#     project(data, args.out)
