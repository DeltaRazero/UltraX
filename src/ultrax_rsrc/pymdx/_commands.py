#region ||  Public command adder  ||

OPM_CLOCK = 4000000 # Hz

class Command:
    """
    MDX performance commands.
    """
    
    def __init__(self, datalist):
        self._a = datalist.append    # Set reference to _datatrack->_Data instance
        self._e = datalist.extend
        self._i = datalist.insert

        self._rsl = []  # Repeat start,  byte counter list
        self._rel = []  # Repeat escape, byte counter list

    def _i_rsl(self, n): # Increase repeat start list byte counter
        if (self._rsl != []):
            [i+n for i in self._rsl]

    def _i_rel(self, n): # Increase repeat escape list byte counter
        if (self._rel != []):
            [i+n for i in self._rel]




    def Rest(self, Clocks):
        """
        Rest command | 休符 コマンド
        """
        cmdCount = 0
        while (Clocks > 128):
            self._a(_Rest(128))
            Clocks -= 128
            cmdCount += 1

        self._i_rsl(1+cmdCount)
        self._i_rel(1+cmdCount)
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

        self._i_rsl(2+cmdCount)
        self._i_rel(2+cmdCount)
        self._a(_Note(Data, Clocks))


    def Tempo(self, Data):
        """
        Tempo command | . . .\n

        """
        self._a(_Tempo_Bpm(Data))
        self._i_rsl(2)
        self._i_rel(2)

    def Tempo_TimerB(self, Data):
        """
        Tempo command | . . .\n

        """
        self._i_rsl(2)
        self._i_rel(2)
        self._a(_Tempo_TimerB(Data))

    def OpmRegister(self, Register, Data):
        self._i_rsl(3)
        self._i_rel(3)
        self._a(_OpmRegister(Register, Data))

    def Tone(self, Data):
        self._i_rsl(2)
        self._i_rel(2)
        self._a(_Tone(Data))

    def Pan(self, Data):
        self._i_rsl(2)
        self._i_rel(2)
        self._a(_Pan(Data))

    def Volume(self, Data):
        self._i_rsl(2)
        self._i_rel(2)
        self._a(_Volume(Data))

    def Volume_Increase(self):
        self._i_rsl(1)
        self._i_rel(1)
        self._a(_Volume_Increase())

    def Volume_Decrease(self):
        self._i_rsl(1)
        self._i_rel(1)
        self._a(_Volume_Decrease())

    def Gate(self, Data):
        self._i_rsl(2)
        self._i_rel(2)
        self._a(_Gate(Data))

    def Legato(self):
        self._i_rsl(1)
        self._i_rel(1)
        self._a(_Legato())

    def Repeat_Start(self, Data):
        self._i_rsl(3)
        self._i_rel(3)
        self._rsl.append(3)  # New byte counter
        self._a(_Repeat_Start(Data))
        
    def Repeat_End(self):
        self._i_rsl(3)
        self._i_rel(3)
        self._a(_Repeat_End(self._rsl[-1]))
        self._rsl.pop(-1)
        if (self._rel != []):
            self._i(-self._rel[-1], _Repeat_Escape(self._rel[-1]))
            self._rel.pop(-1)

    def Repeat_Escape(self):
        self._i_rsl(3)
        self._i_rel(3)
        self._rel.append(0)  # New byte counter

        

        

#endregion


#region ||  MDX Commands (Private)  ||

class _Rest:     # 休符データ
    def __init__(self, Clocks):
        self.Clocks = Clocks

    def Export(self):
        return bytearray(self.Clocks-1)
        # e = bytearray()
        # while (self.Clocks > 128):
        #     e.append(0x7F)
        #     self.Clocks -= 128
        # e.append(self.Clocks-1)
        # return e


class _Note:     # 音符データ
    def __init__(self, Data, Clocks):
        self.Data = Data
        self.Clocks = Clocks

    def Export(self):
        # if (0x80 > self.Data > 0xDF  or  self.Clocks < 0): raise AnException
        return bytearray([self.Data, self.Clocks-1])
        # e = bytearray()
        # while (self.Clocks > 256):
        #     e.extend([0xF7, self.Data, 0xFF])
        #     self.Clocks -= 256
        # e.extend([self.Data, self.Clocks-1])
        # return e


# opm_tempo = 256 - 60 * opm_clock / (bpm_tempo * 48 * 1024)          opm_tempo = 256 - (78125 / (16 * bpm_tempo))
# bpm_tempo = 60 * opm_clock / (48 * 1024 * (256 - opm_tempo))        bpm_tempo = 78125 / (16 * (256 - opm_tempo))
class _Tempo_Bpm:    # テンポ設定
    def __init__(self, Data):   # TODO: Calculate BPM to data
        self.Data = Data

    def Export(self):
        global OPM_CLOCK
        timerb = 256 - 60 * OPM_CLOCK / (self.Data * 48 * 1024)
        return bytearray([0xFF, timerb])

        
class _Tempo_TimerB:    # テンポ設定
    def __init__(self, Data):   # TODO: Calculate BPM to data
        self.Data = Data

    def Export(self):
        return bytearray([0xFF, self.Data])


class _OpmRegister:  # OPMレジスタ設定
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
        return bytearray([0xF5, self.Data])


class _Repeat_Escape:
    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return bytearray([0xF4, self.Data])


class _Detune:
    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return bytearray([0xF3, self.Data])


class _Portamento:
    def __init__(self, Data):
        self.Data = Data

    def Export(self):
        return bytearray([0xF2, self.Data])



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