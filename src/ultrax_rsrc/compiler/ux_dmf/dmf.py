#from .header import Header
#from .moduleinfo import ModuleInfo

import io
import struct
import zlib 

from enum import Enum

class SYSTEM(Enum):
    GENESIS         = 0x02
    GENESIS_EXT_CH3 = 0x12
    SMS             = 0x03
    GAMEBOY         = 0x04
    PCENGINE        = 0x05
    NES             = 0x06
    C64_SID_8580    = 0x07
    C64_SID_6581    = 0x17
    YM2151_SPCM     = 0x08







# Header data for in Dmf.Header
class _Header:
    def __init__(self):
        self.Version    = None
        self.System     = None
        self.SongName   = None
        self.SongAuthor = None

# Module data for in Dmf.Module
class _Module:
    def __init__(self):
        self.TimeBase = None
        self.Tick1    = None
        self.Tick2    = None

        self.Framemode   = None
        self.UseCustomHz = None
        self.CustomHz    = None

        self.TOTAL_ROWS_PER_PATTERN    = None
        self.TOTAL_ROWS_PATTERN_MATRIX = None
        self.SYSTEM_TOTAL_CHANNELS     = None

        self.PatternMatrix = []
        self.Channels      = []

# Channel sequence data class for in Module.Channels[]
class _Channel:
    def __init__(self):
        self.CHANNEL_EFFECT_COLLUMN_COUNT = None
        self.Patterns     = {}
        self.PatternOrder = []

# Pattern data class for in Channel.Patterns{}
class _Pattern:
    def __init__(self):
        self.CHANNEL_EFFECT_COLLUMN_COUNT = None
        self.Id   = None
        self.Rows = []

# Pattern data class for in Pattern.Rows[]
class _Row:
    def __init__(self):
        self.Note   = None
        self.Octave = None
        self.Volume = None
        self.Fx     = []
        self.Instr  = None

# Pattern data class for in Row.Fx[]
class _Fx:
    def __init__(self):
        self.Code  = None
        self.Value = None






# Main class to read DefleMask .dmf file data from
class Dmf:
    """
    DefleMask .dmf file object.
    """

    def __init__(self):
        # Init props
        self.Header = _Header()
        self.Module = _Module()
        self.Instruments = []

    def Load(self, path):
        """
        Read .dmf from disk and populate the current Dmf object with its content.
        
        Args:
            Path: full, absolute path to .dmf file on disk.

        Returns:
            Void.

        Raises:
            FileNotFoundError: when Load() cannot find the file with specified path.
            TypeError: when Load() opens a file which is not a valid .dmf file.
        """

        #self.CheckModule(path)

        with io.BytesIO(zlib.decompress(open(path, 'rb').read()) ) as f:
            #f = io.BytesIO()
            f.seek(19)

            # Header data
            self.Header.SongName   = f.read( f.read(1) ).decode()
            self.Header.SongAuthor = f.read( f.read(1) ).decode()

            # Highlights, useless
            f.seek(2, 1)

            # Initial tempo data
            self.Module.TimeBase    = f.read(1)
            self.Module.Tick1       = f.read(1)
            self.Module.Tick2       = f.read(1)
            self.Module.Framemode   = f.read(1)
            self.Module.UseCustomHz = bool( f.read(1) )
            self.Module.CustomHz    = f.read(1)*100 + f.read(1)*10 + f.read(1)

            # Pattern structure data
            self.Module.TOTAL_ROWS_PER_PATTERN = struct.unpack('l', f.read(4))[0]
            self.Module.TOTAL_ROWS_PATTERN_MATRIX = f.read(1)

            # Read pattern matrix data
                # for _ in range(self.Module.SYSTEM_TOTAL_CHANNELS):
                #     self.Module.PatternMatrix.append(
                #         [i for i in f.read(self.Module.TOTAL_ROWS_PATTERN_MATRIX)]
                #     )

            # Pattern matrix data
            self.Module.PatternMatrix = [
                    [i for i in f.read(self.Module.TOTAL_ROWS_PATTERN_MATRIX)]
                for _ in range(self.Module.SYSTEM_TOTAL_CHANNELS)
            ]

            # Instrument data
            #for _ in range( f.read(1) ):

            # Pattern data
            for channelId in range (13):    # TODO: Hardcoded amount of channels (YM2151+SPCM mode only)
                
                channel = _Channel()
                channel.CHANNEL_EFFECT_COLLUMN_COUNT = f.read(1)
                channel.PatternOrder = [pttrn for pttrn in self.Module.PatternMatrix[channelId]]

                for i in self.Module.TOTAL_ROWS_PATTERN_MATRIX:

                    patternId = channel.PatternOrder[i]

                    # If the pattern has not been parsed already
                    if not (patternId in channel.Patterns):

                        pattern = _Pattern()
                        pattern.Id = patternId

                        for _ in range(self.Module.TOTAL_ROWS_PER_PATTERN):
                            row = _Row()
                            row.Note = struct.unpack('h', f.read(2))[0]
                            
                            row.Octave = struct.unpack('h', f.read(2))[0]
                            if row.Note == 0x0C:    # New octave at 'C'
                                row.Octave += 1

                            row.Volume = struct.unpack('h', f.read(2))[0]

                            for _ in range(channel.CHANNEL_EFFECT_COLLUMN_COUNT):
                                fx = _Fx()
                                fx.Code  = struct.unpack('h', f.read(2))[0]
                                fx.Value = struct.unpack('h', f.read(2))[0]
                                row.Fx.append(fx)

                            row.Instr = struct.unpack('h', f.read(2))[0]

                            pattern.Rows.append(row)

                        channel.Patterns[patternId] = pattern

                    else:
                        skip_amount = (8 + (4 * channel.CHANNEL_EFFECT_COLLUMN_COUNT)) * self.Module.TOTAL_ROWS_PER_PATTERN
                        f.seek(skip_amount, 1)  # Skip amount of bytes
                
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
