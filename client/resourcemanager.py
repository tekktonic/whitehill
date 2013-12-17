#  Copyright (C) 2013 Daniel Wilkins <tekk@parlementum.net>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
from sdl2 import *
import sdl2.sdlimage

class ResourceManager(dict):
    def fetch(self, resource):
        try:
            return self[resource]
        except KeyError:
            self[resource] = sdl2.sdlimage.IMG_Load(bytes("resources/" + resource, encoding="ascii"))
        return self[resource]

