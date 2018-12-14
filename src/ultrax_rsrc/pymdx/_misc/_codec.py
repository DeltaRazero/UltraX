from ._encoding import SAMPLE_ENCODING
from ._oki import Codec_Adpcm_Oki as _Codec_Adpcm_Oki
#from ._lpcm import Codec_Lpcm_8, Codec_Lpcm_16


class SampleContainer:
    Encoding = SAMPLE_ENCODING.NO_ENCODING
    SampleRate = 0
    SampleData = []


class CodecContainer:

    def __init__(self):
        self.ADPCM_OKI = _Codec_Adpcm_Oki(self)
        #self.LPCM_8    = _Codec_Lpcm_8()
        #self.LPCM_16   = _Codec_Lpcm_16()
