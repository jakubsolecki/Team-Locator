import kivy
import ssl
import certifi
import geopy.geocoders
from geopy.geocoders import Nominatim
from mapview import MapView, MapMarker, MapSource
from kivy.clock import Clock
from kivy.garden.mapview import MapMarkerPopup
from kivy.app import App

from teammarker import TeamMarker
from gpsblinker import GpsBlinker

from app.client import Client
import app.gui


class TeamMapView(MapView):
    refresh_timer = None
    isHost = True
    markerArr = []

    client = Client.get_instance()

    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx

    geolocator = Nominatim(user_agent="GeoTestApp")
    location = geolocator.geocode("21 Kawiory, Kraków")
    # location = droid.getLastKnownLocation().result
    # location = location.get('gps') or location.get('network')
    # lon = droid.geocode(location['longitude'])
    # lat = droid.geocode(location['latitude'])
    longitude = location.longitude
    latitude = location.latitude


    def __init__(self, **kwargs):
        Clock.schedule_interval(self.get_markers_in_fov, 2)
        super(TeamMapView, self).__init__(**kwargs)

    # Mock markers
    # TODO: all markers to single 2D-array, markers[0] is local position and move them to another class?
    markers = [[longitude + 0.001, latitude - 0.001], [longitude + 0.0001, latitude + 0.001],
               [longitude + 0.01, latitude - 0.001], [longitude + 0.001, latitude - 0.01]]

    def add_host_buttons(self):
        if self.isHost:
            window = App.get_running_app().root.ids.mw
            btn = app.gui.BtnPopup("Right now new button spawns on zoom. \n"
                                   "Spawn single time after getting host via server\n"
                                   "And improve displaying label on popup to handle 10 teams")
            window.add_widget(btn)

    def draw_markers(self):
        try:
            self.refresh_timer.cancel()
        except:  # TODO: remove?
            pass
        self.refresh_timer = Clock.schedule_once(self.get_markers_in_fov, 0.1)

    def get_markers_in_fov(self, *args):
        for mark in self.markerArr:
            self.remove_widget(mark)  # clear old widgets. Visible by user? Hope not. Efficient? HELL NAH
        self.markerArr.clear()

        d_lat, d_lon, u_lat, u_lon = self.get_bbox()
        for marker in self.markers:
            if d_lat < marker[1] < u_lat and d_lon < marker[0] < u_lon:
                self.add_mark(marker)

    def add_mark(self, marker):
        colornum = App.get_running_app().root.ids.tw.colornum
        lat, lon = marker[1], marker[0]
        popup = TeamMarker(lat=lat, lon=lon, nick="Protagoras", colorNum=colornum)
        self.add_widget(popup)
        self.markerArr.append(popup)

        pass

    def show_full_team(self):  # centers map to middle of the team, not player
        min_lon = min(i[0] for i in self.markers)
        min_lat = min(i[1] for i in self.markers)
        max_lon = max(i[0] for i in self.markers)
        max_lat = max(i[1] for i in self.markers)

        self.lon = (min_lon + max_lon) / 2
        self.lat = (min_lat + max_lat) / 2

        self.zoom = self.zoom + 1

        while True:
            d_lat, d_lon, u_lat, u_lon = self.get_bbox()
            if min_lat > d_lat and max_lat < u_lat and min_lon > d_lon and max_lon < u_lon:
                return
            self.zoom = self.zoom - 1

    pass
