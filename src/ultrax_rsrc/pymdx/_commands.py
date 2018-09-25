import struct as struct
from ._encoding import *

OPM_CLOCK = 4000000 # Hz

class Command:
    """
    MDX performance commands.
    """
    #region ||  Internal props  ||  
    def __init__(self, Datalist):
        self._a = Datalist.append    # Set reference to _datatrack->_Data instance
        self._e = Datalist.extend
        self._i = Datalist.insert

        self._rsl = []  # Repeat start,     byte counter list
        self._rel = []  # Repeat escape,    byte counter list
        self._lm = 0    # Loop mark,        byte counter

    def _i_rsl(self, n): # Increase repeat start byte counter list
        if (self._rsl != []):
            for i in range(len(self._rsl)): self._rsl[i]+=n
            #[i+n for i in self._rsl]

    def _i_rel(self, n): # Increase repeat escape byte counter list
        if (self._rel != []):
            for i in range(len(self._rsl)): self._rel[i]+=n
            #[i+n for i in self._rel]

    def _i_lm(self, n): # Increase loop mark byte counter
        if (self._lm > 0):
            self._lm += n

    def _updateCounters(self, n):
        self._i_lm(n)
        self._i_rsl(n)
        self._i_rel(n)

    #endregion

    #region ||  Public commands interface  ||

    def Rest(self, Clocks):
        """
        Rest command | 休符 コマンド
        """
        cmdCount = 0
        while (Clocks > 128):
            self._a(_Rest(128))
            Clocks -= 128
            cmdCount += 1

        self._updateCounters(1+cmdCount)
        self._a(_Rest(Clocks))

    def Note(self, Data, Clocks):
        """
        Note command | 音符 コマンド\n
        Valid note range: 0x80 (o0d+) -- 0xDF (o8d)
        """
        cmdCount = 0
        while (Clocks > 256):
            self._e([_Legato(), _Note(Data, 256)])
            Clocks -= 256
            cmdCount += 3
        if (cmdCount > 0):
            self._a(_Legato())
            cmdCount += 1

        self._updateCounters(2+cmdCount)
        self._a(_Note(Data, Clocks))


    def Tempo_Bpm(self, Data):
        """
        Tempo command | . . .\n

        """
        self._updateCounters(2)
        self._a(_Tempo_Bpm(Data))

    def Tempo_TimerB(self, Data):
        """
        Tempo command | . . .\n

        """
        self._updateCounters(2)
        self._a(_Tempo_TimerB(Data))

    def OpmControl(self, Register, Data):
        self._updateCounters(3)
        self._a(_OpmControl(Register, Data))

    def Tone(self, Data):
        self._updateCounters(2)
        self._a(_Tone(Data))

    def Pan(self, Data):
        self._updateCounters(2)

        if (type(Data) is str):
            Data = Data.lower()
            if (Data in ['l', 'c', 'r']):
                Data = {
                    'l': 0b01,
                    'c': 0b11,
                    'r': 0b10
                }[Data]
            else:
                Data = 0b11
        else:
            if Data==0b10:   Data=0b01
            elif Data==0b01: Data=0b10
            else: Data=0b11

        self._a(_Pan(Data))

    def Volume(self, Data):
        self._updateCounters(2)
        self._a(_Volume(Data))

    def Volume_Increase(self):
        self._updateCounters(1)
        self._a(_Volume_Increase())

    def Volume_Decrease(self):
        self._updateCounters(1)
        self._a(_Volume_Decrease())

    def Gate(self, Data):
        self._updateCounters(2)
        self._a(_Gate(Data))

    def Legato(self):
        self._updateCounters(1)
        self._a(_Legato())

    def Repeat_Start(self):
        self._updateCounters(3)
        self._rsl.append(0)  # New byte counter
        
    def Repeat_End(self, Data):
        self._updateCounters(3)
        self._a(_Repeat_End(self._rsl[-1])) # Add repeat end command
        self._i(-self._rsl[-1], _Repeat_Start(Data)) # Insert repeat start command at trackdata index (counted from last) of latest byte counter
        self._rsl.pop(-1) # Remove the appropriote byte counter

        if (self._rel != []):   # If a repeat escape byte counter is active
            self._i(-self._rel[-1], _Repeat_Escape(self._rel[-1])) # Insert repeat escape command at trackdata index (counted from last)
            self._rel.pop(-1)

    def Repeat_Escape(self):
        self._updateCounters(3)
        self._rel.append(0)  # New byte counter

    def Detune(self, Data):
        self._updateCounters(3)
        self._a(_Detune(Data))

    def Portamento(self, Data):
        self._updateCounters(3)
        self._a(_Portamento(Data))

    def DataEnd(self, Data=0x00):
        self._updateCounters(2 if Data==0x00 else 3)
        self._a(_DataEnd(Data))

    def DelayKeyon(self, Data):
        self._updateCounters(3)
        self._a(_Portamento(Data))


    # /// Extended commands (+16) ///
    def Ext_16_Terminate(self):
        self._updateCounters(2)

    def Ext_16_Fadeout(self):
        self._updateCounters(3)


    # /// Extended commands (+17) ///  ※Not widely supported -- ※広くサポートされていない
    def Ext_17_Pcm8Control(self):
        self._updateCounters(8)

    def Ext_17_idk(self):
        self._updateCounters(3)

    def Ext_17_ChannelControl(self):
        self._updateCounters(3)

    def Ext_17_AddLenght(self):
        self._updateCounters(3)

    def Ext_17_Note(self, Data, Clocks):
        """
        Note command (+17 cmds) | 音符 コマンド\n
        Valid note range: 0x80 (o0d+) -- 0xDF (o8d)
        """
        cmdCount = 2

        if (Clocks >256):
            self._a(_Note(Data, 256))
            Clocks -= 256
            while (Clocks > 256):
                self._a(_Ext_17_AddLenght(256))
                Clocks -= 256
                cmdCount += 3

        self._updateCounters(cmdCount)
        self._a(_Note(Data, Clocks))

    def Ext_17_UseFlags(self):
        self._updateCounters(3)


    # /// Extended commands (+16/02EX) ///  ※Not widely supported -- ※広くサポートされていない
    def Ext_16_02EX_Terminate(self):
        self._updateCounters(2)

    def Ext_16_02EX_RelativeDetune(self):
        self._updateCounters(4)

    def Ext_16_02EX_Transpose(self):
        self._updateCounters(3)

    def Ext_16_02EX_RelativeTranspose(self):
        self._updateCounters(3)

    #endregion


#region ||  MDX Commands (Internal)  ||

class _Rest:     # 休符データ
    def __init__(self, Clocks):
        self.Clocks = Clocks
    def Export(self):
        return bytearray(self.Clocks-1)


class _Note:     # 音符データ
    def __init__(self, Data, Clocks):
        self.Data = Data
        self.Clocks = Clocks
    def Export(self):
        # if (0x80 > self.Data > 0xDF  or  self.Clocks < 0): raise AnException
        return bytearray([self.Data, self.Clocks-1])


# opm_tempo = 256 - 60 * opm_clock / (bpm_tempo * 48 * 1024)          opm_tempo = 256 - (78125 / (16 * bpm_tempo))
# bpm_tempo = 60 * opm_clock / (48 * 1024 * (256 - opm_tempo))        bpm_tempo = 78125 / (16 * (256 - opm_tempo))
class _Tempo_Bpm:    # テンポ設定
    def __init__(self, Data):   # TODO: Calculate BPM to data
        self.Data = Data
    def Export(self):
        global OPM_CLOCK
        timerb = round(256 - 60 * OPM_CLOCK / (self.Data * 48 * 1024))
        return bytearray([0xFF, timerb])


class _Tempo_TimerB:    # テンポ設定
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([0xFF, self.Data])


class _OpmControl:  # OPMレジスタ設定
    def __init__(self, Register, Data):
        self.Register = Register
        self.Data = Data
    def Export(self):
        return bytearray([self.Register, self.Data])


class _Tone:     # 音色設定
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([0xFD, self.Data])


class _Pan:      # 出力位相設定
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([0xFC, self.Data])


class _Volume:   # 音量設定
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([0xFB, self.Data])


class _Volume_Increase:   # 音量増大
    def Export(self):
        return bytearray([0xFA])


class _Volume_Decrease:   # 音量減小
    def Export(self):
        return bytearray([0xF9])


class _Gate:     # ゲートタイム
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([0xF8, self.Data])


class _Legato:   # Disable keyoff for next note / キーオフ無効
    def Export(self):
        return bytearray([0xF7])


class _Repeat_Start:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        return bytearray([0xF6, self.Data, 0x00])


class _Repeat_End:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        e = bytearray([0xF5])
        e.extend(struct.pack(ENC_WORD, -self.Data))
        return e


class _Repeat_Escape:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        e = bytearray([0xF4])
        e.extend(struct.pack(ENC_WORD, self.Data))
        return e


class _Detune:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        e = bytearray([0xF3])
        e.extend(struct.pack(ENC_WORD, self.Data))
        return e


class _Portamento:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        e = bytearray([0xF2])
        e.extend(struct.pack(ENC_WORD, self.Data))
        return e


class _DataEnd:
    def __init__(self, Data):
        self.Data = Data
    def Export(self):
        if (self.Data < 1):
            return bytearray([0xF1, self.Data])
        else:
            e = bytearray([0xF1])
            e.extend(struct.pack(ENC_WORD, self.Data))
            return e



#endregion



    




# CLOCK DURATIONS:
# -------------------
# * Clock durations are internally: value+1
#
# MININMUM + MAXMIMUM
# * 0x00 = 1 clock
# * 0xff = 256 clocks   (max amount of clocks for one note)
#
# CALCULATION:
# maindivider = 256 / 192
# mainclock = (256 / (maindivider)*multiplier)
# l1 = (mainclock / 1) - 1
# l2 = (mainclock / 2) - 1
# l4 = (mainclock / 4) - 1
# etc.
#
# MUSIC NOTATION VALUES
# * 0xbf / 192 clocks = whole   note / l1
# * 0x5f / 96  clocks = half    note / l2
# * 0x2f / 48  clocks = quarter note / l4
# * 0x17 / 24  clocks = 8th     note / l8
# * 0x0b / 12  clocks = 16th    note / l16
# * 0x05 / 6   clocks = 32th    note / l32
# * 0x02 / 3   clocks = 64th    note / l64