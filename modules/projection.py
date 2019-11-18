#!/usr/bin/env python
"""


(C) 2007-2018 1024jp
"""
from collections import defaultdict
from itertools import groupby

import numpy as np
import cv2


class Projector:
    def __init__(self, image_points, dest_points):
        # group by height
        points = {}
        for image_point, dest_point in zip(image_points, dest_points):
            height = dest_point[2]
            if height not in points:
                points[height] = [[], []]
            points[height][0].append(image_point)
            points[height][1].append(dest_point[:2])

        # get homography for each height
        self.homographies = {}
        for height, points in points.items():
            self.homographies[height] = self._estimate_homography(*points)

    @staticmethod
    def _estimate_homography(image_points, dest_points):
        """Find homography matrix.
        """
        fp = np.array(image_points)
        tp = np.array(dest_points)
        H, _ = cv2.findHomography(fp, tp, 0)
        return H

    def project_point(self, x, y, z=None):
        """Project x, y coordinates using homography matrix.

        Arguments:
        x (float) -- x coordinate to project.
        y (float) -- y coordinate to project.
        z (float) -- z coordinate to project.
        """
        if z:
            homography = self.homographies[z]
        else:
            homography = list(self.homographies.values())[0]
        result = np.dot(homography, [x, y, 1])
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
