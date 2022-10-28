import pathlib

import stgfunc
import vapoursynth
import vsrgtools
from vapoursynth import core


def srcs(*src_input, depth=16, comb="avg", colorspace=None):
    inputs_path = [str(pathlib.Path(inputs).resolve(strict=True)) for inputs in src_input]
    srcs = list(stgfunc.src(inputs, depth=depth) for inputs in inputs_path)
    if comb == "avg":
        if len(src_input) == 2:
            output = core.std.Expr(srcs, 'x y + 2 /')
        elif len(src_input) > 2:
            output = core.average.Mean(*srcs)
        else:
            output = srcs[0]
    elif comb == "lehmer":
        if len(src_input) == 2:
            output = vsrgtools.lehmer_diff_merge(srcs[0], srcs[1])
        elif len(src_input) > 2:
            raise Exception("lehmer merge does not support 2+ srcs!")
        else:
            output = srcs[0]
    else:
        raise Exception(f"Unrecognized combing method: {comb}")
    if colorspace is not None:
        output = output.fmtc.resample(css=colorspace)
    return output


def waifu2x(in_clip, noise=-1, scale=2):
    in_clip = in_clip.fmtc.resample(css="444")
    in_clip = in_clip.fmtc.matrix(mat="601", col_fam=vapoursynth.RGB)
    in_clip = in_clip.fmtc.bitdepth(bits=32)
    return in_clip.w2xnvk.Waifu2x(noise=noise, scale=scale, model=2)


def scale(clip: vapoursynth.VideoFrame, percent=0.5):
    """
    Function used for "thresholds" for vsmask.
    :param clip: Input clip to get bit depth.
    :param percent: 0.0 to 1.0.
    :return: value that is scaled to the max value possible for the clip's format.
    """
    max_v = 1 << clip.format.bits_per_sample
    return max_v * percent
