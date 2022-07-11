import pathlib

import EoEfunc
import ccd
import debandshit
import havsfunc
import jvsfunc
import kagefunc
import lvsfunc
import stgfunc
import vapoursynth
import vardefunc.aa
import vsutil
from lvsfunc.aa import upscaled_sraa

core = vapoursynth.core
fdog = vardefunc.mask.FDOG()

a = str(pathlib.Path("raw/Luminous Witches - 02 (Amazon dAnime CBR 1080p).mkv").resolve())
b = str(pathlib.Path("raw/Luminous Witches - 02 (Amazon dAnime VBR 1080p).mkv").resolve())


def jvs_dehalo(in_clip):  # Done initally by Julek. Deals with main haloing.
    #in_clip = vsutil.depth(in_clip, 16)
    aa = core.bilateral.Gaussian(in_clip, 0.5)
    i_aa = lvsfunc.aa.upscaled_sraa(aa, 1.1)
    mask = jvsfunc.dehalo_mask(i_aa, expand=1, iterations=0, brz=100)
    dehalo = havsfunc.FineDehalo(in_clip, rx=2, darkstr=1, brightstr=1)
    part_a = core.std.MaskedMerge(in_clip, dehalo, mask)
    return part_a, mask, i_aa

def deband(clip: vapoursynth.VideoNode):
    # todo banding fixes. look at frame 12322 for why.
    clip_band = debandshit.dumb3kdb(clip, use_neo=True, threshold=28)
    mask = fdog.get_mask(clip)
    out_clip = core.std.MaskedMerge(clip_band, clip, mask)
    # clip = clip.text.Text("NoDeBand")
    return out_clip


def srcs():
    src = stgfunc.src(a)
    src_b = stgfunc.src(b)
    src = vsutil.depth(src, 16)
    src_b = vsutil.depth(src_b, 16)


    src_c = core.average.Mean([src, src_b])
    src_c = src_c.fmtc.resample(css="444")


    src = src_c
    amz_mean = src_c
    return amz_mean

def denoise(src_avg):
    mask_2 = jvsfunc.dehalo_mask(src_avg, expand=0, iterations=1, brz=100)

    mask_2 = mask_2.std.Invert().bilateral.Gaussian(0.5)

    den = EoEfunc.denoise.BM3D(src_avg, sigma=[4, 0], CUDA=True)

    return den, mask_2

def chroma(src_avg,src_den, den_mask):


    preccd = core.std.MaskedMerge(src_avg, src_den, den_mask)

    ccd_mask = fdog.get_mask(vsutil.get_y(preccd))
    clip_ccd = ccd.ccd(preccd, threshold=10)  # Cleans up chroma
    postccd = core.std.MaskedMerge(clip_ccd, preccd, ccd_mask)
    return postccd

src_avg = srcs()
o_clip,den_m = denoise(src_avg)
o_clip = chroma(src_avg,o_clip,den_m)
o_clip = deband(o_clip)

# todo: redo dehalo mask for aa clamping

halo_mask = havsfunc.FineDehalo(o_clip, rx=0.5, darkstr=0.5, brightstr=0.5, contra=1, showmask=True)



sraa = upscaled_sraa(o_clip, rfactor=1.7)

out_clip = core.std.MaskedMerge(sraa, o_clip, halo_mask)
dehalo, mask, i_aa = jvs_dehalo(out_clip)

# m = src.std.MaskedMerge(den, l_mask, planes=1)
# m = kagefunc.hybriddenoise(src, 0.1, 1.5)  #


out_clip = kagefunc.adaptive_grain(dehalo, strength=0.3, )
out_clip = vsutil.depth(out_clip, 10)

#stgfunc.output(src_avg)
out_clip = out_clip.fmtc.resample(css="420")
out_clip.set_output(0)


# Extra 02 tweaks lol

# freeze frames

#src.set_output(0)
#src.set_output(1)
#out_clip.set_output(0)
#
# from pathlib import Path
# import os
# from lvsfunc.render import find_scene_changes, SceneChangeMode
# out_path = Path(__file__).resolve()
# out_path = out_path.with_suffix('.qp')
#
# out_path.parent.mkdir(parents=True, exist_ok=True)
# #out_clip = run(src=True)[0]
# if os.path.isfile(out_path) is False:
#     with open(out_path, 'w') as o:
#         for f in find_scene_changes(src_b, mode=SceneChangeMode.WWXD_SCXVID_UNION):
#             o.write(f"{f} I -1\n")