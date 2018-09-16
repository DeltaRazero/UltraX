from .header import Header
from .moduleinfo import ModuleInfo

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




class Dmf:
    NotImplemented



def Import(path):
    with open(path, 'rb') as file:
        f = file.read()
    

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
