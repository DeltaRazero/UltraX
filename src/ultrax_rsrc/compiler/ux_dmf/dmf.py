
import io
import os
import struct
import zlib 

from enum import Enum



#************************************************
#
#   Utility classes
#
#************************************************

class _Custom_BytesIO(io.BytesIO):
    def __init__(self, args, *kwargs):
        io.BytesIO.__init__(self, args, kwargs)

    def read_bool(self):
        """Read 1 byte as bool"""
        return struct.unpack('?', self.read(1))[0]

    def readu(self, size=None, mode=None):
        """Read and unpack"""
        if mode == None:
            a = {1:'b', 2:'h', 4:'l',}[size]
        return struct.unpack(a, self.read(size))[0]



#************************************************
#
#   Header data classes
#
#************************************************

# Header data for in Dmf.Header
class _Header:
    def __init__(self):
        self.Version    = None
        self.System     = None
        self.SongName   = None
        self.SongAuthor = None

# Enum for available systems for in Header.System
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



#************************************************
#
#   Module data classes
#
#************************************************

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
        self.TOTAL_INSTRUMENTS         = None
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



#************************************************
#
#   Instrument data classes
#
#************************************************

# Base instrument class
class _Ins:
    def __init__(self):
        self.Name = None
        self.Mode = None
        self.Data = None

# FM instrument data class for in Ins.Data
class _Data_FM:
    def __init__(self):
        self.Alg  = None
        self.Fb   = None
        self.Lfo1 = None
        self.Lfo2 = None
        self.Op   = [_Data_FM_Op() for _ in range(4)]

# FM operator data class for in InsData_FM.Op[]
class _Data_FM_Op:
    def __init__(self):
        self.Am   = None # Amp mod
        self.Ar   = None
        self.Dr   = None # D1R
        self.Mult = None
        self.Rr   = None
        self.Sl   = None
        self.Tl   = None
        self.Dt2  = None
        self.Ks   = None
        self.Dt   = None
        self.Sr   = None  # D2R
        self.Sseg = None

# Lookup table for the parameters to read and store in order
_DFM_OP_ATTR_LIST = [
    'Am', 'Ar', 'Dr', 'Mult', 'Rr', 'Sl',
    'Tl', 'Dt2', 'Ks', 'Dt', 'Sr', 'Sseg'
    ]



#************************************************
#
#   .dmf module class
#
#************************************************

# Main class to read DefleMask .dmf file data from
class Dmf:
    """
    DefleMask .dmf file object.
    """
    global _DFM_OP_ATTR_LIST

    def __init__(self):
        self.Header = _Header()
        self.Module = _Module()
        self.Instruments = []

    def Load(self, path: str) -> None:
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

        if not os.path.exists(path):
            raise FileNotFoundError('File at path {} could not be found or opened.'.format(path))

        #if not self.IsValidModule(path):
        #    raise TypeError('File at path {} is not a supported version.'.format(path))

        with _Custom_BytesIO(zlib.decompress(open(path, 'rb').read()) ) as f:
            #f = io.BytesIO()
            f.seek(19)

            # Header data
            self.Header.SongName   = f.read( f.readu(1) ).decode()
            self.Header.SongAuthor = f.read( f.readu(1) ).decode()

            # Highlights, useless
            f.seek(2, 1)

            # Initial tempo data
            self.Module.TimeBase    = f.readu(1)
            self.Module.Tick1       = f.readu(1)
            self.Module.Tick2       = f.readu(1)
            self.Module.Framemode   = f.readu(1)
            self.Module.UseCustomHz = f.read_bool()
            self.Module.CustomHz    = f.readu(1)*100 + f.readu(1)*10 + f.readu(1)

            # Pattern structure data
            self.Module.TOTAL_ROWS_PER_PATTERN = f.readu(4)
            self.Module.TOTAL_ROWS_PATTERN_MATRIX = f.readu(1)

            # Pattern matrix data
            self.Module.PatternMatrix = [
                    [i for i in f.readu(self.Module.TOTAL_ROWS_PATTERN_MATRIX)]
                for _ in range(self.Module.SYSTEM_TOTAL_CHANNELS)
            ]

            # Instrument data
            for _ in range( f.readu(1) ):
                ins = _Ins()

                ins.Name = f.read( f.readu(1) ).decode()
                ins.Mode = f.readu(1)

                # If FM instrument
                if (ins.Mode == 1):
                    ins.Data = _Data_FM()

                    ins.Data.Alg  = f.readu(1)
                    ins.Data.Fb   = f.readu(1)
                    ins.Data.Lfo1 = f.readu(1)
                    ins.Data.Lfo2 = f.readu(1)

                    for i in range(4):
                        for j in range(12):
                            setattr(ins.Data.Op[i], _DFM_OP_ATTR_LIST[j], f.readu(1))

                self.Instruments.append(ins)

            # Pattern data
            for channelId in range(13):    # TODO: Hardcoded amount of channels (YM2151+SPCM mode only)
                
                channel = _Channel()
                channel.CHANNEL_EFFECT_COLLUMN_COUNT = f.readu(1)
                channel.PatternOrder = [pttrn for pttrn in self.Module.PatternMatrix[channelId]]

                for i in self.Module.TOTAL_ROWS_PATTERN_MATRIX:

                    patternId = channel.PatternOrder[i]

                    # If the pattern has not been parsed already
                    if not (patternId in channel.Patterns):

                        pattern = _Pattern()
                        pattern.Id = patternId

                        for _ in range(self.Module.TOTAL_ROWS_PER_PATTERN):
                            row = _Row()
                            row.Note = f.readu(2)
                            
                            row.Octave = f.readu(2)
                            if (row.Note == 0x0C):    # New octave at 'C'
                                row.Octave += 1

                            row.Volume = f.readu(2)

                            for _ in range(channel.CHANNEL_EFFECT_COLLUMN_COUNT):
                                fx = _Fx()
                                fx.Code  = f.readu(2)
                                fx.Value = f.readu(2)
                                row.Fx.append(fx)

                            row.Instr = f.readu(2)

                            pattern.Rows.append(row)
                        channel.Patterns[patternId] = pattern

                    else:
                        skip_amount = (8 + (4 * channel.CHANNEL_EFFECT_COLLUMN_COUNT)) * self.Module.TOTAL_ROWS_PER_PATTERN
                        f.seek(skip_amount, 1) # Skip amount of bytes
                
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
