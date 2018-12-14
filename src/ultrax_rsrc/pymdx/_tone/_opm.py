
class _OPM_Operator:
    Ar, Dr, Sl, Sr, Rr = 0, 0, 0, 0, 0
    Tl = 0
    Dt1, Dt2 = 0, 0
    Mult = 0
    Ks = 0
    Am_On = 0


class OPM_Channel:

    def __init__(self):
        self.Fb = 0
        self.Alg = 0
        self.Op = [_OPM_Operator() for _ in range(4)]
