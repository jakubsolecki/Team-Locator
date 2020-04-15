import kivy
from geopy.geocoders import Nominatim
from mapview import MapView, MapMarker, MapSource
from kivy.clock import Clock
from kivy.garden.mapview import MapMarkerPopup
from kivy.app import App


class TeamMapView(MapView):
    refresh_timer = None

    geolocator = Nominatim(user_agent="GeoTestApp")
    location = geolocator.geocode("21 Kawiory, Kraków")
    # location = droid.getLastKnownLocation().result
    # location = location.get('gps') or location.get('network')
    # lon = droid.geocode(location['longitude'])
    # lat = droid.geocode(location['latitude'])
    longitude = location.longitude
    latitude = location.latitude

    #Mock markers
    #TODO: all markers to single 2D-array, markers[0] is local position and move them to another class?, add unique ID for each marker?
    markers = [[longitude, latitude], [longitude + 0.0001, latitude + 0.001], [longitude + 0.01, latitude - 0.001], [longitude + 0.001, latitude - 0.01]]

    def draw_markers(self):
        try:
           self.refresh_timer.cancel()
        except:
            pass
        self.refresh_timer = Clock.schedule_once(self.get_markers_in_fov, 0.1)



    def get_markers_in_fov(self, *args):
        dLat, dLon, uLat, uLon = self.get_bbox()
        for marker in self.markers:
            if (marker[1] > dLat and marker[1] < uLat and marker[0] > dLon and marker[0] < uLon):
                self.add_mark(marker)


    def add_mark(self, marker):
        lat, lon = marker[1], marker[0]
        popup = MapMarkerPopup(lat=lat, lon=lon)
        self.add_widget(popup)
        pass

    def show_full_team(self): #centers map to middle of the team, not player
        minLon = min(i[0] for i in self.markers)
        minLat = min(i[1] for i in self.markers)
        maxLon = max(i[0] for i in self.markers)
        maxLat = max(i[1] for i in self.markers)

        self.lon = (minLon + maxLon)/2
        self.lat = (minLat + maxLat)/2

        self.zoom = self.zoom + 1

        while True:
            dLat, dLon, uLat, uLon = self.get_bbox()
            if (minLat > dLat and maxLat < uLat and minLon > dLon and maxLon < uLon):
                return
            self.zoom = self.zoom-1

    pass

