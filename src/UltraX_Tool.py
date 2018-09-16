
'''
    #---------------------------------------------------------------------#
    | Script Name: UltraX - Toolbox
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
UltraX, Toolbox\n\
-------------------------------\n\
Usage: py ultrax_tool.py [option] {arguments}\n\
    [filename]: Name of the input file\n\
Options:\n\
    S: Encode .wav file(s) to OKI ADPCM\n\
        --> py ultrax_tool.py S {sample1.wav} {sample2.wav} etc.\n\
        --> py ultrax_tool.py S {list1.txt} {list2.txt} etc.\n\
    -px: Set .dmf PCM mode to x (0 = OKI ADPCM (default), 1 = MercuryUnit)\n\
    ")

    parser.add_argument('option', action="store")
    parser.add_argument('-P', action="store", dest="P", type=int)
    parser.add_argument('-p', action="store", dest="p", type=int)

    
    #args = parser.parse_args(['filename', '-P1', '-c', '3'])   # Debugging
    #args = parser.parse_args()
    if (len(sys.argv) < 2):
        print(parser.description)

    #endregion


