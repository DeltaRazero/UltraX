
from . import dmf_module
from ... import pymdx

from enum import Enum
import io



class Chan:
    def __init__(self, Channel):
        

        self.IsDuplicate = False # True when directly looping

        self.CurrentIns  = 0
        self.CurrentPtrn = 0

        self.Patterns     = Channel.Patterns
        self.PatternOrder = Channel.PatternOrder


    def ReadRow(self):
        for i in self.Pattern[CurrentPtrn].Rows:
            yield i
        return


    def RowGen(self, Pattern):
        for row in Channel.Patterns[CurrentPtrn].Rows:
            yield row




class UXC_Dmf:

    def __init__(self, path):
        pass


    def Compile(self, Path, *Arguments):
        #self.Dat = FData
        #self.SetCompilerOptions(Arguments)

        dmf = dmf_module.Dmf()
        dmf.Load(Path)

        # Check if other pcm channels active
        mdx = pymdx.Mdx(True)

        tempo = CalcTempo(dmf.Module.Tick1)
        mdx.DataTracks[0].Add.Tempo_Bpm(tempo)


        self.Channels = [i for i in dmf.Module.Channels]


        r = [i.ReadRow() for i in self.Channels]
        for c, channel in enumerate(self.Channels):

            




            data = mdx.DataTracks[i_chn]
            pattern = chn.Patterns[ptrnIndex]

            ptrnRepeats = _C_PatternRepeats(i, chn.PatternOrder)

                # Check fx

            for row in pattern.Rows:
                pass

                



    def _C_PatternRepeats(self, i, PatternOrder):
        j = i + 1
        l = len(PatternOrder)
        repeats = 0

        while (j <= l):
            if (PatternOrder[i] == PatternOrder[j]):
                repeats += 1
                j += 1
            else:
                return repeats



    def SetCompilerOptions(self, *Arguments):
        pass





# pattern_tick = speed / hertz
# beat_duration = pattern_tick * amount_rows_for_beat (8)
# bpm = 60 / beat_duration

def CalcTempo(tickspeed, refresh=60):
    row_duration  = tickspeed / refresh
    beat_duration = row_duration * 8
    bpm = 60 / beat_duration
    return round(bpm)



# PSEUDO CODE FOR DETUNE CALCULATION
# command == E5xx
# if xx > 80:
#   command_value = xx - 80
#   if command_value > 63:
#       command_value = 63
#
# if xx < 80:
#   command_value = 64 - (80 - xx)
#   if command_value > 0:
#       command_value = 0
#   note -= 1
