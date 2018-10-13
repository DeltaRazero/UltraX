from . import _commands as _cmd
from .._misc.exc import *


class Command:
    """
    MDX performance commands.
    """

    #===========================================#
    #   Internal props
    #===========================================#
    #region
    def __init__(self, Datalist):
        self._a = Datalist.append    # Set reference to _datatrack->_Data instance
        self._e = Datalist.extend
        self._i = Datalist.insert

        self._rsc = []  # Repeat start,     byte counter list
        self._rec = []  # Repeat escape,    byte counter list
        self._lmc = 0   # Loop mark,        byte counter

        self.Ext16      = _Command_Ext16(self)
        """MDX performance commands (+16 extension)."""

        self.Ext16_02EX = _Command_Ext16_02EX(self)
        """MDX performance commands (+16/02EX extension)."""

        self.Ext17      = _Command_Ext17(self)
        """MDX performance commands (+17 extension) ※ Not widely supported."""

        return


    def _updateCounters(self, n):
        if (self._rsc != []):   # Increase repeat start byte counter list
            for i, _ in enumerate(self._rsc): self._rsc[i]+=n
        if (self._rec != []):   # Increase repeat escape byte counter list
            for i, _ in enumerate(self._rec): self._rsc[i]+=n
        if (self._lmc > 0):      # Increase loop mark byte counter
            self._lmc += n
        
        return
    #endregion


    #===========================================#
    #   Interface for commands
    #===========================================#
    #region
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

        return


    def Note(self, Data, Clocks) -> int:
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

        return


    def Tempo_Bpm(self, Data):
        """
        Set the tempo in beats per minute.
        -----
        1分あたりの拍数でテンポを設定します。

        """
        self._updateCounters(2)
        self._a(_cmd.Tempo_Bpm(Data))
        return


    def Tempo_TimerB(self, Data):
        """
        Tempo command | . . .\n

        """
        self._updateCounters(2)
        self._a(_cmd.Tempo_TimerB(Data))
        return


    def Opm_Control(self, Register, Data):
        self._updateCounters(3)
        self._a(_cmd.OpmControl(Register, Data))
        return


    def Tone(self, Data):
        self._updateCounters(2)
        self._a(_cmd.Tone(Data))
        return


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

        return


    def Volume(self, Data):
        self._updateCounters(2)
        self._a(_cmd.Volume(Data))
        return


    def Volume_Increase(self):
        self._updateCounters(1)
        self._a(_cmd.Volume_Increase())
        return


    def Volume_Decrease(self):
        self._updateCounters(1)
        self._a(_cmd.Volume_Decrease())
        return


    def Gate(self, Data):
        self._updateCounters(2)
        self._a(_cmd.Gate(Data))
        return


    def Legato(self):
        self._updateCounters(1)
        self._a(_cmd.Legato())
        return


    def SetDetune(self, Data):
        self._updateCounters(3)
        self._a(_cmd.Detune(Data))
        return


    def Portamento(self, Data):
        self._updateCounters(3)
        self._a(_cmd.Portamento(Data))
        return


    def DataEnd(self, Data=0x00):
        self._updateCounters(2 if Data==0x00 else 3)
        self._a(_cmd.DataEnd(Data))
        return


    def DelayKeyon(self, Data):
        self._updateCounters(2)
        self._a(_cmd.DelayKeyon(Data))
        return


    def Sync_Resume(self, Data):
        self._updateCounters(2)
        self._a(_cmd.Sync_Resume(Data))
        return


    def Sync_Wait(self):
        self._updateCounters(1)
        self._a(_cmd.Sync_Wait())
        return


    def AdpcmFreq(self, Data):
        self._updateCounters(2)
        self._a(_cmd.AdpcmFreq(Data))
        return

    
    def Expcm_Enable(self):
        """
        Enable EX-PCM mode |
        """
        self._updateCounters(1)
        self._a(_cmd.Expcm_Enable())
        return


    def LoopMark(self):
        self._lmc = 1
        return


# :: Repeat commands ::
    def Repeat_Start(self):
        self._updateCounters(3)
        self._rsc.append(0)  # New repeat start byte counter
        return


    def Repeat_End(self, Data):
        self._updateCounters(3)

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
        
        self._a(_cmd.Repeat_End(self._rsc[-1]))
        self._i(-self._rsc[-1], _cmd.Repeat_Start(Data))
        self._rsc.pop(-1)

        # If the repeat escape byte counter ('_rec') has a value (i.e. is counting), insert a repeat escape command
        # at the index position from the counter at the last position in the buffer (the same way how we insert repeat
        # start commands).
        # After that we can safely remove the counter value from the list buffer / free up memory, as we have no more
        # further use for it anymore.

        # repeat escapeバイトカウンタ（ '_rec'）に値がある場合（意味：カウント中）、インデックス位置に 'repeat_escape'コマンドが挿入されます。
        # インデックス位置は、カウンタバッファの最後の位置の値です（リピート開始コマンドの挿入方法と同じです）。
        # カウンタバッファの最後の値を使用する必要はもうありません。 したがって、リストバッファ/空きメモリからカウンタ値を安全に削除できます。

        if (self._rec != []):
            self._i(-self._rec[-1], _cmd.Repeat_Escape(self._rec[-1]))
            self._rec.pop(-1)

        return


    def Repeat_Escape(self):
        self._updateCounters(3)
        self._rec.append(0)  # New escape byte counter
        return


# :: LFO commands // Pitch ::
    def Lfo_Pitch_Enable(self):
        self._updateCounters(2)
        self._a(_cmd.Lfo_Pitch_Enable())
        return

    def Lfo_Pitch_Disable(self):
        self._updateCounters(2)
        self._a(_cmd.Lfo_Pitch_Disable())
        return

    def Lfo_Pitch_Control(self, Wave, Freq, Amp):
        self._updateCounters(6)
        self._a(_cmd.Lfo_Pitch_Control(Wave, Freq, Amp))
        return


# :: LFO commands // Volume ::
    def Lfo_Volume_Enable(self):
        self._updateCounters(2)
        self._a(_cmd.Lfo_Volume_Enable())
        return

    def Lfo_Volume_Disable(self):
        self._updateCounters(2)
        self._a(_cmd.Lfo_Volume_Disable())
        return

    def Lfo_Volume_Control(self, Wave, Freq, Amp):
        self._updateCounters(6)
        self._a(_cmd.Lfo_Volume_Control(Wave, Freq, Amp))
        return


# :: LFO commands // Opm ::
    def Lfo_Opm_Enable(self):
        self._updateCounters(2)
        self._a(_cmd.Lfo_Opm_Enable())
        return

    def Lfo_Opm_Disable(self):
        self._updateCounters(2)
        self._a(_cmd.Lfo_Opm_Disable())
        return

    def Lfo_Opm_Control(self, Wave, Speed, Pmd=0, Amd=0, Pms=0, Ams=0, RestartWave=0):  # TODO: these are wrong input
        self._updateCounters(7)

        # Pitch / Amp mod depth low precision
        Pms_Ams = (Pms<<4 & 0x07) & (Ams & 0x07)

        # PMD / AMS --> Pitch / Amp mod depth high precision
        # LFRQ --> speed
        # SYNC --> RestartWave
        
        self._a(_cmd.Lfo_Opm_Control(RestartWave, Wave, Speed, Pmd, Amd, Pms_Ams))
        return
#endregion


#===============================================#
#   Interface for commands
#   (+16 extension class)
#===============================================#
#region
class _Command_Ext16:
    def __init__(self, ObjRef):
        self._updateCounters = ObjRef._updateCounters   # Set references to main object
        self._a = ObjRef._a


    def Fadeout(self, Data):
        self._updateCounters(3)
        self._a(_cmd.Ext_16_Fadeout(Data))
        return
#endregion


#===============================================#
#   Interface for commands
#   (+16/02EX extension class)
#===============================================#
#region
class _Command_Ext16_02EX:
    def __init__(self, ObjRef):
        self._updateCounters = ObjRef._updateCounters
        self._a = ObjRef._a


    def RelativeDetune(self, Data):
        self._updateCounters(4)
        self._a(_cmd.Ext_16_02EX_RelativeDetune(Data))
        return


    def Transpose(self, Data):
        self._updateCounters(3)
        self._a(_cmd.Ext_16_02EX_Transpose(Data))
        return


    def RelativeTranspose(self, Data):
        self._updateCounters(3)
        self._a(_cmd.Ext_16_02EX_RelativeTranspose(Data))
        return
#endregion


#===========================================#
#   Interface for commands
#   (+17 extension class)
#===========================================#
# ※Not widely supported / ※広くサポートされていない
#region
class _Command_Ext17:
    def __init__(self, ObjRef):
        self._updateCounters = ObjRef._updateCounters
        self._a = ObjRef._a

    def Pcm8_Control(self, d0, d1):
        self._updateCounters(8)
        self._a(_cmd.Ext_17_Pcm8_Control(d0, d1))
        return

    def UseKeyoff(self, Data):  # Use keyoff y/n
        self._updateCounters(3)
        self._a(_cmd.Ext_17_UseKeyoff(Data))
        return


    def Channel_Control(self, Data):
        """
        Control other channel

        Prepares MML command to be inserted into another channel

        -- 
        """
        self._updateCounters(3)
        self._a(_cmd.Ext_17_Channel_Control(Data))
        return


    def AddLenght(self, Clocks):
        cmdCount = 3

        while (Clocks > 256):
            self._a(_cmd.Ext_17_AddLenght(256))
            Clocks -= 256
            cmdCount += 3

        self._updateCounters(cmdCount)
        self._a(_cmd.Ext_17_AddLenght(Clocks))

        return


    def Note(self, Data, Clocks):
        """
        Note command (+17 cmds) | 音符 コマンド\n
        Valid note range: 0x80 (o0d+) -- 0xDF (o8d)
        """
        self._updateCounters(2)

        if (Clocks > 256):
            self._a(_cmd.Note(Data, 256))
            Clocks -= 256
            # The rest of command adding/counting is done in Ext_17_AddLenght
            self._a(_cmd.Ext_17_AddLenght(Clocks))
        else:
            self._a(_cmd.Note(Data, Clocks))

        return


    def UseFlags(self, Data):
        self._updateCounters(3)
        self._a(_cmd.Ext_17_UseFlags(Data))
        return
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