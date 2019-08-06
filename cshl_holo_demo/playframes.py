from __future__ import print_function, division
import numpy as np
import pyglet
from pyglet.gl import *
import time
import gevent
from io import BytesIO
from PIL import Image

from . import frame


class Frameplayer(pyglet.window.Window):
    def __init__(self, width=800, height=600, fullscreen=True):
        platform = pyglet.window.get_platform()
        display = platform.get_default_display()

        screen_h = None
        if fullscreen == 'auto':
            # if 800x600 display attached, use that and fullscreen = True
            for i, screen in enumerate(display.get_screens()):
                if screen.width == width and screen.height == height:
                    screen_h = screen
                    fullscreen = True
                    break
            if fullscreen == 'auto':  # didn't find a 800x600 screen
                print("Screen set to auto, but didn't find SLM")
                fullscreen = False

        if screen_h is None:
            screen_h = display.get_screens()[-1]

        if fullscreen is True:
            super(Frameplayer, self).__init__(vsync=True, screen=screen_h, fullscreen=True)
            # TODO check width and height are correct if not auto?
        else:
            super(Frameplayer, self).__init__(width=width, height=height, vsync=True, screen=screen_h, fullscreen=fullscreen)
        self.set_caption("Frameplayer")

        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

        self.nframes = None
        self.frames = None
        pyglet.clock.set_fps_limit(60)
        self.fps_display = pyglet.clock.ClockDisplay()

        self.starttime = None

    def loadframes(self, frames):
        self.frames = [self.to_texture(fr.hologram) for fr in frames]
        self.durations = [fr.duration for fr in frames]
        self.currentframe = 0

    def to_texture(self, framedata):
        # TODO assert uint8? and size?
        temp = BytesIO()
        Image.fromarray(framedata.T).save(temp, format='png')
        return pyglet.image.load('.png', file=temp).get_texture()

    def update(self, dt):
        gevent.sleep(.001)

    def on_draw(self):
        pyglet.gl.glClearColor(0, 0, 0, 0)
        self.clear()

        if time.time() - self.starttime >= self.durations[self.currentframe]:
            self.currentframe += 1
            self.starttime = time.time()

            if self.currentframe == len(self.frames):
                pyglet.app.event_loop.has_exit = True
                self.currentframe = 0

        self.frames[self.currentframe].blit(0, 0, 0)

    def playframes(self):
        self.starttime = time.time()
        pyglet.app.run()

    def playframes_nonblocking(self):
        self.starttime = time.time()
        return gevent.spawn(pyglet.app.run)

    def playframes_with_callback(self, callback, calltime):
        self.starttime = time.time()

        def dummy(dt):
            callback()

        pyglet.clock.schedule_once(dummy, calltime)
        pyglet.app.run()

    def quick_display(self, image):
        blank = frame.Frame.blankframe(duration=.1)
        blank.hologram = image.astype(np.uint8)
        self.loadframes([blank])
        self.playframes()
