 # 
 # main.py: Run Step Tracking algorithm and save results
 # Copyright (c) 2023 Gonzalo J. Carracedo
 # 
 # This program is free software: you can redistribute it and/or modify  
 # it under the terms of the GNU General Public License as published by  
 # the Free Software Foundation, version 3.
 #
 # This program is distributed in the hope that it will be useful, but 
 # WITHOUT ANY WARRANTY; without even the implied warranty of 
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
 # General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License 
 # along with this program. If not, see <http://www.gnu.org/licenses/>.
 #

from RMSListener import RMSListener
from RotorController import RotorController
from SunLocation import SunLocation
from StepTracker import StepTracker
from astropy.time import Time
from astropy.coordinates import Angle
import astropy.units as u
import sys
from datetime import datetime

import time
import numpy as np

OBS_LATITUDE  = 40.45     # deg
OBS_LONGITUDE = -3.483056 # deg
OBS_HEIGHT    = 600       # m

MIN_ELEVATION = 22        # deg

sunloc = SunLocation(OBS_LATITUDE, OBS_LONGITUDE, OBS_HEIGHT)

az, el = sunloc.azel()

def azel2str(az, el):
  az = Angle(az * u.deg)
  el = Angle(el * u.deg)

  astr = az.to_string(unit = u.deg, sep = ('º ', "' ", '" '))
  estr = el.to_string(unit = u.deg, sep = ('º ', "' ", '" '))

  return f'{astr:12.15}, {estr:12.15}'

if el < MIN_ELEVATION:
  print(f'\033[1;31mRefusing to start:\033[0;1m Sun is too low now \033[0m({azel2str(az, el)})')
  sys.exit(1)


# Initialize rotor
rotor = RotorController("/dev/ttyUSB0")
az, el = rotor.readCurrentPos()

# Adjust max current
rotor.setMaxCurrent('AZ', 10)
rotor.setMaxCurrent('EL', 10)

rotor.setMinSpeed('AZ', 75)
rotor.setMinSpeed('EL', 100)

# Initialize SigDigger connection
listener = RMSListener("0.0.0.0", 9999)
print("[i] Waiting for SigDigger... ", end = "")
client = listener.listen()
print(fr"connected! ({client[0]}:{client[1]})")

# Create step step tracker and track
tracker = StepTracker(listener, rotor, threshold = 1e-5, wait = 2.5)

def mjd():
  return Time(time.time(), format = 'unix').mjd

az, el = sunloc.azel()

timeStamp = datetime.now().strftime("%Y%m%d_%H%M%SZ")

logFile = fr'sun_{timeStamp}.csv'
fp = open(logFile, 'w')

print(f'[i] Saving Sun to {logFile}...')

while True:
  power, az, el, count = tracker.track(az, el)
  rotor.goto(az, el)

  sunAz, sunEl = sunloc.azel()
  fp.write(f'{time.time()},{mjd()},{az},{el},{sunAz},{sunEl},{power},{10 * np.log10(power)},{count}\n')
  fp.flush()

  timeStamp = datetime.now().strftime("%Y/%m/%d-%H:%M:%SZ")

  print(f'\033[1;33mSUN LOCATION REPORT\033[0;1m - {timeStamp}\033[0m')
  print(f'  \033[1;32mPREDICTED\033[0m:\033[1m {azel2str(sunAz, sunEl)}')
  print(f'  \033[1;32mMEASURED\033[0m:\033[1m  {azel2str(az, el)}')
  print(f'  \033[1;32mPOWER\033[0m:\033[1m     {10 * np.log10(power):.3f} dB\033[0m')

  time.sleep(10)
