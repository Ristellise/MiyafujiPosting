"""
Tools for dumb ideas.
"""

import numpy
import vapoursynth
import inspect

try:
    from PIL import Image
    FuncWrite = True
except ImportError:
    FuncWrite = False

def tag(clip:vapoursynth.VideoNode):
    """
    Returns a clip with the name of the clip (if possible).
    :param clip:
    :return:
    """
    ref_id = str(id(clip))
    index = len(vapoursynth.get_outputs()) + 1
    ref_name = f"Clip {index}"

    for x in inspect.currentframe().f_back.f_locals.items():  # type: ignore
        if (str(id(x[1])) == ref_id):
            ref_name = x[0]
            break

    ref_name = ref_name.title()
    return clip.text.Text(ref_name, alignment=7, scale=2)

def Write(clip: vapoursynth.VideoNode, filepath, frame=0):
    """
    Writes a file using pillow.
    Note that this is kinda stingy on clip type. Only RGB24 is supported.
    Convert using wformat of this library.
    :param frame:
    :param clip:
    :param filepath:
    :return:
    """
    if FuncWrite:
        with clip.get_frame(frame) as vframe:
            print(vframe.format)
            if vframe.format.name != "RGB24":
                raise Exception("Frame given not in RGB24.")
            rPlane = numpy.ctypeslib.as_array(vframe[0]).view(numpy.uint8)
            gPlane = numpy.ctypeslib.as_array(vframe[1]).view(numpy.uint8)
            bPlane = numpy.ctypeslib.as_array(vframe[2]).view(numpy.uint8)
            rgb = (rPlane[..., numpy.newaxis], gPlane[..., numpy.newaxis], bPlane[..., numpy.newaxis])
            im = Image.fromarray(numpy.concatenate(rgb, axis=-1), "RGB")
            im.save(filepath)
    else:
        raise NotImplementedError("PIL/Pillow not detected, is your env borked?")
