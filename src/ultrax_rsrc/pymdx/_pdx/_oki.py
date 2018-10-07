
# Encoding algorithm: Copyright (c) 2001 Tetsuya Isaki. All rights reserved.

class Oki:

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

    # Converts a single sample: signed linear 16 bit --> Oki ADPCM 4 bit
    # See bottom of this file for comments/notes on the algorithm
    def _EncodeSample(self, n):
        df = n - self.amp # Delta of current sample - previous estimated sample
        dl = self._ADPCM_ESTIM[self.estim]   
        c = ((df / 16) * 8) / dl    # Scale 16bit to 12bit

        b = int(c/2)
        if (df < 0):    # If delta negative
            b = -b
            s = 0x08    # Set negative bit (bit3)
        else: s = 0x00

        if (b > 0x07): b = 0x07     # Clip ADPCM sample (3 bits max) 

        s |= b  # Combine

        self.amp += self._ADPCM_ESTIM_INDEX[s] * dl
        self.estim += self._ADPCM_ESTIM_STEP[b]

        # Clip value
        if (self.estim < 0): self.estim = 0
        elif (self.estim > 48): self.estim = 48

        return s


    def Encode(self, wavedata):
        """Encode 8bit or 16bit linear PCM """

        # read wave from a wave module

        # if not 8bit or 16bit encoding: return

        # if 8bit encoding:
        # normalize routine

        self.amp = 0; self.estim = 0    # Reset
        e = bytearray()
        for c, v in enumerate(wavedata):
            if not ((c-1)%2):
                temp = self._EncodeSample(v)
            else:
                e.append(temp<<4 | self._EncodeSample(v))   # Combine

        return e



# Encoding comments by Tetsuya Isaki
# (Japanese loosely translated to English)
# ------------------------------------------
# mc_estim contains the index value of the previous difference ratio
# prediction value.

# df is the difference between the actual PCM value (Smp)
# and the previous predicted PCM value.

# dl is obtained by extracting the predicted difference ratio
# from the difference ratio prediction value table adpcm_estim[].

# c converts the difference to 12 bits and gives the ratio to (dl / 8).
#   --> /16 is the difference between 16 bits and 12 bits, that is, 2 ^ 4.
#   --> *8 is due to the fact that the value of dl i.e. adpcm_estim[]
#       is recorded with 8 times value.

# Processing changes depending on whether c is positive or negative.
#   --> However, c may be 0 by division, and df is used for sign
#       determination in order to avoid treating it as positive in that case.
#   --> The ADPCM data to actually encode is a combination of sign bit and
#       amplitude bit. The amplitude bit is obtained by dividing c by 2.

# Since the stored ADPCM amplitude is 3 bits, it is limited by 7.

# By doing s |= b, s is followed by a signed 4 bit.
#   --> b can be used properly as an unsigned absolute value.

# With the conversion so far after s|=b, the relationship between
# the amplitude bit b and the actual ratio c becomes:
#     b: ratio range c =
#          0: 0 <= Ratio <2
#          1: 2 <= Ratio <4
#          2: 4 <= Ratio <6
#          3: 6 <= Ratio <8
#          4: 8 <= Ratio <10
#          5: 10 <= Ratio <12
#          6: 12 <= Ratio <14
#          7: 14 <= Ratio

# Afterwards: Predict the next PCM value. It is very refreshing, but it is actually.
#
#   static int adpcm_estindex_ 0 [16] = {
#        1, 3, 5, 7, 9, 11, 13, 15,
#       -1, -3, -5, -7, -9, -11, -13, -15
#   };
#   mc -> mc_amp + = (short) (adpcm_estimindex - 0 [(int) s] * 16/8 * dl);
#          
# adpcm_estindex_0[] is 1/2 value of adpcm_estimindex[], meaning of this sequence
# is the median value of the above ratio range.
# By multiplying this ratio by 16 = 2 ^ 4 to make it into 16 bits and multiplying
# it by (dl / 8), the predicted difference value is obtained and recorded.
# That's why it's clearer if you doubled adpcm_estimindex[] beforehand.

# According to the value of b, predict the difference ratio to be used next
# time and save it in mc_estim. A total of 49 stages.
# Aside from that, when only used here (in encoding), adpcm_estimstep[16] can
# be adpcm_estimstep[8].
# adpcm_estimstep[16] is only necessary for in use for adpcm2pcm.