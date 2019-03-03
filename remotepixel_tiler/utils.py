"""Utility functions."""

import numpy

from rio_color.operations import parse_operations
from rio_color.utils import scale_dtype, to_math_type

from rio_tiler.utils import linear_rescale


def _postprocess(tile, mask, tilesize, rescale=None, color_formula=None):
    if tile is None:
        # Return empty tile
        tile = numpy.zeros((1, tilesize, tilesize), dtype=numpy.uint8)
        mask = numpy.zeros((tilesize, tilesize), dtype=numpy.uint8)
    else:
        if rescale:
            rescale = (tuple(map(float, rescale.split(","))),) * tile.shape[0]
            for bdx in range(tile.shape[0]):
                tile[bdx] = numpy.where(
                    mask,
                    linear_rescale(
                        tile[bdx], in_range=rescale[bdx], out_range=[0, 255]
                    ),
                    0,
                )
            tile = tile.astype(numpy.uint8)

        if color_formula:
            for ops in parse_operations(color_formula):
                tile = scale_dtype(ops(to_math_type(tile)), numpy.uint8)

    return tile, mask
