import kivy
from kivy.app import App
from geopy.geocoders import Nominatim
from mapview import MapView, MapMarker
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from teammapview import TeamMapView
from gui import WindowManager
from gpsmodule import GpsModule
import certifi
import os
import atexit

from app.client import Client


class MainApp(App):
    def on_start(self):
        atexit.register(disconnect)
        GpsModule().run()
        pass


def disconnect():
    client.send_message(client.DISCONNECT_MESSAGE, "#ABCD")


if __name__ == "__main__":
    client = Client.get_instance()
    # Allows Internet connection on Android
    # os.environ['SSL_CERT_FILE'] = certifi.where()
    MainApp().run()

'''
TODO APP LIST:
1. better looking points
'''
