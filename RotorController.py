 # 
 # RotorController.py: Interact with the AzElBox controller
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

import serial, time
import numpy as np

class RotorController:
  def __init__(self, port: str, baudrate: int = 115200):
    self._port = port
    self._minspeed = {'AZ' : 70, 'EL' : 100}

    self._serial = serial.Serial(
      port       = port,
      baudrate   = baudrate,
      parity     = serial.PARITY_NONE,
      stopbits   = serial.STOPBITS_ONE,
      bytesize   = serial.EIGHTBITS,
      timeout    = 1)

    self.readCurrentPos()
  
  def readline(self):
    data = self._serial.readline()
    return data
    
  def readfields(self):
    line = self.readline().decode('utf-8').strip()
    return line.split(':')
  
  def writeCmd(self, cmd):
    self._serial.write(f'{cmd}\n'.encode('utf-8'))
  
  def waitInfo(self):
    while True:
      fields = self.readfields()
      if fields[0] == "I" and len(fields) > 1:
        return fields  
      elif fields[0] == "E":
        raise RuntimeError('Command error: ' + (': '.join(fields[1:])))
    
  def setMaxCurrent(self, motor: str, current: float):
    self.writeCmd(fr'OVERCURRENT {motor} {current}')

    while True:
      fields = self.waitInfo()
      if fields[1] == fr"OVERCURRENT[{motor}]":
        return
    
  def minSpeed(self, motor: str):
    return self._minspeed[motor]
  
  def setMinSpeed(self, motor: str, speed: float):
    self.writeCmd(fr'MINSPEED {motor} {speed}')
    self._minspeed[motor] = speed

    while True:
      fields = self.waitInfo()
      if fields[1] == fr"MINSPEED[{motor}]":
        return
    
  def waitMotors(self):
    azReason = None
    elReason = None

    while azReason is None or elReason is None:
      fields = self.waitInfo()
      if fields[1] == 'FINALIZED[AZ]':
        azReason = fields[2]
      elif fields[1] == 'FINALIZED[EL]':
        elReason = fields[2]

    time.sleep(.1)
    return azReason, elReason

  def readCurrentPos(self):
    self.writeCmd("POS")

    while True:
      fields = self.waitInfo()
      if fields[1] == "POS" and len(fields) == 4:
        az = float(fields[2])
        el = float(fields[3])
        self._az = az
        self._el = el
        return az, el

  def goto(self, az: float, el: float):
    az = np.remainder(.5 * round(2 * az), 360)
    el = np.remainder(.5 * round(2 * el), 360)

    self.writeCmd(fr"GOTO {az} {el}")
    sAz, sEl = self.waitMotors()

    if sAz != 'SUCCESS':
      raise RuntimeError(fr'Azimuth motor failed to move with status {sAz}')
    
    if sEl != 'SUCCESS':
      raise RuntimeError(fr'Elevation motor failed to move with status {sEl}')
  