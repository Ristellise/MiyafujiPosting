"""
Extremely cursed code for NCOP of Srike Witches.
"""
import debandshit
import fvsfunc
import kagefunc
import mvsfunc
import stgfunc
from vsgan import ESRGAN

from WitchCommon import *

core = vapoursynth.core
vapoursynth.core.num_threads = 8

def compute_pairs(a, b, foff):
    return f"[{a - foff} {b - foff}]"

black_frames = 11

src_clip = lvsfunc.misc.source("raw/Strike Witches/Witch NCOP.m2ts", )
#src_clip = src_clip.resize.Point(matrix_in_s='709', matrix_s='170m').std.SetFrameProp(prop="_Matrix", intval=1)
ivtc_clip = detelecine(src_clip)
ivtc_clip = ivtc_clip[132:]  # remove inital card
ivtc_clip = ivtc_clip[black_frames:]  # remove inital black frames
#ivtc_clip = ivtc_clip[:]  # remove inital black frames
stgfunc.output(ivtc_clip)
denoised_a = mvsfunc.BM3D(ivtc_clip, sigma=[2, 0.5])
dehalo, dehalo_mask, i_aa_o = jvs_dehalo(denoised_a)
dehalo_black, dehalo_black_mask = black_dehalo(dehalo, i_aa_o)
dehalo_f = fvsfunc.ReplaceFrames(dehalo_black, dehalo, mappings=compute_pairs(1047, 1060, black_frames))


def more_denoise(in_clip):
    denoised_a = mvsfunc.BM3D(in_clip, sigma=[4, 0])
    return denoised_a


dehalo_f = fvsfunc.ReplaceFrames(dehalo_f, more_denoise(dehalo_f), mappings=compute_pairs(1217, 1319, black_frames))

deband_m = lvsfunc.mask.detail_mask(dehalo_f, brz_a=0.02, brz_b=0.03)

deband_d1 = debandshit.dumb3kdb(dehalo_f, radius=21, threshold=25, use_neo=True)
deband_d2 = debandshit.dumb3kdb(dehalo_f, radius=21, threshold=80, use_neo=True)
deband_f1 = core.std.MaskedMerge(deband_d1, dehalo_f, deband_m)
deband_f1 = fvsfunc.ReplaceFrames(deband_f1, core.std.MaskedMerge(deband_d2, dehalo_f, deband_m),
                                  mappings=compute_pairs(1217, 1319, black_frames))
aa = lvsfunc.aa.upscaled_sraa(deband_f1, 1.3)
aa = mvsfunc.BM3D(aa, sigma=[2, 0])  # don't judge me
grainy = kagefunc.adaptive_grain(aa, 0.5)
grainy = vsutil.depth(grainy, 10)
stgfunc.output(aa)

lin_kern = lvsfunc.kernels.Bilinear()
bic_kern = lvsfunc.kernels.Bicubic()
cat_kern = lvsfunc.kernels.BicubicDidee()

width = 480



desc = cat_kern.descale(aa, vsutil.get_w(width), width)
stgfunc.output(desc)
desc.set_output(10)

#upsc = ESRGAN(YUV420toRGB(desc), device="cuda").\
#    load(r"../Utils/4x_NMKD-YandereNeo-F64B2_200k.pth").\
#    apply(overlap=16).clip
#stgfunc.output(upsc)

# if __name__ == '__vapoursynth__':
#     import os
#     from pathlib import Path
#
#     from lvsfunc.render import SceneChangeMode, find_scene_changes
#
#     out_path = Path(__file__).resolve()
#     out_path = out_path.with_name(f"{out_path.name}_qpfile").with_suffix(".txt")
#
#     out_path.parent.mkdir(parents=True, exist_ok=True)
#
#     if os.path.isfile(out_path) is False:
#         with open(out_path, 'w') as o:
#             for f in find_scene_changes(ivtc_clip, SceneChangeMode.WWXD_SCXVID_UNION):
#                 o.write(f"{f} I -1\n")
#