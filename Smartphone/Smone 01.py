import pathlib

import EoEfunc
import awsmfunc
import ccd
import debandshit
import fvsfunc
import lvsfunc
import stgfunc
import vapoursynth
import vardefunc.aa
import vsmask.edge
import vsutil
from lvsfunc.aa import nnedi3
from stgfunc import Grainer
from vsutil import get_w

core = vapoursynth.core

fdog = vsmask.edge.FDoGTCanny()

a = str(pathlib.Path(
    r"raws/00001.m2ts").resolve())
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


src = stgfunc.src(a)
src = vsutil.depth(src, 16)

# src.set_output(0)

ef = awsmfunc.bbmod(src, 2, 2, 2, 2, blur=20)  # meh, good enough

pred = mmsize(ef[:3693], no_mask=True)
op = mmsize(ef[3693:3693 + 2157])
m = mmsize(ef[3693 + 2157:3693 + 2157 + 26039], no_mask=True)
ed = mmsize(ef[3693 + 2157 + 26039:])

desc = pred[0] + op[0] + m[0] + ed[0]
cm = pred[1] + op[1] + m[1] + ed[1]
stgfunc.output(src)


# stgfunc.output(desc)

def compute_pairs(a, b, foff):
    return f"[{a - foff} {b - foff}]"


def deband(clip: vapoursynth.VideoNode):
    # todo banding fixes. look at frame 12322 for why.
    clip_band = debandshit.dumb3kdb(clip, use_neo=True, threshold=38)
    mask = fdog.edgemask(clip)
    out_clip = core.std.MaskedMerge(clip_band, clip, mask)
    # clip = clip.text.Text("NoDeBand")
    return out_clip


def denoise(r_clip: vapoursynth.VideoNode, credit_mask: vapoursynth.VideoNode, *_):
    pred = r_clip[:3693]
    op = r_clip[3693:3693 + 2157]
    main = r_clip[3693 + 2157:3693 + 2157 + 26039]
    ed = r_clip[3693 + 2157 + 26039:]

    pred = EoEfunc.denoise.BM3D(pred, sigma=[2, 0], CUDA=True)
    main = EoEfunc.denoise.BM3D(main, sigma=[2, 0], CUDA=True)
    op = EoEfunc.denoise.BM3D(op, sigma=[2, 0], CUDA=True)
    ed = EoEfunc.denoise.BM3D(ed, sigma=[1.7, 0], CUDA=True)

    clip = pred + op + main + ed
    mask = fdog.edgemask(vsutil.get_y(clip))
    clip_ccd = ccd.ccd(clip)  # Cleans up chroma
    out_clip = core.std.MaskedMerge(clip_ccd, clip, mask)
    credit_mask = credit_mask.resize.Point(format=vapoursynth.GRAY16)
    out_clip = core.std.MaskedMerge(out_clip, clip, credit_mask)
    return out_clip, credit_mask


den, _ = denoise(desc, cm)
deb = deband(den)
stgfunc.output(deb)



mask = fdog.edgemask(vsutil.get_y(deb)).std.Invert().std.Inflate()

ccd_mask = fdog.edgemask(vsutil.get_y(deb))
clip_ccd = ccd.ccd(deb)  # Cleans up chroma
postccd = core.std.MaskedMerge(clip_ccd, deb, mask)

out_clip = stgfunc.adaptive_grain(postccd,
                                  [0.2, 0.06], 0.95, 65, False, 10,
                                  Grainer.AddNoise, temporal_average=2)
# out_clip = vsutil.depth(out_clip, 10)
stgfunc.output(out_clip)
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
