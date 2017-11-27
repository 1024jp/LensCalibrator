#!/usr/bin/env python
"""


(C) 2007-2017 1024jp
"""

import numpy as np
import cv2


class Projector:
    def __init__(self, image_points, ideal_points):
        self.homography = self._estimate_homography(image_points, ideal_points)

    @staticmethod
    def _estimate_homography(image_points, ideal_points):
        """Find homography matrix.
        """
        fp = np.array(image_points)
        tp = np.array(ideal_points)
        H, _ = cv2.findHomography(fp, tp, 0)
        return H

    def project_point(self, x, y):
        """Project x, y coordinates using homography matrix.

        Arguments:
        homography (list[list[float]]) -- 3x3 homography matrix.
        x (float) -- x coordinate to project.
        y (float) -- y coordinate to project.
        """
        result = np.dot(self.homography, [x, y, 1])
        projected_x = result[0] / result[2]
        projected_y = result[1] / result[2]

        return projected_x, projected_y

    def project_image(self, image, size, offset=(0, 0)):
        """Remove parspective from given image.

        Arguments:
        image numpy.array -- Image source in numpy image form.
        size ([int]) -- Size of the output image.
        """
        translation = np.matrix([
            [1.0, 0.0, -offset[0]],
            [0.0, 1.0, -offset[1]],
            [0.0, 0.0, 1.0]
        ])
        matrix = translation * self.homography

        return cv2.warpPerspective(image, matrix, tuple(size))
