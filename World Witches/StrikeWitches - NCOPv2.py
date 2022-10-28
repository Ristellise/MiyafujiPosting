import pathlib

import EoEfunc
import ccd
import debandshit
import havsfunc
import jvsfunc
import lvsfunc
import stgfunc
import vapoursynth
import vsdehalo
import vskernels
import vsmask.edge
import vsutil
from stgfunc import Grainer
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


def load_wobbly(path):
    if isinstance(path, str):
        path = pathlib.Path(path).resolve()
    import importlib.machinery

    loader = importlib.machinery.SourceFileLoader('report', str(path))
    handle = loader.load_module('report')
    vapoursynth.clear_output(0)
    return getattr(handle, "src")


def mask_deflate(mask_clip, iterations):
    mask_clip = vsutil.iterate(mask_clip, vapoursynth.core.std.Deflate, iterations)
    return mask_clip


def mask_inflate(mask_clip, iterations):
    mask_clip = vsutil.iterate(mask_clip, vapoursynth.core.std.Inflate, iterations)
    return mask_clip


ivtc_clip = load_wobbly("raw/Strike Witches/Witch NCOP.m2ts.wob.py")

ivtc_clip = ivtc_clip[132:]  # remove inital card
ivtc_clip = ivtc_clip[black_frames:]  # remove inital black frames

# stgfunc.output(ivtc_clip)

ivtc_clip = ivtc_clip.fmtc.resample(css="444").fb.FillBorders(bottom=1)  # Setsu: probably don't crop.

stgfunc.output(ivtc_clip)
ivtc_clip = ivtc_clip.std.SetFieldBased(0)
ivtc_clip_mod = havsfunc.bbmod(ivtc_clip, 0, 5, 0, 0, blur=5)

ivtc_clip = vapoursynth.core.std.ShufflePlanes(clips=[ivtc_clip, ivtc_clip_mod],
                                               planes=[0, 1, 2],
                                               colorfamily=vapoursynth.YUV)
aaa = 720

witty = vsmask.edge.FDoGTCanny()


def jvs_dehalo(in_clip):  # Julek
    in_clip = jvsfunc.depth(in_clip, 16)
    mask = jvsfunc.dehalo_mask(in_clip, expand=3, brz=80, iterations=1)
    dehalo = havsfunc.YAHR(in_clip, depth=64)  # you can try lvf.dehalo.bidehalo(src) here or something else too
    return dehalo, mask, None


def deband(clip: vapoursynth.VideoNode):
    base_line = debandshit.dumb3kdb(clip, use_neo=True, radius=20, threshold=30)
    mask = witty.edgemask(vsutil.get_y(clip), lthr=shynonon.scale(clip, 0.3))
    # stgfunc.output(mask)
    deb_clip = vapoursynth.core.std.MaskedMerge(base_line, clip, mask)

    # clip = clip.text.Text("NoDeBand")
    return deb_clip


# Uh why?
# preclean 1080p for some of the inital haloing seems to work.

# stgfunc.output(ivtc_clip)
deh, m, _ = jvs_dehalo(ivtc_clip)
merg = vapoursynth.core.std.MaskedMerge(ivtc_clip, deh, m)

# stgfunc.output(ivtc_clip)
# stgfunc.output(deh)
# stgfunc.output(merg)

# Downscale to 720p
# [This will never be the correct resolution compared to DVD but
# looks like the best if scaled back up to 1080p, so it is as it is.]
# DideeBicubic descale to preserve detail
didee = vskernels.BicubicDidee()

dvd = didee.descale(merg, get_w(aaa), aaa)
dvd720 = didee.descale(ivtc_clip.std.SetFieldBased(0), get_w(720), 720)

# The rest is a standard afair at 720p, denoise, deband, a bit of AA, etc.

den = EoEfunc.denoise.BM3D(dvd, [2, 0])
stgfunc.output(vsutil.plane(den, 1), "preccd")
den = ccd.ccd(den, 15)
stgfunc.output(vsutil.plane(den, 1), "postccd")

# stgfunc.output(den)
# stgfunc.output(den)
deb = deband(den)
# stgfunc.output(deb)

# Dehalo/Dering for 480.

# Redo this YAHR.


der_mask = jvsfunc.dehalo_mask(deb, expand=0.5, iterations=1, brz=60)
der_mask = mask_deflate(der_mask, 1)
der = vsdehalo.fine_dehalo2(deb, radius=3)

# stgfunc.output(deb)
# stgfunc.output(der)

der2 = vsdehalo.fine_dehalo(der, brightstr=0.5)

# stgfunc.output(der2)
# stgfunc.output(der_mask)

# der_m = der
der_m = vapoursynth.core.std.MaskedMerge(der, der2, der_mask)

# stgfunc.output(der_m)

aa = lvsfunc.aa.based_aa(der_m, rfactor=2)
aafb = aa.std.SetFieldBased(0)

# Rescale up to 720p

scale720 = vskernels.Bicubic().scale(aafb, 1280, 720).fmtc.resample(css="420")

out_clip = stgfunc.adaptive_grain(scale720,
                                  [0.2, 0.06], 0.95, 65, False, 10,
                                  Grainer.AddNoise, temporal_average=2)
out_clip = vsutil.depth(out_clip, 10)

stgfunc.output(dvd720)
# out_clip.set_output()
stgfunc.output(out_clip)
