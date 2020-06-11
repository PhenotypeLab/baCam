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
from kivy.uix.slider import Slider

from kivy.clock import Clock

class Screen3(Screen):
    def __init__(self, config_list,  debug,**kwargs):
        super(Screen3, self).__init__(**kwargs)
        self.debug = debug
        self.config_list=config_list
        
        
        self.msgs=GridLayout(cols=2, rows=3, pos_hint={'center_y':0.9, 'center_x':0.75}, size_hint=(0.4, 0.15))
        #self.msgs.add_widget(Label(text='cam_stat:'))
        #self.stat_msg=Label(text='Loading...')
        #self.msgs.add_widget(self.stat_msg)
        self.msgs.add_widget(Label(text='cal_stat:'))
        self.ba_stat_txt=Label(text='Waiting a capture...')
        self.msgs.add_widget(self.ba_stat_txt)

        self.msgs.add_widget(Label(text="current value:"))
        self.current_values_text=Label(text='(0,0,0)')
        self.msgs.add_widget(self.current_values_text)

        self.msgs.add_widget(Label(text="reference:"))
        self.ref_values_text=Label(text='(0,0,0)')
        self.msgs.add_widget(self.ref_values_text)

        self.sliders=GridLayout(cols=1, rows=10, pos_hint={'center_y':0.6, 'center_x':0.75}, size_hint=(0.4, 0.4))
        self.sliders_values=[]
        self.sliders.add_widget(Label(text="shutter"))
        self.sliders_values.append(Slider(min=5000, max=100000, value=13000, step=1000))
        self.sliders.add_widget(self.sliders_values[-1])

        self.sliders.add_widget(Label(text="bright"))
        self.sliders_values.append(Slider(min=0, max=100, value=50, step=1))
        self.sliders.add_widget(self.sliders_values[-1])

        self.sliders.add_widget(Label(text="red"))
        self.sliders_values.append(Slider(min=0.0, max=4.0, value=1.92, step=0.03))
        self.sliders.add_widget(self.sliders_values[-1])

        self.sliders.add_widget(Label(text="blue"))
        self.sliders_values.append(Slider(min=0.0, max=4.0, value=0.93, step=0.03))
        self.sliders.add_widget(self.sliders_values[-1])

        self.sliders.add_widget(Label(text="contrast"))
        self.sliders_values.append(Slider(min=0, max=100, value=0, step=1))
        self.sliders.add_widget(self.sliders_values[-1])


        self.photo_name=TextInput(pos_hint={'center_y':0.8, 'x':0.1}, size_hint=(0.8, 0.05), multiline=False)
        

        self.layout=FloatLayout()
        #self.layout.add_widget(self.photo_name)
        #self.layout.add_widget(self.photo_fruit)
        self.add_widget(self.layout)
        self.grid=GridLayout(cols=3, rows=1, pos_hint={'top':0.1, 'center_x':0.5}, size_hint=(0.6, 0.1))
        self.layout.add_widget(self.grid)
        self.grid.add_widget(Button(text='Back', on_release=self.back))
        self.grid.add_widget(Button(text='Capture', on_release=self.capture))
        self.grid.add_widget(Button(text='Apply settings', on_release=self.save_values))
        #self.grid.add_widget(Button(text='Check images', on_release=self.checkout))
        self.on_enter=self.in_screen
        self.on_leave=self.out_screen
        self.layout.add_widget(self.msgs)
        self.layout.add_widget(self.sliders)

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

        
        
        

        
        self.photo = Image(pos_hint={'top': 0.7, 'center_x': 0.3}, allow_stretch=True, size_hint_y=0.5, color=[0,0,0,0])
        self.add_widget(self.photo)

        self.wait_new_img=False

        if "camera.txt" in listdir("./"):
            self.apply_values()

        
    def save_values(self, dt=None):
        filess = open("camera.txt", "w")
        temp=[]
        temp.append(str(int(self.sliders_values[0].value)))
        temp.append(str(int(self.sliders_values[1].value)))
        temp.append(str((self.sliders_values[2].value,self.sliders_values[3].value)))
        temp.append(str(int(self.sliders_values[4].value)))
        filess.write("\n".join(temp))
        filess.close()
        print(self.apply_values())

    def apply_values(self):
        filess = open("camera.txt", "r")
        temp=filess.read().split("\n")
        filess.close()
        try:
            temp=[int(temp[0]), int(temp[1]), tuple(map(float,temp[2][1:-1].split(","))), int(temp[3])]
        except:
            return "Error parsing settings"
        self.sliders_values[0].value=temp[0]
        self.sliders_values[1].value=temp[1]
        self.sliders_values[2].value=temp[2][0]
        self.sliders_values[3].value=temp[2][1]
        self.sliders_values[4].value=temp[3]
        print(temp[0], temp[1], temp[2], temp[3])
        return self.config_list[3].set_params(temp[0], temp[1], temp[2], temp[3])


    def check_save_image(self, dt=None):
        if self.photo_stat:
            #if len(self.photo_name.text)!=0:
            if len(self.Labeler.total_text())!=0:
                self.current_name=self.Labeler.total_text()
                if self.current_name+'.png' not in listdir(self.config_list[0]):
                    self.save_image()
                else:
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

    def in_screen(self):
        

        self.ba_stat_txt.text='Waiting a capture...'
        self.wait_new_img=False
        self.photo.color = [0, 0, 0, 0]
        self.photo_stat = False

        self.updater = Clock.schedule_interval(self.status_update,1/2)

    def out_screen(self):
        self.updater.cancel()
        
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
        else:
            pass


    def ba_stat_update(self):
        if self.ba_stat_txt.text == self.config_list[3].get_ba_state():
            return
        self.ba_stat_txt.text = self.config_list[3].get_ba_state()
        
        
        
        if self.ba_stat_txt.text == "values ready":
            self.ba_stat_txt.color= [0, 1, 0, 1]
            temp=self.config_list[3].calibration_values()
            self.current_values_text.text="("+",".join(list(map(str,temp[0])))+")"
            self.ref_values_text.text="("+",".join(list(map(str,temp[1])))+")"
            
        
        elif self.ba_stat_txt.text == "BA deactivated" or self.ba_stat_txt.text == "checking":
            self.ba_stat_txt.color= [0, 1, 1, 1]
        else:
            self.ba_stat_txt.color= [1, 0, 0, 1]

    def status_update(self, dt):
        self.ba_stat_update()
        self.img_update()

    def capture(self,dt):
        if not self.config_list[3].get_busy_state():
            self.config_list[3].capture_calibration()
            self.wait_new_img=True
            self.photo.color = [0, 0, 0, 0]
            self.current_name=datetime.now().strftime("%Y%m%d_%H%M%S")
