from kivy.garden.mapview import MapMarkerPopup
from kivy.animation import Animation
from kivy.utils import get_color_from_hex

from app.colordict import color_dictionary


class GpsBlinker(MapMarkerPopup):
    text = ''
    color = get_color_from_hex(color_dictionary[2])

    animColor = []
    zipper = zip(color, [0, 0, 0, 0.4])
    for c_i, aC_i in zipper:
        animColor.append(c_i - aC_i)  # We need alpha < 1 for blink animation

    # TODO: MAKE BETTER LOOKING POINTS
    # TODO: INHERIT FROM TeamMarker??

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

    def __init__(self, text='PLACEHOLDER', *args, **kwargs):
        self.text = text
        super(GpsBlinker, self).__init__(*args, **kwargs)
