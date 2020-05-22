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


class MainApp(App):
    gps_mod = GpsModule()

    def on_start(self):
        self.gps_mod.run()
        pass


if __name__ == "__main__":
    MainApp().run()

'''
TODO APP LIST:
    deal with included libraries trash
    clean cache 
    need to show info after host terminated game. Prolly in teammapview drawing points check if connection is closed  
    show team codes as host
    what if you dont get a host?
'''

