import lvsfunc.misc
import vapoursynth
import vardefunc.aa
import vsutil

core_limit = 4

core = vapoursynth.core
core.max_cache_size = 1024*2*core_limit
core.num_threads = core_limit
SLICING = 4
fdog = vardefunc.mask.FDOG()
def source():
    src = lvsfunc.misc.source("raw/HasshinMovie.m2ts")
    src = vsutil.depth(src, 16)
    print(core.list_functions())
    src = src.resize.Point(format=vapoursynth.RGBS)
    srcd = core.vsdpir.Deblock(src, 1000, 0, 0, 0)
    # src = mvsfunc.Depth(src, 16, dither=6) # NOTE: Avoid using mvsfunc
    return src, srcd
a,b = source()
a.set_output(0)
b.set_output(1)