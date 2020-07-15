from kivy.app import App
from teammapview import TeamMapView
from gpsmodule import GpsModule


class MainApp(App):
    gps_mod = GpsModule()

    def on_start(self):
        self.gps_mod.run()
        pass


if __name__ == "__main__":
    MainApp().run()


'''
TODO LIST:
1. Bind return (esc) button
2. Resize confirmation button
3. Test build on phone
'''