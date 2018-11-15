from ._commands_itf import Command, _cmd
from enum import Enum


class Datatrack():

    def __init__(self):
        self.Data = []
        self.Add = Command(self.Data)
        return

    def _Export(self):
        """Exports the current datatrack object to a bytearray."""

        counterobj = CounterObj(self.Data)

        exported = [i.Export(counterobj) for i in self.Data]
        for i in counterobj.Rsc.Counters:
            exported[i.Position] = _cmd.Repeat_Start(i.Loopback_Times).Export_NoCounter()

        if counterobj.Lmc > 0:
            counterobj.UpdateCounters(3)
            exported.append(_cmd.DataEnd(counterobj.Lmc -1 ).Export(counterobj))
        else:
            exported.append(_cmd.DataEnd(0).Export(counterobj))
        
        b = bytearray()
        for i in exported:
            b.extend(i)

        return b




#**********************************************************
#
#    Command counters
#
#**********************************************************

# Generic counter
class Counter:
    def __init__(self, CounterObject):
        self.Counters = []
        self._buffer = []
        self._type = CounterObject

    def Stop1(self):
        if (self._buffer != []):
            self.Counters.append(self._buffer[-1])
            self._buffer.pop(-1)
        return
        
    def Add1(self, Index):
        self._buffer.append(self._type(Index))
        return

    def Update(self, n):
        if (self._buffer != []):
            for i in self._buffer:
                i.Loopback_Amount += n
        return


# Counter for Repeat_Start commands
class RepeatStartCounter:
    def __init__(self, Position):
        self.Position = Position

        self.Loopback_Amount = 0
        self.Loopback_Times  = 0


# Counter for Repeat_Escape commands
class RepeatEscapeCounter:
    def __init__(self, Position):
        self.Position = Position

        self.Loopback_Amount = 0
        self.Loopback_Times  = 0


# Main object containing counters
class CounterObj:
    def __init__(self, Datalist):
        self.Datalist = Datalist

        self.CommandCounter = -1

        self.Rsc = Counter(RepeatStartCounter)
        self.Rec = Counter(RepeatEscapeCounter)

        self.Lmc = 0   # Loop mark,        byte counter

    def UpdateCounters(self, n):
        for i in (self.Rsc, self.Rec):
            i.Update(n)

        if (self.Lmc > 0):      # Increase loop mark byte counter
            self.Lmc += n

        self.CommandCounter += 1

        return
