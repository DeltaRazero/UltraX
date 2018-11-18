from ._commands_itf import Command_Interface
from enum import Enum


class Datatrack():

    def __init__(self):
        self.Data = []
        self.Add = Command_Interface(self.Data)
        return

    def _Export(self):
        """Exports the current datatrack object to a bytearray."""

        self._Precompile()

        e = bytearray()
        for i in self.Data:
            e.extend(i.Export()) 

        return e

    def _Precompile(self):
        counterobj = CounterObj(self.Data)
        for i in self.Data:
            i.Count(counterobj)

        # Repeat start
        for i in counterobj.Rsc.Counters:
            self.Data[i.Position].Data = i.Loop_Times

        # Repeat end
        for i in counterobj.Rec.Counters:
            self.Data[i.Position].Data = i.Loopback_Amount

        # Repeat escape
        for i in counterobj.Rescc.Counters:
            self.Data[i.Position].Data = i.Loopskip_Amount

        # Data end
        if counterobj.Lmc > 0:
            counterobj.UpdateCounters(3)
            self.Add.DataEnd(counterobj.Lmc-1)
        else:
            counterobj.UpdateCounters(2)
            self.Add.DataEnd(0)

        return




#**********************************************************
#
#    Command counters
#
#**********************************************************

# Generic counter
class Counter:
    def __init__(self, CounterObject):
        self.Counters = []
        self._buffer  = []
        self._type    = CounterObject

    def Stop1(self):
        if (self._buffer != []):
            self.Counters.append(self._buffer[-1])
            self._buffer.pop(-1)
        return
        
    def Add1(self):
        self._buffer.append(self._type())
        return

    def GetLast(self):
        return self._buffer[-1]

    def Update(self, n):
        if (self._buffer != []):
            for i in self._buffer:
                i.Update(n)
        return


# Counter for Repeat_Start commands
class RepeatStartCounter:
    Position   = 0
    Loop_Times = 0


# Counter for Repeat_Start commands
class RepeatEndCounter:
    Position        = 0
    Loopback_Amount = 0

    def Update(self, n):
        self.Loopback_Amount += n
        return


# Counter for Repeat_Escape commands
class RepeatEscapeCounter:
    Position        = 0
    Loopskip_Amount = 0

    def Update(self, n):
        self.Loopskip_Amount += n
        return


# Main object containing counters
class CounterObj:
    def __init__(self, Datalist):
        self.Datalist = Datalist

        self.Position = -1

        self.Rsc   = Counter(RepeatStartCounter)
        self.Rec   = Counter(RepeatEndCounter)
        self.Rescc = Counter(RepeatEscapeCounter)

        self.Lmc = 0   # Loop mark,        byte counter

    def UpdateCounters(self, n):
        for i in (self.Rec, self.Rescc):
            i.Update(n)

        if (self.Lmc > 0):      # Increase loop mark byte counter
            self.Lmc += n

        self.Position += 1

        return
