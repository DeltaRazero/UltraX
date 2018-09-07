from ._commands import Command
from enum import Enum




class Datatrack():

    def __init__(self):
        self._Data = []

        #self.SetClockValue_WholeNote(ClockWholeNote)
        self.Add = Command(self._Data)
        return

    #def SetClockValue_WholeNote(self, ClockWholeNote):
        


    def Export(self):
        """Exports the current datatrack object to a bytearray."""
        e = bytearray()

        for i in self._Data:
            e.extend(i.Export())

        return e
