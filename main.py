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
from Logger import Logger
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

def azel2str(az, el):
  az = Angle(az * u.deg)
  el = Angle(el * u.deg)

  astr = az.to_string(unit = u.deg, sep = ('º ', "' ", '" '))
  estr = el.to_string(unit = u.deg, sep = ('º ', "' ", '" '))

  return f'{astr:12.15}, {estr:12.15}'

def mjd():
  return Time(time.time(), format = 'unix').mjd

az, el = sunloc.azel()
log = Logger()

while el < MIN_ELEVATION:
  timeStamp = datetime.now().strftime("%Y/%m/%d-%H:%M:%SZ")
  log.idle(f'Sun is too low now \033[0m({azel2str(az, el)})', end = '\r')
  time.sleep(1)
  az, el = sunloc.azel()

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
log.info("Waiting for SigDigger... ", end = "")
client = listener.listen()
log.info(fr"connected! ({client[0]}:{client[1]})")

# Create step step tracker and track
tracker = StepTracker(listener, rotor, threshold = 1e-5, wait = 2.5)

timeStamp = datetime.now().strftime("%Y%m%d_%H%M%SZ")

logFile = fr'sun_{timeStamp}.csv'
fp = open(logFile, 'w')

log.info(f'Saving Sun to {logFile}...')

az, el = sunloc.azel()
while True:
  if el < MIN_ELEVATION:
    log.info(f"Tracking finished. Elevation fell below {MIN_ELEVATION}\033[0m")
    sys.exit(0)
  
  power, az, el, count = tracker.track(az, el)
  rotor.goto(az, el)

  sunAz, sunEl = sunloc.azel()
  fp.write(f'{time.time()},{mjd()},{az},{el},{sunAz},{sunEl},{power},{10 * np.log10(power)},{count}\n')
  fp.flush()

  timeStamp = datetime.now().strftime("%Y/%m/%d-%H:%M:%SZ")

  log.info('\033[1mSun location report\033[0m:')
  log.info(f'  \033[1mMeasured\033[0m:  {azel2str(az, el)}')
  log.info(f'  \033[1mExpected\033[0m:  {azel2str(sunAz, sunEl)}')
  log.info(f'  \033[1mPower\033[0m:     {10 * np.log10(power):.3f} dB')

  time.sleep(10)
