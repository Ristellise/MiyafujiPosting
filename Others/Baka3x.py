import EoEfunc.denoise
import ccd
import havsfunc
import lvsfunc
import stgfunc
import vsrgtools
import vsutil
from stgfunc import Grainer


def src():
    srcer = stgfunc.src("raw/sm5161232 - 【short】驫麤～とりぷるばか～の絵をトレスして動かしてみようとか.mp4")
    # return srcer
    return srcer.fmtc.resample(css="444")


def denoise(in_clip):
    #blk = in_clip.deblock.Deblock(quant=30,aoffset=10)
    stgfunc.output(in_clip)
    blk = in_clip.deblock.Deblock(quant=30, aoffset=10)
    # stgfunc.output(in_clip.deblock.Deblock(quant=40, aoffset=0), "blk_aoffset=0")
    #stgfunc.output(blk)
    # stgfunc.output(in_clip)
    # stgfunc.output(blk)
    bm3 = EoEfunc.denoise.BM3D(blk, [30, 3])
    cam = ccd.ccd(bm3, 50)
    #stgfunc.output(cam)


    #stgfunc.output(cam)
    #stgfunc.output(c)
    der = havsfunc.HQDeringmod(cam, mthr=180, mrad=1, minp=1)
    #stgfunc.output(der)
    # #stgfunc.output(vsutil.plane(cam, 1))
    # der = havsfunc.HQDeringmod(cam, mthr=100, mrad=3, minp=4)
    stgfunc.output(in_clip)
    stgfunc.output(der)
    contr = vsrgtools.contrasharpening(der, in_clip)
    stgfunc.output(contr)
    # return der  # EoEfunc.denoise.CMDegrain(der,thSAD=600)
    return der
    #return in_clip


src_clip = src()

den = denoise(src_clip)
# debandf = deb(den)

out_clip = stgfunc.adaptive_grain(den,
                                  [0.2, 0.06], 0.95, 65, False, 10,
                                  Grainer.AddNoise, temporal_average=2)
out_clip = vsutil.depth(out_clip, 10)

# stgfunc.output(den)
#stgfunc.output(src_clip)
#stgfunc.output(out_clip)

out_clip.set_output(0)
#src_clip.set_output(0)
