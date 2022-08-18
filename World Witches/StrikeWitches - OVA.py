import EoEfunc
import ccd
import lvsfunc
import stgfunc
import vapoursynth
import vsdehalo
import vsutil
from stgfunc import Grainer
from vsparsedvd import IsoFile, DGIndexNV


def detelecine(clip: vapoursynth.VideoNode, decimate=True, inverse=True,
               nns=2) -> vapoursynth.VideoNode:  # Thanks to Varde for the telecine block.
    clip = vsutil.depth(clip.vivtc.VFM(1), 16).nnedi3.nnedi3(1, nns=nns, pscrn=1, combed_only=True)
    if decimate:
        clip = clip.vivtc.VDecimate()
    if inverse:
        clip = lvsfunc.vinverse(clip)
    return clip


# Indexing with D2VWitch
witch = IsoFile(r"raw/KABA_2501.ISO")
# wo = witch.get_title(None, 1)
# stgfunc.output(wo)
ep, dvd_menu = witch.get_title(None, [(0, 35), -1])
# print(ep)

detelcine = detelecine(ep)
detelcine = detelcine.fmtc.resample(css="444")  # .std.Crop(0, 0, 0, 1)

den = EoEfunc.denoise.BM3D(detelcine, sigma=[4, 0], CUDA=True)

den = ccd.ccd(den, 20)
recons = lvsfunc.chroma_reconstruct(den, 4)
# meh = recons.eedi2cuda.AA2(mthresh=1, estr=0)  # .warp.AWarpSharp2(thresh=10,blur=0,depth=3)
deha = vsdehalo.fine_dehalo2(recons,radius=4)

deha2 = vsdehalo.dehalo_alpha(deha, darkstr=1, rx=2.0, brightstr=1, highsens=50, lowsens=30)
# deha2 = vsdehalo.(deha)

out_clip = stgfunc.adaptive_grain(deha,
                                  [0.3, 0.06], 0.95, 65, False, 10,
                                  Grainer.AddNoise, temporal_average=2)
out_clip = vsutil.depth(out_clip, 10)

# detelcine.set_output(0)

# stgfunc.output(detelcine)
# stgfunc.output(meh)
stgfunc.output(recons)
stgfunc.output(deha)
stgfunc.output(deha2)
# out_clip.set_output(0)

# stgfunc.output(recons)
# stgfunc.output(meh)
