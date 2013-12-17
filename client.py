#  Copyright (C) 2013 Xander Vedejas <xvedejas@gmail.com>
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
import sys
from numpy import array
try:
    from sdl2 import *
    import sdl2.ext as sdl2ext
except ImportError:
    import traceback
    traceback.print_exc()
    sys.exit(1)
    
#pysdl2.readthedocs.org/en/latest/tutorial/pong.html

class SoftwareRenderer(sdl2ext.SoftwareSpriteRenderer):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def render(self, components):
        sdl2ext.fill(self.surface, sdl2ext.Color(0, 0, 0))
        super(SoftwareRenderer, self).render(components)

class Entity(sdl2ext.Entity):
    """An entity is something drawn on the map that can change position
       (and thus can be re-drawn), as opposed to the map itself or
       overlays like menus and text"""
    def __init__(self, world, sprite, position):
        self.sprite = sprite
        self.sprite.position = position
    def move(self, speed, direction):
        self.speed = speed
        self.direction = direction
    
def run():
    sdl2ext.init()
    window = sdl2ext.Window("The White Hill", size=(800, 600))
    window.show()
    
    world = sdl2ext.World()

    spriterenderer = SoftwareRenderer(window)
    world.add_system(spriterenderer)

    factory = sdl2ext.SpriteFactory(sdl2ext.SOFTWARE)
    sp_p1 = factory.from_color(sdl2ext.Color(255, 255, 255), size=(20, 100))
    sp_p2 = factory.from_color(sdl2ext.Color(255, 255, 255), size=(20, 100))

    player1 = Entity(world, sp_p1, array((0, 250)))
    player2 = Entity(world, sp_p2, array((780, 250)))
    
    running = True
    while running:
        events = sdl2ext.get_events()
        for event in events:
            if event.type == SDL_QUIT:
                running = False
                break
        world.process()
        
    return 0

if __name__ == "__main__":
    sys.exit(run())
