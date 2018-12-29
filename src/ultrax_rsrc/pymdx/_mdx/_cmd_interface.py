from . import _cmd
from .._misc.exc import *


class Command_Interface:
    """
    MDX performance commands.
    """

    #**********************************************************
    #
    #    Internal stuff
    #
    #**********************************************************
    #region
    def __init__(self, Datalist):

        self._a = Datalist.append    # Set reference to _datatrack->_Data instance

        self.Ext16      = _Command_Ext16(self)
        """MDX performance commands (+16 extension)."""

        self.Ext16_02EX = _Command_Ext16_02EX(self)
        """MDX performance commands (+16/02EX extension)."""

        self.Ext17      = _Command_Ext17(self)
        """MDX performance commands (+17 extension) ※ Not widely supported."""

        return    
    #endregion


    #**********************************************************
    #
    #    Public interface for commands
    #
    #**********************************************************
    #region
    def Rest(self, Clocks):
        """
        Rest command | 休符 コマンド
        """
        self._a(_cmd.Rest(Clocks))
        return


    def Note(self, Data, Clocks):
        """
        Note command | 音符 コマンド\n
        Valid note range: 0x80 (o0d+) -- 0xDF (o8d)
        """
        self._a(_cmd.Note(Data, Clocks))

        return


    def Tempo_Bpm(self, Data):
        """
        Set the tempo in beats per minute.
        -----
        1分あたりの拍数でテンポを設定します。

        """
        self._a(_cmd.Tempo_Bpm(Data))
        return


    def Tempo_TimerB(self, Data):
        """
        Tempo command | . . .\n

        """
        self._a(_cmd.Tempo_TimerB(Data))
        return


    def Opm_Control(self, Register, Data):
        self._a(_cmd.OpmControl(Register, Data))
        return


    def Tone(self, Data):
        self._a(_cmd.Tone(Data))
        return


    def Pan(self, Data):
        self._a(_cmd.Pan(Data))
        return


    def Volume(self, Data):
        self._a(_cmd.Volume(Data))
        return


    def Volume_Increase(self):
        self._a(_cmd.Volume_Increase())
        return


    def Volume_Decrease(self):
        self._a(_cmd.Volume_Decrease())
        return


    def Gate(self, Data):
        self._a(_cmd.Gate(Data))
        return


    def Legato(self):
        self._a(_cmd.Legato())
        return


    def SetDetune(self, Data):
        self._a(_cmd.Detune(Data))
        return


    def Portamento(self, Data):
        self._a(_cmd.Portamento(Data))
        return


    def DataEnd(self, Data=0x00):
        self._a(_cmd.DataEnd(Data))
        return


    def DelayKeyon(self, Data):
        self._a(_cmd.DelayKeyon(Data))
        return


    def Sync_Resume(self, Data):
        self._a(_cmd.Sync_Resume(Data))
        return


    def Sync_Wait(self):
        self._a(_cmd.Sync_Wait())
        return


    def Noise_Control(self, Data, NoiseEnabled=None):
        self._a(_cmd.Noise_Control(Data, NoiseEnabled))
        return


    def Adpcm_Control(self, Data):
        self._a(_cmd.Adpcm_Control(Data))
        return

    
    def Expcm_Enable(self):
        """
        Enable EX-PCM mode |
        """
        self._a(_cmd.Expcm_Enable())
        return


    def LoopMark(self):
        self._a(_cmd.LoopMark())
        return


# :: Repeat commands ::
    def Repeat_Start(self, Repeats=0):
        self._a(_cmd.Repeat_Start(Repeats))
        return


    def Repeat_End(self, Data=0, Repeats=0):
        self._a(_cmd.Repeat_End(Data))
        return


    def Repeat_Escape(self):
        self._a(_cmd.Repeat_Escape())
        return


# :: LFO commands // Pitch ::
    def Lfo_Pitch_Enable(self):
        self._a(_cmd.Lfo_Pitch_Enable())
        return

    def Lfo_Pitch_Disable(self):
        self._a(_cmd.Lfo_Pitch_Disable())
        return

    def Lfo_Pitch_Control(self, Wave, Freq, Amp):
        self._a(_cmd.Lfo_Pitch_Control(Wave, Freq, Amp))
        return


# :: LFO commands // Volume ::
    def Lfo_Volume_Enable(self):
        self._a(_cmd.Lfo_Volume_Enable())
        return

    def Lfo_Volume_Disable(self):
        self._a(_cmd.Lfo_Volume_Disable())
        return

    def Lfo_Volume_Control(self, Wave, Freq, Amp):
        self._a(_cmd.Lfo_Volume_Control(Wave, Freq, Amp))
        return


# :: LFO commands // Opm ::
    def Lfo_Opm_Enable(self):
        self._a(_cmd.Lfo_Opm_Enable())
        return

    def Lfo_Opm_Disable(self):
        self._a(_cmd.Lfo_Opm_Disable())
        return

    def Lfo_Opm_Control(self, Wave, Speed, Pmd=0, Amd=0, Pms=0, Ams=0, RestartWave=0):

        # Pitch / Amp mod depth low precision
        Pms_Ams = (Pms<<4 & 0x07) & (Ams & 0x07)

        # PMD / AMS --> Pitch / Amp mod depth high precision
        # LFRQ --> speed
        # SYNC --> RestartWave
        
        self._a(_cmd.Lfo_Opm_Control(RestartWave, Wave, Speed, Pmd, Amd, Pms_Ams))
        return
#endregion




#**********************************************************
#
#    Interface for commands
#    (+16 extension class)
#
#**********************************************************
#region
class _Command_Ext16:
    def __init__(self, ObjRef):
        self._a = ObjRef._a


    def Fadeout(self, Data):
        self._a(_cmd.Ext_16_Fadeout(Data))
        return
#endregion



#**********************************************************
#
#    Interface for commands
#    (+16/02EX extension class)
#
#**********************************************************
#region
class _Command_Ext16_02EX:
    def __init__(self, ObjRef):
        self._a = ObjRef._a


    def RelativeDetune(self, Data):
        self._a(_cmd.Ext_16_02EX_RelativeDetune(Data))
        return


    def Transpose(self, Data):
        self._a(_cmd.Ext_16_02EX_Transpose(Data))
        return


    def RelativeTranspose(self, Data):
        self._a(_cmd.Ext_16_02EX_RelativeTranspose(Data))
        return
#endregion




#**********************************************************
#
#    Interface for commands
#    (+17 extension class)
#
#**********************************************************
# ※Not widely supported / ※広くサポートされていない
#region
class _Command_Ext17:
    def __init__(self, ObjRef):
        self._a = ObjRef._a


    def Pcm8_Control(self, d0, d1):
        self._a(_cmd.Ext_17_Pcm8_Control(d0, d1))
        return

    def UseKeyoff(self, Data):  # Use keyoff y/n
        self._a(_cmd.Ext_17_UseKeyoff(Data))
        return


    def Channel_Control(self, Data):
        """
        Control other channel

        Prepares MML command to be inserted into another channel

        --
        """
        self._a(_cmd.Ext_17_Channel_Control(Data))
        return


    def AddLenght(self, Clocks):
        self._a(_cmd.Ext_17_AddLenght(Clocks))
        return


    def Note(self, Data, Clocks):
        """
        Note command (+17 cmds) | 音符 コマンド\n
        Valid note range: 0x80 (o0d+) -- 0xDF (o8d)
        """
        self._a(_cmd.Ext_17_Note(Data, Clocks))
        return


    def UseFlags(self, Data):
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