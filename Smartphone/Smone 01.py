import pathlib

import EoEfunc
import awsmfunc
import ccd
import havsfunc
import jvsfunc
import lvsfunc
import stgfunc
import vapoursynth
import vardefunc.aa
import vsutil
from lvsfunc.aa import nnedi3,based_aa
from vsutil import get_w, get_y

core = vapoursynth.core
fdog = vardefunc.mask.FDOG()

a = str(pathlib.Path(
    r"H:\Sanya Flies In The Night Sky [AnimeBytes]\[BDMV] In Another World with My Smartphone\異世界はスマートフォンとともに。 VOL1\ISESUMA_1\BDMV\STREAM\00001.m2ts").resolve())
nnedi3 = nnedi3(opencl=True)


def mmsize(clip, width=810, no_mask=False):
    clip32l = vsutil.get_y(clip)
    clip32l = vsutil.depth(clip32l, 32)

    bic_kern = lvsfunc.kernels.Bicubic()

    descale = bic_kern.descale(clip32l, get_w(width), width)
    upscale = bic_kern.scale(descale, 1920, 1080)
    if not no_mask:
        descale_mask = lvsfunc.scale.descale_detail_mask(clip32l, upscale, threshold=0.040)
    else:
        descale_mask = core.std.BlankClip(clip32l)
    rescale = lvsfunc.kernels.Bicubic(b=-1 / 2, c=1 / 4).scale(vardefunc.scale.nnedi3_upscale(descale, pscrn=1),
                                                               clip.width, clip.height)
    # rescale = vsutil.depth(rescale, 16)
    rescale = core.std.MaskedMerge(rescale, clip32l, descale_mask)
    rescale = vsutil.depth(rescale, 16)
    scaled = vardefunc.misc.merge_chroma(rescale, clip)
    return scaled, descale_mask


def jvs_dehalo(in_clip):  # Done initally by Julek. Deals with main haloing.
    # in_clip = vsutil.depth(in_clip, 16)
    aa = core.bilateral.Gaussian(in_clip, 1)
    i_aa = lvsfunc.aa.upscaled_sraa(aa, 1.1)
    mask = jvsfunc.dehalo_mask(i_aa, expand=1, iterations=0, brz=100)
    dehalo = havsfunc.FineDehalo(in_clip, rx=2, darkstr=1, brightstr=1)
    part_a = core.std.MaskedMerge(in_clip, dehalo, mask)
    return part_a, mask, i_aa


src = stgfunc.src(a)
src = vsutil.depth(src, 16)

# src.set_output(0)

ef = awsmfunc.bbmod(src, 2, 2, 2, 2, blur=20)  # meh, good enough
# stgfunc.output(ef)

# split into 3
pred = mmsize(ef[:3693], no_mask=True)
op = mmsize(ef[3693:3693 + 2157])
m = mmsize(ef[3693 + 2157:3693 + 2157 + 26039], no_mask=True)
ed = mmsize(ef[3693 + 2157 + 26039:])

desc = pred[0] + op[0] + m[0] + ed[0]
cm = pred[1] + op[1] + m[1] + ed[1]
stgfunc.output(src)
# stgfunc.output(desc)


def denoise(r_clip: vapoursynth.VideoNode, credit_mask: vapoursynth.VideoNode, *_):
    pred = r_clip[:3693]
    op = r_clip[3693:3693 + 2157]
    main = r_clip[3693 + 2157:3693 + 2157 + 26039]
    ed = r_clip[3693 + 2157 + 26039:]

    pred = EoEfunc.denoise.BM3D(pred, sigma=[1.7, 0], CUDA=True)
    main = EoEfunc.denoise.BM3D(main, sigma=[1.7, 0], CUDA=True)
    op = EoEfunc.denoise.BM3D(op, sigma=[2, 0], CUDA=True)
    ed = EoEfunc.denoise.BM3D(ed, sigma=[1.7, 0], CUDA=True)

    clip = pred + op + main + ed
    mask = fdog.get_mask(vsutil.get_y(clip))
    clip_ccd = ccd.ccd(clip)  # Cleans up chroma
    out_clip = core.std.MaskedMerge(clip_ccd, clip, mask)
    credit_mask = credit_mask.resize.Point(format=vapoursynth.GRAY16)
    out_clip = core.std.MaskedMerge(out_clip, clip, credit_mask)
    return out_clip, credit_mask


den, _ = denoise(desc, cm)
stgfunc.output(den)
den_lum = get_y(den)
lum_aa = based_aa(den_lum, eedi3_kwargs=dict(gamma=80))
ee = vardefunc.misc.merge_chroma(lum_aa, den)
# aa = vardefunc.aa.upscaled_sraa(den, singlerater=ee)
stgfunc.output(ee)
# awsmfunc.bbmod(src, 2, 2, 2, 2, blur=20)  # meh, good enough
# stgfunc.output(src)
# d_m = lvsfunc.mask.halo_mask(src)
# lum = vsutil.get_y(src)
# l_mask = lum.std.Sobel().std.Invert()
# mask = fdog.get_mask(vsutil.get_y(src)).std.Invert().std.Inflate()
# den = EoEfunc.denoise.BM3D(src, sigma=[2, 0], CUDA=True)
#
# preccd = core.std.MaskedMerge(src, den, mask)
#
# ccd_mask = fdog.get_mask(vsutil.get_y(preccd))
# clip_ccd = ccd.ccd(preccd)  # Cleans up chroma
# postccd = core.std.MaskedMerge(clip_ccd, preccd, mask)
# out_clip = postccd
#
# halo_mask = havsfunc.FineDehalo(out_clip, rx=0.5, darkstr=0.5, brightstr=0.5, contra=1, showmask=True)
#
# weak = lvsfunc.aa.nneedi3_clamp(postccd)
# sraa = upscaled_sraa(out_clip, rfactor=1.7)
#
# out_clip = core.std.MaskedMerge(sraa, out_clip, halo_mask)
#
# dehalo, mask, i_aa = jvs_dehalo(out_clip)
#
# # m = src.std.MaskedMerge(den, l_mask, planes=1)
# # m = kagefunc.hybriddenoise(src, 0.1, 1.5)  #
# # stgfunc.output(src)
#
# out_clip = kagefunc.adaptive_grain(out_clip, strength=0.3, )
# out_clip = vsutil.depth(out_clip, 10)
# # stgfunc.output()
# src.set_output(0)
# out_clip.set_output(1)
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
