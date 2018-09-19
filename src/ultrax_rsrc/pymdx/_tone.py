from libPyFMT import opmn


class Tone(opmn.OPMN_Channel):
    """MDX tone definition object."""

    def __init__(self):
        self.ToneId = 0
        self.SlotMask = 0
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
        e = bytearray([self.ToneId, self.Fb, self.Alg, self.SlotMask])
        for op in self.Op:
            e.extend([
                op.Dt1<<4   | op.Mult,
                op.Tl,
                op.Ks<<6    | op.Ar,
                op.Am_On<<7 | op.Dr,
                op.Dt2<<6   | op.Sr,
                op.Sl<<4    | op.Rr
            ])
        return e
