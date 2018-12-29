
import io
from enum import Enum

from . import dmf as dmfm
from .. import uxc_util
from ... import pymdx

from .reader import Channel_Reader, Pattern_Reader


#rowtick = 0x18
rowtick = 0x06


class UXC_Dmf:


    VALUES_STEREO = {
        0x10: 0b01,  0xF0: 0b01,
        0x11: 0b11,  0xFF: 0b11,
        0x01: 0b10,  0x0F: 0b10,
        0x00: 0b00
    }

    EMPTY_FX_CMDS = [ [], [] ]




    global rowtick

    def __init__(self):
        pass


    def Compile(self, Path, **Kwargs):

        #self.SetCompilerOptions(Arguments)

        # Load and parse DefleMask module
        dmf = dmfm.Dmf()
        dmf.Load(Path)

        # argparse thing
        if ('UseExpcm' in Kwargs):
            UseExpcm = Kwargs['UseExpcm']
        else:
            UseExpcm = UsesExpcm(dmf)

        # Create mdx object
        mdx = pymdx.Mdx(UseExpcm)

        # Set header data
        mdx.Header.Title = dmf.Header.SongName + " - " + dmf.Header.SongAuthor

        # Set tones
        for c, ins in enumerate(dmf.Instruments):
            tone = self._ConvertInstrument_FM(ins)
            tone.ToneId = c
            mdx.Tones.append(tone)

        # Set speed related variables
        mod_tb = dmf.Module.TimeBase + 1

        if (dmf.Module.UseCustomHz):
            mod_hz = dmf.Module.CustomHz
        else:
            if (dmf.Module.Framemode == 0):
                mod_hz = 50
            elif (dmf.Module.Framemode == 1):
                mod_hz = 60
            else:
                raise Exception

        if (UseExpcm):
            amount_chn = 13
        else:
            amount_chn = 9

        cr = [Channel_Reader(channel) for channel in dmf.Module.Channels[:amount_chn]]


        # Calculate the initial tempo
        
        tempo = CalcTempo(dmf.Module.Tick1, mod_hz, mod_tb)
        #tempo = 240
        mdx.DataTracks[0].Add.Tempo_Bpm(tempo)

        # Init channel-pattern positions
        for c, channel in enumerate(cr):
            mdx.DataTracks[c].Add.Volume(0x80)
            channel.Volume = 0x7F
            channel.Bpm = tempo
            

        done = [False for _ in range(len(cr))]
        #done = [True for _ in range(len(cr))]
        #done[7] = False
        while not all(done):

            # Effects/commands
            special_cmds = [ [], [] ]

            # Special commands
            # for c, channel in enumerate(cr):

            #     if (done[c]):
            #         continue

            #     row = channel.Pattern.Row

            #     for fx in row.Fx:
            #     # FX commands only for YM2151
            #         if (fx.Code == )


            # if tempo change
            #   if Porta not None / if channel.Porta
            #       readadjust porta shit

            # actual parsing shit here
            for c, channel in enumerate(cr):

                #print("channel {} : position {}, pattern {} : row {}".format(c+1, channel.Pattern.Position, channel.Pattern.PatternId, channel.Pattern.Position) )

                #if (c==7 and channel.Pattern.PatternId==11 and channel.Pattern.Position==11):
                #    print("fuck off")

                if (done[c]):
                    continue

                #a = mdx.DataTracks[0].Add.Re
                #b = mdx.DataTracks[0].

                row = channel.Pattern.Row

                # Effects/commands
                fx_cmds = [ [], [] ]

                if not (row.Instr == -1):
                    if not (row.Instr is channel.Instrument):
                        fx_cmds[0].append(pymdx.command.Tone(row.Instr))
                        channel.Instrument = row.Instr

                if not (row.Volume == -1):
                    if not (row.Volume is channel.Volume):
                        volume = (-(row.Volume - 0x7F)) + 0x80
                        fx_cmds[0].append(pymdx.command.Volume(volume))
                        channel.Volume = row.Volume

                for fx in row.Fx:
                    # FX commands only for YM2151
                    if (c < 8):

                        # Vibrato
                        if (fx.Code == 0x04):
                            pass

                        # Stereo/pan
                        if (fx.Code == 0x08):
                            if (fx.Value in self.VALUES_STEREO):
                                fx_cmds[0].append(pymdx.command.Pan(self.VALUES_STEREO[fx.Value]))
                            else:
                                raise Exception

                        # Porta commands
                        elif (fx.Code == 0x01  or  fx.Code == 0x02  or  fx.Code == 0x03):

                            if (fx.Value == 0  or  fx.Value == -1):
                                channel.Porta = None
                                channel.PortaCount = 0

                            else:
                                # TODO: The calculation is probably incorrect
                                mdx_hz = channel.Bpm / 60
                                multiplier = mod_hz / mdx_hz
                                value = round(fx.Value * (rowtick * dmf.Module.Tick1) * multiplier)
                                value = pymdx._misc._util.Clamp(value, -32768, 32767)

                                # TODO: Note actions are a bit bugged with portas

                                # Porta up
                                if (fx.Code == 0x01):
                                    fx_cmds[0].append(pymdx.command.Portamento(value))

                                # Porta down
                                elif (fx.Code == 0x02):
                                    fx_cmds[0].append(pymdx.command.Portamento(-value))

                                #channel.Porta = fx_cmds[0][-1]
                                # Porta up
                                #elif (fx.Code == 0x03):
                                #    fx_cmds[0].append(pymdx.command.Portamento(fx.Value * multiplier))
                                #    fx_cmds[1].append(pymdx.command.Note(0x80, 0))
                                    # channel.new.portacounter()


                # Row Note actions
                # Empty
                if (row.Note == 0 and row.Octave == 0):
                    # If first row in module
                    if (channel.Note is None):
                        mdx.DataTracks[c].Extend(fx_cmds[0])
                        mdx.DataTracks[c].Add.Rest(rowtick)
                        channel.Note = mdx.DataTracks[c].Data[-1]
                    else:
                        if (fx_cmds != self.EMPTY_FX_CMDS):
                            if (channel.NoteActive):
                                mdx.DataTracks[c].Data.insert(-1, pymdx.command.Legato() ) # TODO: make this better, not use insert?
                                #mdx.DataTracks[c].Add.Legato()
                                mdx.DataTracks[c].Extend(fx_cmds[0])
                                if (fx_cmds[1] != []):
                                    mdx.DataTracks[c].Extend(fx_cmds[1])
                                else:
                                    mdx.DataTracks[c].Add.Note(channel.Note.Data, 0)
                            else:
                                mdx.DataTracks[c].Extend(fx_cmds[0])
                                mdx.DataTracks[c].Add.Rest(0)
                            # Set reference to current Note/Rest
                            channel.Note = mdx.DataTracks[c].Data[-1]

                        channel.Note.Clocks += rowtick
                        #print(channel.Note.Clocks)

                else:
                # Note OFF
                    if (row.Note == 100):
                        if (channel.NoteActive):
                            if (fx_cmds != []): mdx.DataTracks[c].Extend(fx_cmds[0])
                            mdx.DataTracks[c].Add.Rest(rowtick)
                            channel.NoteActive = False
                            channel.Note = mdx.DataTracks[c].Data[-1]
                        # Note OFF when note already OFF
                        else:
                            if not (channel.Note is None):
                                channel.Note.Clocks += rowtick
                # Note ON
                    else:
                        if (fx_cmds != []): mdx.DataTracks[c].Extend(fx_cmds[0])
                        note = row.Note + (12 * row.Octave) + 0x7D
                        mdx.DataTracks[c].Add.Note(note, rowtick)
                        channel.NoteActive = True
                        channel.Note = mdx.DataTracks[c].Data[-1]


            # Read next row into reader objects
            for c, channel in enumerate(cr):

                # Check whether channel is done
                if (done[c]):
                    continue

                pattern = channel.Pattern # Current pattern
                pattern.AdvanceRow()

                if (pattern.Row is None):
                    channel.AdvancePattern()
                    pattern = channel.Pattern # Current pattern
                    # If all patterns done/read
                    if (pattern is None):
                        done[c] = True
                        continue
                    
        
        # Cut off any notes, if active
        for c, channel in enumerate(cr):
            if (channel.NoteActive):
                mdx.DataTracks[c].Add.Rest(5)


        #mdx.DataTracks[0].Add.Repeat_End()


        # pdx = pymdx.Pdx()

        # for i, sample in enumerate(dmf.Samples):
        #     pdx.Banks[0].Samples[i].Rate = sample.Rate
        #     pdx.Banks[0].Samples[i].Data = sample.Data

        # pdx_exported = pdx.Export()


        uxobj = uxc_util.UX_CompiledObj()
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

            tone.Op[op].Dt1 = ins.Data.Op[op].Dt
            tone.Op[op].Dt2 = ins.Data.Op[op].Dt2

            tone.Op[op].Mult = ins.Data.Op[op].Mult

            tone.Op[op].Ks = ins.Data.Op[op].Ks

            tone.Op[op].Am_On = ins.Data.Op[op].Am

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








# pattern_tick = speed / hertz
# beat_duration = pattern_tick * amount_rows_for_beat (8)
# bpm = 60 / beat_duration

def CalcTempo(tickspeed, refresh=60, basetime=1):
    row_duration  = tickspeed / refresh
    beat_duration = row_duration * 8
    bpm = (60 / beat_duration) / basetime
    return round(bpm)

def UsesExpcm(dmf):
    for c in range(8, 12):
        for seq in dmf.Module.Channels[c].Sequence:
            for row in dmf.Module.Channels[c].Patterns[seq].Rows:
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
