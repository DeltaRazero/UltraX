

'''
    #---------------------------------------------------------------------#
    | Script Name: UltraX - Multi format MDX compiler
    | Author: DeltaRazero
    #---------------------------------------------------------------------#	
    | Python version: v3.5+ // Visual Studio Code 1.19.2
    | Script version: v0.1
    #---------------------------------------------------------------------#	
    | License: LGPL v3
    #---------------------------------------------------------------------#	
'''
import sys, argparse
from ultrax_rsrc import pymdx



if __name__ == "__main__":

    #region ||  Argparser  ||

    parser = argparse.ArgumentParser(description="\
UltraX, MDX compiler for MXDRV2\n\
-------------------------------\n\
Usage: py ultrax.py [filename] [] [] {option}\n\
    [filename]: Name of the input file\n\
Options:\n\
    -Px: Set .dmf PCM mode to x (0 = OKI ADPCM (default), 1 = MercuryUnit)"
    )

    parser.add_argument('filename', action="store")
    parser.add_argument('-P', action="store", dest="P", type=int)

    #args = parser.parse_args(['-a', '-bval', '-c', '3'])
    #args = parser.parse_args()
    if (len(sys.argv) < 2):
        print(parser.description)
    #endregion


    

# parser.add_argument('-at', action="store_true", default=False)
# parser.add_argument('-b', action="store", dest="baa")
# parser.add_argument('-c', action="store", dest="c", type=int)