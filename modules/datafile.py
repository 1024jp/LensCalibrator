#!/usr/bin/env python
"""
Datafile object for tracklog and Loc file.

(C) 2016 1024jp
"""

import csv
import os
from itertools import izip


# constants
LOC_FILENAME = "Location.csv"
IGNORE_COLUMNS = 2  # number of first columns to ignore in data file
FIND_LEVEL = 3  # number of parent directories to find in.


class Data(object):
    def __init__(self, datafile, z=None):
        """Initialize Data object.

        Arguments:
        datafile (file) -- main data file in file-like object form.
        z_filter (int) -- Z-axis in destination points to obtain.
        """
        # sanitize path
        self.datafile = datafile
        self.dirpath = os.path.dirname(datafile.name)

        # load Loc file
        self.loc_path = self._find_file(LOC_FILENAME)[0]
        image_points, dest_points = self._load_location(z_filter=z)
        self.image_points = image_points
        self.dest_points = dest_points

    def _find_file(self, filename, subdirectory=None):
        """Find file in the same directory and also parent directories

        Arguments:
        filename (str) -- filename.
        subdirectory (str) -- directory where file is located.
        """
        paths = []
        dirpath = self.dirpath
        for _ in range(FIND_LEVEL):
            components = [dirpath, filename]
            if subdirectory:
                components.insert(subdirectory)
            path = os.path.join(*components)
            if os.path.exists(path):
                paths.append(path)
            dirpath = os.path.dirname(dirpath)

        return paths

    def _load_location(self, z_filter=None):
        """Load location definition file.

        Returns:
        image_points -- x,y pairs of reference points in image.
        dest_points -- corresponding x,y pairs of ref points in field.
        """
        image_points = []
        dest_points = []
        with open(self.loc_path, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                if len(row) < 4:
                    continue
                first_char = row[0][0]
                if first_char.isalpha() or first_char is '#':
                    continue
                row = map(float, row)
                image_point = row[3:5]
                dest_point = row[0:3]
                if z_filter and dest_point[2] != z_filter:
                    continue
                image_points.append(image_point)
                dest_points.append(dest_point[0:2])

        return image_points, dest_points

    def file_named(self, filename, exists=False):
        path = os.path.join(self.dirpath, filename)
        if exists and not os.path.exists(path):
            return None
        return path

    def process_coordinates(self, processor_handler, output):
        with self.datafile as file_in:
            # detect delimiter
            dialect = csv.Sniffer().sniff(file_in.read(1024), delimiters=',\t')
            file_in.seek(0)

            reader = csv.reader(file_in, dialect)
            writer = csv.writer(output, dialect)

            for row in reader:
                new_row = row[:]  # copy
                for i, pair in enumerate(pairwise(row[IGNORE_COLUMNS:])):
                    try:
                        x, y = map(float, pair)
                    except ValueError:  # go to next column if not number
                        break

                    # translate
                    x, y = processor_handler(x, y)

                    column = 2 * i + IGNORE_COLUMNS
                    new_row[column] = int(x)
                    new_row[column + 1] = int(y)

                writer.writerow(new_row)


def pairwise(iterable):
    """Iterate every two items.

    Arguments:
    iterable -- an iterable object.
    """
    it = iter(iterable)
    return izip(it, it)
