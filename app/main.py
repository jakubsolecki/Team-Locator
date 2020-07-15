from kivy.app import App
from teammapview import TeamMapView
from gpsmodule import GpsModule
from returnbinder import ReturnBinder

class MainApp(App):
    gps_mod = GpsModule()

    def on_start(self):
        self.gps_mod.run()

        from kivy.base import EventLoop
        EventLoop.window.bind(on_keyboard=ReturnBinder.get_instance().changed_screen)


if __name__ == "__main__":
    MainApp().run()


'''
TODO LIST:
1. Bind return (esc) button  # DONE? -> needs further testing
2. Resize confirmation button
3. Test build on phone
'''