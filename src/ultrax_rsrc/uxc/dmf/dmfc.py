
from os.path import basename as _basename

from . import dmf as dmfm
from . import routine1
from . import util as _util
from .. import uxc_util
from ... import pymdx


class UXC_Dmf:


    def __init__(self):
        pass

    def SetCompilerOptions(self, *Arguments):
        pass


    def Compile(self, Path, **Kwargs):

        #self.SetCompilerOptions(Arguments)

        ccntr = _util.Dmfc_Container()

        # Load and parse DefleMask module
        dmf = dmfm.Dmf()
        dmf.Load(Path)
        ccntr.DmfObj = dmf

        # Set PCM info
        pcminfo = _util.PcmInfo()
        pcminfo.Analyse(dmf)

        if ('UseExpcm' in Kwargs):
            ccntr.USES_EXPCM = Kwargs['UseExpcm']
        else:
            ccntr.USES_EXPCM = pcminfo.Uses_Expcm

        if (ccntr.USES_EXPCM):
            ccntr.AMOUNT_CHANNELS = 13
        else:
            ccntr.AMOUNT_CHANNELS = 9

        # Create mdx object
        mdx = pymdx.Mdx(ccntr.USES_EXPCM)
        ccntr.MdxObj = mdx

        # Set header data
        mdx.Header.Title = dmf.Header.SongName + " - " + dmf.Header.SongAuthor
        mdx.Header.PdxFilename = "outre.pdx"

        # Set tones
        for c, ins in enumerate(dmf.Instruments):
            tone = _util.Set_MDX_Tone(ins)
            tone.ToneId = c
            mdx.Tones.append(tone)

        # Set speed related variables
        ccntr.TIME_BASE = dmf.Module.TimeBase + 1
        if (dmf.Module.UseCustomHz):
            ccntr.REFRESH_RATE = dmf.Module.CustomHz
        else:
            if (dmf.Module.Framemode == 0):
                ccntr.REFRESH_RATE = 50
            elif (dmf.Module.Framemode == 1):
                ccntr.REFRESH_RATE = 60
            else:
                raise Exception

        # Prepare the container
        ccntr.InitList()


        routine1.Dmfc_Parser().Compiler(ccntr)

        uxobj = uxc_util.UX_CompiledObj()

        errors = False
        for channel in ccntr.Channels:
            if (channel.Errors != []):
                uxobj.Errors.append(channel.Errors)
                errors = True

        if not (errors):
            ccntr.Export()
            uxobj.MdxObj = ccntr.MdxObj


        #mdx.DataTracks[0].Add.Repeat_End()

        pcminfo.Uses_Pcm = False ######

        # PCM compiling
        if (pcminfo.Uses_Pcm):
            ccntr.MdxObj.Header.PdxFilename = _basename(Path).split('.')[0]
            pdx = pymdx.Pdx()

            for i, sample in enumerate(dmf.Samples):
                pdx.Banks[0].Samples[i].Rate = sample.Rate



                if sample.Bits == 8:
                    pdx.Banks[0].Samples[i].Encoding = pymdx._misc._encoding.SAMPLE_ENCODING.LPCM_8
                elif sample.Bits == 16:
                    pdx.Banks[0].Samples[i].Encoding = pymdx._misc._encoding.SAMPLE_ENCODING.LPCM_16
                else:
                    raise Exception

                pdx.Banks[0].Samples[i].EncodeTo = pymdx._misc._encoding.SAMPLE_ENCODING.ADPCM_OKI

                pdx.Banks[0].Samples[i].Data = sample.Data

            # errors / warnings

            uxobj.PdxObj = pdx


        return uxobj
