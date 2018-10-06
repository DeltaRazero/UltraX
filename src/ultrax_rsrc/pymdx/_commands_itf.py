from . import _commands as _cmd


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
        self._lm  = 0   # Loop mark,        byte counter

        self.Ext16      = _Command_Ext16(self)
        """MDX performance commands (+16 extension)."""

        self.Ext16_02EX = _Command_Ext16_02EX(self)
        """MDX performance commands (+16/02EX extension)."""

        self.Ext17      = _Command_Ext17(self)
        """MDX performance commands (+17 extension) ※ Not widely supported."""

        return

    def _updateCounters(self, n):
        if (self._rsl != []):   # Increase repeat start byte counter list
            for i, _ in enumerate(self._rsl): self._rsl[i]+=n
        if (self._rel != []):   # Increase repeat escape byte counter list
            for i, _ in enumerate(self._rel): self._rsl[i]+=n
        if (self._lm > 0):      # Increase loop mark byte counter
            self._lm += n
        
        return

    #endregion


    #region ||  Public commands interface  ||

    def Rest(self, Clocks):
        """
        Rest command | 休符 コマンド
        """
        cmdCount = 0
        while (Clocks > 128):
            self._a(_cmd.Rest(128))
            Clocks -= 128
            cmdCount += 1

        self._updateCounters(1+cmdCount)
        self._a(_cmd.Rest(Clocks))

    def Note(self, Data, Clocks):
        """
        Note command | 音符 コマンド\n
        Valid note range: 0x80 (o0d+) -- 0xDF (o8d)
        """
        cmdCount = 0
        while (Clocks > 256):
            self._e([_cmd.Legato(), _cmd.Note(Data, 256)])
            Clocks -= 256
            cmdCount += 3
        if (cmdCount > 0):
            self._a(_cmd.Legato())
            cmdCount += 1

        self._updateCounters(2+cmdCount)
        self._a(_cmd.Note(Data, Clocks))


    def Tempo_Bpm(self, Data):
        """
        Tempo command | . . .\n

        """
        self._updateCounters(2)
        self._a(_cmd.Tempo_Bpm(Data))

    def Tempo_TimerB(self, Data):
        """
        Tempo command | . . .\n

        """
        self._updateCounters(2)
        self._a(_cmd.Tempo_TimerB(Data))

    def OpmControl(self, Register, Data):
        self._updateCounters(3)
        self._a(_cmd.OpmControl(Register, Data))

    def Tone(self, Data):
        self._updateCounters(2)
        self._a(_cmd.Tone(Data))

    def Pan(self, Data):
        self._updateCounters(2)

        # Correct the panning
        if (type(Data) is str):
            Data = Data.lower()
            if (Data in ['l', 'c', 'r']):
                Data = {
                    'l': 0b01,
                    'c': 0b11,
                    'r': 0b10
                }[Data]
            else: Data = 0b11
        elif (type(Data) is int):
            if    Data == 0b10: Data = 0b01
            elif  Data == 0b01: Data = 0b10
            else: Data = 0b11

        self._a(_cmd.Pan(Data))

    def Volume(self, Data):
        self._updateCounters(2)
        self._a(_cmd.Volume(Data))

    def Volume_Increase(self):
        self._updateCounters(1)
        self._a(_cmd.Volume_Increase())

    def Volume_Decrease(self):
        self._updateCounters(1)
        self._a(_cmd.Volume_Decrease())

    def Gate(self, Data):
        self._updateCounters(2)
        self._a(_cmd.Gate(Data))

    def Legato(self):
        self._updateCounters(1)
        self._a(_cmd.Legato())

    def Repeat_Start(self):
        self._updateCounters(3)
        self._rsl.append(0)  # New repeat start byte counter
        
    def Repeat_End(self, Data):
        self._updateCounters(3)
        self._a(_cmd.Repeat_End(self._rsl[-1])) # Add repeat end command
        self._i(-self._rsl[-1], _cmd.Repeat_Start(Data)) # Insert repeat start command at trackdata index (counted from last) of latest byte counter
        self._rsl.pop(-1) # Remove the appropriote byte counter

        if (self._rel != []):   # If a repeat escape byte counter is active
            self._i(-self._rel[-1], _cmd.Repeat_Escape(self._rel[-1])) # Insert repeat escape command at trackdata index (counted from last)
            self._rel.pop(-1)

    def Repeat_Escape(self):
        self._updateCounters(3)
        self._rel.append(0)  # New escape byte counter

    def SetDetune(self, Data):
        self._updateCounters(3)
        self._a(_cmd.Detune(Data))

    def Portamento(self, Data):
        self._updateCounters(3)
        self._a(_cmd.Portamento(Data))

    def DataEnd(self, Data=0x00):
        self._updateCounters(2 if Data==0x00 else 3)
        self._a(_cmd.DataEnd(Data))

    def DelayKeyon(self, Data):
        self._updateCounters(2)
        NotImplemented

    def SyncResume(self, Data):
        self._updateCounters(2)
        NotImplemented

    def SyncWait(self, Data):
        self._updateCounters(1)
        NotImplemented

    def AdpcmFreq(self, Data):
        self._updateCounters(2)
        self._a(_cmd.AdpcmFreq(Data))

    def ExpcmEnable(self):
        self._updateCounters(1)
        self._a(_cmd.Pcm8Shift())

#*********************************************************

# /// Extended commands (+16) ///
class _Command_Ext16:
    def __init__(self, ObjRef):
        self._updateCounters = ObjRef._updateCounters   # Set references to main object
        self._a = ObjRef._a

    def Terminate(self):
        self._updateCounters(2)

    def Fadeout(self):
        self._updateCounters(3)

# /// Extended commands (+16/02EX) ///
class _Command_Ext16_02EX:
    def __init__(self, ObjRef):
        self._updateCounters = ObjRef._updateCounters
        self._a = ObjRef._a

    def Terminate(self):
        self._updateCounters(2)

    def RelativeDetune(self):
        self._updateCounters(4)

    def Transpose(self):
        self._updateCounters(3)

    def RelativeTranspose(self):
        self._updateCounters(3)

# /// Extended commands (+17) ///  ※Not widely supported -- ※広くサポートされていない
class _Command_Ext17:
    def __init__(self, ObjRef):
        self._updateCounters = ObjRef._updateCounters
        self._a = ObjRef._a

    def Pcm8Control(self):
        self._updateCounters(8)

    def idk(self):
        self._updateCounters(3)

    def ChannelControl(self):
        self._updateCounters(3)

    def AddLenght(self):
        self._updateCounters(3)

    def Note(self, Data, Clocks):
        """
        Note command (+17 cmds) | 音符 コマンド\n
        Valid note range: 0x80 (o0d+) -- 0xDF (o8d)
        """
        cmdCount = 2

        if (Clocks > 256):
            self._a(_cmd.Note(Data, 256))
            Clocks -= 256
            while (Clocks > 256):
                self._a(_cmd.Ext_17_AddLenght(256))
                Clocks -= 256
                cmdCount += 3

        self._updateCounters(cmdCount)
        self._a(_cmd.Note(Data, Clocks))

    def UseFlags(self):
        self._updateCounters(3)









#region ||  MDX Commands (Internal)  ||



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