import pathlib

import EoEfunc
import ccd
import havsfunc
import jvsfunc
import kagefunc
import lvsfunc
import stgfunc
import vapoursynth
import vardefunc.aa
import vsutil
from lvsfunc.aa import nnedi3, upscaled_sraa

core = vapoursynth.core
fdog = vardefunc.mask.FDOG()

a = str(pathlib.Path(r"E:\Miyafuji-BDMV\Narumin\BDROM\BDMV\STREAM\00004.m2ts").resolve())
nnedi3 = nnedi3(opencl=True)


def jvs_dehalo(in_clip):  # Done initally by Julek. Deals with main haloing.
    #in_clip = vsutil.depth(in_clip, 16)
    aa = core.bilateral.Gaussian(in_clip, 1)
    i_aa = lvsfunc.aa.upscaled_sraa(aa, 1.1)
    mask = jvsfunc.dehalo_mask(i_aa, expand=1, iterations=0, brz=100)
    dehalo = havsfunc.FineDehalo(in_clip, rx=2, darkstr=1, brightstr=1)
    part_a = core.std.MaskedMerge(in_clip, dehalo, mask)
    return part_a, mask, i_aa


src = stgfunc.src(a)
src = vsutil.depth(src, 16)
# d_m = lvsfunc.mask.halo_mask(src)
lum = vsutil.get_y(src)
l_mask = lum.std.Sobel().std.Invert()
mask = fdog.get_mask(vsutil.get_y(src)).std.Invert().std.Inflate()
den = EoEfunc.denoise.BM3D(src, sigma=[2, 0], CUDA=True)

preccd = core.std.MaskedMerge(src, den, mask)

ccd_mask = fdog.get_mask(vsutil.get_y(preccd))
clip_ccd = ccd.ccd(preccd)  # Cleans up chroma
postccd = core.std.MaskedMerge(clip_ccd, preccd, mask)
out_clip = postccd

halo_mask = havsfunc.FineDehalo(out_clip, rx=0.5, darkstr=0.5, brightstr=0.5, contra=1, showmask=True)

weak = lvsfunc.aa.nneedi3_clamp(postccd)
sraa = upscaled_sraa(out_clip, rfactor=1.7)

out_clip = core.std.MaskedMerge(sraa, out_clip, halo_mask)

dehalo, mask, i_aa = jvs_dehalo(out_clip)

# m = src.std.MaskedMerge(den, l_mask, planes=1)
# m = kagefunc.hybriddenoise(src, 0.1, 1.5)  #
# stgfunc.output(src)

out_clip = kagefunc.adaptive_grain(out_clip, strength=0.3, )
out_clip = vsutil.depth(out_clip, 10)
# stgfunc.output()
src.set_output(0)
out_clip.set_output(1)
# from pathlib import Path
# import os
# from lvsfunc.render import find_scene_changes,SceneChangeMode
# out_path = Path(__file__).resolve()
# out_path = out_path.with_name(f"{out_path.stem}_qpfile").with_suffix(".txt")
#
# out_path.parent.mkdir(parents=True, exist_ok=True)
# #out_clip = run(src=True)[0]
# if os.path.isfile(out_path) is False:
#     with open(out_path, 'w') as o:
#         for f in find_scene_changes(src, mode=SceneChangeMode.WWXD_SCXVID_UNION):
#             o.write(f"{f} I -1\n")