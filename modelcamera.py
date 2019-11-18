#!/usr/bin/env python
"""Create camera model from chessboard images.

(C) 2018 1024jp
"""

import argparse
import os
import sys
from glob import glob

import cv2
import numpy

from modules.undistortion import Undistorter
from modules.stdout import Style


# consts
SUBPIXEL_OPTIONS = {
    'winSize': (11, 11),
    'zeroZone': (-1, -1),
    'criteria': (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, .001),
}


def main(imgdir_path, out_path, chessboard_size, displays=False):
    """Create camera model from chessboard images and pickle the model.

    Arguments:
    imgdir_path (str) -- path to the directory containing image files.
    out_path (str) -- path for camera model to pickle.
    chessboard_size (int, int) -- number of inner corners in the chessboard
    """
    # grab a set of chessboard images taken with the camera to calibrate
    image_paths = glob(os.path.join(imgdir_path, '*.jpg'))
    if not image_paths:
        sys.exit("Calibration failed. No images of chessboards were found.")

    # detect images
    img_points = []  # 2D point in image plane
    image_size = None
    for image_path in sorted(image_paths):
        # load image
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if not image_size:
            image_size = gray.shape[::-1]

        # find chessboard in the image
        found, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

        if found:
            # enhance corner accuracy
            corners = cv2.cornerSubPix(
                    image=gray,
                    corners=corners,
                    **SUBPIXEL_OPTIONS)

            # store result
            img_points.append(corners)

        # display result to stdout
        filename = os.path.basename(image_path)
        if found:
            mark = Style.OK + '✔' + Style.END
        else:
            mark = Style.FAIL + '━' + Style.END
        print("{} {}".format(mark, filename))

        # display detection result
        img = cv2.drawChessboardCorners(img, chessboard_size, corners, found)
        if displays:
            display_size = tuple([int(l / 2) for l in image_size])
            img = cv2.resize(img, display_size)
            cv2.imshow('Chessboard', img)
            cv2.waitKey(0)  # wait for key press

    # destroy any open CV windows
    if displays:
        cv2.destroyAllWindows()

    # exit on failures
    if not img_points:
        sys.exit("Calibration failed. No chessboards were detected.")

    # theoretical 3D object points for the chessboard that will come out like:
    #     (0, 0, 0), (1, 0, 0), ...,
    #     (chessboard_size[0]-1, chessboard_size[1]-1, 0)
    objp = numpy.zeros((chessboard_size[0]*chessboard_size[1], 3),
                       numpy.float32)
    objp[:, :2] = numpy.mgrid[0:chessboard_size[0],
                              0:chessboard_size[1]].T.reshape(-1, 2)
    obj_points = [objp] * len(img_points)

    # create calibration model
    _, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            objectPoints=obj_points,
            imagePoints=img_points,
            imageSize=image_size,
            cameraMatrix=None,
            distCoeffs=None)

    # pickle
    camera = Undistorter(camera_matrix, dist_coeffs, rvecs, tvecs, image_size)
    camera.save(out_path)

    # display result to stdout
    print("Found {} chessboards in total {} images.".format(
            Style.BOLD + str(len(img_points)) + Style.END,
            Style.BOLD + str(len(image_paths)) + Style.END
    ))


def parse_args():
    """Parse command-line arguments.

    Returns:
    args (Namespace) -- namespace object contains parsed arguments
    """
    parser = argparse.ArgumentParser(
            description='Create camera model from chessboard images.')

    # argument
    parser.add_argument('imgdir_path',
                        type=str,
                        metavar='DIR_PATH',
                        help="path to the directory containing image files"
                        )
    parser.add_argument('out_file',
                        type=argparse.FileType('wb'),
                        metavar='FILE',
                        help="path for camera model to pickle"
                        )

    # optional arguments
    options = parser.add_argument_group('chessboard options')
    options.add_argument('-c', '--corners',
                         type=int,
                         nargs=2,
                         default=(6, 9),
                         metavar=('LOW', 'COL'),
                         help=("number of inner corners in chessboard"
                               " (default: %(default)s)")
                         )
    options.add_argument('-d', '--display',
                         action='store_true',
                         default=False,
                         help=("whether display the processing image"
                               " (default: %(default)s)")
                         )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.imgdir_path, args.out_file, args.corners, args.display)
