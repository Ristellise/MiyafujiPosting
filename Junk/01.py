import havsfunc
import lvsfunc.render
import vapoursynth
import vsutil


def deinterlace(clip: vapoursynth.VideoNode) -> vapoursynth.VideoNode:  # Varde.
    clip = vsutil.depth(clip.vivtc.VFM(1), 16).nnedi3.nnedi3(1, nns=2, pscrn=1, combed_only=True)
    clip = clip.vivtc.VDecimate()
    clip = havsfunc.Vinverse(clip)
    return clip


src_clip = lvsfunc.misc.source("raw/Witch 01.m2ts")
ivtc_clip = deinterlace(src_clip)

h_mask = lvsfunc.mask.halo_mask(ivtc_clip, rad=2,)
# src_clip.set_output(0)
ivtc_clip.set_output(0)
h_mask.set_output(1)
