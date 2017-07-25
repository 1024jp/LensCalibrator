#!/usr/bin/env python
"""


(C) 2007-2017 1024jp
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt


class Undistorter(object):
    flags = (cv2.CALIB_ZERO_TANGENT_DIST |
             cv2.CALIB_FIX_K3
             )

    def __init__(self, image_points, dest_points, size=(3840, 2160)):
        self.image_points = np.float32([image_points])
        self.dest_3dpoints = np.float32([[[x, y, 0] for x, y in dest_points]])
        self.image_size = size
        self._calibrate_lens()

    def _calibrate_lens(self):
        retval, camera_matrix, coeffs, rvecs, tvecs = cv2.calibrateCamera(
                [self.dest_3dpoints], [self.image_points], self.image_size,
                None, None, flags=self.flags)

        self.new_camera_matrix = cv2.getOptimalNewCameraMatrix(
                camera_matrix, coeffs, self.image_size, 0)[0]

        self.camera_matrix = camera_matrix
        self.dist_coeffs = coeffs

    @property
    def undistorted_refpoints(self):
        return self.calibrate_points(self.image_points[0])

    def calibrate_points(self, points):
        return cv2.undistortPoints(np.array([points]), self.camera_matrix,
                                   self.dist_coeffs,
                                   P=self.new_camera_matrix)[0]

    def undistort_image(self, image):
        return cv2.undistort(image, self.camera_matrix, self.dist_coeffs,
                             newCameraMatrix=self.new_camera_matrix)

    def show_map(self):
        interval = 200
        size = self.image_size
        w, h = np.meshgrid(range(0, size[0], interval),
                           range(0, size[1], interval))
        points = np.vstack((w.flatten(), h.flatten())).T.astype('float32')
        new_points = self.calibrate_points(points)

        plt.scatter(points[:, 0], points[:, 1], 20, 'b', alpha=.5)
        plt.scatter(new_points[:, 0], new_points[:, 1], 20, 'r', alpha=.5)

        plt.axes().set_aspect('equal', 'datalim')
        plt.show()
