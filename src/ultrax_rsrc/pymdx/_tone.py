from libPyFMT import opmn


class Tone(opmn.OPMN_Channel):
    """MDX tone definition object."""

    def __init__(self):
        self.ToneId = 0
        self.SlotMask = 15
        opmn.OPMN_Channel.__init__(self)
        return

    def SetTone(self, Patch):
        """Set tone data from an existing FMT OPMN object."""
        self.Fb = Patch.Fb
        self.Alg = Patch.Alg
        self.Op = Patch.Op
        return

    def _Export(self):
        """Exports the current tone object to a bytearray."""
        e = bytearray([self.ToneId, self.Fb<<3 | self.Alg, self.SlotMask])

        temp = [[] for _ in range(len(self.Op))]
        for c, op in enumerate(self.Op):
            a = temp[c].append
            a(op.Dt1<<4   | op.Mult)
            a(op.Tl)
            a(op.Ks<<6    | op.Ar)
            a(op.Am_On<<7 | op.Dr)
            a(op.Dt2<<6   | op.Sr)
            a(op.Sl<<4    | op.Rr)

        for i in range(len(temp[0])):
            for j in range(len(temp)):
                e.append(temp[j][i])

        return e
