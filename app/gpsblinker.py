from kivy.garden.mapview import MapMarkerPopup
from kivy.animation import Animation
from kivy.properties import ObjectProperty
from kivy.utils import get_color_from_hex
from kivy.graphics import *

from app.colordict import color_dictionary


class GpsBlinker(MapMarkerPopup):
    animColor = []
    # TODO: INHERIT FROM TeamMarker??
    def set_properties(self, text, color_number):
        self.text = text
        self.color = get_color_from_hex(color_dictionary[color_number])
        self.nick_label.text = text
        with self.canvas:
            Color(rgba=self.color)

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

    def __init__(self, color_number=0,  nick='PLACEHOLDER', *args, **kwargs):
        self.colorNum = color_number
        self.color = get_color_from_hex(color_dictionary[color_number])
        self.nick = nick

        zipper = zip(self.color, [0, 0, 0, 0.4])
        for c_i, aC_i in zipper:
            self.animColor.append(c_i - aC_i)  # We need alpha < 1 for blink animation

        super(GpsBlinker, self).__init__(*args, **kwargs)