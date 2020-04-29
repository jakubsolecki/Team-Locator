from kivy.app import App

class GpsModule():
    def run(self):
        #TODO: UPDATE POSITION OF BLINKER
        blinker = App.get_running_app().root.ids.mw.ids.map.ids.blinker
        blinker.blink()
