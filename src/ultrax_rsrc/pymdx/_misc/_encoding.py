from enum import Enum


ENC_WORD = ">h"
ENC_LONG = ">l"

class SAMPLE_ENCODING(Enum):
    "Sample encoding values, to be used in PDX."

    PCM_16      = 0
    PCM_8       = 1
    ADPCM_OKI   = 2
    PCM_U8      = 3
    PCM_U16     = 4
