 # 
 # SunLocation.py: Retrieve Sun AzEl from a given location on Earth
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

from astropy.time import Time
from astropy.coordinates import get_sun
import astropy.units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord

import time

class SunLocation:
  def __init__(self, lat: float, lon: float, height: float):
    self._lat    = lat
    self._lon    = lon
    self._height = height

    self._loc     = EarthLocation(lat = lat, lon = lon, height = height)

  def azel(self, when: Time = None):
    if when is None:
      when = Time(time.time(), format = 'unix')

    sun = get_sun(when)
    azimuthal = sun.transform_to(AltAz(obstime = when, location = self._loc))
    return azimuthal.az / u.deg, azimuthal.alt / u.deg

