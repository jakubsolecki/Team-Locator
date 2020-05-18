from kivy.garden.mapview import MapMarkerPopup
from kivy.animation import Animation
from kivy.uix.label import Label


class TeamMarker(MapMarkerPopup):
    text = 'placeholder'
    isRed = True


    if isRed:
        color = [1, 0.3, 0.3, 1]
    else:
        color = [0.1, 0.8, 1, 1]

    def __init__(self, text, *args, **kwargs):
        self.text = text
        super(TeamMarker, self).__init__(*args, **kwargs)
