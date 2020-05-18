from kivy.garden.mapview import MapMarkerPopup
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex

from app.colordict import color_dictionary


class TeamMarker(MapMarkerPopup):
    text = 'placeholder'
    color = get_color_from_hex(color_dictionary[2])

    def __init__(self, text, *args, **kwargs):
        self.text = text
        super(TeamMarker, self).__init__(*args, **kwargs)
