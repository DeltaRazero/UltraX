

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




e = pymdx.Mdx()

tonetest = pymdx.Tone()
tonetest.Alg = 5
e.Tones.append(tonetest)



e.DataTracks[1].Add.Note(0x99, 400)
e.DataTracks[1].Add.Note(0x99, 200)
e.DataTracks[1].Add.Note(0x99, 257)


exported = e.Export()
print (exported)
#print (exported[len(exported)-1])


if __name__ == "__main__":

    #region ||  Argparser  ||

    parser = argparse.ArgumentParser(description="\
UltraX, MDX compiler for MXDRV2\n\
-------------------------------\n\
Usage: py ultrax.py [filename] [] [] {option}\n\
    [filename]: Name of the input file\n\
Options:\n\
    -Px: Force MML PCM mode to x (0 = OKI ADPCM only (default), 1 = MercuryUnit only)\n\
    -px: Set .dmf PCM mode to x (0 = OKI ADPCM (default), 1 = MercuryUnit)\n\
    ")

    parser.add_argument('filename', action="store")
    parser.add_argument('-P', action="store", dest="P", type=int)
    parser.add_argument('-p', action="store", dest="p", type=int)

    
    #args = parser.parse_args(['filename', '-P1', '-c', '3'])   # Debugging
    #args = parser.parse_args()
    if (len(sys.argv) < 2):
        print(parser.description)

    #endregion

