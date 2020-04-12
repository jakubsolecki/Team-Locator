import kivy
from kivy.app import App
# from geopy.geocoders import Nominatim
from kivy.garden.mapview import MapView, MapMarker
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
import android


droid = android.Android()


class WindowManager(ScreenManager):
    pass


class TokenWindow(Screen):
    pass


class MapWindow(Screen):
    # geolocator = Nominatim(user_agent="GeoTestApp")
    # location = geolocator.geocode("21 Kawiory, Kraków")
    location = droid.getLastKnownLocation().result
    location = location.get('gps') or location.get('network')
    lon = droid.geocode(location['longitude'])
    lat = droid.geocode(location['latitude'])
    pass


kv = Builder.load_file("gui.kv")


class MainApp(App):
    def build(self):
        return kv


if __name__ == "__main__":
    MainApp().run()
