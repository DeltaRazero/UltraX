import struct as struct
from .._misc._encoding import *

OPM_CLOCK = 4000000 # Hz


class Rest:     # 休符データ
    def __init__(self, Clocks):
        self.Clocks = Clocks
    def Export(self):
        return bytearray(self.Clocks-1)


class Note:     # 音符データ
    def __init__(self, Data, Clocks):
        self.Data = Data
        self.Clocks = Clocks
    def Export(self):
        # if (0x80 > self.Data > 0xDF  or  self.Clocks < 0): raise AnException
        return bytearray([self.Data, self.Clocks-1])


# opm_tempo = 256 - 60 * opm_clock / (bpm_tempo * 48 * 1024)          opm_tempo = 256 - (78125 / (16 * bpm_tempo))
# bpm_tempo = 60 * opm_clock / (48 * 1024 * (256 - opm_tempo))        bpm_tempo = 78125 / (16 * (256 - opm_tempo))
class Tempo_Bpm:    # テンポ設定
    def __init__(self, Data):   # TODO: Calculate BPM to data
        self.Data = Data
    def Export(self):
        global OPM_CLOCK
        timerb = round(256 - 60 * OPM_CLOCK / (self.Data * 48 * 1024))
        return bytearray([0xFF, timerb])


class Tempo_TimerB:    # テンポ設定
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([0xFF, self.Data])


class OpmControl:  # OPMレジスタ設定
    def __init__(self, Register, Data):
        self.Register = Register
        self.Data = Data
    def Export(self):
        return bytearray([self.Register, self.Data])


class Tone:     # 音色設定
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([0xFD, self.Data])


class Pan:      # 出力位相設定
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([0xFC, self.Data])


class Volume:   # 音量設定
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([0xFB, self.Data])


class Volume_Increase:   # 音量増大
    def Export(self):
        return bytearray([0xFA])


class Volume_Decrease:   # 音量減小
    def Export(self):
        return bytearray([0xF9])


class Gate:     # ゲートタイム
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([0xF8, self.Data])


class Legato:   # Disable keyoff for next note / キーオフ無効
    def Export(self):
        return bytearray([0xF7])


class Repeat_Start:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([0xF6, self.Data, 0x00])


class Repeat_End:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        e = bytearray([0xF5])
        e.extend(struct.pack(ENC_WORD, -self.Data))
        return e


class Repeat_Escape:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        e = bytearray([0xF4])
        e.extend(struct.pack(ENC_WORD, self.Data))
        return e


class Detune:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        e = bytearray([0xF3])
        e.extend(struct.pack(ENC_WORD, self.Data))
        return e


class Portamento:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        e = bytearray([0xF2])
        e.extend(struct.pack(ENC_WORD, self.Data))
        return e


class DataEnd:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        if (self.Data < 1):
            return bytearray([0xF1, self.Data])
        else:
            e = bytearray([0xF1])
            e.extend(struct.pack(ENC_WORD, self.Data))
            return e


class AdpcmFreq:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        e = bytearray([0xED])
        e.append(self.Data)
        return e


class Pcm8Shift:
    def Export(self):
        return bytearray([0xE8])

