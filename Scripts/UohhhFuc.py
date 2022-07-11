"""
UohhhFuc: Shinon's rewritten functions from discord. Contains the following:
 - z_decensor (Zastin's decensor Script)
 - setsu_cubic (Setsugen's Bicubic (Used in Summer time Render (WEB)))
"""
from vskernels import Bicubic
from vsutil import split, fallback, iterate
import vapoursynth as vs
import debandshit as db
import logging

logger = logging.getLogger('UohhhFuc')
core = vs.core

try:
    expr_func = core.akarin.Expr
    logger.info("Using Akarin Expr")
except Exception:
    expr_func = core.std.Expr
    logger.info("Using Std Expr")

"""
clip, cen, cenmask = decensor(vrv, atx, atxref, radius=5, min_length=1, smooth=0, thr=, bordfix=10, debug=False,
                              output=True)
"""

def expando(clip, mode='minm',sy:int=2,sc:int=2) -> vs.VideoNode:
    yp = sy >= sc
    yiter = 1 if yp else 0
    cp = sc >= sy
    citer = 1 if cp else 0
    planes = [0] if yp and not cp else [1, 2] if cp and not yp else [0, 1, 2]
    coor = [0, 1, 0, 1, 1, 0, 1, 0] if (max(sy, sc) % 3) != 1 else [1] * 8

    if sy > 0 or sc > 0:
        if mode =='minm':
            return expando(clip.std.Minimum(planes=planes, coordinates=coor),'minm', sy=sy - yiter, sc=sc - citer)
        elif mode == 'maxm':
            return expando(clip.std.Maximum(planes=planes, coordinates=coor),'minm', sy=sy - yiter, sc=sc - citer)
    else:
        return clip


def rangemask(clip: vs.VideoNode, rad: int = 2, radc: Optional[int] = None) -> vs.VideoNode:
    isRGB = clip.format.color_family == vs.RGB
    radc = (rad if isRGB else 0) if radc is None else radc
    if radc == 0:
        clip.fmtc.re
        clip = togray(clip, int16=False)
    ma = maxm(clip, rad, radc)
    mi = minm(clip, rad, radc)

    expr = 'x y -'
    if not rad:
        expr = ['', 'x y -']
    if not radc:
        expr = ['x y -', '']

    return core.std.Expr([ma, mi], expr)


def setsu_cubic():
    """
    Returns a Bicubic based on some... Questionable values from Setsugen.
    "The Geneva convention prohibits the use of this." - Light

    :return: Bicube with preset b and c values.
    """
    return Bicubic(-0.26470935063297507, 0.7358829780174403)


def z_decensor(source, decensored, decensored_ref,
               radius=5, min_length=3, smooth=6,
               thr=5 << 8, bordfix=10, alt=None,
               post_process=None, **kwargs):
    """
    This function detects common "censor" elements (Light beams / Black bars).
    The source and the decensored clip are both absolute diff'd, binarized and them compared.
    A mask is created when the comparison happens.
    If the script detects a censor (The mask is resized to 1 pixel for detection),
    it will use the censor clip parts contained in the mask.

    This script is kinda slow. You should clip to the sections where you think there is censored elements.

    :param source: The Base Source clip, treat this as the source that is censored.
    :param decensored: The Decensored clip.
    :param decensored_ref: The Decensored clip referance.
    :param radius: The radius to shrink the difference.
    :param min_length: The minimum clip length to detect
    :param smooth: Smooths the mask, which catches edges shadows if it has been missed.
    :param thr: Threshold to detect if a "Scene" has been modified or not.
    :param bordfix: Fixes the border
    :param alt: Alternative clip to be used instead of source when source is unavailable.
    :param post_process: Apply any additional post_processing before the frames are compared and outputted.
    :param debug: Debug logs the current frame source being viewed as Text in the output.
    :param output: Debug logs the output frames it detected.
    :return: Returns the final (hopefully decensored) clip, the original censored clip and the mask used for detection.
    """

    def combine(comb):
        return expr_func(comb, 'x y max')

    def minm(minm_clip: vs.VideoNode, sy: int = 2, sc: int = 2) -> vs.VideoNode:
        return expando(minm_clip, 'minm', sy=sy, sc=sc)

    def maxm(maxm_clip: vs.VideoNode, sy: int = 2, sc: int = 2) -> vs.VideoNode:
        return expando(maxm_clip, 'maxm', sy=sy, sc=sc)

    debug = kwargs.get('debug', False)
    output = kwargs.get('debug', False)

    if thr is None:
        raise Exception("Threshold cannot be None!")

    core = vs.core

    fmt = source.format
    peak = (1 << fmt.bits_per_sample) - 1
    thr = fallback(thr, 24 << (fmt.bits_per_sample - 8))
    base_src = fallback(alt, source)

    clip = expr_func([source, decensored_ref], 'x y - abs')

    mask = expr_func(split(clip.resize.Point(format=source.format.replace(subsampling_w=0, subsampling_h=0).id)),
                     'x y z max max')
    mask1_ = mask.std.Binarize(3 * 256).std.Minimum().std.Minimum()
    mask1 = iterate(mask1_, core.std.Maximum, 15)
    mask2 = iterate(iterate(mask.std.Binarize(25 << 8), core.std.Minimum, 5), core.std.Maximum, 25)
    mask = combine([mask1, mask2])
    mask = expr_func([mask, combine([mask1_, mask2]).fmtc.bitdepth(bits=32, fulls=1).fmtc.resample(1, 1,
                                                                                                   kernel='box').std.Expr(
        f'x 0.5 > 1 0 ?', vs.GRAY8).resize.Point(1920, 1080)], 'y 65535 x ?')
    mask = maxm(mask, sw=50)[-1]
    mask = minm(mask, sw=30)[-1]
    mask = minm(mask, sw=20, threshold=65536 // 21)[-1]

    clip = core.resize.Point(clip, format=fmt.replace(subsampling_w=0, subsampling_h=0).id).std.Binarize(thr)
    clip = expr_func(split(clip), 'x y z max max')
    clip0 = iterate(clip, core.std.Minimum, radius)
    vrv = source.rgvs.RemoveGrain(20)
    decensored_ref = decensored_ref.rgvs.RemoveGrain(20)
    clip = expr_func(split(
        expr_func([db.rangemask(vrv, 3, 2), db.rangemask(decensored_ref, 3, 2)], 'x y - abs').std.Binarize(
            20 * 256).resize.Point(format=fmt.replace(subsampling_w=0, subsampling_h=0).id)), 'x y z max max')
    clip = combine([clip0, clip])

    def binarize_frame(n, f, clip=clip):
        return core.std.BlankClip(clip, 1, 1, color=peak if f.props.PlaneStatsMax else 0)

    prop_src = clip.std.Crop(bordfix, bordfix, bordfix, bordfix).std.PlaneStats()
    clip = core.std.FrameEval(core.std.BlankClip(clip, 1, 1), binarize_frame, prop_src=prop_src)

    if min_length == 2:
        med = clip.tmedian.TemporalMedian(1)  # faster than Clense
        clip = expr_func([clip, med], 'x y min')
    if min_length > 2:
        avg = core.misc.AverageFrames(clip, [1] * ((min_length * 2) + 1)).std.Binarize(peak // 2)
        clip = expr_func([clip, avg], 'x y min')
    if smooth > 0:
        clip = zzt.shiftframes(clip, [-smooth, smooth])
        clip = combine(clip)
        clip = core.misc.AverageFrames(clip, [1] * ((smooth * 2) + 1))
        smooth //= 2
        mask = zzt.shiftframes(mask, [-smooth, smooth])
        mask = combine(mask)
        mask = core.misc.AverageFrames(mask, [1] * ((smooth * 2) + 1))

    if output:
        import os
        clip = clip.std.PlaneStats()
        out_txt = ''
        for i in range(1, clip.num_frames - 1):
            if clip.get_frame(i).props.PlaneStatsMax > 0:
                if clip.get_frame(i - 1).props.PlaneStatsMax > 0:
                    if clip.get_frame(i + 1).props.PlaneStatsMax == 0:
                        out_txt += f'{i}]'
                elif clip.get_frame(i + 1).props.PlaneStatsMax > 0:
                    out_txt += f'[{i} '
                else:
                    out_txt += f' {i} '
        out_path = os.path.expanduser("~") + "/Desktop/censored_scenes.txt"
        with open(out_path, "w") as text_file:
            text_file.write(out_txt)

    if callable(post_process):
        decensored = post_process(decensored)

    if debug:
        base_src = base_src.text.Text('Censored')
        decensored = decensored_ref.text.Text('Horny')

    def _merge_tits(_, f):
        weight = f.props.PlaneStatsMax
        if weight == peak:
            return base_src.std.MaskedMerge(decensored, mask, [0, 1, 2], True)
        if weight == 0:
            return base_src
        return core.std.Merge(base_src, base_src.std.MaskedMerge(decensored, mask, [0, 1, 2], True), weight / peak)

    return [core.std.FrameEval(base_src, _merge_tits, prop_src=clip.std.PlaneStats()), clip, mask]
