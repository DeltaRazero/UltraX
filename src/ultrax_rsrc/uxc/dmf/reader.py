

from . import dmf
from ... import pymdx



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


class Channel_Reader:
    """Reads channels"""


    NoteActive : bool = False
    Note : pymdx.command.Note = None    # Reference to current note command obj
    Instrument : int = None
    Volume : int = None

    Tickspeed : int = 1

    Porta : pymdx.command.Portamento = None
    PortaCount = 0

    Vibrato = None

    Bpm : int = 0

    SampleBank : int = 0

    Pattern : Pattern_Reader = None # Reference to patternreader object
    Position : int = None

    _Patterns = {}
    _Sequence = []

    def __init__(self, DmfChannel_Obj):
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
