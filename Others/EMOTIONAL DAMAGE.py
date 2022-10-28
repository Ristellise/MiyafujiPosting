import EoEfunc.denoise
import debandshit
import lvsfunc
import stgfunc
import vapoursynth
import vsutil
from stgfunc import Grainer


def detelecine(clip: vapoursynth.VideoNode, decimate=True, inverse=True,
               nns=2) -> vapoursynth.VideoNode:  # Thanks to Varde for the telecine block.
    clip = vsutil.depth(clip.vivtc.VFM(1), 16).nnedi3.nnedi3(1, nns=nns, pscrn=1, combed_only=True)
    if decimate:
        clip = clip.vivtc.VDecimate()
    if inverse:
        clip = lvsfunc.vinverse(clip)
    return clip


def src():
    return stgfunc.src("raw/MOYAI.m2ts")


def telecine(in_clip):
    return detelecine(in_clip, decimate=False)


def denoise(in_clip):
    return EoEfunc.denoise.BM3D(in_clip, [2, 0])


def deb(in_clip):
    return debandshit.dumb3kdb(in_clip, threshold=30, use_neo=True)


src_clip = src()
src_clip = detelecine(src_clip, decimate=False)
#stgfunc.output(src_clip)
den = denoise(src_clip)
debandf = deb(den)

out_clip = stgfunc.adaptive_grain(debandf,
                                  [0.2, 0.06], 0.95, 65, False, 10,
                                  Grainer.AddNoise, temporal_average=2)
out_clip = vsutil.depth(out_clip, 10)

#stgfunc.output(debandf)
#stgfunc.output(out_clip)

out_clip.set_output(0)
# src_clip.set_output(0)