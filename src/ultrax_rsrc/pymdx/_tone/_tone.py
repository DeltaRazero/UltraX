from array import array

from . import _opm


class Tone(_opm.OPM_Channel):
    """MDX tone definition object."""

    ToneId   = 0
    SlotMask = 15

    def __init__(self):
        _opm.OPM_Channel.__init__(self)
        return

    def SetTone(self, Patch):
        """Set tone data from an existing FMT OPMN object."""
        self.Fb = Patch.Fb
        self.Alg = Patch.Alg
        self.Op = Patch.Op
        return

    def _Export(self):
        """Exports the current tone object to a bytearray."""

        l_op = len(self.Op)
        l_param = 6

        tone = [[] for _ in range(l_op)]
        for c, op in enumerate(self.Op):
            a = tone[c].append
            a(op.Dt1<<4   | op.Mult)
            a(op.Tl)
            a(op.Ks<<6    | op.Ar)
            a(op.Am_On<<7 | op.Dr)
            a(op.Dt2<<6   | op.Sr)
            a(op.Sl<<4    | op.Rr)

        e = array('B', [self.ToneId, self.Fb<<3 | self.Alg, self.SlotMask])

        for param in range(l_param):
            for op in range(l_op):
                e.append(tone[op][param])

        return e
