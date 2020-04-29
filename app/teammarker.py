from kivy.garden.mapview import MapMarker
from kivy.animation import Animation


class TeamMarker(MapMarker):
    isRed = True

    if isRed:
        color = [1,0.3,0.3,1]
    else:
        color = [0.1,0.8,1,1]


