
# Encoding algorithm: Copyright (c) 2001 Tetsuya Isaki. All rights reserved.
# Comments to be added later

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

    # Converts a single sample:
    # signed linear 16 bit --> Oki ADPCM 4 bit
    def _EncodeSample(self, Smp):
        estim = self.mc_estim

        df = a - self.mc_amp
        dl = self._ADPCM_ESTIM[self.mc_estim]
        c = int(df / 16 * 8 / dl)

        if (df < 0):
            b = int(-c / 2)
            s = 0x08
        else:
            b = int(c /2)
            s = 0x00

        if (b > 0x07):
            b = 0x07

        s |= b

        self.mc_amp += self._ADPCM_ESTIM_INDEX[s] * dl
        estim += self._ADPCM_ESTIM_STEP[b]

        if (estim < 0):
            estim = 0
        elif (estim > 48):
            estim = 48

        self.mc_estim = estim
        return s


    def Encode(self, wavedata):

        # read wave from a wave module

        # if not 8bit or 16bit encoding: return

        # if 8bit encoding:
        # normalize routine

        self.mc_amp = 0
        self.mc_estim = 0
        enc = self._EncodeSample

        e = bytearray()
        for c, v in enumerate(wavedata):
            if not ((c-1)%2):
                temp = enc(v)
            else:
                e.append(enc(v)<<4 | temp)

        return e

