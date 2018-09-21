

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



tone = pymdx.Tone()
tone.Alg = 7
tone.Op[0].Ar = 31
tone.Op[0].Dr = 15
tone.Op[0].Sl = 15
tone.Op[0].Rr = 15
tone.Op[0].Mult = 1
tone.Op[0].Tl = 0
e.Tones.append(tone)

e.DataTracks[0].Add.Tone(0)

e.DataTracks[0].Add.Repeat_Start(2)
e.DataTracks[0].Add.Note(0xAF, 48)
e.DataTracks[0].Add.Note(0xAF, 48)
e.DataTracks[0].Add.Note(0xAF, 48)
e.DataTracks[0].Add.Repeat_End()




exported = e.Export()
print (exported)

with open(r"D:\Programming\UltraX\temp\test.mdx", "wb") as f:
    f.write(exported)

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

