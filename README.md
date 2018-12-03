
LensCalibrator
========================

__LensCalibrator__ converts coordinates in a picture to the real world based on multiple reference points in the picture.

Requirements
------------------------

- Python 3.x
- modules
    - see [requirements.txt](requirements.txt)


Sample
------------------------

The blue circles are the reference points that located 1700 mm height from the floor and were manually plotted from still frames. The blue lines are guidelines connecting reference points drawn on an assumption. Then, the red circles are re-calculated points via this script from the original (blue) reference points.

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


Location file format
------------------------

- The file name must be `Location.csv`.
- comma-separated, LF line endings
- Each line describes the relationship between a reference point in the picture and the real world. The first three columns represent x,y,z coordinates in the real world in mm, and the remaining two columns represent x,y coordinates in the picture in pixel.
- See file at `test/Location.csv` for example.
