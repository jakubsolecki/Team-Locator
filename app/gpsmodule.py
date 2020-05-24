from kivy.app import App
from kivy.utils import platform
from client import Client


class GpsModule():
    blinker = None
    has_centered_map = False

    def run(self):

        # persmissions on Android:
        if platform == 'android':
            from android.permissions import Permission, request_permissions
            def callback(permission, results):
                if all([res for res in results]):
                    print("Got all permissions")

            request_permissions([Permission.ACCESS_COARSE_LOCATION,
                                 Permission.ACCESS_FINE_LOCATION], callback)

    def start_updating(self, blinker):
        self.blinker = blinker
        if platform == 'android':
            from plyer import gps
            gps.configure(on_location=self.update_gps_position, on_status=self.on_auth_status)
            gps.start(minTime=1000, minDistance=0)

    def update_gps_position(self, *arg, **kwargs):
        my_lat = kwargs['lat']
        my_lon = kwargs['lon']

        print("GPS POSITTION", my_lat, my_lon)

        self.blinker.lat = my_lat
        self.blinker.lon = my_lon

        client = Client.get_instance()
        client._lon = my_lon  # HUGELY UNRECOMMENDED
        client._lat = my_lat

        # centers map:
        if not self.has_centered_map:
            map = App.get_running_app().root.ids.mw.ids.map
            map.center_on(my_lat, my_lon)
            self.has_centered_map = True

    def on_auth_status(self, general_status, status_message):
        if general_status == 'provider-enabled':
            pass
        else:
            print("GPS ERROR, you need to enable all access")

    pass
