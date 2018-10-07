
from ._oki import Oki
from .._misc._encoding import *






class Pdx:
    def __init__(self, Expdx=False):
        pass


class Sample:
    def __init__(self, Data, Encoding=0, EncodeAdpcm=True):
        self.Encoding = Encoding
        self.SampleData = Data
        self.EncodeAdpcm = EncodeAdpcm


    def Export(self):
        if self.Encoding == (SAMPLE_ENCODING.PCM_8 or SAMPLE_ENCODING.PCM_16):
            if (self.Encoding == SAMPLE_ENCODING.PCM_8):   # Must be signed
                self.SampleData = [i*256 for i in self.SampleData]  # Convert 8bit pcm to 16bit pcm

            if (self.EncodeAdpcm):
                self.SampleData = Oki().Encode(self.SampleData)
            # else:
            #     if (len(self.SampleData)//2 != 0): self.SampleData.append(0)



        


class Bank:
    def __init__(self):
        self.Map = [_ for _ in range(96)]



a = Bank()



print (a.Map)