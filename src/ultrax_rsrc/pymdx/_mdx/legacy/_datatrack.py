from ._commands_itf import Command
from enum import Enum


class Datatrack():

    def __init__(self):
        self._Data = []
        self.Add = Command(self._Data)
        return

    def _Export(self):
        """Exports the current datatrack object to a bytearray."""

        if (self.Add._lmc > 0):
            self.Add.DataEnd(self.Add._lmc)    # Loop back with the amount stored in byte counter
        else:
            self.Add.DataEnd(0)

        e = bytearray()
        for i in self._Data:
            e.extend(i.Export())

        return e
