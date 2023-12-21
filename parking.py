 # 
 # parking.py: Moves the dish to the parking position
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

from RotorController import RotorController
from Logger import Logger

PARKING_AZ = 180
PARKING_EL = 60

log = Logger()
# Initialize rotor
rotor = RotorController("/dev/ttyUSB0")
az, el = rotor.readCurrentPos()

# Adjust max current
rotor.setMaxCurrent('AZ', 10)
rotor.setMaxCurrent('EL', 10)

rotor.setMinSpeed('AZ', 100)
rotor.setMinSpeed('EL', 100)

repeat = True
failed = False
minSpeedAz = rotor.minSpeed('AZ')
minSpeedEl = rotor.minSpeed('EL')

while repeat:
  try:
    rotor.goto(PARKING_AZ, PARKING_EL)
    repeat = False
  except RuntimeError as e:
    explain = str(e)
    if explain.find('TIMEOUT') == -1:
      raise e
    failed = True
    rotor.setMinSpeed('AZ', 100)
    rotor.setMinSpeed('EL', 100)
    log.warning(f'Dish stuck! Trying again...')

if failed:
  rotor.setMinSpeed('AZ', minSpeedAz)
  rotor.setMinSpeed('EL', minSpeedEl)


