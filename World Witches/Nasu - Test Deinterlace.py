import stgfunc
import vapoursynth
import vsutil
import havsfunc
import Oyster
core = vapoursynth.core
vapoursynth.core.num_threads = 8


def compute_pairs(a, b, foff):
    return f"[{a - foff} {b - foff}]"


def detelecine(clip: vapoursynth.VideoNode, decimate=True, inverse=True, nns=2) -> vapoursynth.VideoNode:
    clip = vsutil.depth(clip.vivtc.VFM(0), 16).nnedi3.nnedi3(1, nns=nns, pscrn=1, combed_only=True)
    return clip

def refried(src):
    refield_ref = core.eedi3m.EEDI3(
        core.eedi3m.EEDI3(
            src, 1, alpha=0.25, beta=0.20, gamma=500, nrad=3, mdis=20, vcheck=3,
            sclip=core.nnedi3.nnedi3(src, 1, nsize=3, nns=3, qual=1, pscrn=4)
        ), 0, alpha=0.25, beta=0.45, gamma=500, nrad=3, mdis=20, vcheck=3,
        sclip=core.nnedi3.nnedi3(src, 0, nsize=3, nns=3, qual=1, pscrn=4)
    )
    return refield_ref

def refry(refield_ref):
    refielded = core.eedi3m.EEDI3(
        refield_ref, 1, alpha=0.25, beta=0.35, gamma=400, nrad=3, mdis=20, vcheck=3,
        sclip=core.nnedi3.nnedi3(refield_ref, 1, nsize=3, nns=3, qual=2, pscrn=4)
    )
    return refielded

src_clip = stgfunc.src(r"H:\Eila is Sleeping [Dumping Grounds]\[philosophy-raws][Strike Witches]\Bonus\[philosophy-raws][Strike Witches][NCOP][BDRIP][Hi10P FLAC][1920X1080].mkv")
stgfunc.output(src_clip)
stgfunc.output(vsutil.depth(vsutil.get_y(src_clip), 8).fftspectrum.FFTSpectrum(grid=True))

#sup = Oyster.Super()
# ref_f = Oyster.Basic(tel, sup, short_time=False)
# ref_s = Oyster.Basic(tel, sup, short_time=True)
# clip = Oyster.Deblocking(tel, ref_f, block_step=2)

