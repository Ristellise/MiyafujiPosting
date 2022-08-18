import lvsfunc
import stgfunc
import vapoursynth
import vardefunc
import vsdehalo
import vsmask.edge
import vsutil
from vsutil import get_w


def RGBtoYUV420(clip):
    clip = clip.fmtc.matrix(mat="601", col_fam=vapoursynth.YUV, bits=16)
    return clip


qtec = RGBtoYUV420(stgfunc.src("tests/screenshot03.png", 16))


def scale(clip: vapoursynth.VideoFrame, percent=0.5):
    """
    Function used for "thresholds" for vsmask.
    :param clip: Input clip to get bit depth.
    :param percent: 0.0 to 1.0.
    :return: value that is scaled to the max value possible for the clip's format.
    """
    max_v = 1 << clip.format.bits_per_sample
    return max_v * percent


def thefucking(clip, width=480):
    print(clip.format.color_family)
    if clip.format.color_family != vapoursynth.ColorFamily.YUV:
        raise Exception("Not YUV.")
    desc = lvsfunc.kernels.BicubicDidee()  # Wait, this works??
    base_scale = desc.descale(clip, get_w(width), width)
    lum = vsutil.get_y(base_scale)
    lum_prescale = vsutil.get_y(clip)
    sober = vsmask.edge.Sobel()

    sraa2 = vapoursynth.core.eedi2cuda.AA2(lum)
    dehalo = vsdehalo.fine_dehalo(sraa2, rx=2, darkstr=1, brightstr=1)
    msk = sober.edgemask(lum, scale(sraa2))
    dehalo = vapoursynth.core.std.MaskedMerge(lum, dehalo, msk)

    rescale = lvsfunc.kernels.Bicubic(b=-1 / 2, c=1 / 4).scale(vardefunc.scale.nnedi3_upscale(dehalo, pscrn=1),
                                                               clip.width, clip.height)

    # lum_prescale_msk = sober.edgemask(lum_prescale, scale(lum_prescale, 0.2), scale(lum_prescale, 0.4)).std.Inflate().std.Inflate().std.Inflate()
    # stgfunc.output(lum_prescale_msk)
    # stgfunc.output(vsutil.get_y(clip))

    # rescale = vapoursynth.core.std.MaskedMerge(vsutil.get_y(clip), rescale, lum_prescale_msk)

    ups = vapoursynth.core.std.ShufflePlanes([rescale, clip], [0, 1, 2], vapoursynth.YUV)

    return ups


WelcomeToFucking = thefucking(qtec)
stgfunc.output(qtec)
stgfunc.output(WelcomeToFucking)
