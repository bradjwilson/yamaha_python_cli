#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
import argparse
import configparser
import os
from html.parser import HTMLParser

program_version = '0.0.1'

power = 0
volume = 0
input_sel = 0
sound_program = 0
model_name = 0
system_id = 0
version = 0
ip = ''

config = configparser.ConfigParser()
config.read(os.path.dirname(__file__)+'/network.conf')
ip = config.get('yamaha.config', 'yamaha_ip')

url = 'http://' + ip + '/YamahaRemoteControl/ctrl'

class MyHTMLParser(HTMLParser):

  def __init__(self):
    HTMLParser.__init__(self)
    self.recording = 0 
    self.data = []
    self.save_next_data = False
    self.sound_programs = []
  def handle_starttag(self, tag, attrs):
    if tag == 'option':
      for name, value in attrs:
        if name == 'class' and value == 'zoneselectinput':
            self.save_next_data = True

  def handle_endtag(self, tag):
    if tag == 'option':
      self.recording -=1 
      #print("Encountered the end of a %s tag" % tag)

  def handle_data(self, data):
    if self.recording:
      self.data.append(data)
    if self.save_next_data:
        self.sound_programs.append(data)
        self.save_next_data = False




def list_sound_programs():
    x = requests.get(url= 'http://' + ip)
    parser = MyHTMLParser()
    parser.feed(str(x.content))
    print(*parser.sound_programs, sep = "\n") 


def list_inputs():
    data = '<YAMAHA_AV cmd="GET"><System><Config>GetParam</Config></System></YAMAHA_AV>'
    x = requests.post(url,data)
    root = ET.fromstring(x.content)
    for child in root.iter('*'):
        if child.tag == 'Input':
            for inputs in child.iter('*'):
                print(inputs.text)
                


def get_config():
    global model_name
    global system_id
    global version
    data = '<YAMAHA_AV cmd="GET"><System><Config>GetParam</Config></System></YAMAHA_AV>'
    x = requests.post(url,data)
    root = ET.fromstring(x.content)
    for child in root.iter('*'):
        #print(child.tag, " ", child.text)
        if child.tag == 'Model_Name':
            model_name = child.text
        if child.tag == 'System_ID':
            system_id = child.text
        if child.tag == 'Version':
            version = child.text

def get_settings():
    global power
    global volume
    global input_sel
    global sound_program
    data = '<YAMAHA_AV cmd="GET"><Main_Zone><Basic_Status>GetParam</Basic_Status></Main_Zone></YAMAHA_AV>'
    x = requests.post(url,data)
    root = ET.fromstring(x.content)
    for child in root.iter('*'):
            if child.tag == 'Power':
                power = child.text
            if child.tag == 'Val':
                volume = int(child.text)
            if child.tag == 'Input_Sel':
                input_sel = child.text
            if child.tag == 'Sound_Program':
                sound_program = child.text

def set_volume_raw(volume_raw):
    print(str(10 * float(volume_raw)).replace('.0', ''))
    data = '<YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Lvl><Val>' + str(10 * float(volume_raw)).replace('.0', '') + '</Val><Exp>1</Exp><Unit>dB</Unit></Lvl></Volume></Main_Zone></YAMAHA_AV>'
    x = requests.post(url,data)

def toggle_power():
    global power
    if power == "On":
        power = 'Standby'
    else:
        power = 'On'
    print(power)
    data = '<YAMAHA_AV cmd="PUT"><Main_Zone><Power_Control><Power>'+power+'</Power></Power_Control></Main_Zone></YAMAHA_AV>'
    x = requests.post(url,data)

def set_volume_increase():
    global volume
    get_settings()
    volume += 5
    print(volume)
    data = '<YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Lvl><Val>' + str(volume) + '</Val><Exp>1</Exp><Unit>dB</Unit></Lvl></Volume></Main_Zone></YAMAHA_AV>'
    x = requests.post(url,data)

def set_volume_decrease():
    get_settings()
    global volume
    volume -= 5
    print(volume)
    data = '<YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Lvl><Val>' + str(volume) + '</Val><Exp>1</Exp><Unit>dB</Unit></Lvl></Volume></Main_Zone></YAMAHA_AV>'
    x = requests.post(url,data)

def set_input(input):
    data = '<YAMAHA_AV cmd="PUT"><Main_Zone><Input><Input_Sel>' + input + '</Input_Sel></Input></Main_Zone></YAMAHA_AV>'
    x = requests.post(url,data)

def set_sound_stage(sound_stage):
    data = '<YAMAHA_AV cmd="PUT"><Main_Zone><Surround><Program_Sel><Current><Straight>Off</Straight><Sound_Program>'+sound_stage+'</Sound_Program></Current></Program_Sel></Surround></Main_Zone></YAMAHA_AV>'
    x = requests.post(url,data)


def print_settings():
    get_settings()
    get_config()
    print("Model:",model_name," ID:",system_id, " Version:", version, "IP:",ip)
    print("Power:",power," Volume:",volume, " Input:", input_sel, " Sound:", sound_program)
    print("---------------------------------------------------------")

# parse args
desc = '''CLI controls for yamaha receiver.

'''
parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-v', '--version', dest='display_version', action='store_true',
                    help=('Display version'))

parser.add_argument('-vu', '--volume-up', dest='volume_up', default=False,action='store_true',
                    help=('Increase volume by .5 dbm '))

parser.add_argument('-vd','--volume-down',dest='volume_down', default=False, action='store_true',
                    help=('Decrease volume by .5 dbm'))

parser.add_argument('-tp','--toggle-power',dest='toggle', default=False, action='store_true',
                    help=('Toggle power'))                       

parser.add_argument('--input', dest='input',
                    help=('Change input to provided string'))

parser.add_argument('--volume', dest='volume',
                    help=('Directly sets the volume based off raw dbm must be a factor of .5. e.g. -43.5 (Be careful)'))

parser.add_argument('--sound', dest='sound',
                    help=('Changes the sound program. Replace names that have spaces with "_" e.g. 7ch_Stereo, 2ch_Stereo'))

parser.add_argument('--list-inputs', dest='list_inputs', action='store_true',
                    help=('Display all inputs'))

parser.add_argument('--list-sounds', dest='list_sound', action='store_true',
                    help=('Displays all sound programs'))

args = parser.parse_args()


print_settings()

if args.volume_up:
    set_volume_increase()
elif args.volume_down:
    set_volume_decrease()
elif args.volume:
    set_volume_raw(str(args.volume))
elif args.input:
    set_input(str(args.input))
elif args.list_inputs:
    list_inputs()
elif args.display_version:
    print("Program Version:",program_version)
elif args.toggle:
    toggle_power()
elif args.sound:
    set_sound_stage(str(args.sound).replace('_', ' '))
elif args.list_sound:
    list_sound_programs()

