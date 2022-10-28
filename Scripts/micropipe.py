import contextlib
import os
import pathlib
import subprocess
import sys

import click
import vapoursynth
import yaml


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
@click.option("--executable", default="x264")
@click.argument("output", type=click.Path(writable=True, resolve_path=True, dir_okay=False))
def run(yaml_config, executable, vpy, output):
    """

    Micropipe: An alternative vspipe replacement.

    :param yaml_config: The YAML config for input. the
    :param executable: The executable to invoke.
    :param output: The file as an output.
    :param vpy: The vapoursynth script. The script should contain only 1 output. Micropipe will prompt if the script does not provide a single output.
    :return:
    """
    output = pathlib.Path(output)
    vpy = pathlib.Path(vpy)

    if output.is_dir():
        raise Exception("Output is a directory, specify an actual file location.")
    output = output.resolve()
    if isinstance(yaml_config,str):
        yaml_config = pathlib.Path(yaml_config)
    cfg = yaml_config.resolve()
    print("[INF]: Load pipe config...")
    if cfg.exists():
        with open(cfg, "r", encoding="utf-8") as f:
            pipe_config = yaml.safe_load(f)
    else:
        print(f"Failed to find: {cfg}")
        return -1
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
        if not isinstance(clip, vapoursynth.VideoOutputTuple):
            raise NotImplementedError("Audio output not implemented!")
        fps = f"{clip.clip.fps.numerator}/{clip.clip.fps.denominator}"

        exec_config = pipe_config.get(executable)
        if not exec_config:
            print(f"[ERR]: Cannot find: {executable} Configuration in the yml file.")
        exec_confg_parsed = {}
        for cfg in exec_config:
            exec_confg_parsed[list(cfg.keys())[0]] = list(cfg.values())[0]

        mapping = {
            "_output": str(output),
            "_fps": str(fps),
            "_qp": str(vpy.with_suffix('.qp')),
            "_frames": str(clip.clip.num_frames),
            "_input": "-"
        }
        has_input = False
        mapping_key = list(mapping.keys())
        for k, v in exec_confg_parsed.items():
            if v in mapping_key:
                print(f"[INF]: Setting {v} of {k} to: {mapping[v]}")
                exec_confg_parsed[k] = mapping[v]
                if v == "_input":
                    has_input = True

        list_args = [f"{k}" if v == "_" else f"{k} \"{str(v).format(output=output, vpy=vpy.with_suffix('.qp'))}\""
                     for k, v in exec_confg_parsed.items()] + ['-'] if not has_input else []
        str_args = " ".join([executable, " ".join(list_args)])
        print(f"Subprocess Arguments\n==================\n{str_args}\n====================================")
        print(f"Starting Encode. Please have patience...")
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
        # out_clip = run(src=True)[0]
        if os.path.isfile(qpfile) is False:
            with open(qpfile, 'w') as o:
                for f in find_scene_changes(vapoursynth.get_output(outs[0]).clip,
                                            mode=SceneChangeMode.WWXD_SCXVID_UNION):
                    o.write(f"{f} I -1\n")


if __name__ == '__main__':
    root()
