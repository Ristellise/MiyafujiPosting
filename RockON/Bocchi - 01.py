import EoEfunc.denoise
import ccd
import debandshit
import lvsfunc
import stgfunc
import vapoursynth
import vsaa
import vsdehalo
import vsmask
import vsutil
import jvsfunc
from stgfunc import Grainer

import shynonon as sh

witty = vsmask.edge.FDoGTCanny()


def srcs():
    return stgfunc.src("raws/[Gotch] Bocchi the Rock! - 01 [8C6FC777].mkv", depth=16)


def denoise(src_in):
    den = EoEfunc.denoise.BM3D(src_in, [2, 0])
    den = ccd.ccd(den, 1)
    out = den
    return out


def deband(src_in):
    base_line = debandshit.dumb3kdb(src_in, use_neo=True, threshold=38)
    mask = witty.edgemask(vsutil.get_y(src_in))
    deb_clip = base_line.std.MaskedMerge(src_in, mask)
    return deb_clip

sober = vsmask.edge.Sobel()

def aa(src_clip):
    # # det = lvsfunc.detail_mask(src_clip, rad=0, brz_a=1, brz_b=1)
    halo_mask = witty.edgemask(vsutil.get_y(src_clip), sh.scale(src_clip, 0.8)).std.Inflate().std.Inflate()

    aa3 = lvsfunc.aa.based_aa(src_clip, rfactor=1.5)
    aa3 = src_clip.std.MaskedMerge(aa3, halo_mask)
    # # aa2 = vsaa.masked_clamp_aa(src_clip,strength=10)
    # # stgfunc.output(src_clip)
    # # stgfunc.output(halo_mask)
    # # stgfunc.output(aa3)1212
    #stgfunc.output(aa3,"PreAA")
    #stgfunc.output(aa2,"LWAA")
    return aa3


def dehalo(src_clip):
    shalod = vsdehalo.fine_dehalo(src_clip, rx=2, darkstr=0,
                                  lowsens=5,
                                  highsens=20,
                                  brightstr=1, thlimi=100,
                                  thlima=512, show_mask=False)

    aa = vapoursynth.core.bilateral.Gaussian(src_clip, 0.5)
    i_aa = vsaa.upscaled_sraa(aa, 1.1)
    halo_mask = jvsfunc.dehalo_mask(i_aa, expand=2, iterations=0, brz=220)
    out = src_clip.std.MaskedMerge(shalod, halo_mask)
    # stgfunc.output(shalod)
    # stgfunc.output(halo_mask)
    # stgfunc.output(out)
    return out


src = srcs()
#stgfunc.output(src)
clip = denoise(src)
#stgfunc.output(clip, text="Denoise")
clip = deband(clip)
#stgfunc.output(clip, text="Deband")
clip = dehalo(clip)
#stgfunc.output(clip, text="Dehalo")
clip = aa(clip)
#stgfunc.output(clip, text="AA")

out_clip = stgfunc.adaptive_grain(clip,
                                  [0.2, 0.06], 0.95, 65, False, 10,
                                  Grainer.AddNoise, temporal_average=5)
out_clip = vsutil.depth(out_clip, 10)



#src.set_output(0)
#out_clip.set_output(1)
stgfunc.output(src, text="Src")
stgfunc.output(out_clip, text="Final")
