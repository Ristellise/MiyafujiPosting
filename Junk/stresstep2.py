"""
Extremely cursed code for NCOP of Srike Witches.
"""
import EoEfunc
import havsfunc
import jvsfunc
import lvsfunc
import stgfunc
import vapoursynth
import vsutil

core = vapoursynth.core
vapoursynth.core.num_threads = 8


def RGBtoYUV420(clip):
    clip = clip.fmtc.matrix(mat="601", col_fam=vapoursynth.YUV, bits=16)
    # clip = clip.fmtc.resample(css="420")
    clip = clip.fmtc.bitdepth(bits=8)
    return clip


def jvs_dehalo(in_clip):  # Done initally by Julek. Deals with main haloing.
    in_clip = vsutil.depth(in_clip, 16)
    aa = core.bilateral.Gaussian(in_clip, 1)
    i_aa = lvsfunc.aa.upscaled_sraa(aa, 1.1)
    mask = jvsfunc.dehalo_mask(i_aa, expand=2, iterations=0, brz=75)
    dehalo = havsfunc.FineDehalo(in_clip, rx=2, darkstr=0, brightstr=2)
    part_a = core.std.MaskedMerge(in_clip, dehalo, mask)
    return part_a, mask, i_aa


src_clip = stgfunc.src("src_cleaner2-4x-AnimeSharp.png")
src_clip = RGBtoYUV420(src_clip)
src_clip = src_clip.fmtc.resample(w=1920, h=1080)
# a, mask, iass = jvs_dehalo(src_clip)
stgfunc.output(src_clip)
aa = lvsfunc.aa.upscaled_sraa(src_clip, 1.3)
mask = jvsfunc.dehalo_mask(aa, expand=2, iterations=0, brz=75)
stgfunc.output(aa)
dehalo = havsfunc.FineDehalo(aa, rx=2, darkstr=1, brightstr=1)
fanfiction = core.std.MaskedMerge(aa, dehalo, mask)
stgfunc.output(mask)
fanfiction = core.bilateral.Gaussian(fanfiction, 0.5)
stgfunc.output(fanfiction)