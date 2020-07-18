# Yamaha Python CLI

The purpose of this project was to bring controls of the yamaha receiver to the the command line.


## Description

It was tricky always working with the network api for the yahmaha receiver. Most of what I wanted to do was change volume and inputs.
This was formally done by running curl commands but that didnt scale so here we are.

## Getting Started

### Dependencies

* Python3

### Installing

* Edit network.config to contain the ip address of your yamaha device

```
sudo chmod +x yamaha_controls.py
```
* Make program executable

```
sudo chmod +x yamaha_controls.py
```
### Executing program

```
./yamaha_controls.py 

Model: RX-V867  ID: 0B974DF3  Version: 2.70/2.01
Power: On  Volume: -390  Input: HDMI1  Sound: 7ch Stereo
---------------------------------------------------------
```
```
./yamaha_controls.py --list-inputs

MULTI CH
Brad-PC
Chrome
HDMI3
HDMI4
HDMI5
AV1
AV2
AV3
AV4
AV5
AV6
V-AUX
AUDIO1
AUDIO2
DOCK
```


## Help

```
./yamaha_controls.py -h


usage: yamaha_controls.py [-h] [-v] [-vu] [-vd] [--input INPUT] [--volume VOLUME] [--list-inputs]

CLI controls for yamaha receiver.

optional arguments:
  -h, --help          show this help message and exit
  -v, --version       Display version
  -vu, --volume-up    Increase volume by .5 dbm
  -vd, --volume-down  Decrease volume by .5 dbm
  --input INPUT       Change input to provided string
  --volume VOLUME     Directly sets the volume based off raw dbm must be a factor of .5. e.g. -43.5 (Be careful)
  --list-ind to run if program contains helper info
```

## Authors

* Brad Wilson

## Version History

* 0.0.1
    * Initial Release


