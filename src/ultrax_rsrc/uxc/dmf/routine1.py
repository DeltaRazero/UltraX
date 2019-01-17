
from .reader import Channel_Reader
from .reader import Pattern_Reader
from .reader import PORTA_TYPES as _PORTA_TYPES

from .. import locale
from ... import pymdx


#**********************************************************
#
#    Constants
#
#**********************************************************
#region

# Default: 6 ticks per row + 8 rows per beat
# 6*8 = 48 clocks per beat (default MXDRV behaviour)
TICKS_PER_ROW = 6
TICK_RATIO = TICKS_PER_ROW / 6
ROWS_PER_BEAT = 8

VALUES_STEREO = {
        0x10: 0b10,  0xF0: 0b10,
        0x11: 0b11,  0xFF: 0b11,
        0x01: 0b01,  0x0F: 0b01,
        0x00: 0b00
    }

EMPTY_FX_CMDS = [ [], [] ]

ENABLE_FX_0A = False



#**********************************************************

class Dmfc_Parser:
    Dmfc_Cntr = None

    CHANNEL_MASK = [1,1,1,1,1,1,1,1, 1,1,1,1,1]

#**********************************************************
#
#    Set general variables and settings
#
#**********************************************************
#region
    def Compiler(self, Dmfc_Cntr):

        self.Dmfc_Cntr = Dmfc_Cntr
        mod = Dmfc_Cntr.DmfObj.Module

        cr = [
            Channel_Reader(channel) for channel in 
                Dmfc_Cntr.DmfObj.Module.Channels[:Dmfc_Cntr.AMOUNT_CHANNELS]
        ]

        # Calculate the initial tempo
        tempo = CalcTempo(mod.Tick1, Dmfc_Cntr.REFRESH_RATE, Dmfc_Cntr.TIME_BASE)
        if (mod.Tick1 == mod.Tick2 - 1  or  mod.Tick1 == mod.Tick2 + 1):
            tempo = round((tempo + CalcTempo(mod.Tick2, Dmfc_Cntr.REFRESH_RATE, Dmfc_Cntr.TIME_BASE)) / 2)
        Dmfc_Cntr.MdxObj.DataTracks[0].Add.Tempo_Bpm(tempo)

        # Init channel settings
        for c, channel in enumerate(cr):

            chn_data = Dmfc_Cntr.Channels[c]

            # Tempo related
            channel.State.Tempo_Tick1 = mod.Tick1
            channel.State.Tempo_Tick2 = mod.Tick2
            channel.State.Tempo_BaseTime = Dmfc_Cntr.TIME_BASE
            channel.State.Tempo_RefreshRate = Dmfc_Cntr.REFRESH_RATE

            # Volume + Tone
            # FM channels
            if (c < 8):
                chn_data.Add(pymdx.command.Volume(0x80) ); channel.State.Volume = 0x7F
                chn_data.Add(pymdx.command.Tone(0) ); channel.State.Tone_Number = 0
                
            # Sample channels
            else:
                if (Dmfc_Cntr.USES_EXPCM):
                    chn_data.Add(pymdx.command.Tone(0) )
                chn_data.Add(pymdx.command.Volume(0x9D) ); channel.State.Volume = 0x7F
                
            channel.State.Tempo_Bpm = tempo

#endregion
#**********************************************************
#
#    Global module reading routine
#
#**********************************************************
#region
        # Set channel mask
        done = [False for _ in range(len(cr))]
        for i, mask in enumerate(self.CHANNEL_MASK):
            if mask is False: 
                done[i] = True

        # Set rest if first row empty
        for c, channel in enumerate(cr):
            row = channel.Pattern.Row
            chn_data = self.Dmfc_Cntr.Channels[c]
            if (row.Note == 0 and row.Octave == 0):
                chn_data.Add(pymdx.command.Rest(0) )
                channel.State.Note_Cmd = chn_data.Get(-1)

        # Main loop
        while not all(done):

            # Effects/commands
            #special_cmds = [ [], [] ]

            # Special commands
            # for c, channel in enumerate(cr):

            #     if (done[c]):
            #         continue

            #     row = channel.Pattern.Row

            #     for fx in row.Fx:
            #         if (fx.Value == 0x09  or  fx.Value == 0x0F):
            #             if (fx.Value == 0x09): mod.Tick1 = fx.Value
            #             if (fx.Value == 0x0F): mod.Tick2 = fx.Value
            #             tempo = round((tempo + CalcTempo(mod.Tick2, Dmfc_Cntr.REFRESH_RATE, Dmfc_Cntr.TIME_BASE)) / 2)
            #             Dmfc_Cntr.MdxObj.DataTracks[0].Add.Tempo_Bpm(tempo)


            # if tempo change
            #   if Porta not None / if channel.Porta
            #       readadjust porta shit

            # Row data parsing
            for c, channel in enumerate(cr):

                #print("channel {} : position {}, pattern {} : row {}".format(c+1, channel.Pattern.Position, channel.Pattern.PatternId, channel.Pattern.Position) )

                if (done[c]):
                    continue

                fx_cmds = self.Read_Fx(c, channel)
                self.Read_Note(c, channel, fx_cmds)


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
                    else:
                        Dmfc_Cntr.Channels[c].Advance()
                    
        
        # Cut off any notes, if active
        for c, channel in enumerate(cr):
            if (channel.State.Note_IsActive):
                Dmfc_Cntr.Channels[c].Add(pymdx.command.Rest(TICKS_PER_ROW) )

        return


#**********************************************************
#
#    Row reading : Vol, Ins, Fx
#
#**********************************************************
#region
    def Read_Fx(self, c, channel):
        """Handles vol, ins, fx commands."""
        
        #region Effects/commands
        fx_cmds = [ [], [] ]

        row = channel.Pattern.Row

        # Instrument column
        if not (row.Instr == -1):
            if (c < 8):
                if not (row.Instr is channel.State.Tone_Number):
                    fx_cmds[0].append(pymdx.command.Tone(row.Instr))
                    channel.State.Tone_Number = row.Instr

        # Volume column
        if not (row.Volume == -1):
            if not (row.Volume is channel.State.Volume):
                volume = (-(row.Volume - 0x7F)) + 0x80
                fx_cmds[0].append(pymdx.command.Volume(volume))
                channel.State.Volume = row.Volume

        # Set continious commands' state
        #noVolAdd = True

        # Read and parse FX columns
        for fx in row.Fx:
            # FX commands only for YM2151
            if (c < 8):

                # Volume 0Axy
                if (fx.Code == 0x0A  and  ENABLE_FX_0A):
                    noVolAdd = False

                    # Disable
                    if (fx.Value == 0x00):
                        channel.State.Vol_Add = None
                    else:
                        val_x = GetHexDigit(1, fx.Value)
                        val_y = GetHexDigit(0, fx.Value)
                        
                        if not (val_x != 0  and  val_y != 0):
                            if (val_x != 0):
                                channel.State.Vol_Add = val_x
                            else:
                                channel.State.Vol_Add = -val_y

                        multiplier = self.Dmfc_Cntr.REFRESH_RATE / 60
                        value = channel.Volume + round(channel.VolAdd * (TICKS_PER_ROW * channel.Tickspeed) * multiplier)
                        channel.VolAdd = value

                        if (0 <= channel.Volume <= 0x7F):
                            fx_cmds[0].append(CalcVolAdd(channel) )
                        

                    # vol = (channel.volume + value) * ticks
                    # add command
                    # channel.volume = vol
                    # 
                    # when reading row/fx
                    # if 0A = true
                    # if 0A command not in fx:
                    # repeat the volume commands above


                # Vibrato
                elif (fx.Code == 0x04):
                    if (fx.Value == 0x00 or fx.Value == -1):
                        if (channel.State.Vib_IsActive):
                            fx_cmds[0].append(pymdx.command.Lfo_Pitch_Disable() )
                            channel.State.Vib_Cmd = None
                            channel.State.Vib_IsActive = False
                    else:

                        if not (channel.State.Vib_IsActive):
                            fx_cmds[0].append(pymdx.command.Lfo_Pitch_Enable() )
                            channel.State.Vib_IsActive = True
                        fx_cmds[0].append(pymdx.command.Lfo_Pitch_Control(
                            # TODO: _cmd.py LFO commands should check if enum or int and convert to int if enum
                            2, #pymdx.command.LFO_WAVEFORM.TRIANGLE.value,
                            30, #GetHexDigit(1, fx.Value) * 1 * 3, # * mod_hz,
                            GetHexDigit(0, fx.Value) * 120
                        ))
                        channel.State.Vib_Cmd = fx_cmds[0][-1]

                        # Speed: Set the number of steps. Step number of LFO 1/4 period (the smaller, the faster)
                        # Depth: Units are 1/64 of semitone (= D1)

                # Stereo/pan
                elif (fx.Code == 0x08):
                    if (fx.Value in VALUES_STEREO):
                        value = VALUES_STEREO[fx.Value]
                        if not (value == channel.State.Pan_Cmd.Data):
                            fx_cmds[0].append(pymdx.command.Pan(value) )


                # Porta commands
                elif (fx.Code == 0x01  or  fx.Code == 0x02  or fx.Code == 0x03):    #   or  fx.Code == 0x03

                    # Disable any form of porta
                    if (fx.Value == 0  or  fx.Value == -1):
                        if (channel.State.Porta_IsActive):
                            fx_cmds[0].append(pymdx.command.Portamento(0))
                            channel.State.Porta_Reset()

                    else:
                        # TODO: The calculation is probably incorrect
                        mdx_hz = channel.State.Tempo_Bpm / 60
                        multiplier = self.Dmfc_Cntr.REFRESH_RATE / mdx_hz
                        #value = round(fx.Value * (TICKS_PER_ROW * channel.State.Tempo_Tick1 * channel.State.Tempo_BaseTime) * multiplier / TICK_RATIO)
                        value = round(fx.Value * (TICKS_PER_ROW * channel.State.Tempo_Tick1) * multiplier / TICK_RATIO)
                        value = pymdx._misc._util.Clamp(value, -32768, 32767)


                        # Porta up or Porta Down
                        # TODO: Cleanup
                        if (fx.Code == 0x01 or fx.Code == 0x02):

                            if (fx.Code == 0x01):
                                channel.State.Porta_Type = _PORTA_TYPES.PORTA_01
                            else:
                                channel.State.Porta_Type = _PORTA_TYPES.PORTA_02
                                value = -value

                            if not (channel.State.Porta_Cmd.Data == value):
                                fx_cmds[0].append(pymdx.command.Portamento(value))
                                channel.State.Porta_IsActive = True
                                channel.Porta_Cmd = fx_cmds[0][-1]

                            channel.State.Porta_IsTonePorta = False


                        elif (fx.Code == 0x03):
                            if (row.Note != -1):

                                channel.State.Porta_Type = _PORTA_TYPES.PORTA_03

                                inter = (row.Note + (12 * row.Octave) + 0x7D)

                                target = inter - 0x80
                                target *= 16384
                                #note += channel.Detune

                                channel.State.Porta_Current = (channel.State.Note_Cmd.Data - 0x80) * 16384

                                # Delete note value as its not going to be used in note on
                                # TODO: Make this better / more elegant
                                row.Note = 0
                                row.Octave = 0

                                # target = row.Note + (12 * row.Octave) - 0x80
                                # target *= 64

                                if (channel.State.Porta_Current != target):

                                    #portanote = channel.PortaCurrent + channel.Porta.Data * TICKS_PER_ROW

                                    channel.State.Porta_Target = target
                                    # If porta DOWN
                                    if (channel.State.Porta_Current > target):
                                        value = -value

                                    fx_cmds[0].append(pymdx.command.Portamento(value))
                                    channel.State.Porta_Cmd = fx_cmds[0][-1]


            # FX commands only for PCM/ADPCM
            else:
                # Stereo/pan
                if (fx.Code == 0x08):
                    # Correct value
                    # TODO: add volume support
                    value = 0x00
                    if (GetHexDigit(0, fx.Value) > 0): value |= 0x01
                    if (GetHexDigit(1, fx.Value) > 0): value |= 0x10

                    channel

                    fx_cmds[0].append(pymdx.command.Pan(VALUES_STEREO[value]) )


            # FX/Commands supported by all channels
            # Sample bank switch
            if (fx.Code == 0xEB):
                # TODO: value checking
                # TODO: only update for sample channels
                # TODO: dont update if same value(?)
                for chn in channel:
                    chn.SampleBank = fx.Value


        # Continious commands handling
        # if (channel.VolAdd  and  noVolAdd):
        #     if (channel.VolAdd < 0 < channel.Volume):
        #         fx_cmds[0].append(CalcVolAdd(channel) )

        #     elif (channel.VolAdd > 0  and  channel.Volume < 0x7F):
        #         fx_cmds[0].append(CalcVolAdd(channel) )

        if (channel.State.Porta_IsAdjusted):
            portanote = channel.State.Porta_Current + (channel.State.Porta_Cmd.Data * TICKS_PER_ROW)
            #channel.PortaNote = pymdx._misc._util.Clamp(portanote, 0, 32000)

            if (channel.State.Porta_IsAdjusted):

                #fx_cmds[0].append(pymdx.command.Legato() )
                fx_cmds[0].append(pymdx.command.Portamento(0))
                note = int(channel.PortaTarget / 16384) + 0x80
                fx_cmds[1].append(pymdx.command.Note(note, 0) )
                channel.State.Note_Cmd = fx_cmds[1][-1] ####

                channel.State.Porta_Reset()


            elif (channel.State.Porta_Type is _PORTA_TYPES.PORTA_03):
                portaup = channel.Porta.Data > 0
                # 0x03 cmd
                if (portaup and portanote > channel.State.Porta_Target) or (not portaup and portanote < channel.State.Porta_Target):
                    adjust = (channel.State.Porta_Target - channel.State.Porta_Current)
                    adjust = int(adjust / TICKS_PER_ROW)
                    adjust = pymdx._misc._util.Clamp(adjust, -32768, 32767)
                    fx_cmds[0].append(pymdx.command.Portamento(adjust)) ##
                    channel.State.Porta_Cmd = fx_cmds[0][-1]

                    channel.State.Porta_IsAdjusted = True


            else:
                channel.PortaCurrent += (channel.Porta.Data * TICKS_PER_ROW)


        return fx_cmds
#endregion


#**********************************************************
#
#    Row reading : Note
#    Command parsing
#
#**********************************************************
#region
    def Read_Note(self, c, channel, fx_cmds):
        """Handles Note actions."""

        row = channel.Pattern.Row
        chn_data = self.Dmfc_Cntr.Channels[c]

        uses_fx = fx_cmds != EMPTY_FX_CMDS
        
        # No note data
        if (row.Note == 0 and row.Octave == 0):

            # If FX/Commands present
            if (uses_fx):
                if (channel.State.Note_IsActive):
                    chn_data.Insert(-1, pymdx.command.Legato() ) # TODO: make this better, not use insert?
                    chn_data.Extend(fx_cmds[0])
                    if (fx_cmds[1] != []):
                        chn_data.Extend(fx_cmds[1])
                    elif (channel.State.Porta_IsAdjusted):
                        chn_data.Add(pymdx.command.Rest(0) )
                    else:
                        chn_data.Add(pymdx.command.Note(channel.State.Note_Cmd.Data, 0) )
                else:
                    chn_data.Extend(fx_cmds[0])
                    chn_data.Add(pymdx.command.Rest(0) )
                # Set reference to current Note/Rest
                channel.State.Note_Cmd = chn_data.Get(-1)

            # If sample channel
            # Sample channels dislike usage of legato command
            if (c > 7):
                if (channel.State.Note_Cmd.Clocks + TICKS_PER_ROW > 0xFF):
                    chn_data.Add(pymdx.command.Rest(0) )
                    channel.State.Note_Cmd = chn_data.Get(-1) ####
                    channel.State.Note_IsActive = False

            channel.State.Note_Cmd.Clocks += TICKS_PER_ROW


        # Note data
        else:

            if (channel.State.Porta_IsActive):

                if (channel.State.Porta_IsTonePorta):
                    chn_data.Add(pymdx.command.Portamento(0) )
                    channel.State.Porta_Reset()
                else:
                    porta = pymdx.command.Portamento(channel.State.Porta_Cmd.Data)
                    #channel.Porta = 
                    chn_data.Add(porta)

                

            if (uses_fx):
                chn_data.Extend(fx_cmds[0])

            # Note OFF
            if (row.Note == 100):
                if (channel.State.Note_IsActive or uses_fx):
                    chn_data.Add(pymdx.command.Rest(TICKS_PER_ROW) )
                    channel.State.Note_IsActive = False
                    channel.State.Note_Cmd = chn_data.Get(-1)
                # Note OFF when note already OFF
                else:
                    channel.State.Note_Cmd.Clocks += TICKS_PER_ROW

            # Note ON
            else:
                #note = row.Note + (12 * row.Octave) + 0x7D
                # FM channels
                if (c < 8):
                    note = row.Note + (12 * row.Octave) + 0x7D
                    if (note < 0x80):

                        self.Dmfc_Cntr.Channels[c].Errors.append(locale.JSON_DATA['error']['note_below'].format(
                            channel.Position, channel.Pattern.PatternId, channel.Pattern.Position
                        ))
                    else:
                        chn_data.Add(pymdx.command.Note(note, TICKS_PER_ROW) )

                # Sample channels
                else:
                    note = row.Note + (12 * channel.State.SampleBank) + 0x80
                    chn_data.Add(pymdx.command.Note(note, TICKS_PER_ROW) )

                channel.State.Note_IsActive = True
                channel.State.Note_Cmd = chn_data.Get(-1)

        return
#endregion



#**********************************************************
#
#    Utility methods
#
#**********************************************************
#region

# pattern_tick = speed / hertz
# beat_duration = pattern_tick * amount_rows_for_beat (8)
# bpm = 60 / beat_duration

def CalcTempo(tickspeed, refresh=60, basetime=1):
    row_duration  = tickspeed / refresh
    beat_duration = row_duration * ROWS_PER_BEAT
    bpm = 60 / beat_duration / basetime
    return round(bpm * TICK_RATIO)


# TODO: inaccurate calculation + not taking REFRESH_RATE into account
# TODO: have possibility to do addition/subtraction per clock instead of per row
def CalcVolAdd(channel):
    


    vol = (channel.Volume + channel.VolAdd) * channel.Tickspeed
    channel.Volume = pymdx._misc._util.Clamp(vol, 0, 0x7F)
    vol = (-(channel.Volume - 0x7F)) + 0x80
    return pymdx.command.Volume(vol)


# TODO: Make something better (this is way too pythonic and shitty)
def GetHexDigit(position, hex_var):
    var = "{0:0{1}x}".format(hex_var,2)[-position - 1]
    # TODO: code to control if position not too far
    return int("0x"+var, 0)

#endregion

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



# 0Axy:
#
# vol = (channel.volume + value) * ticks
# add command
# channel.volume = vol
# 
# when reading row/fx
# if 0A = true
# if 0A command not in fx:
# repeat the volume commands above

