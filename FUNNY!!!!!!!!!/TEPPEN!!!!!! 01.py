import EoEfunc.denoise
import ccd
import debandshit
import jvsfunc
import lvsfunc
import stgfunc
import vapoursynth
import vardefunc
import vsdehalo
import vsmask
import vsutil
from stgfunc import Grainer
from vapoursynth import core
from vsutil import get_w

import shynonon as sh

witty = vsmask.edge.FDoGTCanny()


def resizer(clip, width, no_mask=False):
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


def src():
    return sh.srcs("raws/[SubsPlease] Teppen - 01 (1080p) [5FEE3923].mkv")


def chroma(src_den, ccd_mask):
    # src_den = src_den.fmtc.resample(css="444")

    clip_ccd = ccd.ccd(src_den, threshold=5)  # Cleans up chroma
    # stgfunc.output(vsutil.plane(src_den, 2))
    # stgfunc.output(vsutil.plane(src_den, 1))
    # stgfunc.output(vsutil.plane(clip_ccd, 1))
    postccd = core.std.MaskedMerge(clip_ccd, src_den, ccd_mask)
    return postccd


def denoise(in_clip):
    mask = witty.edgemask(vsutil.get_y(src_clip), lthr=sh.scale(src_clip, .5),
                          hthr=sh.scale(src_clip, 0.9))
    # Cursed
    mask = mask.std.Deflate().std.Deflate().std.Deflate().std.Deflate().std.Invert()
    # stgfunc.output(mask)
    denoised = EoEfunc.denoise.BM3D(in_clip, [2, 0])
    denoised_chrm = chroma(denoised, mask)
    return denoised_chrm


def aa(src_clip):
    # det = lvsfunc.detail_mask(src_clip, rad=0, brz_a=1, brz_b=1)
    halo_mask = witty.edgemask(vsutil.get_y(src_clip), sh.scale(src_clip, 0.8)).std.Inflate().std.Inflate()
    aa3 = lvsfunc.aa.based_aa(src_clip, rfactor=1.8)
    # aa2 = vsaa.masked_clamp_aa(src_clip,strength=10)
    # stgfunc.output(src_clip)

    # stgfunc.output(halo_mask)
    # stgfunc.output(aa2)
    return aa3


def deband(clip: vapoursynth.VideoNode):
    base_line = debandshit.dumb3kdb(clip, use_neo=True, threshold=38)
    mask = witty.edgemask(vsutil.get_y(clip))
    deb_clip = core.std.MaskedMerge(base_line, clip, mask)

    return deb_clip


def jvs_dehalo(in_clip):  # Done initally by Julek. Deals with main haloing.
    # in_clip = vsutil.depth(in_clip, 16)
    aa = core.bilateral.Gaussian(in_clip, 0.5)
    i_aa = lvsfunc.aa.upscaled_sraa(aa, 1.1)
    mask = jvsfunc.dehalo_mask(i_aa, expand=1, iterations=1, brz=80)

    dehalo = vsdehalo.dehalo_alpha(in_clip,darkstr=0.5,brightstr=1)
    part_a = core.std.MaskedMerge(in_clip, dehalo, mask)
    # stgfunc.output(i_aa)
    # stgfunc.output(mask)
    # stgfunc.output(part_a)
    return part_a


src_clip = src()
# scaled_clip, descale_mask = resizer(src_clip, 960)

stgfunc.output(src_clip)
# src_clip.set_output(0)
# stgfunc.output(scaled_clip)
den = denoise(src_clip)
# stgfunc.output(den)
debanded = deband(den)
# stgfunc.output(debanded)
deh = jvs_dehalo(debanded)
# stgfunc.output(deh)
# stgfunc.output(deh)
aa_clip = aa(deh)
# stgfunc.output(aa_clip)

out_clip = stgfunc.adaptive_grain(aa_clip,
                                  [0.2, 0.06], 0.95, 65, False, 10,
                                  Grainer.AddNoise, temporal_average=2)
out_clip = vsutil.depth(out_clip, 10)

stgfunc.set_output(out_clip)
#src_clip.set_output(0)
# out_clip.set_output()