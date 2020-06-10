from kivy.garden.mapview import MapMarkerPopup
from kivy.utils import get_color_from_hex
from kivy.graphics import *
from colordict import color_dictionary


class TeamMarker(MapMarkerPopup):
    def __init__(self, nick, colorNum, *args, **kwargs):
        self.color = get_color_from_hex(color_dictionary[colorNum])
        self.nick = nick
        super(TeamMarker, self).__init__(*args, **kwargs)
        with self.canvas:
            Color(rgba=self.color)

