import ssl
import certifi
import geopy.geocoders
from geopy.geocoders import Nominatim
from mapview import MapView, MapMarker, MapSource
from kivy.clock import Clock
from kivy.app import App
from teammarker import TeamMarker
from client import Client
import gui


class TeamMapView(MapView):
    markerArr = []
    host_buttons = None
    event = None
    start_checking = False
    client = Client.get_instance()

    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx

    geolocator = Nominatim(user_agent="GeoTestApp")
    location = geolocator.geocode("21 Kawiory, Kraków")

    longitude = location.longitude
    latitude = location.latitude

    def __init__(self, **kwargs):
        self.event = Clock.schedule_interval(self.get_markers_in_fov, 2)
        super(TeamMapView, self).__init__(**kwargs)

    def add_host_buttons(self):
        window = App.get_running_app().root.ids.mw
        codes = ''
        i = 1
        for token in self.client.get_all_tokens():
            codes = "\n" + codes + "Team " + str(i) + ":  " + token + "\n"
            i = i + 1

        self.host_buttons = gui.BtnPopup(codes)
        window.add_widget(self.host_buttons)

    def remove_host_buttons(self):
        window = App.get_running_app().root.ids.mw
        window.remove_widget(self.host_buttons)
        self.host_buttons = None

    def get_markers_in_fov(self, *args):
        if not self.client.get_token() and self.start_checking:  # Returns you to menu if server restarted
            self.remove_widget(App.get_running_app().root.ids.tw.current_blinker)
            screen = App.get_running_app().root
            screen.current = "menu"
            self.start_checking = False
            return

        markers = self.client.get_markers()

        for mark in self.markerArr:
            self.remove_widget(mark)  # Visible by user? Nope. Efficient? HELL NAH; Easy to implement? HELL YEAH
        self.markerArr.clear()

        for marker in markers:
            self.add_mark(marker)

    def add_mark(self, marker):
        nick, lon, lat = marker
        if not self.host_buttons:
            if 'host-' in nick:
                color_num = 10
            else:
                color_num = App.get_running_app().root.ids.tw.colornum
        else:
            color_num, nick = nick.split(':', 1)
            color_num = int(color_num)

        popup = TeamMarker(lat=lat, lon=lon, nick=nick, colorNum=color_num)
        self.add_widget(popup)
        self.markerArr.append(popup)

    def show_full_team(self):  # centers map on the player
        tw = App.get_running_app().root.ids.tw
        self.center_on(tw.current_blinker.lat, tw.current_blinker.lon)

        markers = self.client.get_markers()
        if not markers:
            self.zoom = 16
            return

        min_lon = min(i[1] for i in markers)
        min_lat = min(i[2] for i in markers)
        max_lon = max(i[1] for i in markers)
        max_lat = max(i[2] for i in markers)

        while True:
            d_lat, d_lon, u_lat, u_lon = self.get_bbox()
            if min_lat < d_lat or max_lat > u_lat or min_lon < d_lon or max_lon > u_lon:
                break
            self.zoom = self.zoom + 1
        while True:
            d_lat, d_lon, u_lat, u_lon = self.get_bbox()
            if min_lat > d_lat and max_lat < u_lat and min_lon > d_lon and max_lon < u_lon:
                return
            self.zoom = self.zoom - 1
