import time
import numpy as np
from playframes import Frameplayer

width = 1920
height = 1080
fp = Frameplayer(width, height)
xx, yy = np.meshgrid(np.arange(width), np.arange(height))

for t in np.linspace(1, 20, 100):
    fp.quick_display((xx % (4 * t)) * 255 / (4 * t), duration=.1)
