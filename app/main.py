import kivy
from kivy.app import App
from geopy.geocoders import Nominatim
from mapview import MapView, MapMarker
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from teammapview import TeamMapView
from gui import WindowManager
import certifi
import os


# kv = Builder.load_file("gui.kv")


class MainApp(App):
    def on_start(self):
        pass


if __name__ == "__main__":
    # Allows Internet connection on Android
    os.environ['SSL_CERT_FILE'] = certifi.where()
    MainApp().run()
