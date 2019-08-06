import copy

import numpy as np
from PIL import Image

from .svg_util import add_background, svg_to_np, set_svg_bounds_centered, empty_svg

compute_size = (792, 792)
target_size = (792, 600)
svg_target_size_x = 384  # in um for target field size
svg_target_size_y = int(svg_target_size_x * float(compute_size[0]) / compute_size[1])


class Frame(object):
    def __init__(self, svg=None, raster=None, hologram=None, Zlevel=0, frame_num=None, duration=0):
        self.svg = svg
        self.raster = raster
        self.Zlevel = Zlevel
        self.frame_num = frame_num
        self.duration = duration
        self.hologram = hologram
        self.computedpattern = None

    def rasterize(self):
        assert self.svg
        self.set_svg_bounds()

        dpi = (72 * svg_target_size_x / float(compute_size[0]))
        raster = svg_to_np(self.svg, dpi)
        assert np.diff(raster[:, :, :3]).sum() == 0, 'All svg color channels should be the same'
        # there's some rounding issues with rasterization depending on dpi, poking in cairo didn't get far yet
        assert compute_size == raster.shape[:-1]

        self.raster = raster[:, :, 0]

    @classmethod
    def from_svg_path(self, svgpath, *args, **kwargs):
        with open(svgpath) as f:
            svg = f.read()
        return self(svg, *args, **kwargs)

    @classmethod
    def from_raster_path(self, rasterpath, *args, **kwargs):
        raster = np.asarray(Image.open(rasterpath))
        return self(raster=raster, *args, **kwargs)

    @classmethod
    def blankframe(cls, *args, **kwargs):
        svg = empty_svg()
        raster = np.zeros(target_size)
        return cls(svg=svg, raster=raster, *args, **kwargs)

    def copy(self):
        return copy.deepcopy(self)

    def set_svg_bounds(self):
        self.svg = add_background(set_svg_bounds_centered(self.svg, svg_target_size_x, svg_target_size_y))
