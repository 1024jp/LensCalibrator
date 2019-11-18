
LensCalibrator
========================

[![Test Status](https://github.com/1024jp/LensCalibrator/workflows/Test/badge.svg)](https://github.com/1024jp/LensCalibrator/actions)

__LensCalibrator__ converts coordinates in a picture to the real-world based on multiple reference points in the picture using openCV.

Requirements
------------------------

- Python 3.x
- modules
    - see [requirements.txt](requirements.txt)


Sample
------------------------

The blue circles in the images below are the reference points that located 1,700 mm height from the floor and were manually plotted from still frames. The blue lines are guidelines connecting reference points drawn on an assumption. Then, the red circles are re-calculated points via this script from the original (blue) reference points.

|                | Image |
|----------------|-------|
| original image | <img src="documentation/example_original.png" width="480"/> |
| undistorted    | <img src="documentation/example_undistortion.png" width="480"/> |
| undistorted + projected | <img src="documentation/example_projection.png" width="480"/> |


Usage
------------------------

See `--help`.

```sh
$ ./calibrate.py --help
usage: calibrate.py [-h] [--version] [-t] [-v] [--out FILE]
                    [--size WIDTH HEIGHT] [--in_cols INDEX INDEX]
                    [--out_cols INDEX INDEX] [-z Z]
                    [FILE]

Translate coordinates in a picture to the real world.

positional arguments:
  FILE                  path to source file

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -t, --test            test the program
  -v, --verbose         display debug info to standard output (default: False)

output options:
  --out FILE            path to output file (default: display to standard
                        output)

input options:
  --location FILE       path to location file (default: Localiton.csv in the
                        same directory of source fil)
  --camera FILE         path to camera model file for undistortion (default:
                        points in source file are used)

format options:
  --size WIDTH HEIGHT   dimension of the image (default: (3840, 2160))
  --in_cols INDEX INDEX
                        column positions of x, y in file (default: [2, 3])
  --out_cols INDEX INDEX
                        column positions of x, y in file for calibrated data
                        (default: same as in_cols
```


Mechanism of coordinates translation
------------------------

This program, `calibrate.py`, translates x, y (,z) coordinates in a 2D picture to the real world in two steps:

1. __undistortion__: Remove the camera lens distortion.
2. __projection__: Translate coordinates from a 2D space to the real-world space.


### 1. Undistotion

There are two strategies for the removal of the camera lens distortion:

1. Use reference points in the location file.
2. Use a camera model file.

You can choose one of those according to your data source. When a valid camera model file is given to the `calibrate.py` script with `-- camera` option, the second strategy is used; otherwise, the reference points in the location file is also used for the undistortion. In general, using a camera model file is recommended, especially when you have only a small number of reference points. If you use your reference points for undistortion, take many reference points, such as 20 or 30, to calculate accurate lens distortion.


### 2. Projection

The undistorted coordinates are then translated to the real-world space based on pairs of the reference point coordinates in the real-world and the picture.

When you take a video data, Shoot some reference points, of which x,y,z coordinates are known, with the same camera condition. Here, more than four reference points for each elevation level are required. Afterwards, measure the x, y coordinates of those reference points in the picture. The reference points are described in a location file and given to the program via `--location` option.




File format
------------------------

### Location file

- CSV format: comma-separated, LF line endings.
- Each line describes the relationship between a reference point in the picture and the real world. The first three columns represent x, y, z coordinates in the real world in mm, and the remaining two columns represent x,y coordinates in the picture in pixel.
- See file at `test/Location.csv` for example.


### Camera model file

Create a camera model file using `modelcamera.py`. Take more than 20 pictures of a checker pattern with different angles and place all of them in the same directory. Run `modelcamera.py` by passing the path to the checker pattern picture directory. See `modelcamera.py --help` for details.

You can obtain a checker pattern image from the openCV repository: [checker pattern image by openCV](https://github.com/opencv/opencv/blob/master/doc/pattern.png).