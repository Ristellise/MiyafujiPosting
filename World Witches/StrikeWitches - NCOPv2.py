import EoEfunc
import jvsfunc
import lvsfunc
import stgfunc
import vapoursynth
import vardefunc
import vsdehalo
import vsmask
from vapoursynth import core
import vsutil
from vsutil import get_w

import shynonon

black_frames = 11


def detelecine(clip: vapoursynth.VideoNode, decimate=True, inverse=True,
               nns=2) -> vapoursynth.VideoNode:  # Thanks to Varde for the telecine block.
    clip = vsutil.depth(clip.vivtc.VFM(1), 16).nnedi3.nnedi3(1, nns=nns, pscrn=1, combed_only=True)
    if decimate:
        clip = clip.vivtc.VDecimate()
    if inverse:
        clip = lvsfunc.vinverse(clip)
    return clip


src_clip = lvsfunc.misc.source("raw/Witch NCOP.m2ts", )
# src_clip = src_clip.resize.Point(matrix_in_s='709', matrix_s='170m').std.SetFrameProp(prop="_Matrix", intval=1)
ivtc_clip = detelecine(src_clip)
ivtc_clip = ivtc_clip[132:]  # remove inital card
ivtc_clip = ivtc_clip[black_frames:]  # remove inital black frames

ivtc_clip = ivtc_clip.fmtc.resample(css="444").std.Crop(0, 0, 0, 1)

sober = vsmask.edge.Sobel()

with vardefunc.YUVPlanes(ivtc_clip) as split:
    split.Y = core.knlm.KNLMeansCL(split.Y, s=1, a=2)
    split.U = core.knlm.KNLMeansCL(split.U, s=2, a=5, rclip=split.Y)
    split.V = core.knlm.KNLMeansCL(split.V, s=2, a=5, rclip=split.Y)

dehalo = split.clip

a = vsutil.get_y(ivtc_clip)
a = EoEfunc.denoise.BM3D(a, sigma=[6, 0], CUDA=True)
welcometofucking = a

lum = vsutil.get_y(ivtc_clip)
sc = shynonon.scale
stgfunc.output(ivtc_clip)
# bmsk = sober.edgemask(vsutil.get_y(ivtc_clip),lthr=sc(lum, 0.2),multi=1.0)
# hal2 = jvsfunc.iterate(bmsk,core.std.Maximum, 1)
# hal = jvsfunc.iterate(bmsk,core.std.Maximum, 5)
# hal = core.std.Expr([hal,hal2], " x y -")


welcometofucking = vsdehalo.dehalo_alpha(welcometofucking, rx=4, darkstr=0.25, brightstr=0.7, lowsens=70)
# stgfunc.output(hal)
stgfunc.output(welcometofucking)

iwillnowshowyoufucking = core.eedi2cuda.AA2(welcometofucking, mthresh=1, estr=0).warp.AWarpSharp2(blur=2, depth=8)
lvsfunc.upscaled_sraa(iwillnowshowyoufucking, 1.3)
stgfunc.output(iwillnowshowyoufucking)

beautifulvillagesituatedontheaustrianalps = core.std.ShufflePlanes([iwillnowshowyoufucking, ivtc_clip], [0, 1, 2],
                                                                   vapoursynth.YUV)


def mmsize(clip, width=540, no_mask=False):
    clip32l = vsutil.get_y(clip)
    clip32l = vsutil.depth(clip32l, 32)

    bic_kern = lvsfunc.kernels.Bicubic()

    descale = bic_kern.descale(clip32l, get_w(width), width)
    upscale = bic_kern.scale(descale, 1920, 1080)
    if not no_mask:
        descale_mask = lvsfunc.scale.descale_detail_mask(clip32l, upscale, threshold=0.040)
    else:
        descale_mask = core.std.BlankClip(clip32l)
    rescale = lvsfunc.kernels.Bilinear().scale(vardefunc.scale.nnedi3_upscale(descale, pscrn=1),
                                               clip.width, clip.height)
    # rescale = vsutil.depth(rescale, 16)
    rescale = core.std.MaskedMerge(rescale, clip32l, descale_mask)
    rescale = vsutil.depth(rescale, 16)
    scaled = vardefunc.misc.merge_chroma(rescale, clip)
    return scaled, descale_mask


allthevillagerssharethesameloveforfucking,_ = mmsize(beautifulvillagesituatedontheaustrianalps,no_mask=True)

stgfunc.output(beautifulvillagesituatedontheaustrianalps)
stgfunc.output(allthevillagerssharethesameloveforfucking)
# stgfunc.output(beautifulvillagesituatedontheaustrianalps)
