import vsutil
import lvsfunc
import jvsfunc
import havsfunc
from vapoursynth import core
from . import wformat
def witch_dehalo1(
        in_clip,
        gaussian_blur=1,
        sraa=1.1,
        **kwargs
        ):  # Done initally by Julek. Deals with main haloing.
    aa = core.bilateral.Gaussian(in_clip, gaussian_blur)
    i_aa = lvsfunc.aa.upscaled_sraa(aa, sraa)
    mask = jvsfunc.dehalo_mask(
        i_aa,
        expand=kwargs.get("mask_expand",5),
        iterations=kwargs.get("mask_iterations",0),
        brz=kwargs.get("mask_brz",75))

    dehalo = havsfunc.FineDehalo(
        in_clip,
        rx=kwargs.get("dehalo_rx",2), 
        darkstr=kwargs.get("dehalo_darkstr",0), 
        brightstr=kwargs.get("dehalo_darkstr",2))

    part_a = core.std.MaskedMerge(in_clip, dehalo, mask)
    return part_a, mask, i_aa

