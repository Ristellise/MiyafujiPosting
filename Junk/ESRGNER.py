import pathlib
import random,asyncio
from concurrent.futures import ThreadPoolExecutor

import stgfunc as stg
import tqdm
import vapoursynth as vs

core = vs.core

src2 = None
for file in pathlib.Path(
        r"H:\Eila is Sleeping [Dumping Grounds]\Strike Witches S02 (BD 1080p x264 10bit - FLAC 2.0 FLAC 5.1) [Quetzal]").iterdir():
    if file.is_file() and file.suffix.endswith(".mkv"):
        if src2 is not None:
            src2 += stg.src(str(file))
            print(str(file))
        else:
            src2 = stg.src(str(file))
            print(str(file))
p = pathlib.Path.cwd().joinpath("cel_07")
p.mkdir(exist_ok=True, parents=True)
src = src2.resize.Point(format=vs.RGBS, matrix_in=1)
a = core.imwri.Write(src, "png", str(p.joinpath("%04d.png")))
t_frames = len(src)
print(t_frames)
def main():
    frames = []
    for i in range(20000):
        frames.append(random.randint(0, t_frames))
    frames = set(frames)
    for p in tqdm.tqdm(frames):
        a.get_frame(p)

main()
# src2.set_output(0)
