"""
Extremely cursed code for NCOP of Srike Witches.
"""
import EoEfunc
import ccd
import havsfunc
import jvsfunc
import lvsfunc
import stgfunc
import vapoursynth
import vsutil

from WitchFunc import wformat

core = vapoursynth.core
vapoursynth.core.num_threads = 8


def jvs_dehalo(in_clip):  # Done initally by Julek. Deals with main haloing.
    in_clip = vsutil.depth(in_clip, 16)
    aa = core.bilateral.Gaussian(in_clip, 0.5)
    i_aa = lvsfunc.aa.upscaled_sraa(aa, 1.1)
    mask = jvsfunc.dehalo_mask(i_aa, expand=1, iterations=0, brz=35)
    dehalo = havsfunc.FineDehalo(in_clip, rx=1, darkstr=0, brightstr=2)
    part_a = core.std.MaskedMerge(in_clip, dehalo, mask)
    return part_a, mask, i_aa


src_clip = stgfunc.src("visual.jpg")
src_clip = wformat.RGBtoYUV420(src_clip, out_depth=16)
denoise = EoEfunc.denoise.BM3D(src_clip, sigma=[10, 8], CUDA=True)
stgfunc.output(src_clip)
a, mas, i_aa = jvs_dehalo(denoise)
stgfunc.output(mas)
a = ccd.ccd(a,80)
stgfunc.output(a)
