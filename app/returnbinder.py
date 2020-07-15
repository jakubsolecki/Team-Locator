from kivy.app import App


class ReturnBinder:
    __instance = None


    @staticmethod
    def get_instance():
        if ReturnBinder.__instance is None:
            ReturnBinder()

        return ReturnBinder.__instance

    def __init__(self):
        if ReturnBinder.__instance is not None:
            raise Exception("ReturnBinder must be a singleton")
        else:
            ReturnBinder.__instance = self

        self.current_screen = "token_window"

    def changed_screen(self, window, key, *largs):
        if key == 27:
            if self.current_screen is "token_window":
                return False
            screen = App.get_running_app().root
            if self.current_screen is "host":
                screen.current = "menu"
                self.current_screen = "menu"
                return True
            if self.current_screen is "viewer":
                screen.current = "menu"  # TODO: DISCONNECT?
                self.current_screen = "menu"
                return True
            if self.current_screen is "host_window":
                screen.current = "menu"
                self.current_screen = "menu"
                return True


