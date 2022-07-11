"""
Format magic.
"""
import vapoursynth

if getattr(vapoursynth.core, "fmtc") is None:
    raise NotImplementedError("fmtconv library missing, install from here: <https://github.com/EleonoreMizo/fmtconv>")


def YUV420toRGB(clip):
    """
    Converts YUV420 (Or any variant) to RGB.
    :param clip:
    :return:
    """
    clip = clip.fmtc.resample(css="444")
    clip = clip.fmtc.matrix(mat="601", col_fam=vapoursynth.RGB)
    clip = clip.fmtc.bitdepth(bits=8)
    return clip


def RGBtoYUV420(clip,out_depth=8):
    """
    Converts RGB to YUV444. (Yes it's a bit of a misnomer.)
    :param clip:
    :return:
    """
    clip = clip.fmtc.matrix(mat="601", col_fam=vapoursynth.YUV, bits=16)
    clip = clip.fmtc.resample(css="444")
    clip = clip.fmtc.bitdepth(bits=out_depth)
    return clip
