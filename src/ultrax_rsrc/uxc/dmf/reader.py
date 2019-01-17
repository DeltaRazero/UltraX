

from . import dmf
from ... import pymdx

from enum import Enum as _Enum



class Pattern_Reader:
    """Reads patterns"""

    PatternId = None
    _Rows = []

    # dmf_module._Pattern
    Row : dmf._Row = None # Current row ref
    Position : int = None


    def __init__(self, Pattern):
        self._Rows = Pattern.Rows
        self.PatternId = Pattern.Id
        self.Position = 0
        self.Row = self._Rows[self.Position]
        return

    def SeekRow(self, Position, Mode=0):
        #Mode: absolute, relative
        if Mode is 0:
            self.Position = Position

        elif Mode is 1:
            self.Position += Position

        self._SetRow(Position)
        return

    def _SetRow(self, Position):
        self.Row = self._Rows[self.Position]
        return

    def AdvanceRow(self):
        self.Position += 1
            
        if (self.Position > len(self._Rows)-1 ):
            self.Row = None
        else:
            self.Row = self._Rows[self.Position]
        return



class PORTA_TYPES(_Enum):
    PORTA_NONE = 0
    PORTA_01 = 1
    PORTA_02 = 2
    PORTA_03 = 3
    PORTA_E1 = 4
    PORTA_E2 = 5



class Channel_States:

    Porta_Cmd : pymdx.command.Portamento = pymdx.command.Portamento(0)
    Porta_Current : int = 0
    Porta_Target : int = 0
    Porta_Type : PORTA_TYPES = PORTA_TYPES.PORTA_NONE
    Porta_IsTonePorta : bool = False
    Porta_IsAdjusted : bool = False
    Porta_IsActive : bool = False

    def Porta_Reset(self):
        self.Porta_Cmd = pymdx.command.Portamento(0)
        self.Porta_Type = PORTA_TYPES.PORTA_NONE
        self.Porta_IsTonePorta  = False
        self.Porta_IsAdjusted = False
        self.Porta_IsActive = False
        self.Porta_Current = 0
        self.Porta_Target = 0
        return

    Note_Cmd : pymdx.command.Note = None    # Reference to current note command obj
    # NOTE: Maybe have seperate Rest command ref var?
    Note_IsActive : bool = False

    Tone_Number : int = 0

    Volume : int = 0
    Vol_Add = None

    Pan_Cmd : pymdx.command.Pan = pymdx.command.Pan(0b11)

    Tempo_Bpm : int = 0
    Tempo_Tick1 : int = 0
    Tempo_Tick2 : int = 0
    Tempo_BaseTime : int = 0
    Tempo_RefreshRate : int = 0

    Vib_Cmd : pymdx.command.Lfo_Pitch_Control = None
    Vib_IsActive : bool = False

    SampleBank : int = 0




class Channel_Reader:
    """Reads channels"""

    State : Channel_States = None

    Pattern : Pattern_Reader = None # Reference to patternreader object
    Position : int = None

    _Patterns = {}
    _Sequence = []

    def __init__(self, DmfChannel_Obj):
        self.State = Channel_States()
        self._Patterns = DmfChannel_Obj.Patterns
        self._Sequence = DmfChannel_Obj.Sequence
        self.Position = 0
        self.Pattern = Pattern_Reader(self._Patterns[self._Sequence[self.Position]])
        return

    def SeekPattern(self, Position, Mode=0):
        #Mode: absolute, relative
        if Mode is 0:
            self.Position = Position

        elif Mode is 1:
            self.Position += Position

        self._SetPattern(Position)

        return

    def _SetPattern(self, Position):
        self.Pattern = Pattern_Reader(self._Patterns[self._Sequence[Position]])
        return

    def AdvancePattern(self):
        self.Position += 1

        if (self.Position > len(self._Sequence)-1 ):
            self.Pattern = None
        else:
            self.Pattern = Pattern_Reader(self._Patterns[self._Sequence[self.Position]])

        return
