from os import getcwd, environ
from sys import argv

environ['KIVY_GL_BACKEND'] = 'gl'

from kivy.core.window import Window
Window.fullscreen = True

from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '1')
#Config.set('graphics', 'fullscreen', 'fake')
#Config.set('graphics', 'borderless', '0')
#Config.set('graphics', 'height', '600')
#Config.set('graphics', 'width', '800')
#Config.set('graphics', 'resizable', '0')
Config.write()

from kivy.app import App



from kivy.uix.screenmanager import ScreenManager
from screen1 import Screen1
from screen2 import Screen2
from screen3 import Screen3

from main import Cameraman

main_camera=Cameraman()

class Bigbox_ui(App):
    def build(self):
        main_list=[getcwd(),1,None,main_camera]
        base = argv[0][:argv[0].rfind('/')]
        self.Sm = ScreenManager()
        self.Sc1=Screen1(name='external', config_list=main_list, debug = False)
        self.Sm.add_widget(self.Sc1)
        self.Sc2 = Screen2(name='Capture', config_list=main_list, debug = False)
        self.Sm.add_widget(self.Sc2)
        self.Sc3 = Screen3(name='Analyze', config_list=main_list, debug = False)
        self.Sm.add_widget(self.Sc3)
        self.Sm.current='external'
        return self.Sm

if __name__ == '__main__':
    Bigbox_ui().run()
