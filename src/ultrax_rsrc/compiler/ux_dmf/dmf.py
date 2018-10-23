#from .header import Header
#from .moduleinfo import ModuleInfo

import io
import struct
import zlib 

from enum import Enum

class SYSTEM(Enum):
    GENESIS = 0x02
    GENESIS_EXT_CH3 = 0x12
    SMS = 0x03
    GAMEBOY = 0x04
    PCENGINE = 0x05
    NES = 0x06
    C64_SID_8580 = 0x07
    C64_SID_6581 = 0x17
    YM2151_SPCM = 0x08


class Header:
    def __init__(self):
        self.Version = None
        self.System = None
        self.SongName = None
        self.SongAuthor = None


class Module:
    def __init__(self):
        self.TimeBase = None
        self.Tick1 = None
        self.Tick2 = None

        self.Framemode = None
        self.UseCustomHz = None
        self.CustomHz = None

        self.TOTAL_ROWS_PER_PATTERN = None
        self.TOTAL_ROWS_PATTERN_MATRIX = None
        self.SYSTEM_TOTAL_CHANNELS = None

        self.PatternMatrix = []
        self.Channels = []


class Channel:
    def __init__(self):
        self.CHANNEL_EFFECT_COLLUMN_COUNT = None
        self.Patterns = {}
        self.PatternOrder = []


class Pattern:
    def __init__(self):
        self.CHANNEL_EFFECT_COLLUMN_COUNT = None
        self.Id = None
        self.Rows = []


class Row:
    def __init__(self):
        self.Note = None
        self.Octave = None
        self.Volume = None
        self.Fx = []
        self.Instrument = None


class Fx:
    def __init__(self):
        self.Code = None
        self.Value = None







class Dmf:

    def __init__(self):
        # Init props
        self.Header = Header()
        self.Module = Module()
        self.Instruments = []

    def Load(self, path):
        #self.CheckModule(path)

        with io.BytesIO(zlib.decompress(open(path, 'rb').read()) ) as f:
            #f = io.BytesIO()
            f.seek(19)

            self.Header.SongName   = f.read( f.read(1) ).decode()
            self.Header.SongAuthor = f.read( f.read(1) ).decode()

            # Highlights, useless
            f.seek(2, 1)

            # Custom Hz, TODO
            f.read(3)

            self.Module.TOTAL_ROWS_PER_PATTERN = f.read(4)
            self.Module.TOTAL_ROWS_PATTERN_MATRIX = f.read(1)

            # Read pattern matrix data
                # for _ in range(self.Module.SYSTEM_TOTAL_CHANNELS):
                #     self.Module.PatternMatrix.append(
                #         [i for i in f.read(self.Module.TOTAL_ROWS_PATTERN_MATRIX)]
                #     )

            self.Module.PatternMatrix = [
                    [i for i in f.read(self.Module.TOTAL_ROWS_PATTERN_MATRIX)]
                for _ in range(self.Module.SYSTEM_TOTAL_CHANNELS)
            ]

            #for _ in range( f.read(1) ):

            # Pattern data
            for channelId in range (13):    # TODO: Hardcoded amount of channels (YM2151+SPCM mode only)
                
                channel = Channel()
                channel.CHANNEL_EFFECT_COLLUMN_COUNT = f.read(1)
                channel.PatternOrder = [i for i in self.Module.PatternMatrix[channelId]]

                for i in self.Module.TOTAL_ROWS_PATTERN_MATRIX:

                    patternId = channel.PatternOrder[i]

                    if not (patternId in channel.Patterns):

                        pattern = Pattern()
                        pattern.Id = patternId

                        for _ in range(self.Module.TOTAL_ROWS_PER_PATTERN):
                            row = Row()
                            row.Note = f.read(2)
                            row.Octave = f.read(2)
                            row.Volume = f.read(2)

                            for _ in range(channel.CHANNEL_EFFECT_COLLUMN_COUNT):
                                fx = Fx()
                                fx.Code  = f.read(2)
                                fx.Value = f.read(2)
                                row.Fx.append(fx)

                            row.Instrument = f.read(2)

                            pattern.Rows.append(row)

                        channel.Patterns[patternId] = pattern

                    else:
                        skip = (8 + (4 * channel.CHANNEL_EFFECT_COLLUMN_COUNT)) * self.Module.TOTAL_ROWS_PER_PATTERN
                        f.seek(skip, 1)  # Skip amount of bytes
                
                self.Module.Channels.append(channel)

        return

    

    # def CheckModule(self, path):
    #     with io.BytesIO(open(path, 'rb').read(18)) as f:
    #         # Check format and version
    #         if not (f.read(16) == b".DelekDefleMask."):
    #             FileNotFoundError("File not DMF")
    #         if not (f.read(1) >= 0x18):
    #             FileNotFoundError("File not correct version")

    #         # System
    #         if not (f.read(1) == SYSTEM.YM2151_SPCM):
    #             FileNotFoundError("File not using correct mode")

    #     return
        




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
