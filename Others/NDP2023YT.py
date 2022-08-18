import EoEfunc
import ccd
import debandshit
import lvsfunc
import stgfunc
import vapoursynth
import vsmask
import vsutil
import shynonon

witty = vsmask.edge.FDoGTCanny()


def srcs():
    im = stgfunc.src("raw/test.png")
    im = im.fmtc.matrix(mat="601", col_fam=vapoursynth.YUV, bits=16).fmtc.resample(css="444")
    return im


def denoise(clip: vapoursynth.VideoNode):
    sc = shynonon.scale
    mask_2 = witty.edgemask(vsutil.get_y(clip), lthr=sc(clip, .8),
                            hthr=sc(clip, .9)).std.Deflate().std.Deflate().std.Deflate().std.Deflate().std.Invert()

    den = EoEfunc.denoise.BM3D(clip, sigma=[5, 0], CUDA=True)
    src_den = vapoursynth.core.std.MaskedMerge(clip, den, mask_2)
    return src_den


def chroma(src_den):
    ccd_mask = witty.edgemask(vsutil.get_y(src_den))
    clip_ccd = ccd.ccd(src_den, threshold=50)  # Cleans up chroma
    postccd = vapoursynth.core.std.MaskedMerge(clip_ccd, src_den, ccd_mask)
    return postccd


def deband(clip: vapoursynth.VideoNode):
    clip_band = debandshit.dumb3kdb(clip, use_neo=True, threshold=60)
    mask = witty.edgemask(vsutil.get_y(clip))
    out_clip = vapoursynth.core.std.MaskedMerge(clip_band, clip, mask)
    # clip = clip.text.Text("NoDeBand")
    return out_clip


src = srcs()

stgfunc.output(src)

dpir = src.deblock.Deblock(quant=28)


den = denoise(dpir)

den = chroma(den)

stgfunc.output(den)
deb = deband(den)
stgfunc.output(deb)