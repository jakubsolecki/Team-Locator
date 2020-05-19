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
    code = ''

    def on_start(self):
        GpsModule().run()
        pass


if __name__ == "__main__":
    MainApp().run()

'''
TODO APP LIST:
    first number in pass is color
    krotka(nazwa,lon, lat)
'''
