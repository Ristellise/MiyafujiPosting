import types

import lvsfunc.misc
import mvsfunc

from WitchCommon import *

core = vapoursynth.core
vapoursynth.core.num_threads = 8

def source():
    src = lvsfunc.misc.source("[SOURCE]")
    src = mvsfunc.Depth(src,16, dither=8)
    return src

def resize(clip):
    pass

def denoise(clip):
    pass

def dehalo(clip):
    pass

def AA(clip):
    pass

def deband(clip):
    pass

def output(clip):
    pass

chain:types.FunctionType = [source]


def run():
    clip = None
    for func in chain:
        if func.