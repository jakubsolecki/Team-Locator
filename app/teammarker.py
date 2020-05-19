from kivy.garden.mapview import MapMarkerPopup
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
from kivy.graphics import *

from app.colordict import color_dictionary


class TeamMarker(MapMarkerPopup):
    colorNum = 0
    nick = 'placeholder'
    color = get_color_from_hex(color_dictionary[colorNum])

    def __init__(self, nick, colorNum, *args, **kwargs):
        self.colorNum = colorNum
        self.color = get_color_from_hex(color_dictionary[colorNum])
        self.nick = nick
        super(TeamMarker, self).__init__(*args, **kwargs)
        with self.canvas:
            Color(rgba=self.color)

