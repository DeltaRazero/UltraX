from enum import Enum as _Enum


ENC_WORD = ">h"
ENC_LONG = ">l"


class SAMPLE_ENCODING(_Enum):
    "Sample encoding values, to be used in PDX."

    UNSUPPORTED = -1
    NO_ENCODING = 0
    ADPCM_OKI   = 1
    LPCM_16     = 2
    LPCM_8      = 3
    LPCM_U16    = 4
    LPCM_U8     = 5
