
from ultrax_rsrc import pymdx

a = pymdx.Mdx()

tone = pymdx.Tone()
tone.Alg = 7
tone.Op[0].Ar = 31
tone.Op[0].Dr = 15
tone.Op[0].Sl = 15
tone.Op[0].Rr = 15
tone.Op[0].Mult = 1
tone.Op[0].Tl = 0

a.Tones.append(tone)

b = a.DataTracks[0]

b.Add.Tone(0)

b.Add.Tempo_Bpm(150)

# b.Add.Repeat_Start()

b.Add.Note(0xB0, 96)
b.Add.Note(0xBA, 96)
b.Add.LoopMark()
b.Add.Note(0xC0, 96)
b.Add.Note(0xCA, 96)
b.Add.Note(0xD0, 96)
# b.Add.Repeat_End(5)



exported = a.Export()

with open(r"D:\Programming\UltraX\src\test.mdx", "wb") as f:
    f.write(exported)

