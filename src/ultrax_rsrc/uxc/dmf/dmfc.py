
from . import dmf_module
from ... import pymdx

from enum import Enum
import io



class UX_CompiledObj:
    def __init__(self):
        self.Ticks = [0,0,0,0,0,0,0,0,0]
        self.Errors = []
        self.MdxObj = None


class Row_Reader:
    def __init__(self, Channel):
        self.Patterns = Channel.Patterns
        self.Sequence = Channel.Sequence

        self.Seq_Index = 0
        self.Row_Index = 0

        self.Note_Active = False


    def Seek(self, Seq_Index, Row_Index)



    def Read(self):
        # uint8_t   seq_index;
        # uint8_t   row_index;

        # bool   position_jump;
        # bool   pattern_break;

        if (Seq_Index):
            seq_index = Seq_Index
        else:
            seq_index = 0

        if (Row_Index):
            pattern_break = True
            row_index = Row_Index
        else:
            pattern_break = False

        # Iterate through patterns in sequence order
        while (seq_index <= len(self.Sequence)):
            seq = self.Sequence[seq_index]

            position_jump = False
            for pattern in self.Patterns[seq]:

                if (position_jump): break
                if not (pattern_break): row = 0

                pattern_break = False
                while (row_index <= len(pattern.Rows)):
                    row = pattern.Rows[row_index]

                    if (position_jump or pattern_break): break

                    for fx in row.Fx:

                        if (fx.Code == 0x0B):
                            if (fx.Value > seq_index):
                                seq_index = fx.Value
                                position_jump = True

                        elif (fx.Code == 0x0D):
                            row_index = fx.Value
                            pattern_break = True
                        
                    yield row
                    row_index += 1

            seq_index += 1


class PatternReader:




class Channel_Reader:
    def __init__(self, Channel):
        

        self.IsDuplicate = False # True when directly looping

        self.CurrentIns  = 0
        self.CurrentPtrn = 0

        self.Patterns = Channel.Patterns
        self.Sequence = Channel.Sequence

        #self.Seq_Index = 0
        #self.Row_Index = 0


    def Create_RowReader(self, Seq_Index=None, Row_Index=None):
        return Row_Reader(self, Seq_Index, Row_Index)


    # NOTE: make class instead?
    def RowReader(self, Seq_Index=None, Row_Index=None):
        # uint8_t   seq_index;
        # uint8_t   row_index;

        # bool   position_jump;
        # bool   pattern_break;

        if (Seq_Index):
            seq_index = Seq_Index
        else:
            seq_index = 0

        if (Row_Index):
            pattern_break = True
            row_index = Row_Index
        else:
            pattern_break = False

        # Iterate through patterns in sequence order
        while (seq_index <= len(self.Sequence)):
            seq = self.Sequence[seq_index]

            position_jump = False
            for pattern in self.Patterns[seq]:

                if (position_jump): break
                if not (pattern_break): row = 0

                pattern_break = False
                while (row_index <= len(pattern.Rows)):
                    row = pattern.Rows[row_index]

                    if (position_jump or pattern_break): break

                    for fx in row.Fx:

                        if (fx.Code == 0x0B):
                            if (fx.Value > seq_index):
                                seq_index = fx.Value
                                position_jump = True

                        elif (fx.Code == 0x0D):
                            row_index = fx.Value
                            pattern_break = True
                        
                    yield row
                    row_index += 1

            seq_index += 1




class UXC_Dmf:

    def __init__(self):
        pass


    def Compile(self, Path, **Kwargs):

        #self.SetCompilerOptions(Arguments)

        # Load and parse DefleMask module
        dmf = dmf_module.Dmf()
        dmf.Load(Path)

        # argparse thing
        if ('UseExpcm' in Kwargs):
            UseExpcm = Kwargs['UseExpcm']
        else:
            UseExpcm = UsesExpcm(dmf)

        # Create mdx object
        mdx = pymdx.Mdx(UseExpcm)


        # Set tones
        for c, ins in enumerate(dmf.Instruments):

            tone = self._ConvertInstrument_FM(ins)
            tone.ToneId = c
            mdx.Tones.append(tone)


        # Calculate the initial tempo
        tempo = CalcTempo(dmf.Module.Tick1)
        mdx.DataTracks[0].Add.Tempo_Bpm(tempo)


        if (UseExpcm):
            self.Channels = [Channel_Reader(chn) for chn in dmf.Module.Channels]
        else:
            self.Channels = [Channel_Reader(chn) for chn in dmf.Module.Channels[:9]]


        r = [chn.RowReader() for chn in self.Channels]
        for c, channel in enumerate(self.Channels):
            
            row = next(r[c])    # r[c].GetRow()


            if (row.Note is 0):
                pass

            elif (row.Note is 100): # not needed
                pass

            else:
                notereader = channel.RowReader()
                
                mdx.DataTracks[c].Add.Note(note, clocks)



            if (row.Note != 0):


            #if 

            
            rr = channel.RowReader()
            #while :



               # next(rr, None)







            
            

        for _ in range(dmf.Module.TOTAL_ROWS_PER_PATTERN):
            for channel in self.Channels:

                channel.next()



            data = mdx.DataTracks[i_chn]
            pattern = chn.Patterns[ptrnIndex]

            ptrnRepeats = _C_PatternRepeats(i, chn.PatternOrder)

                # Check fx

            for row in pattern.Rows:
                pass


        uxobj = UX_CompiledObj()
        uxobj.MdxObj = mdx

        return uxobj




    def _ConvertInstrument_FM(self, ins) -> pymdx.Tone :
        """..."""
        tone = pymdx.Tone()

        tone.Alg = ins.Data.Alg
        tone.Fb = ins.Data.Fb

        for op in range(4):
            tone.Op[op].Ar = ins.Data.Op[op].Ar
            tone.Op[op].Dr = ins.Data.Op[op].Dr
            tone.Op[op].Sl = ins.Data.Op[op].Sl
            tone.Op[op].Sr = ins.Data.Op[op].Sr
            tone.Op[op].Rr = ins.Data.Op[op].Rr

            tone.Op[op].Tl = ins.Data.Op[op].Tl

            tone.Op[op].Dt1 = ins.Data.Op[op].Dt1
            tone.Op[op].Dt2 = ins.Data.Op[op].Dt2

            tone.Op[op].Mult = ins.Data.Op[op].Mult

            tone.Op[op].Ks = ins.Data.Op[op].Ks

            tone.Op[op].Am_On = ins.Data.Op[op].Am_On

        return tone


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


    def RowReader(self, Channel: dmf_module._Channel, Seq_Index=None, Row_Index=None) -> dmf_module._Row:

        # uint8_t   seq_index;
        # uint8_t   row_index;

        # bool   position_jump;
        # bool   pattern_break;

        if (Seq_Index):
            seq_index = Seq_Index
        else:
            seq_index = 0

        if (Row_Index):
            pattern_break = True
            row_index = Row_Index
        else:
            pattern_break = False

        # Iterate through patterns in sequence order
        while (seq_index <= len(Channel.Sequence)):
            seq = Channel.Sequence[seq_index]

            position_jump = False
            for pattern in Channel.Patterns[seq]:

                if (position_jump): break
                if not (pattern_break): row = 0

                pattern_break = False
                while (row_index <= len(pattern.Rows)):
                    row = pattern.Rows[row_index]

                    if (position_jump or pattern_break): break

                    for fx in row.Fx:

                        if (fx.Code == 0x0B):
                            if (fx.Value > seq_index):
                                seq_index = fx.Value
                                position_jump = True

                        elif (fx.Code == 0x0D):
                            row_index = fx.Value
                            pattern_break = True
                        
                    yield row
                    row_index += 1

            seq_index += 1



    
    def Semantic(self, dmf: dmf_module.Dmf):

        # Set jump positions
        rr = [self.RowReader(channel) for channel in dmf.Module.Channels]

        l_channel = len(dmf.Module.Channels)
        for channel in dmf.Module.Channels:
            
            for seq in channel.Sequence:

                for pattern in channel.Patterns[seq]:

                    for i in range(l_channel):

                        row = next(rr, None)
                        
                        for fx in row.Fx:

                            if fx.Code == 1:
                                ""

        for i in rr:
            row = next(i, None)


            

        #dmf.Module.


        #except StopIteration



        return 






# pattern_tick = speed / hertz
# beat_duration = pattern_tick * amount_rows_for_beat (8)
# bpm = 60 / beat_duration

def CalcTempo(tickspeed, refresh=60):
    row_duration  = tickspeed / refresh
    beat_duration = row_duration * 8
    bpm = 60 / beat_duration
    return round(bpm)

def UsesExpcm(dmf):
    for channel in range(8, 12):
        for seq in channel.Sequence:
            for row in channel.Patterns[seq].Rows:
                if (row.Note != 0 and row.Octave != 0):
                    return True

                for fx in row.Fx:
                    if (fx.Code != -1 or fx.Value != -1):
                        return True
    return False



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
