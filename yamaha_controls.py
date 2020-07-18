#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
import argparse
import configparser

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
config.read('network.conf')
ip = config.get('yamaha.config', 'yamaha_ip')

url = 'http://' + ip + '/YamahaRemoteControl/ctrl'

def display_inputs():
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
    #x = requests.post(url,data)


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

parser.add_argument('--input', dest='input',
                    help=('Change input to provided string'))

parser.add_argument('--volume', dest='volume',
                    help=('Directly sets the volume based off raw dbm must be a factor of .5. e.g. -43.5 (Be careful)'))


parser.add_argument('--list-inputs', dest='list_inputs', action='store_true',
                    help=('Display all inputs'))

args = parser.parse_args()


print_settings()

if args.volume_up:
    set_volume_increase()
elif args.volume_down:
    set_volume_decrease()
elif args.volume != None:
    set_volume_raw(str(args.volume))
elif args.input != None:
    set_input(str(args.input))
elif args.list_inputs:
    display_inputs()
elif args.display_version:
    print("Program Version:",program_version)



