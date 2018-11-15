import struct as struct
from .._misc._encoding import *
from .._misc.exc import *

_OPM_CLOCK = 4000000 # Hz

__CMD_EXT       = 0xE7
__CMD_EXT_02EX  = 0xE6
# TODO: Make these globals in classes


#===========================================#
#   Standard commands
#===========================================#
#region
class Rest:     # 休符データ
    def __init__(self, Clocks):
        self.Clocks = Clocks
    def Export(self):
        return bytearray(self.Clocks-1)


class Note:     # 音符データ
    def __init__(self, Data, Clocks):
        if not(0x80 <= Data <= 0xDF):
            raise ValueError("Data out of range")
        else:
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
        global _OPM_CLOCK
        timerb = round(256 - 60 * _OPM_CLOCK / (self.Data * 48 * 1024))
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


class Tone:     # 音色設定  //  also doubles as Expdx bank selector - Expdx銀行のセレクタとしても倍増
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
            e.extend(struct.pack(ENC_WORD, -self.Data))
            return e


class DelayKeyon:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        e = bytearray([0xF0])
        e.append(self.Data)
        return e


class Sync_Resume:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        e = bytearray([0xEF])
        e.append(self.Data)
        return e


class Sync_Wait:
    def Export(self):
        return bytearray([0xEE])



class AdpcmFreq:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        e = bytearray([0xED])
        e.append(self.Data)
        return e


class Expcm_Enable:
    def Export(self):
        return bytearray([0xE8])


# :: LFO commands // Pitch ::
class Lfo_Pitch_Enable:
    def Export(self):
        return bytearray([0xEC, 0x81])

class Lfo_Pitch_Disable:
    def Export(self):
        return bytearray([0xEC, 0x80])

class Lfo_Pitch_Control:
    def __init__(self, Wave, Freq, Amp):
        self.Wave = Wave
        self.Freq = Freq
        self.Amp  = Amp
    def Export(self):
        e = bytearray([0xEC, self.Wave])
        e.extend(struct.pack(ENC_WORD, self.Freq))
        e.extend(struct.pack(ENC_WORD, self.Amp))
        return e


# :: LFO commands // Volume ::
class Lfo_Volume_Enable:
    def Export(self):
        return bytearray([0xEB, 0x81])

class Lfo_Volume_Disable:
    def Export(self):
        return bytearray([0xEB, 0x80])

class Lfo_Volume_Control:
    def __init__(self, Wave, Freq, Amp):
        self.Wave = Wave
        self.Freq = Freq
        self.Amp  = Amp
    def Export(self):
        e = bytearray([0xEB, self.Wave])
        e.extend(struct.pack(ENC_WORD, self.Freq))
        e.extend(struct.pack(ENC_WORD, self.Amp))
        return e


# :: LFO commands // Opm ::
class Lfo_Opm_Enable:
    def Export(self):
        return bytearray([0xEA, 0x81])

class Lfo_Opm_Disable:
    def Export(self):
        return bytearray([0xEA, 0x80])

class Lfo_Opm_Control:
    def __init__(self, RestartWave, Wave, Speed, Pmd, Amd, Pms_Ams):
        self.RestartWave = RestartWave
        self.Wave        = Wave
        self.Speed       = Speed
        self.Pmd         = Pmd
        self.Amd         = Amd
        self.Pms_Ams     = Pms_Ams
    def Export(self):
        return bytearray([0xEA, self.RestartWave*0x40 + self.Wave, self.Speed, self.Pmd, self.Amd, self.Pms_Ams])
#endregion


#===========================================#
#   Extended Commands (+16)
#===========================================#
#region
class Ext_16_Fadeout:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([__CMD_EXT, 0x01, self.Data])
#endregion


#===========================================#
#   Extended Commands (+16/02EX)
#===========================================#
#region
class Ext_16_02EX_RelativeDetune:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        e = bytearray([__CMD_EXT_02EX, 0x01])
        e.extend(struct.pack(ENC_WORD, self.Data))
        return e


class Ext_16_02EX_Transpose:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([__CMD_EXT_02EX, 0x02, self.Data])


class Ext_16_02EX_RelativeTranspose:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([__CMD_EXT_02EX, 0x03, self.Data])
#endregion


#===========================================#
#   Extended Commands (+17)
#===========================================#
#region
class Ext_17_Pcm8_Control:
    def __init__(self, d0, d1):
        self.d0 = d0
        self.d1 = d1
    def Export(self):
        e = bytearray([__CMD_EXT, 0x02])
        e.extend(struct.pack(ENC_WORD, self.d0))
        e.extend(struct.pack(ENC_WORD, self.d1))
        return 


class Ext_17_UseKeyoff:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([__CMD_EXT, 0x03, self.Data])


class Ext_17_Channel_Control:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([__CMD_EXT, 0x04, self.Data])


class Ext_17_AddLenght:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([__CMD_EXT, 0x05, self.Data])


class Ext_17_UseFlags:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([__CMD_EXT, 0x06, self.Data])
#endregion
