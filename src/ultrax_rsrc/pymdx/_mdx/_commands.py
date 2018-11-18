import struct as struct
from .._misc._encoding import *
from .._misc.exc import *


#**********************************************************
#
#    Internal stuff
#
#**********************************************************

_OPM_CLOCK = 4000000 # Hz

_CMD_EXT       = 0xE7
_CMD_EXT_02EX  = 0xE6
# TODO: Make these globals in classes


# Abstract base command class to inherit. If working with
# C++, C#, etc. you can use the 'abstract' class prefix.
# Export always needs to be implemented by the programmer.

class Command:
    AmountBytes = None

    def Count(self, CounterObj):
        CounterObj.UpdateCounters(self.AmountBytes)
        return

    def Export(self, Command_Parameter):
        raise NotImplementedError




#**********************************************************
#
#    Standard commands
#
#**********************************************************
#region

# 休符データ
class Rest(Command):
    def __init__(self, Clocks: int) -> bytearray:
        self.Clocks = Clocks

    def Count(self, CounterObj):
        self.AmountBytes = -(-self.Clocks // 128)
        CounterObj.UpdateCounters(self.AmountBytes)
        return

    def Export(self):
        if self.Clocks > 128:
            clocks = self.Clocks
            cmds = bytearray()
            
            while (clocks > 128):
                cmds.append(Rest(128).Export())
                clocks -= 128
            cmds.append(Rest(clocks).Export())
            
            return cmds

        else:
            return bytearray(self.Clocks-1)


# 音符データ
class Note(Command):
    def __init__(self, Data, Clocks):
        if not(0x80 <= Data <= 0xDF):
            raise ValueError("Data out of range")
        else:
            self.Data = Data
            self.Clocks = Clocks

    def Count(self, CounterObj):
        self.AmountBytes = 2 + (-(-self.Clocks // 256)-1) * 3
        CounterObj.UpdateCounters(self.AmountBytes)
        return

    def Export(self):
        # if (0x80 > self.Data > 0xDF  or  self.Clocks < 0): raise AnException

        if self.Clocks > 256:
            clocks = self.Clocks
            cmds = bytearray()
            
            cmds.extend(Legato().Export())
            while (clocks > 256):
                cmds.extend(Note(self.Data, 256).Export())
                cmds.extend(Legato().Export())
                clocks -= 256
            cmds.extend(Note(self.Data, clocks).Export())
            
            return cmds

        else:
            return bytearray([self.Data, self.Clocks-1])



# opm_tempo = 256 - 60 * opm_clock / (bpm_tempo * 48 * 1024)          opm_tempo = 256 - (78125 / (16 * bpm_tempo))
# bpm_tempo = 60 * opm_clock / (48 * 1024 * (256 - opm_tempo))        bpm_tempo = 78125 / (16 * (256 - opm_tempo))
class Tempo_Bpm(Command):    # テンポ設定
    def __init__(self, Data):   # TODO: Calculate BPM to data
        self.Data = Data

    AmountBytes = 2
    def Export(self):
        global _OPM_CLOCK

        timerb = round(256 - 60 * _OPM_CLOCK / (self.Data * 48 * 1024))
        if timerb < 0:
            timerb = 0
        elif timerb > 256:
            timerb = 256

        return bytearray([0xFF, timerb])


class Tempo_TimerB(Command):    # テンポ設定
    AmountBytes = 2

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return bytearray([0xFF, self.Data])


class OpmControl(Command):  # OPMレジスタ設定
    AmountBytes = 3

    def __init__(self, Register, Data):
        self.Register = Register
        self.Data = Data

    def Export(self):
        return bytearray([0xFE, self.Register, self.Data])


class Tone(Command):     # 音色設定  //  also doubles as Expdx bank selector - Expdx銀行のセレクタとしても倍増
    AmountBytes = 2

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return bytearray([0xFD, self.Data])


class Pan(Command):      # 出力位相設定
    AmountBytes = 2

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return bytearray([0xFC, self.Data])


class Volume(Command):   # 音量設定
    AmountBytes = 2

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return bytearray([0xFB, self.Data])


class Volume_Increase(Command):   # 音量増大
    AmountBytes = 1

    def Export(self):
        return bytearray([0xFA])


class Volume_Decrease(Command):   # 音量減小
    AmountBytes = 1

    def Export(self):
        return bytearray([0xF9])


class Gate(Command):     # ゲートタイム
    AmountBytes = 2

    def __init__(self, Data):
        self.Data = Data

    def Export(self, CounterObj):
        return bytearray([0xF8, self.Data])


class Legato(Command):   # Disable keyoff for next note / キーオフ無効
    AmountBytes = 1

    def Export(self):
        return bytearray([0xF7])


class Repeat_Start(Command):
    AmountBytes = 3

    def __init__(self, Data=0):
        self.Data = Data

    def Count(self, CounterObj):
        CounterObj.UpdateCounters(self.AmountBytes)

        CounterObj.Rsc.Add1()
        CounterObj.Rsc.GetLast().Position = CounterObj.Position

        CounterObj.Rec.Add1()
        return

    def Export(self):
        return bytearray([0xF6, self.Data, 0x00])


class Repeat_End(Command):
    AmountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Count(self, CounterObj):

        # First we add a repeat end command at the end of the trackdata. The loopback point to insert in this
        # command is the last one added in the 'repeat start' counter ('_rsc'), as if it were to be a 
        # stack / LIFO buffer.
        # Then we insert a repeat start command at the index position of the counter we just used.
        # After that we can safely remove the counter value from the list buffer / free up memory, as we have
        # no more further use for it anymore.

        # 最初に、トラックデータの最後にrepeat endコマンドを追加します。挿入するループバックポイントの値は、
        # スタック / LIFOバッファであるかのように、 'repeat start'カウンタ（'_rsc'）に最後に追加されたものです。
        # 次に、直前に使用したカウンタのインデックス位置にrepeat startコマンドを挿入します。
        # カウンタバッファの最後の値を使用する必要はもうありません。 したがって、リストバッファ / 空きメモリからカウンタ値を安全に削除できます。

        # If the repeat escape byte counter ('_rec') has a value (i.e. is counting), insert a repeat escape command
        # at the index position from the counter at the last position in the buffer (the same way how we insert repeat
        # start commands).
        # After that we can safely remove the counter value from the list buffer / free up memory, as we have no more
        # further use for it anymore.

        # repeat escapeバイトカウンタ（ '_rec'）に値がある場合（意味：カウント中）、インデックス位置に 'repeat_escape'コマンドが挿入されます。
        # インデックス位置は、カウンタバッファの最後の位置の値です（リピート開始コマンドの挿入方法と同じです）。
        # カウンタバッファの最後の値を使用する必要はもうありません。 したがって、リストバッファ/空きメモリからカウンタ値を安全に削除できます。

        CounterObj.Rescc.Stop1()

        CounterObj.UpdateCounters(self.AmountBytes)

        CounterObj.Rsc.GetLast().Loop_Times = self.Data
        CounterObj.Rsc.Stop1()

        CounterObj.Rec.GetLast().Position = CounterObj.Position
        CounterObj.Rec.Stop1()
        
        return

    def Export(self):
        e = bytearray([0xF5])
        e.extend(struct.pack(ENC_WORD, -self.Data))
        return e


class Repeat_Escape(Command):
    AmountBytes = 3

    def __init__(self, Data=0):
        self.Data = Data

    def Count(self, CounterObj):
        CounterObj.UpdateCounters(self.AmountBytes)

        CounterObj.Rescc.Add1()
        CounterObj.Rescc.GetLast().Position = CounterObj.Position
        
        return

    def Export(self):
        e = bytearray([0xF4])
        e.extend(struct.pack(ENC_WORD, self.Data+1))
        return e


class Detune(Command):
    AmountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        e = bytearray([0xF3])
        e.extend(struct.pack(ENC_WORD, self.Data))
        return e


class Portamento(Command):
    AmountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        e = bytearray([0xF2])
        e.extend(struct.pack(ENC_WORD, self.Data))
        return e


class DataEnd(Command):
    def __init__(self, Data):
        self.Data = Data

    def Count(self, CounterObj):
        if (self.Data < 1):
            self.AmountBytes = 2
        else:
            self.AmountBytes = 3
        CounterObj.UpdateCounters(self.AmountBytes)
        return

    def Export(self):
        if (self.Data < 1):
            e = bytearray([0xF1, self.Data])
            return e 

        else:
            e = bytearray([0xF1])
            e.extend(struct.pack(ENC_WORD, -self.Data))
            return e


class DelayKeyon(Command):
    AmountBytes = 2

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        e = bytearray([0xF0])
        e.append(self.Data)
        return e


class Sync_Resume(Command):
    AmountBytes = 2

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        e = bytearray([0xEF])
        e.append(self.Data)
        return e


class Sync_Wait(Command):
    AmountBytes = 1

    def Export(self):
        return bytearray([0xEE])



class AdpcmFreq(Command):
    AmountBytes = 2

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        e = bytearray([0xED])
        e.append(self.Data)
        return e


class Expcm_Enable(Command):
    AmountBytes = 1
    
    def Export(self):
        return bytearray([0xE8])


class LoopMark(Command):
    def Count(self, CounterObj):
        CounterObj.UpdateCounters(0)
        CounterObj.Lmc = 1
        return

    def Export(self):
        return bytearray()


# :: LFO commands // Pitch ::
class Lfo_Pitch_Enable(Command):
    AmountBytes = 2

    def Export(self):
        return bytearray([0xEC, 0x81])


class Lfo_Pitch_Disable(Command):
    AmountBytes = 2

    def Export(self):
        return bytearray([0xEC, 0x80])


class Lfo_Pitch_Control(Command):
    AmountBytes = 6

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
class Lfo_Volume_Enable(Command):
    AmountBytes = 2

    def Export(self):
        return bytearray([0xEB, 0x81])


class Lfo_Volume_Disable(Command):
    AmountBytes = 2

    def Export(self):
        return bytearray([0xEB, 0x80])


class Lfo_Volume_Control(Command):
    AmountBytes = 6

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
class Lfo_Opm_Enable(Command):
    AmountBytes = 2

    def Export(self):
        return bytearray([0xEA, 0x81])

class Lfo_Opm_Disable(Command):
    AmountBytes = 2

    def Export(self):
        return bytearray([0xEA, 0x80])

class Lfo_Opm_Control(Command):
    AmountBytes = 7

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




#**********************************************************
#
#    Extended Commands (+16)
#
#**********************************************************
#region
class Ext_16_Fadeout(Command):
    global _CMD_EXT
    AmountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return bytearray([_CMD_EXT, 0x01, self.Data])
#endregion




#**********************************************************
#
#    Extended Commands (+16/02EX)
#
#**********************************************************
#region
class Ext_16_02EX_RelativeDetune(Command):
    global _CMD_EXT_02EX
    AmountBytes = 4

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        e = bytearray([_CMD_EXT_02EX, 0x01])
        e.extend(struct.pack(ENC_WORD, self.Data))
        return e


class Ext_16_02EX_Transpose(Command):
    global _CMD_EXT_02EX
    AmountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return bytearray([_CMD_EXT_02EX, 0x02, self.Data])


class Ext_16_02EX_RelativeTranspose(Command):
    global _CMD_EXT_02EX
    AmountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return bytearray([_CMD_EXT_02EX, 0x03, self.Data])
#endregion




#**********************************************************
#
#    Extended Commands (+17)
#
#**********************************************************
#region

class Ext_17_Pcm8_Control(Command):
    global _CMD_EXT
    AmountBytes = 8

    def __init__(self, d0, d1):
        self.d0 = d0
        self.d1 = d1

    def Export(self):
        e = bytearray([_CMD_EXT, 0x02])
        e.extend(struct.pack(ENC_WORD, self.d0))
        e.extend(struct.pack(ENC_WORD, self.d1))
        return 


class Ext_17_UseKeyoff(Command):
    global _CMD_EXT
    AmountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return bytearray([_CMD_EXT, 0x03, self.Data])


class Ext_17_Channel_Control(Command):
    global _CMD_EXT
    AmountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        # TODO: Using rest, note, ext17_not or ext17_addlenght commands longer than 128/256 clocks, does not work
        return bytearray([_CMD_EXT, 0x04, self.Data])


class Ext_17_AddLenght(Command):
    global _CMD_EXT

    def __init__(self, Clocks):
        self.Clocks = Clocks

    def Count(self, CounterObj):
        self.AmountBytes = -(-self.Clocks // 256) * 3
        CounterObj.UpdateCounters(self.AmountBytes)
        return

    def Export(self):
        if (self.Clocks > 256):
            clocks = self.Clocks
            cmds = bytearray()

            while (clocks > 256):
                cmds.extend(Ext_17_AddLenght(256).Export())
                clocks -= 256
            cmds.extend(Ext_17_AddLenght(clocks).Export())

            return cmds

        else:
            return bytearray([_CMD_EXT, 0x05, self.Clocks-1])
    

class Ext_17_UseFlags(Command):
    global _CMD_EXT
    AmountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return bytearray([_CMD_EXT, 0x06, self.Data])


# 音符データ
class Ext_17_Note(Command):
    def __init__(self, Data, Clocks):
        self.Data = Data
        self.Clocks = Clocks

    def Count(self, CounterObj):
        CounterObj.UpdateCounters(2)
        if (self.Clocks > 256):
            Ext_17_AddLenght(self.Clocks-256).Count(CounterObj)
        return

    def Export(self):
        if self.Clocks > 256:
            cmds = bytearray()
            
            cmds.extend(Note(self.Data, 256).Export())
            cmds.extend(Ext_17_AddLenght(self.Clocks-256).Export())
            
            return cmds

        else:
            return Note(self.Data, self.Clocks).Export()
#endregion
