"""
Strike Witches Common Functions
Hasshin Movie doesn't use it as it doesn't need to.
"""

import havsfunc
import jvsfunc
import lvsfunc.dehalo
import vapoursynth
from vapoursynth import core
import vsutil

def detelecine(clip: vapoursynth.VideoNode, decimate=True, inverse=True, nns=2) -> vapoursynth.VideoNode:  # Thanks to Varde for the telecine block.
    clip = vsutil.depth(clip.vivtc.VFM(1), 16).nnedi3.nnedi3(1, nns=nns, pscrn=1, combed_only=True)
    if decimate:
        clip = clip.vivtc.VDecimate()
    if inverse:
        clip = havsfunc.Vinverse(clip)
    return clip

def YUV420toRGB(clip):
    clip = clip.fmtc.resample(css="444")
    clip = clip.fmtc.matrix(mat="601", col_fam=vapoursynth.RGB)
    clip = clip.fmtc.bitdepth(bits=8)
    return clip

def RGBtoYUV420(clip):
    clip = clip.fmtc.matrix (mat="601", col_fam=vapoursynth.YUV, bits=16)
    clip = clip.fmtc.matrix(mat="601", col_fam=vapoursynth.RGB)
    clip = clip.fmtc.bitdepth(bits=8)
    return clip

def jvs_dehalo(in_clip):  # Done initally by Julek. Deals with main haloing.
    in_clip = vsutil.depth(in_clip, 16)
    aa = core.bilateral.Gaussian(in_clip, 1)
    i_aa = lvsfunc.aa.upscaled_sraa(aa, 1.1)
    mask = jvsfunc.dehalo_mask(i_aa, expand=5, iterations=0, brz=75)
    dehalo = havsfunc.FineDehalo(in_clip, rx=2, darkstr=0, brightstr=2)
    part_a = core.std.MaskedMerge(in_clip, dehalo, mask)
    return part_a, mask, i_aa


def black_dehalo(in_clip, i_aa):  # Modified Julek to deal with really shit black halos/ringing.
    mask_black_2 = jvsfunc.dehalo_mask(i_aa, expand=7, iterations=0, brz=185)
    # Dehalo for darks
    dehalo_2 = havsfunc.EdgeCleaner(in_clip, strength=6)
    # yes, this is a warpsharp. I swear that I wish I will never have to do this again!
    dehalo_2 = havsfunc.YAHR(dehalo_2, blur=2, depth=80)
    dehalo_black = core.std.MaskedMerge(in_clip, dehalo_2, mask_black_2)
    return dehalo_black, mask_black_2