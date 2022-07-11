"""
501st Hasshin Shimasu VS Script.
Notable things:
 - Each def is a encode step that is common in all scripts.
   - The
"""

import EoEfunc
import ccd
import debandshit
import kagefunc
import lvsfunc.misc
import vapoursynth
import vardefunc.aa
import vardefunc.mask
import vsutil
from awsmfunc import awsmfunc
from vsutil import get_w

core_limit = 4

core = vapoursynth.core
core.max_cache_size = 1024 * 3 * core_limit
core.num_threads = core_limit

# Config
SLICING = 1
SOURCE_COMP = False
# Global Params
fdog = vardefunc.mask.FDOG()


def source():
    src = lvsfunc.misc.source("raw/HasshinMovie.m2ts")
    src = vsutil.depth(src, 16)
    # src = mvsfunc.Depth(src, 16, dither=6) # NOTE: Avoid using mvsfunc
    return src


def edgefix(clip: vapoursynth.VideoNode, *_):
    ef = awsmfunc.bbmod(clip, 2, 2, 2, 2, blur=20)  # meh, good enough
    return ef


def mmsize(clip, width, no_mask=False):
    clip32l = vsutil.get_y(clip)
    clip32l = vsutil.depth(clip32l, 32)

    bic_kern = lvsfunc.kernels.Bicubic()

    descale = bic_kern.descale(clip32l, get_w(width), width)
    upscale = bic_kern.scale(descale, 1920, 1080)
    if not no_mask:
        descale_mask = lvsfunc.scale.descale_detail_mask(clip32l, upscale, threshold=0.040)
    else:
        descale_mask = core.std.BlankClip(clip32l)
    rescale = lvsfunc.kernels.Bicubic(b=-1 / 2, c=1 / 4).scale(vardefunc.scale.nnedi3_upscale(descale, pscrn=1),
                                                               clip.width, clip.height)
    # rescale = vsutil.depth(rescale, 16)
    rescale = core.std.MaskedMerge(rescale, clip32l, descale_mask)
    rescale = vsutil.depth(rescale, 16)
    scaled = vardefunc.misc.merge_chroma(rescale, clip)
    return scaled, descale_mask



def resize(clip: vapoursynth.VideoNode, *_):  # TODO: probably change the *_ to annoy people less.
    op = clip[0:2184]
    main = clip[2184:42888]
    ed = clip[42888:]
    # Yes, I could do replace frames but meh. This is also probably much faster.
    op_pair = mmsize(op, 864)
    main_pair = mmsize(main, 882, no_mask=True)
    ed_pair = mmsize(ed, 864)
    sc = op_pair[0] + main_pair[0] + ed_pair[0]
    cm = op_pair[1] + main_pair[1] + ed_pair[1]
    # cm = cm.resize.Point(format="")1
    return sc, cm, *_


def denoise(r_clip: vapoursynth.VideoNode, credit_mask: vapoursynth.VideoNode, *_):

    op = r_clip[0:2184]
    main = r_clip[2184:42888]
    ed = r_clip[42888:]

    main = EoEfunc.denoise.BM3D(main, sigma=[1.7, 0], CUDA=True)
    op = EoEfunc.denoise.BM3D(op, sigma=[2, 0], CUDA=True)
    ed = EoEfunc.denoise.BM3D(ed, sigma=[1.7, 0], CUDA=True)

    clip = op + main + ed
    mask = fdog.get_mask(vsutil.get_y(clip))
    clip_ccd = ccd.ccd(clip)  # Cleans up chroma
    out_clip = core.std.MaskedMerge(clip_ccd, clip, mask)
    credit_mask = credit_mask.resize.Point(format=vapoursynth.GRAY16)
    out_clip = core.std.MaskedMerge(out_clip, clip, credit_mask)
    return out_clip, credit_mask, *_


def AA(clip: vapoursynth.VideoNode, *_):
    aa = vardefunc.aa.upscaled_sraa(clip)

    return aa, *_


def deband(clip: vapoursynth.VideoNode, *_):
    # todo banding fixes. look at frame 12322 for why.
    clip_band = debandshit.dumb3kdb(clip, use_neo=True, threshold=40)
    mask = fdog.get_mask(clip)
    out_clip = core.std.MaskedMerge(clip_band, clip, mask)
    # clip = clip.text.Text("NoDeBand")
    return out_clip, *_


def output(clip: vapoursynth.VideoNode, *_):
    clip = kagefunc.adaptive_grain(clip, strength=0.3, )
    clip = vsutil.depth(clip, 10)
    return clip


# """dehalo"""
chain = [source, edgefix, resize, denoise, AA, deband, output]


def run(src=False):
    clips = []
    if SLICING != 0:
        slices = chain[:SLICING]
    elif SLICING == -1:
        slices = chain
    else:
        slices = [chain[0]]
    if src:
        slices = [chain[0]]
    print(f"Running: {', '.join([i.__name__ for i in slices])}")
    raw_comp = None
    for func in slices:
        # timer = time.time()
        if func.__name__ == "source":
            out_clips = func()
            if SOURCE_COMP:
                raw_comp = out_clips
            # print(f"{func.__name__}: {round(time.time() - timer, 2)}s")
        else:
            out_clips = func(*clips)
            # print(f"{func.__name__}: {round(time.time() - timer, 2)}s")
        if isinstance(out_clips, list) or isinstance(out_clips, set) or isinstance(out_clips, tuple):
            clips = list(out_clips)
        elif isinstance(out_clips, vapoursynth.VideoNode):
            clips = [out_clips]
        else:
            raise Exception(f"Output from: \"{func.__name__}\" incorrect. "
                            f"Expected: list, set, tuple or VideoNode. Got: {type(out_clips)}")
    for idx, clip in enumerate(clips):
        clip.set_output(idx)
    if not SOURCE_COMP:
        return clips
    else:
        current = clips[0]
        current = current.text.Text(f"Step: {slices[-1].__name__}")
        raw_comp = raw_comp.text.Text(f"Step: Raw")
        current.set_output(0)
        raw_comp.set_output(1)


# if __name__ == '__main__':
#     from pathlib import Path
#     out_path = Path(__file__).resolve()
#     qp_file = out_path.with_name(f"{out_path.stem}_qpfile").with_suffix(".txt")
#     enc_file = out_path.with_name(f"{out_path.stem}_enc").with_suffix(".264")
#     src = run(src=True)[0]
#     final = run()[0]
#     stg.encode.create_qpfile(src, str(qp_file))
#     stg.encode.encode(final, str(enc_file), False, [], **ENCODING_x264_ARGS(qp_file))

if __name__ == '__vapoursynth__':
    import os, sys
    from pathlib import Path

    from lvsfunc.render import SceneChangeMode, find_scene_changes

    if "writeqp" not in globals():
        print("Running Full Script")
        out_clip = run()[0]
        out_clip.set_output(0)
    else:
        print("Write QPFile")
        print(sys.argv)
        out_path = Path(__file__).resolve()
        out_path = out_path.with_name(f"{out_path.stem}_qpfile").with_suffix(".txt")

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_clip = run(src=True)[0]
        if os.path.isfile(out_path) is False:
            with open(out_path, 'w') as o:
                for f in find_scene_changes(out_clip, mode=SceneChangeMode.WWXD_SCXVID_UNION):
                    o.write(f"{f} I -1\n")
        else:
            print("INFO: File already exists. Skipping...")
else:
    run()
