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
import sdl2.ext # needed for colors
import server
import numpy
import time

def main():
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(b"Whitehill", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, 800, 640, 0)
    windowSurface = SDL_GetWindowSurface(window)
    world = server.WorldMap(binsize=numpy.array((50, 40)))

    player = server.Entity(spritename="player", world=world, position=numpy.array((0,0)), zlayer=1, size=numpy.array((16,16)),
                           collisionbox=server.Box(numpy.ones((16,16))))
    player.direction = numpy.array((1, 1))
    player.speed = 16

    SDL_FillRect(windowSurface, rect.SDL_Rect(0, 0, 16, 16), sdl2.ext.Color())
    SDL_UpdateWindowSurface(window)

    running = True
    while running:
        time.sleep(1.0)
        world.move_all()
        print(player.position)
        x, y = player.position

        SDL_FillRect(windowSurface, rect.SDL_Rect(x, y, 16, 16), sdl2.ext.Color())
        SDL_UpdateWindowSurface(window)
        pass


main()
