 # 
 # RMSListener.py: Listen to RMS measurements
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

import time
import numpy as np

DELTA     = .5
POWERFRAC = 0.1 # At least 10% better


class StepTracker:
  def __init__(self, rms: RMSListener, rotor: RotorController, threshold: float = POWERFRAC, wait: float = 2., delta = DELTA):
    self._rms   = rms
    self._rotor = rotor
    self._k     = 1 + threshold
    self._wait  = wait
    self._delta = delta

  def measurePower(self, az: float, el: float):
    repeat = True

    while repeat:
      try:
        self._rotor.goto(az, el)
        repeat = False
      except RuntimeError as e:
        explain = str(e)
        if explain.find('TIMEOUT') == -1:
          raise e
        print(f'\033[1;31m[T]\033[0m ', end = '', flush = True)
    
    time.sleep(self._wait)
    return self._rms.lastPower()
  
  def diamondSearch(self, az: float, el: float, best = None):
    print(fr'[i] Perform square search around {az}, {el}...')
    # .----- 2 <----.
    # v             |
    # 3     [C] --> 1
    # |      ^
    # .______4
          
    d   = self._delta
    azs = [az, az + d, az    , az - d, az    ]
    els = [el, el    , el + d, el    , el - d]

    azs = d * np.round(np.array(azs) / d)
    els = d * np.round(np.array(els) / d)
    
    pwr = np.zeros(azs.shape)
    
    # If a previous best candidate has been provided, skip central point
    if best is not None:
      i       = 1
      pwr[0]  = best[0]
    else:
      i       = 0

    bestNdx  = i - 1

    while i < len(azs):
      print(fr'[i] GOTO {azs[i]}, {els[i]} => ', end = '', flush = True)
      pwr[i] = self.measurePower(azs[i], els[i])
      print(fr'{10 * np.log10(pwr[i]):g} dB')

      if bestNdx < 0 or pwr[i] > self._k * pwr[bestNdx]:
          bestNdx = i
          print(fr'[i]   Current best!')
      
      i += 1

    return pwr[bestNdx], azs[bestNdx], els[bestNdx], bestNdx

  def track(self, az: float, el: float):
    settle = False
    best   = None
    count  = -1

    while not settle:
      count += 1
      best   = self.diamondSearch(az, el, best)
      settle = best[3] == 0
      az     = best[1]
      el     = best[2]

    bestPower = best[0]

    return bestPower, az, el, count
  