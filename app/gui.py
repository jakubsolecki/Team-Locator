from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from app.client import Client
from app.colordict import color_dictionary
from kivy.utils import get_color_from_hex


class WindowManager(ScreenManager):
    pass

from app.gpsblinker import GpsBlinker

class TokenWindow(Screen):
    nick = ObjectProperty(None)
    code = ObjectProperty(None)
    client = Client.get_instance()
    colornum = 0  # SHOULDN'T STAY THAT WAY

    def host_connect(self):
        self.client.connect()

    def player_connect(self):
        self.client.connect()
        message = self.code.text + ":" + self.nick.text
        print("Message sent to server: " + message)

        # Takes second letter as number from 1 to 10: || #1ABCD means color 1 ||
        if len(self.code.text) >= 2 and self.code.text[1].isdigit():
            self.colornum = int(self.code.text[1])

        map = App.get_running_app().root.ids.mw.ids.map
        blinker = GpsBlinker(lon=19.9125399, lat=50.0680966, nick=self.nick.text, color_number=self.colornum)
        map.add_widget(blinker)
        blinker.blink()
        #START HERE GPS MODULE????

        client = Client.get_instance()
        client.send_message(client.INIT_MESSAGE, message)

    pass


class HostWindow(Screen):
    switch = ObjectProperty(None)  # Set to None because it is created before actual switch from .kv file
    slider = ObjectProperty(None)
    tv = ObjectProperty(None)

    hostVisible = False
    teamNumber = 0

    def create_nodes(self):
        for node in [i for i in self.tv.iterate_all_nodes()]:
            self.tv.remove_node(node)

        for i in range(int(self.slider.value)):
            self.teamNumber = i + 1
            name = 'Druzyna ' + str(i + 1)
            color = get_color_from_hex(color_dictionary[i + 1])
            self.tv.add_node(TreeViewLabel(text=name, color=color))

    def send_to_server(self):
        self.hostVisible = self.switch.active

        nickname = App.get_running_app().root.ids.tw.nick.text
        password = App.get_running_app().root.ids.tw.code.text

        message = password + ":" + nickname + ":" + str(self.hostVisible) + ":" + str(self.teamNumber)
        print("Message sent to server: " + message)


        client = Client.get_instance()
        client.send_message(client.INIT_MESSAGE, message)

        map = App.get_running_app().root.ids.mw.ids.map
        blinker = GpsBlinker(lon=19.9125399, lat=50.0680966, nick=nickname, color_number=10)
        map.add_widget(blinker)
        blinker.blink()
        map.add_host_buttons()

        #START GPS MODULE HERE?




class MapWindow(Screen):
    pass


def show_popup(text):
    show = Pop(text)
    popupWindow = Popup(title="Password for teams:", content=show, size_hint=(None, None), size=(400, 400))
    popupWindow.open()


class Pop(FloatLayout):
    text = "placeholder"

    def __init__(self, text, **kwargs):
        self.text = text
        super(FloatLayout, self).__init__(**kwargs)

    pass


class BtnPopup(Widget):
    text = ''

    def click(self):
        show_popup(text=self.text)

    def __init__(self, text="PLACEHOLDER", *args, **kwargs):
        super().__init__(**kwargs)
        self.text = text
