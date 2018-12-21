from enum import Enum
import io


Channel = {
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 3,
    'E': 4,
    'F': 5,
    'G': 6,
    'H': 7,
}

class UXC_Mml:

    def __init__(self, path):

        io.open(path)

        open

        with open(self.Filepath, 'r') as f:
            pass


    def Compile(self, FData: io.TextIOBase, Arguments):
        self.Dat = FData
        self.SetCompilerOptions()

    def SetCompilerOptions(self):
        while self.Dat.tell() < len(self.Dat):
            Line = self.Dat.readline().split() # Read line + split and cut away all whitespaces
            if Line:    # If not empty
                if (Line[0][0] == '#'):
                    
                    Option = Line[1:].upper()
                    
                    if (Option is "TITLE"):
                        pass

                    elif (Option is "EXPCM"):
                        pass

                    elif (Option is "EXPDX"):
                        pass

                    elif (Option is "OCTAVE-REV"):
                        pass

                    elif (Option is "DETUNE"):
                        pass

                    elif (Option is "EXT-16"):
                        pass

                    elif (Option is "EXT-162"):
                       pass

                    elif (Option is "EXT-17"):
                       pass

                    elif (Option is "OPTIMIZE"):
                       pass

                    elif (Option is "CLOCK-COUNT"):
                       pass

                    elif (Option is "ASSIGN"):
                       pass

                    elif (Option is "INCLUDE"):
                       pass

                    elif (Option is "..."):
                       pass

                
                    # {
                    #     "TITLE": ,
                    #     "EXPCM": ,
                    #     "EXPDX": ,
                    #     "OCTAVE-REV": ,
                    #     "DETUNE": ,
                    #     "EXT-16": ,
                    #     "EXT-162": ,
                    #     "EXT-17": ,
                    #     "OPTIMIZE": ,
                    #     "CLOCK-COUNT": ,
                    #     "ASSIGN": , --> #ASSIGN A, CUSTOM_NAME
                    #     "INCLUDE": ,
                    # }


                #FData.readline()



