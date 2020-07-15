from time import sleep
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.treeview import TreeViewLabel
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from kivy.metrics import *
from client import Client  # from app.client import Client
from colordict import color_dictionary
from gpsblinker import GpsBlinker
from kivy.storage.jsonstore import JsonStore
import atexit
import os
import glob
from returnbinder import ReturnBinder


class WindowManager(ScreenManager):
    pass


class MapWindow(Screen):
    pass


class TokenWindow(Screen):
    nick = ObjectProperty(None)
    code = ObjectProperty(None)
    ip_address = ObjectProperty(None)
    client = Client.get_instance()
    colornum = 10  # Expected to change. If players stay black something is wrong
    current_blinker = None
    stored_data = JsonStore('data.json')

    def __disconnect(self):
        files = glob.glob('cache/*.png')
        for f in files:
            os.remove(f)
        self.client.send_message(self.client.DISCONNECT_MESSAGE, self.code.text)
        sleep(1)

    def __connect(self):
        if 'host-' in self.nick.text or ':' in self.nick.text or\
                len(self.nick.text) >= 16 or\
                len(self.code.text) > 10 or\
                len(self.ip_address.text) > 16:
            return
        self.client.connect(server_ip=self.ip_address.text)

    # after pressing "Host Game" button:
    def host_connect(self):
        self.__connect()
        if not self.client.is_connected():
            return
        atexit.register(self.__disconnect)

        screen = App.get_running_app().root
        screen.current = "host"
        ReturnBinder.get_instance().current_screen = "host"
        self.stored_data.clear()
        self.stored_data.put('credentials', ip_address=self.ip_address.text, nick=self.nick.text)

    # after pressing "Connect Game" button:
    def player_connect(self):
        self.__connect()
        if not self.client.is_connected():
            return
        atexit.register(self.__disconnect)

        message = self.code.text + ":" + self.nick.text
        print("Message being sent to server: " + message)
        self.client.send_message(self.client.INIT_MESSAGE, message)

        sleep(1)
        if self.client.get_token() is None:
            return

        # Takes first letter as number from 0 to 9: || #1ABCD means color 1 ||
        if len(self.code.text) >= 1 and self.code.text[0].isdigit():
            self.colornum = int(self.code.text[0])

        # GPS always starts in AGH WIEiT faculty building
        self.current_blinker = blinker = GpsBlinker(lon=19.9125399, lat=50.0680966,
                                                    nick=self.nick.text, color_number=self.colornum)
        team_map = App.get_running_app().root.ids.mw.ids.map
        team_map.add_widget(blinker)
        team_map.start_checking = True
        blinker.blink()
        App.get_running_app().gps_mod.start_updating(blinker)

        self.stored_data.clear()
        self.stored_data.put('credentials', ip_address=self.ip_address.text, nick=self.nick.text)

        screen = App.get_running_app().root
        screen.current = "viewer"
        ReturnBinder.get_instance().current_screen = "viewer"


class HostWindow(Screen):  # Window for setting game rules
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
            color = get_color_from_hex(color_dictionary[i])
            self.tv.add_node(TreeViewLabel(text=name, color=color))

    def host_to_server(self):
        self.hostVisible = self.switch.active

        nickname = App.get_running_app().root.ids.tw.nick.text
        password = App.get_running_app().root.ids.tw.code.text

        message = password + ":" + nickname + ":" + str(int(self.hostVisible)) + ":" + str(self.teamNumber)
        print("Message sent to server: " + message)

        client = Client.get_instance()
        client.send_message(client.INIT_MESSAGE, message)

        sleep(1)

        if client.get_token is None:
            return

        tw = App.get_running_app().root.ids.tw
        tw.current_blinker = blinker = GpsBlinker(lon=19.9125399, lat=50.0680966, nick=nickname, color_number=10)

        team_map = App.get_running_app().root.ids.mw.ids.map
        team_map.add_widget(blinker)
        team_map.add_host_buttons()

        blinker.blink()
        App.get_running_app().gps_mod.start_updating(blinker)

        screen = App.get_running_app().root
        screen.current = "viewer"
        ReturnBinder.get_instance().current_screen = "viewer"


# -----------------------------These classes made for pop window of team tokens-----------------------------------------
def show_popup(text):
    show = Pop(text)
    popupWindow = Popup(title="Password for teams:", content=show, size_hint=(None, None), size=(sp(200), sp(400)))
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
        content = ConfirmPopup(text='Are you sure?')
        content.bind(on_answer=self._on_answer)
        self.popup = Popup(title="Terminating game",
                           content=content,
                           size_hint=(None, None),
                           size=(480, 400))  # TODO: CHANGE SIZE ETC
        self.popup.open()

    def _on_answer(self, instance, answer):
        if answer is 'yes':
            client = Client.get_instance()
            client.send_message(client.CLOSE_GAME, None)

            team_map = App.get_running_app().root.ids.mw.ids.map
            team_map.remove_host_buttons()
            tw = App.get_running_app().root.ids.tw
            team_map.remove_widget(tw.current_blinker)
            team_map.host_buttons = None
            App.get_running_app().root.current = "menu"
            ReturnBinder.get_instance().current_screen = "menu"
        self.popup.dismiss()


class ConfirmPopup(GridLayout):
    text = StringProperty()

    def __init__(self, **kwargs):
        self.register_event_type('on_answer')
        super(ConfirmPopup, self).__init__(**kwargs)

    def on_answer(self, *args):
        pass