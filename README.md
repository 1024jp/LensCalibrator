
LensCalibrator
========================

__LensCalibrator__ converts coordinates in a picture to the real world based on multiple reference points in the picture.

Requirements
------------------------

- Python 2.x
- modules
    - see [requrements.txt]()


Usage
------------------------

See `--help`.


Location file format
------------------------

- The file name must be `Location.csv`.
- comma-separated, LF line endings
- Each line describes the relationship between a reference point in the picture and the real world. The first three columns represent x,y,z coordinates in the real world in mm, and the remaining two columns represent x,y coordinates in the picture in pixel.
- See file at `test/Location.csv` for example.
