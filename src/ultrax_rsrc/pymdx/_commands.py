
# CLOCK DURATIONS:
# -------------------
# * Clock durations are internally: value+1
#
# MININMUM + MAXMIMUM
# * 0x00 = 1 clock
# * 0x8e = 256 clocks   (max amount of clocks for one note)
#
# MUSIC NOTATION VALUES
# * 0xbf / 192 clocks = whole   note / l1
# * 0x5f / 96  clocks = half    note / l2
# * 0x2f / 48  clocks = quarter note / l4
# * 0x17 / 24  clocks = 8th     note / l8
# * 0x0b / 12  clocks = 16th    note / l16
# * 0x05 / 6   clocks = 32th    note / l32
# * 0x02 / 3   clocks = 64th    note / l64

class Command:
    """MDX performance commands."""
    
    def __init__(self, datalist):
        self._a = datalist.append    # Set reference to _datatrack->_Data instance

    def Rest(self, Clocks):
        """Rest command."""
        self._a(Rest(Clocks))

    def Note(self, Note, Clocks):
        """Note command.\n
        Valid note range: 0x80 - 0xDF\n
        0x80 = o0d+  /  0xDF = o8d"""
        self._a(Note(Note, Clocks))







#region ||  

class Rest:
    def __init__(self, Clocks):
        self.Clocks = Clocks

    def Export(self):
        e = bytearray()
        while (self.Clocks >= 128):
            e.append(0x7F)
            self.Clocks -= 128
        e.append(self.Clocks)
        return e


class Note:
    def __init__(self, Data, Clocks):
        self.Data = Data
        self.Clocks = Clocks

    def Export(self):
        e = bytearray()
        while (self.Clocks >= 128):
            e.append(0x7F)
            self.Clocks -= 128
        e.append(self.Clocks)
        return e





    




