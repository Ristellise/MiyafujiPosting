import inspect

import EoEfunc.denoise
import stgfunc
import vapoursynth
import vsdehalo
import vsmask
import vsrgtools
import vsutil
from lvsfunc.aa import based_aa
from stgfunc import Grainer


def scale(in_clip: vapoursynth.VideoNode, percent=0.5):
    max_v = 1 << in_clip.format.bits_per_sample
    return max_v * percent


def output_luma(in_clip):
    ref_name = "Clip ?"
    ref_id = str(id(in_clip))
    current_frame = inspect.currentframe()
    for x in current_frame.f_back.f_locals.items():
        if (str(id(x[1])) == ref_id):
            ref_name = x[0]
            break

        ref_name = ref_name.title()
    ref_name = ref_name.title()

    lum = vsutil.get_y(in_clip)
    stgfunc.output(lum, text=ref_name)


def src():
    prime = stgfunc.src("raws/Do It Yourself!! - 01 (Amazon Prime CBR 1080p).mkv", 16)[24:-24]
    cr = stgfunc.src("raws/Do It Yourself!! - 01 (1080p) [CR].mkv", depth=16)
    return vsrgtools.lehmer_diff_merge(prime, cr)


clip = src()
witty = vsmask.edge.FDoGTCanny()


def denoise(in_clip: vapoursynth.VideoNode):
    smd = EoEfunc.denoise.CMDegrain(in_clip, tr=3, thSAD=40)
    sloc = [0.0, 0, 0.35, 0, 0.6, 512, 1.0, 512]
    ref = smd.dfttest.DFTTest(slocation=sloc, planes=[0], **EoEfunc.frequencies._dfttest_args)
    den_y = EoEfunc.denoise.BM3D(vsutil.get_y(smd), sigma=[0.2, 0], CUDA=True, ref=vsutil.get_y(ref))
    merg = vapoursynth.core.std.ShufflePlanes([den_y, in_clip], planes=[0, 1, 2], colorfamily=vapoursynth.YUV)

    #stgfunc.output(den_y)
    #stgfunc.output(merg)
    return in_clip


def dehalo(in_clip, src_clip):
    #stgfunc.output(in_clip, text="dehalo-pre")
    halo_mask = witty.edgemask(src_clip, lthr=scale(src_clip, 0.5)).std.Inflate()
    drh = vsdehalo.fine_dehalo(in_clip, brightstr=0.75)
    # output_luma(halo_mask)
    # output_luma(drh)
    merg = in_clip.std.MaskedMerge(drh, halo_mask)
    # stgfunc.output(merg)
    return merg, halo_mask


def aa(in_clip):
    rfac = 1.6
    aad = based_aa(in_clip, rfactor=rfac)
    aadmas = based_aa(in_clip, rfactor=rfac, show_mask=True)
    #stgfunc.output(in_clip)
    #stgfunc.output(aadmas)
    #stgfunc.output(aad)
    return aad


#stgfunc.output(vsutil.get_y(clip))
# stgfunc.output()
den = denoise(clip)
dehalo_d, h_mask = dehalo(den, clip)
aad_clip = aa(dehalo_d)

out_clip = stgfunc.adaptive_grain(aad_clip,
                                  [0.5, 0.06], 0.95, 65, False, 10,
                                  Grainer.AddNoise, temporal_average=2)
out_clip = vsutil.depth(out_clip, 10)

#stgfunc.output(clip)
#stgfunc.output()
clip.set_output(1000)
# Final
out_clip.set_output(0)