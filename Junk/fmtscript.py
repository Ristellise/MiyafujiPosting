import pathlib
import sys

x264_exec = "x264"
pp = pathlib.Path(sys.argv[1]).resolve()
qp = pp.with_name(f"{pp.stem}_qpfile").with_suffix(".txt")
aa = ["vspipe",
      "--y4m",
      f"\"{pp}\" -",
      "|",
      x264_exec,
      "--demuxer y4m",
      f"-o \"{pp.with_suffix('.264')}\" -",
      "--preset veryslow",
      "--crf 15 --deblock -2:-2 --min-keyint 23 --keyint 240",
      "--ref 16 --bframes 16 --aq-mode 3 --aq-strength 0.95 --qcomp 0.72", 
      "--psy-rd 0.90:0.0 --me tesa --merange 32 --direct spatial", 
      "--no-dct-decimate --no-fast-pskip",
      f"--output-depth 10 --qpfile \"{qp}\""]
print(" ".join(aa))
