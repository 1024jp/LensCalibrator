#!/usr/bin/env python
"""Create camera model using chessboard images.

(C) 2018 1024jp

usage:
    python modelcamera.py image_dir_path out_path
"""

import os
import sys
from glob import glob

import cv2
import numpy

from modules.undistortion import Undistorter


# consts
SUBPIXEL_CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
                     30, 0.001)


def main(imgdir_path, out_path='camera.pckl', chessboard_corners=(10, 7)):
    """
    Arguments:
    imgdir_path (str) -- path to the directory containing image files.
    out_path (str) -- path for camera model to pickle.
    chessboard_corners (int, int) -- (row, col)
    """
    obj_points = []  # 3D point in real world space
    img_points = []  # 2D point in image plane

    # grab a set of chessboard images taken with the camera to calibrate
    image_paths = glob(os.path.join(imgdir_path, '*.jpg'))
    if not image_paths:
        sys.exit("Calibration failed. No images of chessboards were found.")

    # detect images
    image_size = None
    for image_path in image_paths:
        # load image
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if not image_size:
            image_size = gray.shape[::-1]

        # find chessboard in the image
        found, corners = cv2.findChessboardCorners(
                gray, chessboard_corners, None)

        if found:
            # enhance corner accuracy
            corners = cv2.cornerSubPix(
                    image=gray,
                    corners=corners,
                    winSize=(11, 11),
                    zeroZone=(-1, -1),
                    criteria=SUBPIXEL_CRITERIA)

            # store result
            img_points.append(corners)

        # display detection result
        img = cv2.drawChessboardCorners(
                img, chessboard_corners, corners, found)
#         cv2.imshow('Chessboard', img)
#         cv2.waitKey(0)  # wait for key press

    # destroy any open CV windows
    cv2.destroyAllWindows()

    # exit on failures
    if not img_points:
        sys.exit("Calibration failed. No chessboards were detected.")

    # theoretical object points for the chessboard that will come out like:
    #     (0, 0, 0), (1, 0, 0), ...,
    #     (chessboard_corners[0]-1, chessboard_corners[1]-1, 0)
    objp = numpy.zeros((chessboard_corners[0]*chessboard_corners[1], 3),
                       numpy.float32)
    objp[:, :2] = numpy.mgrid[0:chessboard_corners[0],
                              0:chessboard_corners[1]].T.reshape(-1, 2)
    for _ in img_points:
        obj_points.append(objp)

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


if __name__ == "__main__":
    main(*sys.argv[1:])
