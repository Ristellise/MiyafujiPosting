import stgfunc as stg
import vapoursynth
from vapoursynth import core
import havsfunc as haf

from acsuite.acsuite import eztrim

core_limit = 8
core.max_cache_size = 1024*2*core_limit

def raw():
    #src = stg.src(, 8, matrix_prop=6)
    eztrim(r"E:\Miyafuji-BDMV\Lynne\BDROM\BDMV\STREAM\00016.m2ts", (28940, 28940+7330),outfile="AAA.mka")
    return src

chain = [raw]

SLICING = 0


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

    for func in slices:
        if func.__name__ == "source":
            out_clips = func()
        else:
            out_clips = func(*clips)
        if isinstance(out_clips, list) or isinstance(out_clips, set) or isinstance(out_clips, tuple):
            clips = list(out_clips)
        elif isinstance(out_clips, vapoursynth.VideoNode):
            clips = [out_clips]
        else:
            raise Exception(f"Output from: \"{func.__name__}\" incorrect. "
                            f"Expected: list, set, tuple or VideoNode. Got: {type(out_clips)}")
    for idx, clip in enumerate(clips):
        clip.set_output(idx)
    return clips


if __name__ == '__vapoursynth__':
    import os, sys
    from pathlib import Path

    from lvsfunc.render import SceneChangeMode, find_scene_changes

    if "writeqp" not in globals():
        print("Running Full Script")
        clip = run()[0]
        clip.set_output(0)
    else:
        print("Write QPFile")
        out_path = Path(__file__).resolve()
        out_path = out_path.with_name(f"{out_path.stem}_qpfile").with_suffix(".txt")

        out_path.parent.mkdir(parents=True, exist_ok=True)
        clip = run(src=True)[0]
        if os.path.isfile(out_path) is False:
            with open(out_path, 'w') as o:
                for f in find_scene_changes(clip, mode=SceneChangeMode.SCXVID):
                    o.write(f"{f} I -1\n")
        else:
            print("INFO: File already exists. Skipping...")
else:
    run()
