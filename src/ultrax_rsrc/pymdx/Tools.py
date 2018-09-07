"""Tools for creation of MDX and related material."""

from enum import Enum as _Enum

__RESOLUTION_TABLE = {
    1: 144, # Max l32
    2: 192, # Max l64
    3: 256, # Max l128
}


def ClockValues(Resolution=2):
    """Returns an `enum` class with note lenght clocks.\n
    Accepted values for 'Resolution' are:
    - 1: 144 (max l32 )
    - 2: 192 (max l64 )
    - 3: 256 (max l128)"""

    ClockWholeNote = __RESOLUTION_TABLE[Resolution]

    CLOCK_VALUE_1   = ClockWholeNote-1   # = 191
    CLOCK_VALUE_2   = (ClockWholeNote /  2)-1
    CLOCK_VALUE_4   = (ClockWholeNote /  4)-1
    CLOCK_VALUE_8   = (ClockWholeNote /  8)-1
    CLOCK_VALUE_16  = (ClockWholeNote / 16)-1
    CLOCK_VALUE_32  = (ClockWholeNote / 32)-1
    if (Resolution>1):
        CLOCK_VALUE_64  = (ClockWholeNote / 64)-1
    if (Resolution>2):
        CLOCK_VALUE_128 = (ClockWholeNote / 128)-1


# class ClockValues(_Enum):
    

#     def __init__(self, Resolution=2):
        




def PcmAdpcm(path):
    NotImplemented