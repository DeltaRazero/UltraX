"""Module description"""


# Clamp = lambda value, minv, maxv: max(min(value, maxv), minv)
def Clamp(value, minv, maxv):
    if (value < minv): return minv
    if (value > maxv): return maxv
    return value

# int.from_bytes(sample, byteorder='little', signed=True) * 256
def Convert_8to16(var):
    if type(var) is int:      return var * 256
    if type(var) is list:     return [byte * 256 for byte in var]

def Convert_16to8(var):
    if type(var) is int:      return round(var / 256)
    if type(var) is list:     return [round(byte / 256) for byte in var]
