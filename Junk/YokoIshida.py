import EoEfunc
import havsfunc
import jvsfunc
import lvsfunc
import stgfunc
from vapoursynth import core
import ccd


def jvs_dehalo(in_clip):  # Done initally by Julek. Deals with main haloing.
    # in_clip = vsutil.depth(in_clip, 16)
    aa = core.bilateral.Gaussian(in_clip, 1)
    i_aa = lvsfunc.aa.upscaled_sraa(aa, 1.1)
    mask = jvsfunc.dehalo_mask(i_aa, expand=1, iterations=0, brz=100)
    dehalo = havsfunc.FineDehalo(in_clip, rx=2, darkstr=1, brightstr=1)
    part_a = core.std.MaskedMerge(in_clip, dehalo, mask)
    return part_a, mask, i_aa


src = stgfunc.src('raws\\石田燿子のテスト配信 [XJJjCrp8AZ4] (Fixd).mkv')
src = src.fmtc.resample(css="444")
stgfunc.output(src)
dehalo, m, aa = jvs_dehalo(src)
stgfunc.output(dehalo)
ccd_clean = ccd.ccd(dehalo, 20)
wat = EoEfunc.denoise.BM3D(ccd_clean, sigma=[0, 2], CUDA=True)
stgfunc.output(ccd_clean)
stgfunc.output(wat)
