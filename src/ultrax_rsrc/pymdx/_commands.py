
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


# The following classes are a way of substituting structs, which aren't available in Python


#region ||  Clock value calculation  ||




class Rest:
    def __init__(self, Clocks):
        self.Clocks = Clocks

    def Export(self):
        e = bytearray()

        Loop = True
        while (Loop):
            if (self.Clocks >= 128):
                e.append(0x7F)
                self.Clocks -= 128
            else:
                e.append(self.Clocks)
                Loop = False
        return e


class Commands:

    def __init__(self, datalist):
        self.datalist = datalist

    def Rest(self, Clocks):
        self.datalist.append(Rest(Clocks))


    




