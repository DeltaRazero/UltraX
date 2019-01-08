#!/usr/bin/python3

# ---------------------------------------------------------
# UltraX - Object oriented MXDRV2 compiler
# ---------------------------------------------------------
# Program author(s):
#   * DeltaRazero 
# Program version:
#   v0.1
# Program UI:
#   Commandline / terminal
# ---------------------------------------------------------
# Python version:
#   v3.6+
# ----------------------------------------------------------
# License / disribution:
#   LGPL v3
# ---------------------------------------------------------


#**********************************************************


import argparse
import glob
import os
import sys

from ultrax_rsrc import uxc


#**********************************************************
#
#   Setable user variables
#
#**********************************************************

# Set the language. See ./ultrax_rsrc/Locale/ for the available languages.
# 言語を設定します。使用可能な言語について ./ultrax_rsrc/Locale/ を参照してください。
LANGUAGE   = 'eng'

# Enable debug mode. Will 
DEBUG_MODE = True


#**********************************************************


class UltraX():
    global DEBUG_MODE


    def __init__(self):
        self.C_MML = False
        self.C_DMF = False

        self.args  = None

        return


    # Set the absolute path of the input file 
    def SetPath(self, fp):
        # If a full path given
        if os.path.exists(fp):
            self.FilePath = fp
            self.DirPath = os.path.dirname(fp)
        # If filename only
        else:
            self.DirPath = os.path.realpath(__file__) # Current directory
            self.FilePath = os.path.join(self.DirPath, fp)
            
            # If no extension given
            if (os.path.splitext(self.FilePath)[1] == ''):
                self.FilePath = glob.glob(self.FilePath+".*")[0] # First file that matches in search

            if not os.path.exists(self.FilePath):
                return 0

        self.FileName = os.path.basename(self.FilePath).split('.')[0]

        return 1


    def ArgParser(self):
        parser = argparse.ArgumentParser(usage=uxc.locale.JSON_DATA['parser']['usage'])

        parser.add_argument('Filename', action="store", type=str)
        parser.add_argument('-F', action="store_true", dest="Force")
        parser.add_argument('-V', action="store_true", dest="Verbose")

        argc = len(sys.argv)
        if (argc < 2  and not DEBUG_MODE):
            print(parser.usage)
        else:
            self.args = parser.parse_args([r"D:\Programming\UltraX\src\outre.dmf"])

            if not self.SetPath(self.args.Filename):
                print(parser.usage)
                print(uxc.locale.JSON_DATA['error']['open_error'])
                return

            if (self.args.Filename[-4:].lower() in [".mml", ".txt"]  or  self.args.Force):
                self.C_MML = True

            if (self.args.Filename[-4:].lower() in [".dmf"]):
                self.C_DMF = True

        return


    # Main UltraX method
    def Run(self):
        self.ArgParser()

        if (self.C_MML  or  self.C_DMF):
            
            if self.C_MML:
                pass
                #mml = uxc.mml.Mml(self.Filepath)
                #obj = mml.Compile(self.args)
            elif self.C_DMF:
                dmfc = uxc.UXC_Dmf()
                obj = dmfc.Compile(self.FilePath)

            # Display errors and warnings
            for c, channel in enumerate(obj.Errors):
                print(uxc.locale.JSON_DATA['error']['error_channel'].format(c+1) )
                for error in channel:
                    print(error)

            # MDX export
            if not (obj.MdxObj is None):
                with open(os.path.join(self.DirPath, self.FileName + r".mdx"), 'wb') as f:
                    f.write(obj.MdxObj.Export())
            
            # PDX export
            if not (obj.PdxObj is None):
                with open(os.path.join(self.DirPath, self.FileName + r".pdx"), 'wb') as f:
                    f.write(obj.PdxObj.Export())

        return


#**********************************************************

# Main()
if __name__ == "__main__":
    uxc.locale.LoadJson(LANGUAGE)
    UltraX().Run()
