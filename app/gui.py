from time import sleep
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.treeview import TreeViewLabel
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from client import Client
from colordict import color_dictionary
from kivy.utils import get_color_from_hex
from gpsblinker import GpsBlinker
import atexit
from gpsmodule import GpsModule


class WindowManager(ScreenManager):
    pass


class MapWindow(Screen):
    pass


class TokenWindow(Screen):
    nick = ObjectProperty(None)
    code = ObjectProperty(None)
    client = Client.get_instance()
    colornum = 0  # Expected to change. If players stay black something is wrong
    current_blinker = None

    def disconnect(self):
        self.client.send_message(self.client.DISCONNECT_MESSAGE, self.code.text)

    def host_connect(self):
        self.client.connect()
        if not self.client._connected:
            return
        screen = App.get_running_app().root
        screen.current = "host"
        atexit.register(self.disconnect)

    def player_connect(self):
        if 'host-' in self.nick.text:
            return

        self.client.connect()
        if not self.client._connected:
            return

        message = self.code.text + ":" + self.nick.text
        print("Message sent to server: " + message)

        self.client.send_message(self.client.INIT_MESSAGE, message)

        sleep(1)

        if self.client._token is None:
            return

        # Takes second letter as number from 0 to 9: || #1ABCD means color 1 ||
        if len(self.code.text) >= 2 and self.code.text[1].isdigit():
            self.colornum = int(self.code.text[1])

        # GPS always starts in our faculty building <3
        self.current_blinker = blinker = GpsBlinker(lon=19.9125399, lat=50.0680966, nick=self.nick.text, color_number=self.colornum)

        map = App.get_running_app().root.ids.mw.ids.map
        map.add_widget(blinker)
        blinker.blink()

        App.get_running_app().gps_mod.start_updating(blinker)

        screen = App.get_running_app().root
        screen.current = "viewer"

        atexit.register(self.disconnect)


class HostWindow(Screen):
    switch = ObjectProperty(None)  # Set to None because it is created before actual switch from .kv file
    slider = ObjectProperty(None)
    tv = ObjectProperty(None)


    hostVisible = False
    teamNumber = 0

    def create_nodes(self):
        if int(self.slider.value) == self.teamNumber:
            return
        self.teamNumber = int(self.slider.value)
        for node in [i for i in self.tv.iterate_all_nodes()]:
            self.tv.remove_node(node)

        for i in range(int(self.slider.value)):
            self.teamNumber = i + 1
            name = 'Druzyna ' + str(i + 1)
            color = get_color_from_hex(color_dictionary[i + 1])
            self.tv.add_node(TreeViewLabel(text=name, color=color))

    def host_to_server(self):
        self.hostVisible = self.switch.active

        nickname = App.get_running_app().root.ids.tw.nick.text
        password = App.get_running_app().root.ids.tw.code.text

        message = password + ":" + nickname + ":" + str(self.hostVisible) + ":" + str(self.teamNumber)
        print("Message sent to server: " + message)

        client = Client.get_instance()
        client.send_message(client.INIT_MESSAGE, message)

        sleep(1)

        # if client._token is None: #TODO: REMOVE THIS COMMENT TO CHECK IF HOST ACTUALLY WORKS
        #    return

        map = App.get_running_app().root.ids.mw.ids.map
        tw = App.get_running_app().root.ids.tw
        tw.current_blinker = blinker = GpsBlinker(lon=19.9125399, lat=50.0680966, nick=nickname, color_number=0)
        map.add_widget(blinker)
        blinker.blink()
        map.add_host_buttons()

        App.get_running_app().gps_mod.start_updating(blinker)

        screen = App.get_running_app().root
        screen.current = "viewer"


# -----------------------------These classes made for pop window of team tokens-----------------------------------------
def show_popup(text):
    show = Pop(text)
    popupWindow = Popup(title="Password for teams:", content=show, size_hint=(None, None), size=(200, 400))
    popupWindow.open()


class Pop(FloatLayout):
    text = "placeholder"

    def __init__(self, text, **kwargs):
        self.text = text
        super(FloatLayout, self).__init__(**kwargs)


class BtnPopup(Widget):
    text = ''

    def __init__(self, text="PLACEHOLDER", *args, **kwargs):
        super().__init__(**kwargs)
        self.text = text

    def click(self):
        show_popup(text=self.text)

    def terminate_game_remove_host_privileges(self):
        client = Client.get_instance()
        client.send_message(client.CLOSE_GAME, '')  # TODO: IS IT CORRECT?

        map = App.get_running_app().root.ids.mw.ids.map
        map.remove_host_buttons()
        tw = App.get_running_app().root.ids.tw
        map.remove_widget(tw.current_blinker)

