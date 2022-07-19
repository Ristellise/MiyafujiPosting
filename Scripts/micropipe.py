import contextlib
import importlib.util
import os
import pathlib
import subprocess
import yaml
import sys

import click
import vapoursynth


@contextlib.contextmanager
def working_directory(path):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = pathlib.Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


@contextlib.contextmanager
def add_to_path(p):
    import sys
    old_path = sys.path
    old_modules = sys.modules
    sys.modules = old_modules.copy()
    sys.path = sys.path[:]
    sys.path.insert(0, p)
    try:
        yield
    finally:
        sys.path = old_path
        sys.modules = old_modules

@click.group()
def root():
    pass

@root.command()
@click.option("-yaml_config",
              type=click.Path(exists=True),
              default=pathlib.Path(__file__).parent.joinpath("micropipe-default.yaml"))
@click.argument("vpy", type=click.Path(exists=True, dir_okay=False))
@click.argument("output", type=click.Path(writable=True, resolve_path=True, dir_okay=False))
def run(output, vpy, yaml_config):
    """
    An portable vspipe that outputs to x264.

    :param output: The .264 file as an output. Note that the file name will always have a .264 file extension at the end.
    :param vpy: The vapoursynth script. The script should contain only 1 output. micropipe will prompt if the script does not provide a single output
    :return:
    """
    output = pathlib.Path(output)
    vpy = pathlib.Path(vpy)

    if output.is_dir():
        raise Exception("Output is a directory, specify an actual file location.")
    output = output.resolve()
    cfg = yaml_config.resolve()
    print("[INF]: Load pipe config...")
    if cfg.exists():
        with open(cfg, "r", encoding="utf-8") as f:
            pipe_config = yaml.safe_load(f)
    print(f"[INF]: Pipe config loaded from: {str(cfg.resolve())}")
    print(vpy.resolve().parent)
    with working_directory(vpy.resolve().parent):
        sys.path.append(str(vpy.resolve().parent))
        try:
            ast_compiled = compile(vpy.resolve().read_bytes(), str(vpy.resolve().name), 'exec', optimize=2)
            script_globals = dict([('__file__', sys.argv[0])])
            exec(ast_compiled, script_globals)
        except BaseException as e:
            raise e
        outs = list(vapoursynth.get_outputs().keys())

        # VPY File checks.
        if len(outs) >= 2:
            raise Exception("Found more than 1 inputs, prepare your script with 1 output only.")
        elif len(outs) == 0:
            raise Exception("No outputs found.")
        if output.with_suffix('.264').exists():
            print("[WARN]: Existing file exist, overwrite? [Yes/No]")
            prompt = input(">:")
            if prompt.lower()[0] == 'y':
                print("[INF]: Overwriting...")
            else:
                print("[INF]: Not overwriting. Exit.")
                return
        if not vpy.with_suffix('.qp').exists():
            raise Exception("[ERR]: QP file missing!")
        print("[INF]: Prepare Clip")
        clip = vapoursynth.get_output(outs[0])
        #print(pipe_config)
        fps = f"{clip.clip.fps.numerator}/{clip.clip.fps.denominator}"
        x264 = {}
        for cfg in pipe_config['x264']:
            x264[list(cfg.keys())[0]] = list(cfg.values())[0]
        pipe_config['x264'] = x264
        print(pipe_config)
        if pipe_config['x264'].get('--fps', "_auto") == "_auto":
            print(f"[INF]: Setting framerate to: {fps}")
            pipe_config['x264']['--fps'] = fps

        args = " ".join([f"{k}" if v == "_" else f"{k} \"{str(v).format(output=output.with_suffix('.264'), vpy=vpy.with_suffix('.qp'))}\""
                         for k, v in pipe_config['x264'].items()] + [f'--frames {clip.clip.num_frames}','-'])
        str_args = " ".join(['x264', args])

        # args = ["--demuxer", "y4m",
        #         "--preset veryslow ",
        #         f"-o \"{output.with_suffix('.264')}\" - ",
        #         "--fps 24000/1001 --range tv --colormatrix bt709 --colorprim bt709 --transfer bt709 ",
        #         "--preset veryslow --crf 15 --deblock -2:-2 --min-keyint 23 --keyint 240",
        #         "--ref 16 --bframes 16",
        #         "--aq-mode 3 --aq-strength 0.95 --qcomp 0.72 --psy-rd 0.90:0.0 --me tesa --merange 32 ",
        #         "--direct spatial --no-dct-decimate --no-fast-pskip",
        #         f"--output-depth 10 --qpfile \"{vpy.with_suffix('.qp')}\""]
        # print(" ".join(['x264', *args]))
        print(str_args)
        with subprocess.Popen(str_args,
                              stdin=subprocess.PIPE) as process:
            if isinstance(clip, vapoursynth.VideoOutputTuple):
                clip.clip.output(process.stdin, y4m=True)
            else:
                raise NotImplementedError("Audio output not implemented!")


@root.command()
@click.argument("vpy", type=click.Path(exists=True, dir_okay=False))
@click.argument("qpfile", type=click.Path(writable=True, resolve_path=True, dir_okay=False))
def qpfile(vpy, qpfile):
    """
    Generates a qpfile.
    """
    qpfile = pathlib.Path(qpfile)
    vpy = pathlib.Path(vpy)

    if qpfile.is_dir():
        raise Exception("Output is a directory, specify an actual file location.")
    qpfile = qpfile.resolve()
    with working_directory(vpy.resolve().parent):
        sys.path.append(str(vpy.resolve().parent))
        try:
            ast_compiled = compile(vpy.resolve().read_bytes(), str(vpy.resolve().name), 'exec', optimize=2)
            script_globals = dict([('__file__', sys.argv[0])])
            exec(ast_compiled, script_globals)
        except BaseException as e:
            raise e
        outs = list(vapoursynth.get_outputs().keys())
        if len(outs) >= 2:
            raise Exception("Found more than 1 inputs, prepare your script with 1 output only.")
        elif len(outs) == 0:
            raise Exception("No outputs found.")
        
        from lvsfunc.render import find_scene_changes, SceneChangeMode
        #out_clip = run(src=True)[0]
        if os.path.isfile(qpfile) is False:
            with open(qpfile, 'w') as o:
                for f in find_scene_changes(vapoursynth.get_output(outs[0]).clip, mode=SceneChangeMode.WWXD_SCXVID_UNION):
                    o.write(f"{f} I -1\n")


if __name__ == '__main__':
    root()
