
class _OPM_Operator:
    Ar, Dr, Sl, Sr, Rr = 0, 0, 0, 0, 0
    Tl = 0
    Dt1, Dt2 = 0, 0
    Mult = 0
    Ks = 0
    Am_On = 0


class _OPM_Channel:

    def __init__(self):
        self.Fb = 0
        self.Alg = 0
        self.Op = [_OPM_Operator() for _ in range(4)]


class Tone(_OPM_Channel):
    """MDX tone definition object."""

    ToneId   = 0
    SlotMask = 15

    def __init__(self):
        _OPM_Channel.__init__(self)
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

        e = bytearray([self.ToneId, self.Fb<<3 | self.Alg, self.SlotMask])

        for param in range(l_param):
            for op in range(l_op):
                e.append(tone[op][param])

        return e
