

'''
    #---------------------------------------------------------------------#
    | Script Name: UltraX - Multi format MDX compiler
    | Author: DeltaRazero
    #---------------------------------------------------------------------#	
    | Python version: v3.5+ // Visual Studio Code 1.28.2
    | Script version: v0.1
    #---------------------------------------------------------------------#	
    | License: LGPL v3
    #---------------------------------------------------------------------#	
'''
import argparse
import glob
import io
import os
import sys

from ultrax_rsrc import uxc

#************************************************
#
#   Setable user variables
#
#************************************************

# Set the language. See ./ultrax_rsrc/Locale/ for the available languages.
# 言語を設定します。使用可能な言語について ./ultrax_rsrc/Locale/ を参照してください。
LANGUAGE   = 'eng'
DEBUG_MODE = True




# TODO:
"""
on topic: XPMCK style notation for definiitons. e.g. {6'3} unrolls to be {6 6 6}, {6:3} unrolls to {6 5 4 3}, {6:3}+3 unrolls to be {9 8 7 6} etc.
"""


#************************************************


class UltraX():
    #global locale   # Does it need to be a global variable to be used within this class?
    global DEBUG_MODE


    def __init__(self):
        self.C_MML = False
        self.C_DMF = False

        self.args  = None


    # Set the absolute path of the input file 
    def SetPath(self, Filename):
        if os.path.exists(Filename):   # If a full path given
            self.pFile = Filename
        else:
            self.pDir = os.path.realpath(__file__)    # Current directory
            
            self.pFile = os.path.join(self.pDir, Filename)
            
            if (os.path.splitext(self.pFile)[1] == ''):  # If no extension given
                self.pFile = glob.glob(self.pFile+".*")[0] # First file that matches in search

            if not os.path.exists(self.pFile):
                return 0

        return 1


    def Parser(self):
        parser = argparse.ArgumentParser(usage=uxc.locale.JSON_DATA['parser']['usage'])

        parser.add_argument('Filename', action="store", type=str)
        parser.add_argument('-F', action="store_true", dest="Force")
        parser.add_argument('-V', action="store_true", dest="Verbose")

        argc = len(sys.argv)
        if (argc < 2  and not DEBUG_MODE):
            print(parser.usage)
        else:
            self.args = parser.parse_args([r"D:\Programming\UltraX\src\Fukurou_no_Hikou_2.dmf"])

            if not self.SetPath(self.args.Filename):
                print(parser.usage)
                print(uxc.locale.JSON_DATA['error']['open_error'])
                return

            if (self.args.Filename[-4:].lower() in [".mml", ".txt"]  or  self.args.Force):
                self.C_MML = True

            if (self.args.Filename[-4:].lower() in [".dmf"]):
                self.C_DMF = True

        return


    # The main function to run the UltraX backend
    def Run(self):
        self.Parser()

        if (self.C_MML  or  self.C_DMF):
            
            if self.C_MML:
                pass
                #mml = uxc.mml.Mml(self.Filepath)
                #obj = mml.Compile(self.args)
            elif self.C_DMF:
                dmf = uxc.dmf.UXC_Dmf()
                obj = dmf.Compile(self.pFile)

            #with open(self.pDir+r"_out.mdx", 'wb') as f:
            with open(self.pFile+r"_out.mdx", 'wb') as f:
                f.write(obj.MdxObj.Export())


#************************************************

if __name__ == "__main__":
    uxc.locale.LoadJson(LANGUAGE)
    UltraX().Run()
