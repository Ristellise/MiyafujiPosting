import EoEfunc
import ccd
import debandshit
import jvsfunc
import lvsfunc
import stgfunc
import vapoursynth
import vsdehalo
import vsmask.edge
import vsutil
from stgfunc import Grainer

import shynonon

core = vapoursynth.core
witty = vsmask.edge.FDoGTCanny()


def jvs_dehalo(in_clip):  # Done initally by Julek. Deals with main haloing.
    # in_clip = vsutil.depth(in_clip, 16)
    aa = core.bilateral.Gaussian(in_clip, 0.5)
    i_aa = lvsfunc.aa.upscaled_sraa(aa, 1.1)
    mask = jvsfunc.dehalo_mask(i_aa, expand=1, iterations=1, brz=150)
    dehalo = vsdehalo.fine_dehalo(in_clip, rx=2, darkstr=1, brightstr=1)
    part_a = core.std.MaskedMerge(in_clip, dehalo, mask)
    # stgfunc.output(mask)
    # stgfunc.output(part_a)
    return part_a


debanding = [
]


def deband(clip: vapoursynth.VideoNode):
    mod_clips = [(clip[i[0]:i[1]+1], i[0], i[2]) for i in debanding]

    base_line = debandshit.dumb3kdb(clip, use_neo=True, threshold=38)
    mask = witty.edgemask(vsutil.get_y(clip))
    #stgfunc.output(mask)
    deb_clip = core.std.MaskedMerge(base_line, clip, mask)

    for i in mod_clips:
        if i[2] == 1:
            mod_band = debandshit.dumb3kdb(i[0], use_neo=True, threshold=58, radius=19)
            mask = witty.edgemask(vsutil.get_y(i[0]))
            #stgfunc.output(mask)
            deb_clip = vsutil.insert_clip(deb_clip, core.std.MaskedMerge(mod_band,i[0], mask), i[1])
    #
    # clip = clip.text.Text("NoDeBand")
    return deb_clip


def srcs():
    return shynonon.srcs("raw/Luminous Witches/Luminous Witches - 12 (Amazon dAnime CBR 1080p).mkv",
                         "raw/Luminous Witches/Luminous Witches - 12 (Amazon dAnime VBR 1080p).mkv", comb="lehmer")


def denoise(src_clip):
    # mask_2 = jvsfunc.dehalo_mask(src_avg, expand=0, iterations=0, brz=220)
    sc = shynonon.scale
    mask_2 = witty.edgemask(vsutil.get_y(src_clip), lthr=sc(src_clip, .8),
                            hthr=sc(src_clip, .9)).std.Deflate().std.Deflate().std.Deflate().std.Deflate().std.Invert()

    den = EoEfunc.denoise.BM3D(src_clip, sigma=[3.5, 0], CUDA=True)
    src_den = core.std.MaskedMerge(src_clip, den, mask_2)
    return src_den, mask_2


def chroma(src_den):
    ccd_mask = witty.edgemask(vsutil.get_y(src_den))
    clip_ccd = ccd.ccd(src_den, threshold=10)  # Cleans up chroma
    postccd = core.std.MaskedMerge(clip_ccd, src_den, ccd_mask)
    return postccd


sober = vsmask.edge.Sobel()


def aa(src_clip):
    sc = shynonon.scale
    # det = lvsfunc.detail_mask(src_clip, rad=0, brz_a=1, brz_b=1)
    halo_mask = sober.edgemask(vsutil.get_y(src_clip), sc(src_clip, 0.5)).std.Inflate()
    # halo_mask = witty.edgemask(vsutil.get_y(src_clip)[20505:20540], sc(src_clip, 0.3))
    # halo_mask = havsfunc.FineDehalo(src_clip, rx=0.5, darkstr=0.5, brightstr=0.5, contra=1, showmask=True)
    sraa2 = core.eedi2cuda.AA2(src_clip)
    aa2 = core.std.MaskedMerge(src_clip, sraa2, halo_mask)
    # stgfunc.output(src_clip)
    # stgfunc.output(halo_mask)
    # stgfunc.output(aa2)
    return aa2


src_fmerg = srcs()
# stgfunc.output(src_fmerg)
# stgfunc.output(src_avg)
denoised, den_m = denoise(src_fmerg)
chroma_den = chroma(denoised)

debanded = deband(chroma_den)

aa_clip = aa(debanded)
dehalo = jvs_dehalo(aa_clip)

# m = src.std.MaskedMerge(den, l_mask, planes=1)
# m = kagefunc.hybriddenoise(src, 0.1, 1.5)  #

# stgfunc.output(src_fmerg)
# balanmced = stgfunc.auto_balance(src_avg)
# stgfunc.output(balanmced)


out_clip = stgfunc.adaptive_grain(dehalo,
                                  [0.2, 0.06], 0.95, 65, False, 10,
                                  Grainer.AddNoise, temporal_average=2)
out_clip = vsutil.depth(out_clip, 10)

## Tests
#stgfunc.output(src_fmerg)
# stgfunc.output(den_m)
#stgfunc.output(out_clip)

# Output
#stgfunc.src("raw/Luminous Witches/Luminous Witches - 12 (Amazon dAnime CBR 1080p).mkv", 16).set_output(0)
out_clip.set_output(0)