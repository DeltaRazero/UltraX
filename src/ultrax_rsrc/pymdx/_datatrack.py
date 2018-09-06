from ._commands import Commands
from enum import Enum



# class ClockValues(Enum, ClockWholeNote):
#     self._CLOCK_VALUE_1 = ClockWholeNote-1   # = 191
#     self._CLOCK_VALUE_2  = int(round(ClockWholeNote /  2))-1
#     self._CLOCK_VALUE_4  = int(round(ClockWholeNote /  4))-1
#     self._CLOCK_VALUE_8  = int(round(ClockWholeNote /  8))-1
#     self._CLOCK_VALUE_16 = int(round(ClockWholeNote / 16))-1
#     self._CLOCK_VALUE_32 = int(round(ClockWholeNote / 32))-1
#     self._CLOCK_VALUE_64 = int(round(ClockWholeNote / 64))-1


class DataTrack():
    '''fuckboi'''

    def __init__(self):
        self._Data = []

        #self.SetClockValue_WholeNote(ClockWholeNote)
        self.Add = Commands(self._Data)
        #Commands.__init__(self)
        return

    #def SetClockValue_WholeNote(self, ClockWholeNote):
        


    def Export(self):
        '''Exports the current tone object to a bytearray.'''
        e = bytearray()

        for i in self._Data:
            e.extend(i.Export())

        return e
