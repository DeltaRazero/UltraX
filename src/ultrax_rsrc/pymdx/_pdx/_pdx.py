import io
import os
import struct

from array import array

from .._misc import _util
from .._misc._encoding import ENC_LONG, ENC_WORD, SAMPLE_ENCODING
from .._misc.codec import *


class Pdx:
    """.PDX sample archive class.

        Attributes:
            Banks: Dictionary containing banks. Key values are
                integers in range 0~255. Number of banks should
                be 1 when not using EX-PCM mode in .MDX.
            InsertEmptyBanks: Bool to enable inserting empty banks
                when banks do not follow eachotherup (i.e. an empty
                bank is created when there is no bank between bank 0
                and bank 2).
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
        self.InsertEmptyBanks = True
        self._bank_filled = False 


    def ImportPdx(self, path, amount_banks=0):
        """Imports and inserts an existing .PDX bank.

        Args:
            path: File path to the .PDX file.
            amount_banks: Amount of banks to import from .PDX
                file. When set to 0, automatically detects the
                amount of banks present in .PDX file. 

        Returns:
            Void.
        """
        with open(path, 'rb') as rf:
            f = io.BytesIO(rf.read())
        l_file = os.path.getsize(path)


        # Bank recognition
        if (amount_banks == 0):

            # Every PDX file has atleast 1 bank
            amount_banks = 1

            #f.seek(4, 1)
            f.seek(0x304, 1)    # Skip to 2nd bank
            is_bank = True
            while (is_bank):
                for _ in range(96):
                    is_header_entry = struct.unpack(ENC_WORD, f.read(2))[0] == 0

                    if not (is_header_entry):
                        # TODO: EX-PDX lenght recognition (?)
                        is_bank = False
                        break

                    f.seek(6, 1)
                amount_banks += 1

        # Reset position + init banks
        f.seek(0, 0)
        banks = [_PdxBank() for _ in range(amount_banks)]

        # Get sample offsets
        sample_offsets = [[] for _ in range(amount_banks)]
        for b in range(amount_banks):
            for i in range(96):
                offset = struct.unpack(ENC_LONG, f.read(4))[0]
                f.seek(2, 1)
                lenght = struct.unpack(ENC_LONG, f.read(4))[0]
                sample_offsets[b].append((offset, lenght))

        # Get PCM data
        for b in range(amount_banks):
            for i, sample_offset in enumerate(sample_offsets[b]):

                if sample_offset[1] > 1 and (sample_offset[0] + sample_offset[1]) <= l_file:

                    f.seek(sample_offset[0])    # Go to sample start offset

                    sample = banks[b].Samples[i]
                    sample.Encoding = SAMPLE_ENCODING.ADPCM_OKI
                    sample.SampleData = f.read(sample_offset[1])
        
        f.close()

        b = sorted(self.Banks.keys())[-1] # Get last key number

        # TODO: actually check if there are empty banks
        if (self._bank_filled):
            b += 1    # Do not overwrite filled bank
            self._bank_filled = True

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

        if (self.InsertEmptyBanks):
            empty_bank_header_data = (struct.pack(ENC_LONG, 0) + pdx_gap + struct.pack(ENC_WORD, 0)) * 96
            empty_bank_header = array('B', empty_bank_header_data)

        previous_bank = next(iter(self.Banks))
        for k, bank in enumerate(self.Banks):

            if (self.InsertEmptyBanks):
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
    """.PDX sample bank class.

        Attributes:
            Samples: Array of type PdxSample class. Has 96
                instances of PdxSample. These will contain
                actual sample related data.
        """

    def __init__(self):
        self.Samples = [_PdxSample() for _ in range(96)]



class _PdxSample(SampleContainer):
    """.PDX sample bank class.

        Attributes:
            Encoding: Contains enum value of SAMPLE_ENCODING.
                Tells which encoding the given sample data is in.
                Set to SAMPLE_ENCODING.LPCM_16 by default.
            EncodeTo: Contains enum value of SAMPLE_ENCODING.
                Tells to which encoding the sample data should be
                converted to during export.
                Set to SAMPLE_ENCODING.ADPCM_OKI by default.
            Data: Vector/list that should contain sample data.
            Rate:
            ResampleTo:
        """

    def __init__(self):
        # Data: list, Encoding=SAMPLE_ENCODING.LPCM_16, EncodeTo=SAMPLE_ENCODING.ADPCM_OKI
        SampleContainer.__init__()
        self.Encoding = SAMPLE_ENCODING.LPCM_16
        self.EncodeTo = SAMPLE_ENCODING.ADPCM_OKI


    def Export(self, CodecContainerObj=None):    # TODO: Move to PDX export?

        if (CodecContainerObj is None):
            CodecContainerObj = CodecContainer()

        if (self.Encoding is self.EncodeTo):
            if type(self.Data) is list:         return bytearray(self.Data)
            if type(self.Data) is bytearray:    return self.Data
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
            self.Data = [_util.Sign_U8(sample) for sample in self.Data]
            self.Encoding = SAMPLE_ENCODING.LPCM_8

        elif (self.Encoding is SAMPLE_ENCODING.LPCM_U16):
            self.Data = [_util.Sign_U16(sample) for sample in self.Data]
            self.Encoding = SAMPLE_ENCODING.LPCM_16

        return
