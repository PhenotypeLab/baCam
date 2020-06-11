from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from shutil import move
from datetime import datetime
from os import listdir, remove
from time import sleep
from tools import Labeler
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

from kivy.clock import Clock

class Screen2(Screen):
    def __init__(self, config_list,  debug,**kwargs):
        super(Screen2, self).__init__(**kwargs)
        self.debug = debug
        self.config_list=config_list
        
        
        self.msgs=GridLayout(cols=2, rows=2, pos_hint={'center_y':0.5, 'center_x':0.75}, size_hint=(0.4, 0.2))
        self.msgs.add_widget(Label(text='cam_stat:'))
        self.stat_msg=Label(text='Loading...')
        self.msgs.add_widget(self.stat_msg)
        self.msgs.add_widget(Label(text='BA_stat:'))
        self.ba_stat_txt=Label(text='Waiting a capture...')
        self.msgs.add_widget(self.ba_stat_txt)

        self.photo_name=TextInput(pos_hint={'center_y':0.8, 'x':0.1}, size_hint=(0.8, 0.05), multiline=False)
        

        self.layout=FloatLayout()
        #self.layout.add_widget(self.photo_name)
        #self.layout.add_widget(self.photo_fruit)
        self.add_widget(self.layout)
        self.grid=GridLayout(cols=4, rows=1, pos_hint={'top':0.1, 'center_x':0.5}, size_hint=(0.6, 0.1))
        self.layout.add_widget(self.grid)
        self.grid.add_widget(Button(text='Back', on_release=self.back))
        self.grid.add_widget(Button(text='Capture', on_release=self.capture))
        self.grid.add_widget(Button(text='Save', on_release=self.check_save_image))
        #self.grid.add_widget(Button(text='Check images', on_release=self.checkout))
        self.on_enter=self.in_screen
        self.on_leave=self.out_screen
        self.layout.add_widget(self.msgs)

        self.warning = FloatLayout()
        self.warning.add_widget(Image(color=[0, 0, 0, 0.7]))
        self.warning_msg = Label(pos_hint={'center_x': 0.5, 'center_y': 0.6}, text='Name already exist. Overwrite?')
        self.warning.add_widget(self.warning_msg)
        self.warning_grid = GridLayout(cols=2, rows=1, pos_hint={'top': 0.8, 'center_x': 0.5}, size_hint=(0.6, 0.1))
        self.warning.add_widget(self.warning_grid)
        self.warning_yes = Button(text='Yes', on_release=self.clear_warning)
        self.warning_grid.add_widget(self.warning_yes)
        self.warning_no = Button(text='No', on_release=self.clear_warning)
        self.warning_grid.add_widget(self.warning_no)

        
        
        

        
        self.photo = Image(pos_hint={'top': 0.7, 'center_x': 0.4}, allow_stretch=True, size_hint_y=0.5, color=[0,0,0,0])
        self.add_widget(self.photo)

        self.wait_new_img=False

        
        

    def in_screen(self):
        
        print(self.config_list[0])
        self.ba_stat_txt.text='Waiting a capture...'
        self.wait_new_img=False
        self.photo.color = [0, 0, 0, 0]
        self.photo_stat = False
        self.stat_msg.text = 'Camera ready'
        
        

        self.Labeler = Labeler(pos_hint={'top': 0.8, 'center_x': 0.5}, size_hint=(1, 0.06))
        self.Labeler.initialize(template_dir=self.config_list[2])
        for n in self.Labeler.buttons:
            if 'button' in n.id:
                n.on_release = self.scroll_labeler
        self.layout.add_widget(self.Labeler)

        self.updater = Clock.schedule_interval(self.status_update,1/2)


    def scroll_labeler(self):
        grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        self.page_scroll = ScrollView(do_scroll_x=False, size_hint=(1, None), size=(Window.width, Window.height))
        for n in self.Labeler.list_display():
            btn = Button(text=n, size_hint_y=None, height=200)
            btn.bind(on_press=self.flush_labeler)
            grid.add_widget(btn)
        self.page_scroll.add_widget(grid)
        self.add_widget(self.page_scroll)

    def flush_labeler(self, dt):
        self.Labeler.buttons[self.Labeler.buttons_index.index(self.Labeler.current[1])].text=dt.text
        self.clear_widgets([self.page_scroll])

    def out_screen(self):
        self.layout.remove_widget(self.Labeler)
        self.updater.cancel()
        
    def check_save_image(self, dt=None):
        if self.photo_stat:
            #if len(self.photo_name.text)!=0:
            if len(self.Labeler.total_text())!=0:
                self.current_name=self.Labeler.total_text()
                if self.current_name+'.png' not in listdir(self.config_list[0]):
                    self.save_image()
                else:
                    self.remove_widget(self.photo)
                    self.remove_widget(self.layout)
                    self.add_widget(self.warning)
            else:
                self.save_image()
        else:
            self.stat_msg.text = 'No photo loaded. Capture an image first'


    def clear_warning(self, dt):
        if dt.text=='Yes':
            remove(self.config_list[0]+self.current_name+'.png')
            sleep(1)
            self.save_image()
        self.remove_widget(self.warning)
        self.add_widget(self.layout)
        self.add_widget(self.photo)

    def save_image(self, dt=None):
        if self.config_list[1]:
            if self.ba_stat_txt.text!="OK":
                self.stat_msg.text="BA check not pass. Correct your photo!"
                self.stat_msg.color=[1, 0, 0, 1]
                return
        move('/home/pi/temp.png', self.config_list[0]+self.current_name+'.png')
        self.stat_msg.text='Image saved.'
        self.stat_msg.color=[1, 1, 1, 1]
        self.photo.color = [0, 0, 0, 0]
        self.photo_stat=False
        
    def back(self, dt):
        self.manager.current='external'

    def img_update(self):
        if self.wait_new_img:
            if not self.config_list[3].get_busy_state():
                self.photo.source='/home/pi/temp_preview.png'
                self.photo.reload()
                self.photo.color=[1,1,1,1]
                self.photo_stat = True
                self.wait_new_img=False
                self.stat_msg.text='Image ready'
            else:
                self.stat_msg.text='Camera busy'
        else:
            pass


    def ba_stat_update(self):
        if self.ba_stat_txt.text == self.config_list[3].get_ba_state():
            return
        self.ba_stat_txt.text = self.config_list[3].get_ba_state()
        
        
        
        if self.ba_stat_txt.text == "OK":
            self.ba_stat_txt.color= [0, 1, 0, 1]
        
        elif self.ba_stat_txt.text == "BA deactivated" or self.ba_stat_txt.text == "checking":
            self.ba_stat_txt.color= [0, 1, 1, 1]
        else:
            self.ba_stat_txt.color= [1, 0, 0, 1]

    def status_update(self, dt):
        self.ba_stat_update()
        self.img_update()

    def capture(self,dt):
        if not self.config_list[3].get_busy_state():
            self.config_list[3].capture_preview(check_img=bool(self.config_list[1]))
            self.wait_new_img=True
            self.photo.color = [0, 0, 0, 0]
            self.current_name=datetime.now().strftime("%Y%m%d_%H%M%S")