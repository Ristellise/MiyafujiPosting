"""
Strike Witches Common Functions
Hasshin Movie doesn't use it as it doesn't need to.
"""

import havsfunc
import jvsfunc
import lvsfunc.dehalo
import vapoursynth
import vsutil

def detelecine(clip: vapoursynth.VideoNode) -> vapoursynth.VideoNode:  # Thanks to Varde for the telecine block.
    clip = vsutil.depth(clip.vivtc.VFM(1), 16).nnedi3.nnedi3(1, nns=2, pscrn=1, combed_only=True)
    clip = clip.vivtc.VDecimate()
    clip = havsfunc.Vinverse(clip)
    return clip

def black_dehalo(in_clip, i_aa):  # Modified Julek to deal with really shit black halos/ringing.
    mask_black_2 = jvsfunc.dehalo_mask(i_aa, expand=7, iterations=0, brz=185)
    # Dehalo for darks
    dehalo_2 = havsfunc.EdgeCleaner(in_clip, strength=6)
    # yes, this is a warpsharp. I swear that I wish I will never have to do this again!
    dehalo_2 = havsfunc.YAHR(dehalo_2, blur=2, depth=80)
    dehalo_black = core.std.MaskedMerge(in_clip, dehalo_2, mask_black_2)
    return dehalo_black, mask_black_2