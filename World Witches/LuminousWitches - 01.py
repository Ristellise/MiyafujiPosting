import EoEfunc
import ccd
import debandshit
import jvsfunc
import lvsfunc
import stgfunc
import vapoursynth
import vardefunc.aa
import vsdehalo
import vsmask.edge
import vsutil
from stgfunc import Grainer

import shynonon

core = vapoursynth.core
witty = vsmask.edge.FDoGTCanny()
fdog = vardefunc.mask.FDOG()


def jvs_dehalo(in_clip):  # Done initally by Julek. Deals with main haloing.
    # in_clip = vsutil.depth(in_clip, 16)
    aa = core.bilateral.Gaussian(in_clip, 0.5)
    i_aa = lvsfunc.aa.upscaled_sraa(aa, 1.1)
    mask = jvsfunc.dehalo_mask(i_aa, expand=1, iterations=0, brz=100)
    dehalo = vsdehalo.fine_dehalo(in_clip, rx=2, darkstr=1, brightstr=1)
    part_a = core.std.MaskedMerge(in_clip, dehalo, mask)
    return part_a, mask, i_aa


def deband(clip: vapoursynth.VideoNode):
    # todo banding fixes. look at frame 12322 for why.
    clip_band = debandshit.dumb3kdb(clip, use_neo=True, threshold=28)
    mask = witty.edgemask(vsutil.get_y(clip))
    out_clip = core.std.MaskedMerge(clip_band, clip, mask)
    # clip = clip.text.Text("NoDeBand")
    return out_clip


def srcs():
    return shynonon.srcs("raw/Luminous Witches - 01 (Amazon dAnime VBR 1080p).mkv",
                         "raw/Luminous Witches - 01 (Amazon dAnime CBR 1080p).mkv")


def denoise(src_clip):
    # mask_2 = jvsfunc.dehalo_mask(src_avg, expand=0, iterations=0, brz=220)
    sc = shynonon.scale
    mask_2 = witty.edgemask(vsutil.get_y(src_clip), lthr=sc(src_clip, .8),
                            hthr=sc(src_clip, .9)).std.Deflate().std.Deflate().std.Deflate().std.Deflate().std.Invert()

    den = EoEfunc.denoise.BM3D(src_clip, sigma=[4, 0], CUDA=True)
    src_den = core.std.MaskedMerge(src_clip, den, mask_2)
    return src_den, mask_2


def chroma(src_den):
    ccd_mask = witty.edgemask(vsutil.get_y(src_den))
    clip_ccd = ccd.ccd(src_den, threshold=10)  # Cleans up chroma
    postccd = core.std.MaskedMerge(clip_ccd, src_den, ccd_mask)
    return postccd


def aa(src_clip):
    sc = shynonon.scale
    det = lvsfunc.detail_mask(src_clip, rad=0, brz_a=1, brz_b=1)
    halo_mask = witty.edgemask(vsutil.get_y(src_clip), sc(src_clip, 0.5))
    #halo_mask = witty.edgemask(vsutil.get_y(src_clip)[20505:20540], sc(src_clip, 0.3))
    # halo_mask = havsfunc.FineDehalo(src_clip, rx=0.5, darkstr=0.5, brightstr=0.5, contra=1, showmask=True)
    sraa2 = core.eedi2cuda.AA2(src_clip)
    aa2 = core.std.MaskedMerge(src_clip, sraa2, halo_mask)
    stgfunc.output(det)
    stgfunc.output(halo_mask)
    stgfunc.output(aa2)
    return aa2


src_avg = srcs()
# stgfunc.output(src_avg)
o_clip, den_m = denoise(src_avg)
o_clip = chroma(o_clip)
# stgfunc.output(den_m)

o_clip = deband(o_clip)
stgfunc.output(o_clip)
out_clip = aa(o_clip)

dehalo, mask, i_aa = jvs_dehalo(out_clip)

# m = src.std.MaskedMerge(den, l_mask, planes=1)
# m = kagefunc.hybriddenoise(src, 0.1, 1.5)  #


out_clip = stgfunc.adaptive_grain(dehalo,
                                  [0.1, 0.06], 0.95, 65, False, 10,
                                  Grainer.AddNoise, temporal_average=2)
out_clip = vsutil.depth(out_clip, 10)

# stgfunc.output(src_avg)
stgfunc.output(out_clip)
out_clip = out_clip.fmtc.resample(css="420")
# out_clip.set_output(0)


# Extra 02 tweaks lol

# freeze frames

# src.set_output(0)
# src.set_output(1)
# out_clip.set_output(0)
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
