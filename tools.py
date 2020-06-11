#import cv2
#import numpy
import os
import sys
from pathlib import Path
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
#from pandas import read_excel

def tsv_parser(url):
    filess=open(url, 'r')
    txt=filess.read()
    txt=[n.split('\t') for n in txt.split('\n')]
    filess.close()
    return txt
def tsv_writter(matrix):
    return '\n'.join(['\t'.join(n) for n in matrix])

def load_dataframe(data_dir):
    df = read_excel(data_dir, header=None)
    if True in df.isna():
        return df.fillna(value=" ").values
    else:
        return df.values

#class Labelers(GridLayout):
#    def __init__(self, label_template, **kwargs):
#        super(Labeler).__init__(**kwargs)
#        templates_terms=["PRE", "NUM", "LST", "TXT"]
#        self.label_template = load_dataframe(label_template)
#        for t in self.label_template[0]:
#            try:
#                assert t in templates_terms
#            except:
#                raise ValueError(t)
#        self.cols=self.label_template[0].size

def options_load(dir):
    if dir[::-1][0]!='/':
        dir=dir+'/'
    temp = []
    for file in os.listdir(dir):
        temp.append([file[:file.rfind('.')]])
        file = open(dir + file, 'r')
        new = file.read()
        file.close()
        new = new.split('>')
        for s in new:
            if len(s)==0:
                continue
            temp[len(temp) - 1].append([])
            s=[i.split('\t') for i in s.split('\n') if len(i) != 1]
            temp[len(temp)-1][len(temp[len(temp)-1])-1].append(s[0][0])
            for i in s[1:]:
                i=[l for l in i if len(l)!=0]
                if len(i)!=0:
                    temp[len(temp) - 1][len(temp[len(temp)-1])-1].append(i)
    return temp

class Labeler(GridLayout):
    def __init__(self, **kwargs):
        super(Labeler, self).__init__(**kwargs)
        base = sys.argv[0][:sys.argv[0].rfind('/')]
        #self.config=config_get()
        #self.profiles = options_load(base+'/lists_tsv')
        self.profiles = options_load('/home/pi/measurement_boxes/stand_alone/lists_tsv')
        self.rows=1
        self.profiles=self.profiles[2][1]
        #self.profiles = self.profiles[0][1]

        self.index=[]
        self.index_num=[]

        self.current=['','']

        self.buttons=[]

        self.options_list=[]

        counter=0
        self.buttons_index=[]

        for n in range(len(self.profiles)):
            if n==0:
                self.options_list.append([])
                self.index.append('None')
                self.index_num.append(n)
                continue
            if '(num)' in self.profiles[n][0]:
                self.index_num.append(n)
                self.options_list.append([])
                self.index.append('None')
                self.buttons.append(Label(text=self.profiles[n][0][:self.profiles[n][0].find('(num)')], id='label'+str(counter)))
                self.buttons_index.append('label'+str(counter))
                self.buttons.append(TextInput(multiline=False, text='0', input_filter='int', id='input'+str(counter)))
                self.buttons_index.append('input' + str(counter))
            else:
                self.options_list.append(self.profiles[n])
                for i in self.profiles[n]:
                    self.index.append(i)
                    self.index_num.append(n)
                self.buttons.append(Button(text=self.profiles[n][0], id='button'+str(counter), on_press=self.set_current))
                self.buttons_index.append('button' + str(counter))
            counter=counter+1
        for n in self.buttons:
            self.add_widget(n)
        #self.add_widget(Button(text='total', on_press=self.total_text))
    def set_current(self, dt):
        self.current[0] = dt.text
        self.current[1] = dt.id
    def list_display(self):
        return self.options_list[self.index_num[self.index.index(self.current[0])]]
    def total_text(self):
        text=''
        for n in self.buttons:
            if 'label' in n.id:
                text = text + n.text + '#'
            else:
                text=text+n.text+'_'
        return text[:len(text)-1]

    def obey(self, label):
        temp=[]
        label=label.split('_')
        for n in label:
            if '#' in n:
                n=n.split('#')
                temp.append(n[0])
                temp.append(n[1])
            else:
                temp.append(n)
        for n in range(len(self.buttons)):
            self.buttons[n].text=temp[n]

def options_load(file):
    file = open(file, 'r')
    new = file.read()
    file.close()
    new=['label']+[i.split('\t') for i in new.split('\n') if len(i) > 0]
    #print(new)
    return new

class Labeler(GridLayout):
    def __init__(self, **kwargs):
        super(Labeler, self).__init__(**kwargs)
        base = sys.argv[0][:sys.argv[0].rfind('/')]
        self.ready=False
    def initialize(self, template_dir):
        try:
            self.load_template(template_dir)
            self.ready=True
            return True
        except:
            self.load_template("./label.tsv")
            self.ready=True
            return False
    def load_template(self, template):
        self.profiles = options_load(template)
        self.rows=1

        self.index=[]
        self.index_num=[]

        self.current=['','','']

        self.buttons=[]

        self.options_list=[]

        counter=0
        self.buttons_index=[]

        for n in range(len(self.profiles)):
            if n==0:
                self.options_list.append([])
                self.index.append('None')
                self.index_num.append(n)
                continue
            if '(sfx)' in self.profiles[n][0]:
                self.index_num.append(n)
                self.options_list.append([])
                self.index.append('None')
                self.buttons.append(Label(text=self.profiles[n][1], id='label'+str(counter)))
                self.buttons_index.append('label'+str(counter))
                #self.buttons.append(TextInput(multiline=False, text='0', input_filter='int', id='input'+str(counter)))
                #self.buttons_index.append('input' + str(counter))
            elif '(num)' in self.profiles[n][0]:
                self.index_num.append(n)
                self.options_list.append([])
                self.index.append('None')
                #self.buttons.append(Label(text=self.profiles[n][0][:self.profiles[n][0].find('(num)')], id='label'+str(counter)))
                #self.buttons_index.append('label'+str(counter))
                self.buttons.append(TextInput(multiline=False, text='0', input_filter='int', id='input'+str(counter)))
                self.buttons_index.append('input' + str(counter))
            elif '(txt)' in self.profiles[n][0]:
                self.index_num.append(n)
                self.options_list.append([])
                self.index.append('None')
                #self.buttons.append(Label(text=self.profiles[n][0][:self.profiles[n][0].find('(txt)')], id='label'+str(counter)))
                #self.buttons_index.append('label'+str(counter))
                self.buttons.append(TextInput(multiline=False, text='example', id='input'+str(counter)))
                self.buttons_index.append('input' + str(counter))
            elif '(lst)' in self.profiles[n][0]:
                self.options_list.append(self.profiles[n][1:])
                for i in self.profiles[n][1:]:
                    self.index.append(i)
                    self.index_num.append(n)
                self.buttons.append(Button(text=self.profiles[n][1], id='button'+str(counter), on_press=self.set_current))
                self.buttons_index.append('button' + str(counter))
            counter=counter+1
        for n in self.buttons:
            self.add_widget(n)
    def set_current(self, dt):
        self.current[0] = dt.text
        self.current[1] = dt.id
    def list_display(self):
        return self.options_list[self.index_num[self.index.index(self.current[0])]]
    def total_text(self):
        text=''
        for n in self.buttons:
            text = text + n.text
        return text[:len(text)]

    def obey(self, label):
        temp=[]
        label=label.split('_')
        for n in label:
            if '#' in n:
                n=n.split('#')
                temp.append(n[0])
                temp.append(n[1])
            else:
                temp.append(n)
        for n in range(len(self.buttons)):
            self.buttons[n].text=temp[n]

def check_label(label_dir):
    options_list=["(sfx)", "(lst)", "(txt)", "(num)"]
    if not Path(label_dir).is_file():
        return False
    try:
        profiles = options_load(label_dir)
        for n in range(len(profiles)):
            if n==0:
                continue
            assert profiles[n][0] in options_list
        return True
    except:
        return False