import io
import os
import struct
from array import array

from .._misc import _util
from .._misc._codec import *
from .._misc._encoding import ENC_LONG, ENC_WORD


class Pdx:
    """.PDX sample archive class.

        Attributes:
            Banks: Dictionary containing banks. Key values are
                integers in range 0~255. Number of banks should
                be 1 when not using EX-PCM mode in .MDX.
            bFillEmptyBanks: Boolean switch to fill in empty
                bank slots or to export them one after eachother.
                Defaults to True.
        """

    def __init__(self, Banks=1):
        """Init PDX class object.

        Args:
            Banks: Number of empty banks to insert in object.
                Input must be integer in range 0~255.
                Leave the default of 1 bank if not using EX-PCM
                mode in .MDX.
        """
        self.Banks = {i: _PdxBank() for i in range(Banks)}
        self.bFillEmptyBanks = True


    def ImportPdx(self, Path, AmountBanks=1):

        # TODO: Bank recognition

        with open(Path, 'rb') as rf:
            f = io.BytesIO(rf.read())
        l_file = os.path.getsize(Path)

        banks = [_PdxBank() for _ in range(AmountBanks)]

        pcm_offsets = [[] for _ in range(AmountBanks)]
        for b in range(AmountBanks):
            for i in range(96):
                offset = struct.unpack(ENC_LONG, f.read(4))
                f.seek(2, 1)
                lenght = struct.unpack(ENC_LONG, f.read(4))
                pcm_offsets[b].append((offset, lenght))

        # Get PCM data
        for b in range(AmountBanks):
            for i, pcm_offset in enumerate(pcm_offsets[b]):

                if pcm_offset[1] > 1 and (pcm_offset[0] + pcm_offset[1]) <= l_file:

                    f.seek(pcm_offset[0])    # Go to sample start offset

                    sample = banks[b].Samples[i]
                    sample.Encoding = SAMPLE_ENCODING.ADPCM_OKI
                    sample.SampleData = f.read(pcm_offset[1])
        
        f.close()

        b = sorted(self.Banks.keys())[-1] # Get last key number
        if (len(self.Banks) > 1):
            b += 1    # Do not overwrite filled bank

        for i, bank in enumerate(banks):
            self.Banks[b + i] = bank

        return


    def AddBank(self, Banknumber):
        """Adds a bank to object's bank map.

        Args:
            Banknumber: Bank key number to insert in map.
                Must be in range 0~255.

        Returns:
            Void.
        """
        if (Banknumber < 0):
            raise ValueError("Banknumber must be in range 0~255, given is \"{}\"".format(Banknumber) )

        if not (type(Banknumber) is int):
            raise TypeError("Input variable \"{}\" is not int".format(Banknumber) )
        
        if (Banknumber in self.Banks):
            raise Warning("Key \"{}\" already exists in bank map".format(Banknumber) )

        self.Banks[Banknumber] = _PdxBank()

        return


    def RemoveBank(self, Banknumber):
        """Remove a bank from object's bank map.

        Args:
            Banknumber (int): Bank key number to remove from map.
                Must be in range 0~255.

        Returns:
            Void.
        """
        if (Banknumber < 0):
            raise ValueError("Banknumber must be in range 0~255, given is \"{}\"".format(Banknumber) )

        if not (type(Banknumber) is int):
            raise TypeError("Input variable \"{}\" is not int".format(Banknumber) )
        
        if not (Banknumber in self.Banks):
            raise Warning("Key \"{}\" does not exist in bank map".format(Banknumber) )

        self.Banks.pop(Banknumber)

        return


    def Export(self):
        """
        Exports object to bytearray.

        Args:
            None.

        Returns:
            Bytearray with object data.
        """
        h = array('B')    # Header data
        s = array('B')    # Sample data

        offset = 0
        pdx_gap = struct.pack(ENC_WORD, 0)

        codecobj = CodecContainer()

        self.Banks = sorted(self.Banks.items())    # In C++ list of pointers maybe?

        if (self.bFillEmptyBanks):
            empty_bank_header_data = (struct.pack(ENC_LONG, 0) + pdx_gap + struct.pack(ENC_WORD, 0)) * 96
            empty_bank_header = array('B', empty_bank_header_data)

        previous_bank = next(iter(self.Banks))
        for k, bank in enumerate(self.Banks):

            if (self.bFillEmptyBanks):
                while (k != previous_bank+1):
                    h += empty_bank_header
                    previous_bank += 1

            for sample in bank.Samples:
                
                samplecntr = sample.Export(codecobj)
                l_sample   = len(samplecntr.SampleData)

                if (l_sample < 1):
                    pointer = struct.pack(ENC_LONG, 0)
                    lenght  = struct.pack(ENC_WORD, 0)
                else:
                    pointer = struct.pack(ENC_LONG, offset)
                    lenght  = struct.pack(ENC_WORD, l_sample)

                h += pointer, pdx_gap, lenght
                s.extend(samplecntr.SampleData)

                offset += l_sample

        return h + s



class _PdxBank:
    
    def __init__(self):
        self.Samples = [_PdxSample() for _ in range(96)]



class _PdxSample(SampleContainer):
    def __init__(self):
        # Data: list, Encoding=SAMPLE_ENCODING.LPCM_16, EncodeTo=SAMPLE_ENCODING.ADPCM_OKI
        self.Encoding = SAMPLE_ENCODING.LPCM_16
        self.SampleData = []

        self.EncodeTo = SAMPLE_ENCODING.ADPCM_OKI


    def Export(self, CodecContainerObj=None):    # TODO: Move to PDX export?

        if (CodecContainerObj is None):
            CodecContainerObj = CodecContainer()

        if (self.Encoding is self.EncodeTo):
            if type(self.SampleData) is list:         return bytearray(self.SampleData)
            if type(self.SampleData) is bytearray:    return self.SampleData
            raise Exception()

        self._Sign_LPCM()

        if (self.EncodeTo is SAMPLE_ENCODING.ADPCM_OKI):
            CodecContainerObj.ADPCM_OKI.Encode(self)

        elif (self.EncodeTo is SAMPLE_ENCODING.LPCM_8):
            CodecContainerObj.LPCM_8.Encode(self)

        elif (self.EncodeTo is SAMPLE_ENCODING.LPCM_8):
            CodecContainerObj.LPCM_16.Encode(self)


    def _Sign_LPCM(self):    # TODO: Move to PDX export?

        if (self.Encoding is SAMPLE_ENCODING.LPCM_U8):
            self.SampleData = [_util.Sign_U8(sample) for sample in self.SampleData]
            self.Encoding = SAMPLE_ENCODING.LPCM_8

        elif (self.Encoding is SAMPLE_ENCODING.LPCM_U16):
            self.SampleData = [_util.Sign_U16(sample) for sample in self.SampleData]
            self.Encoding = SAMPLE_ENCODING.LPCM_16

        return
