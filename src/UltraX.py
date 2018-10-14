

'''
    #---------------------------------------------------------------------#
    | Script Name: UltraX - Multi format MDX compiler
    | Author: DeltaRazero
    #---------------------------------------------------------------------#	
    | Python version: v3.5+ // Visual Studio Code 1.27.2
    | Script version: v0.1
    #---------------------------------------------------------------------#	
    | License: LGPL v3
    #---------------------------------------------------------------------#	
'''
import\
    sys,        \
    argparse,   \
    glob

from ultrax_rsrc import *


Language = 'eng'


#import ultrax_rsrc



# TODO:
"""
on topic: XPMCK style notation for definiitons. e.g. {6'3} unrolls to be {6 6 6}, {6:3} unrolls to {6 5 4 3}, {6:3}+3 unrolls to be {9 8 7 6} etc.




"""

C_MML = False
C_DMF = False




e = pymdx.Mdx(False)
e.Header.PdxFilename = 'BR_ADP'
#e.Header.PdxFilename = 'GR_PCM'



tone = pymdx.Tone()
tone.Alg = 7
tone.Op[0].Ar = 31
tone.Op[0].Dr = 14
tone.Op[0].Sl = 15
tone.Op[0].Rr = 15
tone.Op[0].Mult = 1
tone.Op[0].Tl = 0
e.Tones.append(tone)



b = e.DataTracks

for track in b:
    track.Add.Tone(0)
    track.Add.Volume(0x7f)
e.DataTracks[0].Add.Expcm_Enable()


b[0].Add.Tempo_Bpm(120)
b[0].Add.LoopMark()
b[0].Add.Note(0xC0, 48)
b[0].Add.Note(0xC0, 48)
b[0].Add.Note(0xC0, 48)
b[0].Add.Note(0xC0, 48)


print (b[0].Add._lmc)

channel = 8



exported = e.Export()
print (exported)

with open(r"D:\Programming\UltraX\temp\test.mdx", "wb") as f:
    f.write(exported)

#print (exported[len(exported)-1])



CMDLINE_USAGE = "\
UltraX, MDX compiler for MXDRV2\n\
-------------------------------\n\
Usage: python ultrax.py [filename] [] [] {option}\n\
    [filename]: Name of the input file\n\
Options:\n\
    -F: Force MML compiling\n\
"





class UltraX():
    global CMDLINE_USAGE
    global Language

    def __init__(self):
        self.C_MML = False
        self.C_DMF = False

        self.LangJson = lang.LoadJson(Language)


    # Set the absolute path of the input file 
    def SetPath(self, Filename):
        if os.path.exists(Filename):   # If a full path given
            self.Filepath = Filename
        else:
            dirpath = os.path.realpath(__file__)    # Path in current directory
            
            self.Filepath = os.path.join(dirpath, Filename)
            
            if (os.path.splitext(self.Filepath)[1] == ''):  # If no extension given
                self.Filename = glob.glob(self.Filepath)[0] # First file that matches in search

            if not os.path.exists(self.Filepath):
                return 0

        return 1


    def Parser(self):
        parser = argparse.ArgumentParser(usage=self.LangJson['parser']['description'])

        parser.add_argument('Filename', action="store", type=str)
        parser.add_argument('-F', action="store_true", dest="F")

        argc = len(sys.argv)
        if (argc < 2):
            print(parser.usage)
        else:
            args = parser.parse_args()

            if not self.SetPath(args.Filename):
                print(parser.usage)
                print("\n Error opening file.")
                return

            if (args.filename[-4:].lower() in [".mml", ".txt"]  or  args.F):
                self.C_MML = True

            if (args.filename[-4:].lower() in [".dmf"]):
                self.C_DMF = True

        return


    def Run(self):
        self.Parser()

        if (self.C_MML  or  self.C_DMF):
            if self.C_MML:
                pass
            if self.C_DMF
                pass






if __name__ == "__main__":
    UltraX().Run()
