#!/usr/bin/env python
"""
Remove distortion of camera lens and project to the real world coordinates.

(C) 2016-2017 1024jp
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


def main(datafile, outfile, size=DEFAULT_IMAGE_SIZE, z=None, in_cols=None):
    data = Data(datafile, z=z, in_cols=in_cols)
    undistorter = Undistorter(data.image_points, data.dest_points, size)
    undistorded_refpoints = undistorter.calibrate_points(data.image_points)
    projector = Projector(undistorded_refpoints.tolist(),
                          data.dest_points)

    # process data file
    def processor_handler(x, y):
        x, y = undistorter.calibrate_points([(x, y)])[0]
        return projector.project_point(x, y)
    data.process_coordinates(processor_handler, outfile)


def undistort(datafile, outfile, size=DEFAULT_IMAGE_SIZE, z=None, in_cols=None):
    data = Data(datafile, z=z, in_cols=in_cols)
    undistorter = Undistorter(data.image_points, data.dest_points, size)

    # process data file
    def processor_handler(x, y):
        return undistorter.calibrate_points([(x, y)])[0]
    data.process_coordinates(processor_handler, outfile)


def project(datafile, outfile, z=None, in_cols=None):
    data = Data(datafile, z=z, in_cols=in_cols)
    projector = Projector(data.image_points, data.dest_points)

    # process data file
    def processor_handler(x, y):
        return projector.project_point(x, y)
    data.process_coordinates(processor_handler, outfile)


class TestCase(unittest.TestCase):
    dirname = 'test'

    def test_projection(self):
        result_filename = 'result_projection.tsv'
        test_dir = os.path.join(os.path.dirname(__file__), self.dirname)
        filepath = os.path.join(test_dir, 'tracklog.tsv')
        resultpath = os.path.join(test_dir, result_filename)

        out = io.BytesIO()
        project(open(filepath, 'rU'), out)
        result = out.getvalue()
        expected_result = open(resultpath).read()

        for line, expected_line in zip(result.splitlines(),
                                       expected_result.splitlines()):
            self.assertEqual(line, expected_line)

    def test_undistortion(self):
        result_filename = 'result_undistortion.tsv'
        test_dir = os.path.join(os.path.dirname(__file__), self.dirname)
        filepath = os.path.join(test_dir, 'tracklog.tsv')
        resultpath = os.path.join(test_dir,  result_filename)

        out = io.BytesIO()
        undistort(open(filepath, 'rU'), out, size=(3840, 2160))
        result = out.getvalue()
        expected_result = open(resultpath).read()

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

    main(args.file, args.out, args.size, args.z, args.in_cols)
#     undistort(args.file, args.out, args.size, args.z, args.in_cols)
#     project(args.file, args.out, args.z, args.in_cols)
