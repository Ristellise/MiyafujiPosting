import pathlib

import EoEfunc
import ccd
import lvsfunc
import stgfunc
import vapoursynth
import vsdehalo
import vsutil
from stgfunc import Grainer

def load_wobbly(path):
    if isinstance(path, str):
        path = pathlib.Path(path).resolve()
    import importlib.machinery

    loader = importlib.machinery.SourceFileLoader('report', str(path))
    handle = loader.load_module('report')
    vapoursynth.clear_output(0)
    return getattr(handle, "src")

ep = stgfunc.src("raw/KABA_2501.931-44640.m2v")

stgfunc.output(s1)