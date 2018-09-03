

'''
    #---------------------------------------------------------------------#
    | Module Name: UltraX - Multi format MDX compiler
    | Author: DeltaRazero
    #---------------------------------------------------------------------#	
    | Python version: v3.5+ // Visual Studio Code 1.19.2
    | Script version: v1.0
    #---------------------------------------------------------------------#	
    | License: LGPL v3
    #---------------------------------------------------------------------#	
'''
import sys
from ultrax_rsrc import libMdx



mdxfile = libMdx.Mdx()


# for i in a_list:
#    mdxfile.Tones.append(i)



mdxfile.Data[1].append(6)


print (mdxfile.Data[1])