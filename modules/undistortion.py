#!/usr/bin/env python
"""


(C) 2007-2017 1024jp
"""

import pickle

import cv2
import numpy as np
import matplotlib.pyplot as plt


_flags = (cv2.CALIB_ZERO_TANGENT_DIST |
          cv2.CALIB_FIX_K3
          )


class Undistorter:
    def __init__(self, camera_matrix, dist_coeffs, rvecs, tvecs, image_size,
                 new_camera_matrix=None):
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.rvecs = rvecs
        self.tvecs = tvecs
        self.image_size = image_size
        self.new_camera_matrix = new_camera_matrix

    @classmethod
    def init(cls, image_points, dest_points, image_size):
        dest_3dpoints = [[x, y, 0] for x, y in dest_points]
        _, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
                [np.float32([dest_3dpoints])],
                [np.float32([image_points])],
                image_size, None, None, flags=_flags)

        self = cls(camera_matrix, dist_coeffs, rvecs, tvecs, image_size)
        self.__get_new_camera_matrix()

        return self

    @classmethod
    def load(cls, path):
        with open(path, mode='rb') as f:
            return pickle.load(path)

    def save(self, path):
        with open(path + '.pckl', 'wb') as f:
            pickle.dump(self, f)

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

    def __get_new_camera_matrix(self):
        self.new_camera_matrix = cv2.getOptimalNewCameraMatrix(
                self.camera_matrix, self.dist_coeffs, self.image_size, 0)[0]
