 # 
 # RMSListener.py: Listen to RMS measurements from SigDigger
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

import socket, threading
import time

class RMSListenerThread(threading.Thread):
  def __init__(self, listener):
    threading.Thread.__init__(self)
    self._listener  = listener
    self._power     = None
    self._finalized = False

  def run(self):
    try:
      while True:
        alpha  = self._listener.alpha()
        line   = self._listener.readline()
        parts  = line.split(',')

        if len(parts) == 4:
          try:
              power = float(parts[2])
              time  = float(parts[0])

              if self._power is None:
                self._power = power
              else:
                self._power += alpha * (power - self._power)
                self._listener.setLastPower(time, self._power)
              
          except:
            print(fr"Malformed power ({parts[2]})")
      
    except Exception as e:
      print(fr"Read error: {str(e)}")
      self._finalized = True
      
    
  def finalized(self):
    return self._finalized
  
class RMSListener:
  def __init__(self, ip: str, port: int, alpha: float = .1):
    self._ip = ip
    self._port = port
    self._thread = None
    self._alpha  = alpha

    self._srvsck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._srvsck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self._srvsck.bind((ip, port))
    
    self._clisck  = None
    self._cliaddr = None
    self._clifp   = None

    self._lastPower = None
    self._lastPowerTime = time.time()

  def setLastPower(self, time: float, power: float):
    self._lastPower = power
    self._lastPowerTime = time

  def alpha(self):
    return self._alpha
  
  def listen(self):
    if self._clisck is not None:
      raise RuntimeError("Client already connected")

    self._srvsck.listen(1)
    self._clisck, self._cliaddr = self._srvsck.accept()
    self._clifp = self._clisck.makefile()

    self._thread = RMSListenerThread(self)
    self._thread.start()

    return self._cliaddr
  
  def readline(self):
    if self._clifp is None:
      raise RuntimeError("Client socket is closed")

    return self._clifp.readline()
  
  def lastPower(self):
    return self._lastPower
  
  def lastPowerTime(self, when = None):
    if when is None:
      when = time.time()
    
    while self._lastPowerTime < when:
      time.sleep(.1)
    
    return self._lastPower
  
  def running(self):
    if self._thread is None:
      return False

    return not self._thread.finalized()
  
  def join(self):
    if self._thread is not None:
      self._thread.join()
      self._clifp.close()
      self._clisck.close()
      self._clisck  = None
      self._cliaddr = None
      self._thread  = None