import json
import pathlib
import stgfunc
import debandshit
import vapoursynth
from vapoursynth import core

def srcs(*src_input, depth=16, avg=True,colorspace=None):
    inputs_path = [str(pathlib.Path(inputs).resolve(strict=True)) for inputs in src_input]
    srcs = list(stgfunc.src(inputs, depth=depth) for inputs in inputs_path)
    output = None
    if avg:
        if len(src_input) == 2:
            output = core.std.Expr(srcs, 'x y + 2 /')
        elif len(src_input) > 2:
            output = core.average.Mean(*srcs)
        else:
            output = srcs
    if colorspace is not None:
        output = output.fmtc.resample(css=colorspace)
    return output

def scale(clip:vapoursynth.VideoFrame,percent=0.5):
    """
    Function used for "thresholds" for vsmask.
    :param clip: Input clip to get bit depth.
    :param percent: 0.0 to 1.0.
    :return: value that is scaled to the max value possible for the clip's format.
    """
    max_v = 1<<clip.format.bits_per_sample
    return max_v*percent