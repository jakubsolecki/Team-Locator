import kivy
from kivy.app import App
from geopy.geocoders import Nominatim
from mapview import MapView, MapMarker
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
import certifi
import os

# Here's all the magic !
os.environ['SSL_CERT_FILE'] = certifi.where()




class WindowManager(ScreenManager):
    pass


class TokenWindow(Screen):
    pass


class MapWindow(Screen):
    geolocator = Nominatim(user_agent="GeoTestApp")
    location = geolocator.geocode("21 Kawiory, Kraków")
    # location = droid.getLastKnownLocation().result
    # location = location.get('gps') or location.get('network')
    # lon = droid.geocode(location['longitude'])
    # lat = droid.geocode(location['latitude'])
    lon = location.longitude
    lat = location.latitude
    print(lon, lat)
    pass


kv = Builder.load_file("gui.kv")


class MainApp(App):
    def build(self):
        return kv


if __name__ == "__main__":
    MainApp().run()
