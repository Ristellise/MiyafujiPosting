import importlib.util
import pathlib
import subprocess
from types import TracebackType
from typing import Type, Iterator, AnyStr, Iterable

import click
import tqdm as tqdm
import vapoursynth
from typing.io import BinaryIO


class ProgressWrapper(BinaryIO):

    def __init__(self, wrapped, progress, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wrapped = wrapped
        self.progress = progress

    def write(self, s):
        self.wrapped.write(s)
        self.progress.update(len(s))

    def close(self) -> None:
        self.wrapped.close()

    def fileno(self) -> int:
        return self.wrapped.fileno()

    def flush(self) -> None:
        self.wrapped.flush()

    def isatty(self) -> bool:
        return self.wrapped.isatty()

    def read(self, n: int = ...) -> AnyStr:
        return self.wrapped.read(n)

    def readable(self) -> bool:
        return self.wrapped.readable()

    def readline(self, limit: int = ...) -> AnyStr:
        return self.wrapped.readline(limit)

    def readlines(self, hint: int = ...) -> list[AnyStr]:
        return self.wrapped.readlines(hint)

    def seek(self, offset: int, whence: int = ...) -> int:
        return self.wrapped.seek(offset, whence)

    def seekable(self) -> bool:
        return self.wrapped.seekable()

    def tell(self) -> int:
        return self.wrapped.tell()

    def truncate(self, size: int | None = ...) -> int:
        return self.wrapped.truncate(size)

    def writable(self) -> bool:
        return self.wrapped.writable()

    def writelines(self, lines: Iterable[AnyStr]) -> None:
        return self.wrapped.writelines(lines)

    def __next__(self) -> AnyStr:
        return self.wrapped.__next__()

    def __iter__(self) -> Iterator[AnyStr]:
        return self.wrapped.__iter__()

    def __exit__(self, t: Type[BaseException] | None, value: BaseException | None,
                 traceback: TracebackType | None) -> bool | None:
        return self.wrapped.__exit__(t, traceback)


@click.command()
@click.option("-x264_args", type=click.Path(writable=True, resolve_path=True, dir_okay=False))
@click.argument("vpy", type=click.Path(exists=True, dir_okay=False))
@click.argument("output", type=click.Path(writable=True, resolve_path=True, dir_okay=False))
def run(output, vpy, x264_args):
    """
    An Extremely shitty version of vspipe that outputs to x264.

    :param output: The .264 file as an output. Note that the file name will always have a .264 file extension at the end.
    :param vpy: The vapoursynth script. The script should contain only 1 output. mic
    :param x264_args:
    :return:
    """
    output = pathlib.Path(output)
    vpy = pathlib.Path(vpy)
    if output.is_dir():
        raise Exception
    else:
        spec = importlib.util.spec_from_file_location("vpy", vpy)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        outs = list(vapoursynth.get_outputs().keys())
        if len(outs) >= 2:
            raise Exception("Found more than 1 inputs, prepare your script with 1 output only.")
        elif len(outs) == 0:
            raise Exception("No outputs found.")
        if output.with_suffix('.264').exists():
            print("[WARN]: Existing file exists, overwrite? [Yes/No]")
            prompt = input(">:")
            if prompt.lower()[0] == 'y':
                print("[INF]: Overwriting...")
            else:
                print("[INF]: Not overwriting. Exit.")
                return
        if not vpy.with_suffix('.qp').exists():
            print("[ERR]: QP file missing!")
            return
        if x264_args:
            args = x264_args
        else:
            args = ["--demuxer", "y4m",
                    "--preset veryslow ",
                    f"-o \"{output.with_suffix('.264')}\" - ",
                    "--fps 24000/1001 --range tv --colormatrix bt709 --colorprim bt709 --transfer bt709 ",
                    "--preset veryslow --crf 15 --deblock -2:-2 --min-keyint 23 --keyint 240",
                    "--ref 16 --bframes 16",
                    "--aq-mode 3 --aq-strength 0.95 --qcomp 0.72 --psy-rd 0.90:0.0 --me tesa --merange 32 ",
                    "--direct spatial --no-dct-decimate --no-fast-pskip",
                    f"--output-depth 10 --qpfile \"{vpy.with_suffix('.qp')}\""]
        with subprocess.Popen(" ".join(['x264', *args]),
                              stdin=subprocess.PIPE) as process:
            # tqdmp = tqdm.tqdm(unit='b', desc=f"[PROG]: Bytes written to: {'x264'}")
            # f = ProgressWrapper(, tqdmp)
            clip = vapoursynth.get_output(outs[0])
            if isinstance(clip, vapoursynth.VideoOutputTuple):
                clip.clip.output(process.stdin, y4m=True)
            else:
                raise NotImplementedError("Audio output not implemented!")


if __name__ == '__main__':
    run()
