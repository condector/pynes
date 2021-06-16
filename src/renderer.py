from renderers.pygame import PygameRenderer
from renderers.ncurse import NcurseRenderer
from renderers.pyglet import PygletRenderer


class RendererManager:
    def __init__(self, renderer="pygame"):
        if renderer == "pygame":
            self.display = PygameRenderer()
        elif renderer == "pyglet":
            self.display = PygletRenderer()
        elif renderer == "ncurse":
            self.display = NcurseRenderer()