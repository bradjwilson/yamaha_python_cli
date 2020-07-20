#!/usr/bin/env python3

import sys
import requests
import xml.etree.ElementTree as ET
import argparse
import configparser
import os
from html.parser import HTMLParser
from blessed import Terminal

program_version = '0.0.1'


ip = ''

usage_menu = (
        "  +-------------------------------+-------------------------+\n"
        "  | Volume Down    j or <Down>    | List Inputs        i    |\n"
        "  | Volume Up      k or <Up>      | List Sounds        s    |\n"
        "  | Toggle Power   t              | Input/Sound        /    |\n"
        "  +-------------------------------+-------------------------+\n"
        "   (press q to exit)\n")

config = configparser.ConfigParser()
config.read(os.path.dirname(__file__)+'/network.conf')
ip = config.get('yamaha.config', 'yamaha_ip')

url = 'http://' + ip + '/YamahaRemoteControl/ctrl'
class YamahaCLI():
    def __init__(self):
        self.term = Terminal()
        self.power = 0
        self.volume = 0
        self.input_sel = 0
        self.sound_program = 0
        self.model_name = 0
        self.system_id = 0
        self.version = 0
        self.input_list = []
    class SoundsHTMLParser(HTMLParser):
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

        def handle_data(self, data):
            if self.recording:
                self.data.append(data)
            if self.save_next_data:
                self.sound_programs.append(data)
                self.save_next_data = False


    def list_sound_programs(self):
        x = requests.get(url= 'http://' + ip)
        parser = self.SoundsHTMLParser()
        parser.feed(str(x.content))
        print(*parser.sound_programs, sep = " / ") 


    def list_inputs(self):
        data = '<YAMAHA_AV cmd="GET"><System><Config>GetParam</Config></System></YAMAHA_AV>'
        x = requests.post(url,data)
        root = ET.fromstring(x.content)
        for child in root.iter('*'):
            if child.tag == 'Input':
                for inputs in child.iter('*'):
                    self.input_list.append(inputs.text)
        print(*self.input_list, sep = " / ")
                    

    def get_config(self):
        data = '<YAMAHA_AV cmd="GET"><System><Config>GetParam</Config></System></YAMAHA_AV>'
        x = requests.post(url,data)
        root = ET.fromstring(x.content)
        for child in root.iter('*'):
            #print(child.tag, " ", child.text)
            if child.tag == 'Model_Name':
                self.model_name = child.text
            if child.tag == 'System_ID':
                self.system_id = child.text
            if child.tag == 'Version':
                self.version = child.text

    def get_settings(self):
        data = '<YAMAHA_AV cmd="GET"><Main_Zone><Basic_Status>GetParam</Basic_Status></Main_Zone></YAMAHA_AV>'
        x = requests.post(url,data)
        root = ET.fromstring(x.content)
        for child in root.iter('*'):
                if child.tag == 'Power':
                    self.power = child.text
                if child.tag == 'Val':
                    self.volume = int(child.text)
                if child.tag == 'Input_Sel':
                    self.input_sel = child.text
                if child.tag == 'Sound_Program':
                    self.sound_program = child.text

    def set_volume_raw(self, volume_raw):
        print(str(10 * float(volume_raw)).replace('.0', ''))
        data = '<YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Lvl><Val>' + str(10 * float(volume_raw)).replace('.0', '') + '</Val><Exp>1</Exp><Unit>dB</Unit></Lvl></Volume></Main_Zone></YAMAHA_AV>'
        requests.post(url,data)

    def toggle_power(self):
        if self.power == "On":
            self.power = 'Standby'
        else:
            self.power = 'On'
        print(self.power)
        data = '<YAMAHA_AV cmd="PUT"><Main_Zone><Power_Control><Power>'+self.power+'</Power></Power_Control></Main_Zone></YAMAHA_AV>'
        requests.post(url,data)

    def set_power(self, user_power):
        print(self.power)
        data = '<YAMAHA_AV cmd="PUT"><Main_Zone><Power_Control><Power>'+user_power+'</Power></Power_Control></Main_Zone></YAMAHA_AV>'
        requests.post(url,data)

    def set_volume_increase(self):
        self.get_settings
        self.volume += 5
        data = '<YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Lvl><Val>' + str(self.volume) + '</Val><Exp>1</Exp><Unit>dB</Unit></Lvl></Volume></Main_Zone></YAMAHA_AV>'
        requests.post(url,data)

    def set_volume_decrease(self):
        self.get_settings
        self.volume -= 5
        data = '<YAMAHA_AV cmd="PUT"><Main_Zone><Volume><Lvl><Val>' + str(self.volume) + '</Val><Exp>1</Exp><Unit>dB</Unit></Lvl></Volume></Main_Zone></YAMAHA_AV>'
        requests.post(url,data)

    def set_input(self, input):
        data = '<YAMAHA_AV cmd="PUT"><Main_Zone><Input><Input_Sel>' + input + '</Input_Sel></Input></Main_Zone></YAMAHA_AV>'
        requests.post(url,data)

    def set_sound_stage(self, sound_stage):
        data = '<YAMAHA_AV cmd="PUT"><Main_Zone><Surround><Program_Sel><Current><Straight>Off</Straight><Sound_Program>'+sound_stage+'</Sound_Program></Current></Program_Sel></Surround></Main_Zone></YAMAHA_AV>'
        requests.post(url,data)


    def print_settings(self):
        self.get_settings
        self.get_config
        print("Model:",self.model_name," ID:",self.system_id, " Version:", self.version, "IP:",ip)
        print("Power:",self.power," Volume:",str(self.volume/10.0)+"dbm", " Input:", self.input_sel, " Sound:", self.sound_program)
        print("---------------------------------------------------------")

    def parseargs(self):
        # parse args
        desc = '''CLI controls for yamaha receiver.'''
        parser = argparse.ArgumentParser(
            description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('-v', '--version', dest='display_version', action='store_true',
                            help=('Display version'))

        parser.add_argument('-vu', '--volume-up', dest='volume_up', default=False,action='store_true',
                            help=('Increase volume by .5 dbm '))

        parser.add_argument('-vd','--volume-down',dest='volume_down', default=False, action='store_true',
                            help=('Decrease volume by .5 dbm'))

        parser.add_argument('--on',dest='on', default=False, action='store_true',
                            help=('Power On'))    

        parser.add_argument('--off',dest='off', default=False, action='store_true',
                            help=('Power Off'))    

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

        return parser.parse_args()


    def text_entry(self):
        """ Relay literal text entry from user to Roku until
        <Enter> or <Esc> pressed. """

        allowed_sequences = set(['KEY_ENTER', 'KEY_ESCAPE', 'KEY_DELETE'])

        sys.stdout.write('Enter text (<Esc> to abort) : ')
        sys.stdout.flush()

        # Track start column to ensure user doesn't backspace too far
        start_column = self.term.get_location()[1]
        cur_column = start_column
        choice = ''
        with self.term.cbreak():
            val = ''
            while val != 'KEY_ENTER' and val != 'KEY_ESCAPE':
                val = self.term.inkey()
                if not val:
                    continue
                elif val.is_sequence:
                    val = val.name
                    if val not in allowed_sequences:
                        continue

                if val == 'KEY_ENTER':
                    break
                elif val == 'KEY_ESCAPE':
                    pass
                elif val == 'KEY_DELETE':
                    if cur_column > start_column:
                        sys.stdout.write(u'\b \b')
                        cur_column -= 1
                        choice = choice[:-1]
                else:
                    choice = choice + val
                    sys.stdout.write(val)
                    cur_column += 1
                sys.stdout.flush()

            # Clear to beginning of line
            self.set_input(choice)
            self.set_sound_stage(choice)
            sys.stdout.write(self.term.clear_bol)
            sys.stdout.write(self.term.move(self.term.height, 0))
            sys.stdout.flush()

    def run(self):

        cmd_func_map = {
            'KEY_DOWN':   self.set_volume_decrease,
            'KEY_UP':     self.set_volume_increase,
            'KEY_LEFT':   self.list_inputs,
            'KEY_RIGHT':  self.list_sound_programs,
            't':          self.toggle_power,
            'i':          self.list_inputs,
            's':          self.list_sound_programs,
            '/':          self.text_entry}

        args = self.parseargs()

        if args.volume_up:
            self.set_volume_increase()
        elif args.volume_down:
            self.set_volume_decrease()
        elif args.volume:
            self.set_volume_raw(str(args.volume))
        elif args.input:
            self.set_input(str(args.input))
        elif args.list_inputs:
            self.list_inputs
        elif args.display_version:
            print("Program Version:",program_version)
        elif args.toggle:
            self.toggle_power
        elif args.sound:
            self.set_sound_stage(str(args.sound).replace('_', ' '))
        elif args.list_sound:
            self.list_sound_programs
        elif args.on:
            self.set_power('On')
        elif args.off:
            self.set_power('Standby')
        else:
            # Main interactive loop
            sys.stdout.write(usage_menu)
            sys.stdout.flush()
            with self.term.cbreak():
                val = ''
                while val.lower() != 'q':
                    val = self.term.inkey()
                    if not val:
                        continue
                    if val.is_sequence:
                        val = val.name
                    if val in cmd_func_map:
                        try:
                            cmd_func_map[val]()
                        except:
                            print('Unable to communicate with yamaha at ')
                            print(val)

def main():
    receiver = YamahaCLI()
    receiver.get_config()
    receiver.get_settings()
    receiver.print_settings()
    receiver.run()



main()