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
        #GpsModule().run()
        pass


if __name__ == "__main__":
    MainApp().run()

'''
TODO APP LIST:
    EXIT button for host isn't working
        CAN SERVER BE HOSTED ON SAME PASSWORD? MUST BE CHECKED
    how others see host? Right now I guess the same color as others
    deal with included libraries trash
    clean cache 
    do something when server is down???
    
MY WORRIES:
    gui.py accesses client data without LOCKs
    GPSMODULE OVERRIDES CLIENT'S _LON AND _LAT BUT IS THERE BETTER CHOICE?
'''

