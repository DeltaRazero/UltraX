from .._misc import _util
import struct



# Encoding algorithm: Copyright (c) 2001 Tetsuya Isaki. All rights reserved.

class Oki_Encoder:

    _ADPCM_ESTIM_INDEX = [
         2,  6,  10,  14,  18,  22,  26,  30,
        -2, -6, -10, -14, -18, -22, -26, -30
    ]
    _ADPCM_ESTIM = [
        16,  17,  19,  21,  23,  25,  28,  31,  34,  37,
        41,  45,  50,  55,  60,  66,  73,  80,  88,  97,
        107, 118, 130, 143, 157, 173, 190, 209, 230, 253,
        279, 307, 337, 371, 408, 449, 494, 544, 598, 658,
        724, 796, 876, 963, 1060, 1166, 1282, 1411, 1552
    ]
    _ADPCM_ESTIM_STEP = [
        -1, -1, -1, -1, 2, 4, 6, 8,
        -1, -1, -1, -1, 2, 4, 6, 8
    ]

    _signal = 0
    _estim  = 0


    def Reset(self):
        self._signal = 0
        self._estim  = 0
        return


    # Converts a single sample: signed linear 16 bit --> Oki ADPCM 4 bit
    # See bottom of this file for comments/notes on the algorithm
    def _EncodeSample(self, n):
        """
        Encode a single sample from signed linear 16bit to 4bit OKI ADPCM

        """


        df = n - self._signal    # Delta of current sample - previous estimated sample
        dl = self._ADPCM_ESTIM[self._estim]   
        c = ((df / 16) * 8) / dl    # Scale 16bit to 12bit

        b = int(c/2)
        if (df < 0):    # If delta negative
            b = -b	    # Reverse negative to positve
            s = 0x08    # Set negative bit (bit3)
        else: s = 0x00	# Set positive bit (bit3)

        if (b > 0x07): b = 0x07    # Clip ADPCM sample (3 bits max) 

        s |= b  # Combine sign bit and value

        self._signal += self._ADPCM_ESTIM_INDEX[s] * dl
        self._estim  += self._ADPCM_ESTIM_STEP[b]

        self._estim = _util.Clamp(self._estim, 0, 48)

        return s


    def Encode(self, Sample_Data, Sample_BitDepth):
        """Encode 8bit or 16bit linear PCM """

        if not (Sample_BitDepth == 8 or Sample_BitDepth == 16):
            raise Exception()
        if (Sample_BitDepth == 8):
            Sample_Data = _util.Convert_8to16(Sample_Data)

        l_SampleData = len(Sample_Data)
        b_Add = False

        if (l_SampleData % 2):
            l_SampleData += 1
            b_Add = True

        l_e = l_SampleData / 2
        e = bytearray([0]*l_e)
        
        # for (int s = 0; s < l_e-2; s+=2)
        for s in range(0,l_e-2, 2):
            e[s] = self._EncodeSample(Sample_Data[s]) | (self._EncodeSample(Sample_Data[s+1])<<4)

        if (b_Add):
            e[l_e - 1] = self._EncodeSample(Sample_Data[l_SampleData-2]) | self._EncodeSample(0)
        else:
            e[l_e - 1] = self._EncodeSample(Sample_Data[l_SampleData-2]) | (self._EncodeSample(Sample_Data[l_SampleData-1])<<4)

        return e




class Oki_Decoder:
    """Class that can decode OKI ADPCM encoded audio streams.
    """

    _diff_lookup = None
    @property
    def DIFF_LOOKUP(self):  return type(self)._diff_lookup
    @DIFF_LOOKUP.setter
    def DIFF_LOOKUP(self, value): type(self)._diff_lookup = value

    STEP_INDEX_SHIFT = [-1, -1, -1, -1, 2, 4, 6, 8]

    OUTPUT_BITS = 12
    SIGNAL_GAIN = 4

    _signal = -2
    _step = 0


    def __init__(self):
        if (self.DIFF_LOOKUP is None):
            self.DIFF_LOOKUP = self._Compute_DiffTable()


    def Reset(self):
        """
        Resets the decoder object's SIGNAL and STEP value.
        """

        self.SIGNAL_MAX =  (1 << (self.OUTPUT_BITS - 1)) - 1
        self.SIGNAL_MIN = -(1 << (self.OUTPUT_BITS - 1))

        self._signal = -2
        self._step = 0


    def _Compute_DiffTable(self):
        bitmap = [
            [ 1, 0, 0, 0], [ 1, 0, 0, 1], [ 1, 0, 1, 0], [ 1, 0, 1, 1],
            [ 1, 1, 0, 0], [ 1, 1, 0, 1], [ 1, 1, 1, 0], [ 1, 1, 1, 1],
            [-1, 0, 0, 0], [-1, 0, 0, 1], [-1, 0, 1, 0], [-1, 0, 1, 1],
            [-1, 1, 0, 0], [-1, 1, 0, 1], [-1, 1, 1, 0], [-1, 1, 1, 1]
        ]
        diff_lut = [0] * (49 * 16)
        for step in range(49):

            stepval = int(16.0 * pow(11.0 / 10.0, float(step)))

            for nib in range(16):
                diff_lut[step * 16 + nib] = bitmap[nib][0] * \
                (stepval      * bitmap[nib][1] +
                 stepval // 2 * bitmap[nib][2] +
                 stepval // 4 * bitmap[nib][3] +
                 stepval // 8)
        
        return diff_lut


    def _DecodeNibble(self, nibble):

        self._signal += self.DIFF_LOOKUP[self._step * 16 + (nibble & 15)]
        self._signal = _util.Clamp(self._signal, self.SIGNAL_MIN, self.SIGNAL_MAX)

        self._step += self.STEP_INDEX_SHIFT[nibble & 7]
        self._step = _util.Clamp(self._step, 0, 48)

        decoded = self._signal << self.SIGNAL_GAIN
        decoded = _util.Clamp(decoded, -0x8000, 0x7FFF)

        return decoded


    def Decode(self, Data):
        """
        Decodes a binary OKI ADPCM encoded data stream.
        
        Args:
            Data: Binary OKI ADPCM encoded data stream.
            Splits: List of split points (in samples) to split
                    seperate files.

        Returns:
            Bytearray of decoded stream.
        """

        self.Reset()
        decoded = bytearray()

        for byte in Data:
            for nibble in (byte & 0x0F, byte >> 4):
                decoded.extend(
                    struct.pack("<h", self._DecodeNibble(nibble))
                )

        return decoded




class Oki:

    # Oki_Encoder _Encoder;
    # Oki_Decoder _Decoder;

    def __init__(self):
        self._Encoder = Oki_Encoder()
        self._Decoder = Oki_Decoder()
        self.b_ResetBeforeOperation = True


    def Encode(self, Sample_Data, Sample_BitDepth=16):
        if (self.b_ResetBeforeOperation): self._Encoder.Reset()
        return self._Encoder.Encode(Sample_Data, Sample_BitDepth)

    
    def Decode(self, Sample_Data):
        if (self.b_ResetBeforeOperation): self._Decoder.Reset()
        return self._Decoder.Decode(Sample_Data)
