import EoEfunc
import debandshit
import stgfunc
import vapoursynth
import vsmask
import vsutil
import shynonon

witty = vsmask.edge.FDoGTCanny()


def srcs():
    im = stgfunc.src("raw/MO4AVphr.png")
    im = im.fmtc.matrix(mat="601", col_fam=vapoursynth.YUV, bits=16).fmtc.resample(css="444")
    return im

def denoise(src_clip):
    # mask_2 = jvsfunc.dehalo_mask(src_avg, expand=0, iterations=0, brz=220)
    sc = shynonon.scale
    mask_2 = witty.edgemask(vsutil.get_y(src_clip), lthr=sc(src_clip, .8),
                            hthr=sc(src_clip, .9)).std.Deflate().std.Deflate().std.Deflate().std.Deflate().std.Invert()

    den = EoEfunc.denoise.BM3D(src_clip, sigma=[3.5, 0], CUDA=True)
    src_den = vapoursynth.core.std.MaskedMerge(src_clip, den, mask_2)
    return src_den

def deband(clip: vapoursynth.VideoNode):
    clip_band = debandshit.dumb3kdb(clip, use_neo=True, threshold=60)
    mask = witty.edgemask(vsutil.get_y(clip))
    out_clip = vapoursynth.core.std.MaskedMerge(clip_band, clip, mask)
    # clip = clip.text.Text("NoDeBand")
    return out_clip, mask

src = srcs()
den = denoise(src)
deb, maskdeb = deband(den)
stgfunc.output(den)
stgfunc.output(maskdeb)
stgfunc.output(deb)