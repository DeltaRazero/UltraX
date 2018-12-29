import struct as _struct

from array import array as _array
from enum import Enum as _Enum

from .._misc import _encoding, _util
from .._misc.exc import *

#**********************************************************
#
#    Internal stuff
#
#**********************************************************

OPM_CLOCK = 4000000 # Hz

class LFO_WAVEFORM(_Enum):
    SAWTOOTH  = 0
    SQUARE    = 1
    TRIANGLE  = 2
    OPM_NOISE = 3

_CMD_EXT       = 0xE7
_CMD_EXT_02EX  = 0xE6

# Abstract base command class to inherit. If working with
# C++, C#, etc. you can use the 'abstract' class prefix.
# Export() will always need a custom implementation.
class Command:
    _amountBytes = None

    def Count(self, CounterObj):
        CounterObj.UpdateCounters(self._amountBytes)
        return

    def Export(self, Command_Parameter):
        raise NotImplementedError



#**********************************************************
#
#    Standard commands
#
#**********************************************************
#region


class Rest(Command):
# 休符データ
    def __init__(self, Clocks: int) -> _array:
        self.Clocks = Clocks

    def Count(self, CounterObj):
        _amountBytes = -(-self.Clocks // 128)
        CounterObj.UpdateCounters(_amountBytes)
        return

    def Export(self):
        if self.Clocks > 128:
            clocks = self.Clocks
            cmds = _array('B')
            
            while (clocks > 128):
                cmds.extend(Rest(128).Export())
                clocks -= 128
            cmds.extend(Rest(clocks).Export())
            
            return cmds

        else:
            return _array('B', [self.Clocks-1])


class Note(Command):
# 音符データ
    def __init__(self, Data, Clocks):
        if not(0x80 <= Data <= 0xDF):
            raise ValueError("Data out of range")
            # Data = 0x80
            # self.Data = Data
            # self.Clocks = Clocks
        else:
            self.Data = Data
            self.Clocks = Clocks

    def Count(self, CounterObj):
        _amountBytes = 2 + (-(-self.Clocks // 256)-1) * 3
        CounterObj.UpdateCounters(_amountBytes)
        return

    def Export(self):
        # if (0x80 > self.Data > 0xDF  or  self.Clocks < 0): raise AnException

        if self.Clocks > 256:
            clocks = self.Clocks
            cmds = _array('B')
            
            cmds.extend(Legato().Export())
            while (clocks > 256):
                cmds.extend(Note(self.Data, 256).Export())
                cmds.extend(Legato().Export())
                clocks -= 256
            cmds.extend(Note(self.Data, clocks).Export())
            
            return cmds

        else:
            return _array('B', [self.Data, self.Clocks-1])


class Tempo_Bpm(Command):
# テンポ設定
    _amountBytes = 2
    
    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        global OPM_CLOCK

        timerb = round(256 - 60 * OPM_CLOCK / (self.Data * 48 * 1024))

        # opm_tempo = 256 - 60 * opm_clock / (bpm_tempo * 48 * 1024)
        # bpm_tempo = 60 * opm_clock / (48 * 1024 * (256 - opm_tempo))        
        #
        # If opm_clock == 4mHz:
        #   opm_tempo = 256 - (78125 / (16 * bpm_tempo))
        #   bpm_tempo = 78125 / (16 * (256 - opm_tempo))
        #
        # Thanks to vampirefrog

        timerb = _util.Clamp(timerb, 0, 256)
        return _array('B', [0xFF, timerb])


class Tempo_TimerB(Command):
# テンポ設定
    _amountBytes = 2

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return _array('B', [0xFF, self.Data])


class OpmControl(Command):
# OPMレジスタ設定
    _amountBytes = 3

    def __init__(self, Register, Data):
        self.Register = Register
        self.Data = Data

    def Export(self):
        return _array('B', [0xFE, self.Register, self.Data])


class Tone(Command):
# 音色設定  //  also doubles as Expdx bank selector - Expdx銀行のセレクタとしても倍増
    _amountBytes = 2

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return _array('B', [0xFD, self.Data])


class Pan(Command):
# 出力位相設定
    _amountBytes = 2

    def __init__(self, Data):
        self.Data = Data

    def Export(self):

        # Correct the panning
        if (type(self.Data) is str):
            Data = self.Data.lower()
            if (Data in ['l', 'c', 'r']):
                Data = {
                    'l': 0b01,
                    'c': 0b11,
                    'r': 0b10
                }[Data]
            else: Data = 0b11
        elif (type(self.Data) is int):
            if (self.Data in [0b10, 0b11, 0b01, 0b00]):
                Data = {
                    0b10: 0b01,
                    0b11: 0b11,
                    0b01: 0b10,
                    0b00: 0b00
                }[self.Data]
            else: Data = 0b11

        return _array('B', [0xFC, Data])


class Volume(Command):
# 音量設定
    _amountBytes = 2

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return _array('B', [0xFB, self.Data])


class Volume_Increase(Command):
# 音量増大
    _amountBytes = 1

    def Export(self):
        return _array('B', [0xFA])


class Volume_Decrease(Command):
# 音量減小
    _amountBytes = 1

    def Export(self):
        return _array('B', [0xF9])


class Gate(Command):
# ゲートタイム
    _amountBytes = 2

    def __init__(self, Data):
        self.Data = Data

    def Export(self, CounterObj):
        return _array('B', [0xF8, self.Data])


class Legato(Command):
# キーオフ無効
# Disable keyoff for next note / 次のNOTE発音後キーオフしない
    _amountBytes = 1

    def Export(self):
        return _array('B', [0xF7])


class Repeat_Start(Command):
# リピート開始
    _amountBytes = 3

    def __init__(self, Data=0):
        self.Data = Data

    def Count(self, CounterObj):
        CounterObj.UpdateCounters(self._amountBytes)

        CounterObj.Rsc.Add1()
        CounterObj.Rsc.GetLast().Position = CounterObj.Position

        CounterObj.Rec.Add1()
        return

    def Export(self):
        return _array('B', [0xF6, self.Data, 0x00])


class Repeat_End(Command):
# リピート終端
    _amountBytes = 3

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

        CounterObj.UpdateCounters(self._amountBytes)

        CounterObj.Rsc.GetLast().Loop_Times = self.Data
        CounterObj.Rsc.Stop1()

        CounterObj.Rec.GetLast().Position = CounterObj.Position
        CounterObj.Rec.Stop1()
        
        return

    def Export(self):
        e = _array('B', [0xF5])
        e.extend(_struct.pack(_encoding.ENC_WORD, -self.Data))
        return e


class Repeat_Escape(Command):
# リピート脱出
    _amountBytes = 3

    def __init__(self, Data=0):
        self.Data = Data

    def Count(self, CounterObj):
        CounterObj.UpdateCounters(self._amountBytes)

        CounterObj.Rescc.Add1()
        CounterObj.Rescc.GetLast().Position = CounterObj.Position
        
        return

    def Export(self):
        e = _array('B', [0xF4])
        e.extend(_struct.pack(_encoding.ENC_WORD, self.Data+1))
        return e


class Detune(Command):
# デチューン
    _amountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        e = _array('B', [0xF3])
        e.extend(_struct.pack(_encoding.ENC_WORD, self.Data))
        return e


class Portamento(Command):
# ポルタメント
    _amountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        e = _array('B', [0xF2])
        e.extend(_struct.pack(_encoding.ENC_WORD, self.Data))
        return e


class DataEnd(Command):
# データエンド
    def __init__(self, Data):
        self.Data = Data

    def Count(self, CounterObj):
        if (self.Data < 1):
            self._amountBytes = 2
        else:
            self._amountBytes = 3
        CounterObj.UpdateCounters(self._amountBytes)
        return

    def Export(self):
        if (self.Data < 1):
            e = _array('B', [0xF1, self.Data])
            return e 

        else:
            e = _array('B', [0xF1])
            e.extend(_struct.pack(_encoding.ENC_WORD, -self.Data))
            return e


class DelayKeyon(Command):
# キーオンディレイ
    _amountBytes = 2

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        e = _array('B', [0xF0])
        e.append(self.Data)
        return e


class Sync_Resume(Command):
# 同期信号送出
    _amountBytes = 2

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        e = _array('B', [0xEF])
        e.append(self.Data)
        return e


class Sync_Wait(Command):
# 同期信号待機
    _amountBytes = 1

    def Export(self):
        return _array('B', [0xEE])


class Noise_Control(Command):
# ノイズ周波数設定
# [$ED] + [byte]
#
# FM #7:
#   Bits 0-6 are noise frequency. Bit 7 is a noise mode ON/OFF switch
#   ビット0-6はノイズ周波数。ビット7はノイズON/OFF
    _amountBytes = 2
    
    # Functionally equal to "Static Bool"
    _noiseEnabled = False;
    @property
    def _NoiseEnabled(self):
        return type(self)._noiseEnabled;
    @_NoiseEnabled.setter
    def _NoiseEnabled(self,val):
        type(self)._noiseEnabled = val;

    def __init__(self, Data, NoiseEnabled=None):
        self.Data = Data
        # Nullable Bool, alternatively use *args --> args[1]
        self.NoiseEnabled = NoiseEnabled

    def Export(self):
        if (self.NoiseEnabled is None):
            self._NoiseEnabled = {
                0: False,
                1: True,
            }[self.Data & 0x80]
        elif (type(self.NoiseEnabled) is bool):
            self._NoiseEnabled = self.NoiseEnabled
        else:
            raise TypeError()

        e = _array('B', [0xED])
        e.append(self.Data | self._NoiseEnabled<<7)
        return e


class Adpcm_Control(Command):
# ADPCM ズ周波数設定
# 
# [$ED] + [byte]
#
# ADPCM:
#   0:  3.9 kHz
#   1:  5.2 kHz
#   2:  7.8 kHz
#   3: 10.4 kHz
#   4: 15.6 kHz
#
# PCM8:
#   5: 16 bit pcm / 15.6 KHz
#   6:  8 bit pcm / 15.6 KHz
#
# PCM8++:
#   Values 7 ~ 31 can also be set.
#   7 ～ 31 の値も設定出来ます。
#
    _amountBytes = 2

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        e = _array('B', [0xED])
        e.append(self.Data)
        return e


class Expcm_Enable(Command):
# Declare the use of EX-PCM mode (PCM4, PCM8, Rydeen, etc.)
# EX-PCM使用宣言 (PCM4, PCM8, Rydeen, 等)
    _amountBytes = 1
    
    def Export(self):
        return _array('B', [0xE8])


class LoopMark(Command):
# ループポインタ位置
    def Count(self, CounterObj):
        CounterObj.UpdateCounters(0)
        CounterObj.Lmc = 1
        return

    def Export(self):
        return _array('B')


# :: Pitch LFO // 音程LFO ::
class Lfo_Pitch_Enable(Command):
# 音程LFO ON
    _amountBytes = 2

    def Export(self):
        return _array('B', [0xEC, 0x81])


class Lfo_Pitch_Disable(Command):
# 音程LFO OFF
    _amountBytes = 2

    def Export(self):
        return _array('B', [0xEC, 0x80])


class Lfo_Pitch_Control(Command):
# 音程LFO 制御
    _amountBytes = 6

    def __init__(self, Wave, Freq, Amp):
        self.Wave = Wave
        self.Freq = Freq
        self.Amp  = Amp

    def Export(self):
        e = _array('B', [0xEC, self.Wave])
        e.extend(_struct.pack(_encoding.ENC_WORD, self.Freq))
        e.extend(_struct.pack(_encoding.ENC_WORD, self.Amp))
        return e


# :: Volume LFO // 音量LFO ::
class Lfo_Volume_Enable(Command):
# 音量LFO ON
    _amountBytes = 2

    def Export(self):
        return _array('B', [0xEB, 0x81])


class Lfo_Volume_Disable(Command):
# 音量LFO OFF
    _amountBytes = 2

    def Export(self):
        return _array('B', [0xEB, 0x80])


class Lfo_Volume_Control(Command):
# 音量LFO制御
    _amountBytes = 6

    def __init__(self, Wave, Freq, Amp):
        self.Wave = Wave
        self.Freq = Freq
        self.Amp  = Amp

    def Export(self):
        e = _array('B', [0xEB, self.Wave])
        e.extend(_struct.pack(_encoding.ENC_WORD, self.Freq))
        e.extend(_struct.pack(_encoding.ENC_WORD, self.Amp))
        return e


# :: OPM LFO // OPMLFO ::
class Lfo_Opm_Enable(Command):
# OPMLFO ON
    _amountBytes = 2

    def Export(self):
        return _array('B', [0xEA, 0x81])

class Lfo_Opm_Disable(Command):
# OPMLFO OFF
    _amountBytes = 2

    def Export(self):
        return _array('B', [0xEA, 0x80])

class Lfo_Opm_Control(Command):
# OPMLFO制御
    _amountBytes = 7

    def __init__(self, RestartWave, Wave, Speed, Pmd, Amd, Pms_Ams):
        self.RestartWave = RestartWave
        self.Wave        = Wave
        self.Speed       = Speed
        self.Pmd         = Pmd
        self.Amd         = Amd
        self.Pms_Ams     = Pms_Ams

    def Export(self):
        return _array('B', [0xEA, self.RestartWave*0x40 + self.Wave, self.Speed, self.Pmd, self.Amd, self.Pms_Ams])
#endregion



#**********************************************************
#
#    Extended Commands (+16)
#    拡張コマンド (+16での拡張)
#
#**********************************************************
#region
class Ext_16_Fadeout(Command):
# 可変速でのフェードアウト
    global _CMD_EXT
    _amountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return _array('B', [_CMD_EXT, 0x01, self.Data])
#endregion



#**********************************************************
#
#    Extended Commands (+16/02EX)
#    拡張コマンド (非公式コマンド）+16/02EXのみ)
#
#**********************************************************
#region
class Ext_16_02EX_RelativeDetune(Command):
# 相対デチューン
    global _CMD_EXT_02EX
    _amountBytes = 4

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        e = _array('B', [_CMD_EXT_02EX, 0x01])
        e.extend(_struct.pack(_encoding.ENC_WORD, self.Data))
        return e


class Ext_16_02EX_Transpose(Command):
# 移調
    global _CMD_EXT_02EX
    _amountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return _array('B', [_CMD_EXT_02EX, 0x02, self.Data])


class Ext_16_02EX_RelativeTranspose(Command):
# 相対移調
    global _CMD_EXT_02EX
    _amountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return _array('B', [_CMD_EXT_02EX, 0x03, self.Data])
#endregion



#**********************************************************
#
#    Extended Commands (+17)
#    拡張コマンド (+17での拡張)
#
#**********************************************************
#region

class Ext_17_Pcm8_Control(Command):
# Send data to PCM8 directly
# PCM8を直接ドライブする
    global _CMD_EXT
    _amountBytes = 8

    def __init__(self, d0, d1):
        self.d0 = d0
        self.d1 = d1

    def Export(self):
        e = _array('B', [_CMD_EXT, 0x02])
        e.extend(_struct.pack(_encoding.ENC_WORD, self.d0))
        e.extend(_struct.pack(_encoding.ENC_LONG, self.d1))
        return e


class Ext_17_UseKeyoff(Command):
# Set the KEYOFF flag: $00 = KeyOff, $01 = Do not KeyOff
# $00=KEYOFFする/$01=KEYOFFしない
    global _CMD_EXT
    _amountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return _array('B', [_CMD_EXT, 0x03, self.Data])


class Ext_17_Channel_Control(Command):    # TODO: Currently buggy
# Control another channel
# 他のチャンネルをコントロール
    global _CMD_EXT
    _amountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        # TODO: Using rest, note, ext17_not or ext17_addlenght commands longer than 128/256 clocks, does not work
        return _array('B', [_CMD_EXT, 0x04, self.Data])


class Ext_17_AddLenght(Command):    # TODO: research
# Add note lenght
# 音長加算する
    global _CMD_EXT

    def __init__(self, Clocks):
        self.Clocks = Clocks

    def Count(self, CounterObj):
        _amountBytes = -(-self.Clocks // 256) * 3
        CounterObj.UpdateCounters(_amountBytes)
        return

    def Export(self):
        if (self.Clocks > 256):
            clocks = self.Clocks
            cmds = _array('B')

            while (clocks > 256):
                cmds.extend(Ext_17_AddLenght(256).Export())
                clocks -= 256
            cmds.extend(Ext_17_AddLenght(clocks).Export())

            return cmds

        else:
            return _array('B', [_CMD_EXT, 0x05, self.Clocks-1])
    

class Ext_17_UseFlags(Command):    # TODO: what does this do?
# Declare if flags are still used
# まだフラグを使用してない？
    global _CMD_EXT
    _amountBytes = 3

    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return _array('B', [_CMD_EXT, 0x06, self.Data])


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
            cmds = _array('B')
            
            cmds.extend(Note(self.Data, 256).Export())
            cmds.extend(Ext_17_AddLenght(self.Clocks-256).Export())
            
            return cmds

        else:
            return Note(self.Data, self.Clocks).Export()
#endregion
