import EoEfunc.denoise
import ccd
import debandshit
import stgfunc
import vsrgtools
import vsutil
from stgfunc import Grainer

import shynonon


def srcs():
    f = shynonon.srcs("raw/みんなの世界 [uyUiCBzUxvE].webm",
                      "raw/みんなの世界 [uyUiCBzUxvE].mp4", comb="lehmer")
    return f.fmtc.resample(css="444")


def denoise(in_clip):
    deblk = EoEfunc.denoise.BM3D(in_clip, sigma=[4, 0])
    pl = 1
    # stgfunc.output(vsutil.plane(deblk, pl), "UVPlane")
    c = ccd.ccd(deblk, 10)
    # stgfunc.output(vsutil.plane(c, pl), "UVPlane")
    dumb = debandshit.dumb3kdb(c, threshold=30, use_neo=True)
    #stgfunc.output(c)
    #stgfunc.output(dumb)
    t = vsrgtools.contrasharpening(dumb, in_clip)
    #stgfunc.output(t)
    return t



src_clip = srcs()
#stgfunc.output(src_clip, text="Source")
clip = denoise(src_clip)
#src_clip.set_output(0)
#stgfunc.output(clip, text="Correct")
out_clip = stgfunc.adaptive_grain(clip,
                                  [0.3, 0.06], 0.95, 65, False, 10,
                                  Grainer.AddNoise, temporal_average=5)
out_clip = vsutil.depth(out_clip, 10)
#stgfunc.output(out_clip, text="Out")
out_clip.set_output(0)