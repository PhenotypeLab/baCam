from pathlib import Path
from os import mkdir, listdir, getcwd
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from shutil import rmtree
from tools import check_label
#from kivy.uix.image import Image
#from kivy.graphics.texture import Texture
#import cv2
class Screen1(Screen):
    def __init__(self, config_list, debug, **kwargs):
        super(Screen1, self).__init__(**kwargs)
        self.debug = debug
        self.config_list=config_list
        
        self.layout = FloatLayout()
        self.add_widget(self.layout)
        self.layout.add_widget(Label(pos_hint={'center_x':0.5, 'center_y':0.9}, text='Berry Analyzer Camera - Desarrollado por Programa de Mejoramiento de Vides\nINIA La Platina, 2019', color=[1,1,1,0.65]))
        self.media_status=Label(pos_hint={'center_x':0.5, 'center_y':0.8})
        self.layout.add_widget(self.media_status)
        self.grid=GridLayout(cols=1, rows=4, size_hint=(0.3,0.3), pos_hint={'center_x':0.5, 'center_y':0.5})
        self.layout.add_widget(self.grid)
        self.button_l=Button(on_release=self.change_page)
        self.grid.add_widget(self.button_l)
        self.button_c = Button(text='Load label', on_release=self.load_label)
        self.grid.add_widget(self.button_c)
        self.button_r = Button(text='BA check: Yes', on_release=self.change_BA)
        self.grid.add_widget(self.button_r)
        self.button_z = Button(text='cam calibration', on_release=self.go_calibrate)
        self.grid.add_widget(self.button_z)

        self.temp_dir=Path(self.config_list[0])/"photo_pocket"
        if self.temp_dir.is_dir():
            rmtree(self.temp_dir.as_posix())

        mkdir(self.temp_dir.as_posix())
        
        filess=open((self.temp_dir/"label.tsv").as_posix(), "w")
        if debug:
            filess.write("E1\tE2\tE3\tE50\nH(txt)\nP(num)\ncosecha\tpostcosecha\nr(num)\nbayas\tracimo\traquis\n")
        else:
            filess.write("(txt)\n")
        filess.close()
        
        self.on_enter=self.check_external
        

    def check_external(self):
        if self.debug:
            self.media_status.text = 'Debug storage detected'
            self.button_l.text = 'Save in external\nstorage'
            self.save_dir=self.temp_dir
        
        else:
            list_removable = listdir('/media/pi/')
            if "SETTINGS" in list_removable:
                list_removable.pop(list_removable.index("SETTINGS"))
            if len(list_removable) == 0:
                self.button_l.text = 'Reload'
                self.media_status.text = 'No external storage detected'
                return False
            else:
                self.media_status.text = 'External storage detected'
                self.button_l.text = 'Save in external\nstorage'
                #self.save_dir='/media/pi/'+list_removable[0]+'/'
                self.save_dir=Path("/media/pi/")/list_removable[0]

        #looks for the current number of a new phenobox_data by acquiring the biggest number
        #if 'phenobox_data' in '.'.join(listdir(self.save_dir.as_posix())):
        #    max_num=max([int(n.replace('phenobox_data', '')) for n in listdir(self.save_dir.as_posix()) if 'phenobox_data' in n])
        #    if len(listdir((self.save_dir/("phenobox_data"+str(max_num))).as_posix())) == 0:
        #        current_folder="phenobox_data"+str(max_num)
        #        self.config_list[0]=(self.save_dir/current_folder).as_posix()+"/"
        #        return True
        #    else:
        #        current_folder="phenobox_data"+str(max_num+1)
        #    #current_folder='phenobox_data'+str(max([int(n.replace('phenobox_data', '')) for n in listdir(self.save_dir.as_posix()) if 'phenobox_data' in n])+1)
        #else:
        #    current_folder='phenobox_data1'

        #check if storage is writable by trying to create a folder on it
        try:
            filess=open((self.save_dir/"foo_phenobox_test.txt").as_posix(), "w")
            filess.write("foo\n")
            filess.close()
            #mkdir((self.save_dir/current_folder).as_posix())
        except:
            self.media_status.text = 'Error while writting: storage is read-only'
            self.button_l.text = 'Reload'
            return False

        if not 'phenobox_data' in '.'.join(listdir(self.save_dir.as_posix())):
            mkdir((self.save_dir/'phenobox_data').as_posix())

        self.config_list[0]=(self.save_dir/'phenobox_data').as_posix()+"/"
        return True

    def load_label(self, dt):
        if dt.text=="Load label":
            temp=check_label((self.save_dir/"label.tsv").as_posix())
            if temp:
                self.media_status.text="Label load successful"
                self.config_list[2]=(self.save_dir/"label.tsv").as_posix()
                self.button_c.text="Clear Label"
            else:
                self.media_status.text="Error. Couldn't load label"
        else:
            self.media_status.text="Label clear"
            self.config_list[2]==None
            self.button_c.text="Load label"

    def change_BA(self, dt):
        if dt.text=="BA check: Yes":
            self.button_r.text="BA check: No"
            self.config_list[1]=0
        else:
            self.button_r.text="BA check: Yes"
            self.config_list[1]=1

    def go_calibrate(self, dt=None):
        self.manager.current = 'Analyze'
        

    def change_page(self, dt):
        if dt.text=='Save in external\nstorage':
            self.manager.current = 'Capture'
        
        elif dt.text=='Reload':
            self.check_external()
