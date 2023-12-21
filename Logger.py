 # 
 # Logger.py: Logging singleton
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

from datetime import datetime

class Logger:        
  class _Logger:
    def __init__(self):
      self._brokenLine = False

    def log(self, pfx, color, text, end = '\n'):
      # Write prefix only if the previous line was not broken
      if not self._brokenLine:
        timeStamp = datetime.now().strftime("%Y/%m/%d-%H:%M:%SZ")
        print('\033[2K', end = '')
        print(f'{timeStamp} - ', end = '')
        print(f'\033[1;{30 + color}m{pfx}:\033[0m ', end = '')
      
      print(text, end = end, flush = True)

      self._brokenLine = end is None or len(end) == 0

    def info(self, text, end = '\n'):
      self.log('INFO', 2, text, end)

    def idle(self, text, end = '\n'):
      self.log('IDLE', 6, text, end)
    
    def warning(self, text, end = '\n'):
      self.log('WARN', 3, text, end)

    def error(self, text, end = '\n'):
      self.log(' ERR', 1, text, end)
  
  _instance = None

  def __new__(cls): # __new__ always a classmethod
    if Logger._instance is None:
      Logger._instance = Logger._Logger()
    return Logger._instance
  
  def __getattr__(self, name):
    return getattr(self._instance, name)
  
  def __setattr__(self, name):
    return setattr(self._instance, name)

  