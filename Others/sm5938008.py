import EoEfunc.denoise
import ccd
import havsfunc
import lvsfunc
import stgfunc
import vsutil
from stgfunc import Grainer


def src():
    srcer = stgfunc.src("raw/sm5938008 - 【手書き】ストライクウィッチーズ 赤ずきんチャチャEDパロ.mp4")
    # return srcer
    return srcer.fmtc.resample(css="444")


def denoise(in_clip):
    blk = in_clip.deblock.Deblock(quant=40)
    # stgfunc.output(vsutil.plane(blk, 1))
    bm3 = EoEfunc.denoise.BM3D(blk, [20, 0])  # Holyshit wtf
    bm3 = EoEfunc.denoise.BM3D(bm3, [0, 15])  # Holyshit wtf
    #stgfunc.output(vsutil.plane(bm3, 1))
    rec = lvsfunc.recon.chroma_reconstruct(bm3)
    #stgfunc.output(vsutil.plane(rec, 1))
    cam = ccd.ccd(rec, 20)
    #stgfunc.output(vsutil.plane(cam, 1))
    der = havsfunc.HQDeringmod(cam, mthr=100, mrad=3, minp=4)
    # stgfunc.output(der)
    return der  # EoEfunc.denoise.CMDegrain(der,thSAD=600)

    # return


src_clip = src()

den = denoise(src_clip)
# debandf = deb(den)

out_clip = stgfunc.adaptive_grain(den,
                                  [0.2, 0.06], 0.95, 65, False, 10,
                                  Grainer.AddNoise, temporal_average=2)
out_clip = vsutil.depth(out_clip, 10)

# stgfunc.output(den)
stgfunc.output(src_clip)
stgfunc.output(out_clip)

# out_clip.set_output(0)
# src_clip.set_output(0)
