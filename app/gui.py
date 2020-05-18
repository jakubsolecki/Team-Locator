from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from teammapview import TeamMapView
from kivy.properties import ObjectProperty
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode

from app.client import Client


class WindowManager(ScreenManager):
    client = Client.get_instance()
    #client.connect()
    pass


class TokenWindow(Screen):
    pass


class HostWindow(Screen):
    switch = ObjectProperty(None)  # Set to None because it is created before actual switch from .kv file
    slider = ObjectProperty(None)
    tv = ObjectProperty(None)

    hostVisible = False
    teamNumber = 0

    def createNodes(self):
        for node in [i for i in self.tv.iterate_all_nodes()]:
            self.tv.remove_node(node)

        for i in range(int(self.slider.value)):
            self.teamNumber = i+1
            name = 'Druzyna ' + str(i+1)

            #nodeTmp = self.tv.add_node(MyTreeNode(text=name))
            #self.tv.add_node(MyTreeNode(text=name), nodeTmp)
            self.tv.add_node(TreeViewLabel(text=name))

    def sendToServer(self):
        self.hostVisible = self.switch.active

        # for node in [i for i in self.tv.iterate_all_nodes()]:
        # TODO: GATHER HERE INPUT TEXT FOR PASSWORD?

        print("Host visible set to: ", self.hostVisible)
        print("Number of teams: ", self.teamNumber)

    pass


#class MyNode(BoxLayout):
#    pass
#class MyTreeNode(MyNode, TreeViewNode):
#    pass


class MapWindow(Screen):
    pass
