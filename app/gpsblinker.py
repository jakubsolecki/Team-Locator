from kivy.garden.mapview import MapMarker
from kivy.animation import Animation


class GpsBlinker(MapMarker):
    isRed = False

    #TODO: MAKE BETTER LOOKING POINTS
    if isRed:
        color = [1, 0.3, 0.3, 0.6]
    else:
        color = [0.1, 0.8, 1, 0.6]

    def blink(self):
        self.outer_opacity = 1

        # Animation that changes the blink size and opacity
        anim = Animation(outer_opacity=0, blink_size=50)
        # When the animation completes, reset the animation, then repeat
        anim.bind(on_complete=self.reset)
        anim.start(self)


    def reset(self, *args):
        self.outer_opacity = 1
        self.blink_size = self.default_blink_size
        self.blink()