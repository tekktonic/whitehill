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
import resourcemanager
import time

class Frame():
    def __init__(self, image, t):
        self.image = image
        self.time = t

class Animation():
    def __init__(self, resourceManager, *args):
        self.resourceManager = resourceManager
        self.frames = list()
        self.currentFrame = 0
        self.lastTime = time.time()
        [self.LoadFrame(arg) for arg in args]

    def LoadFrame(self, frametuple):
        string, t = frametuple
        self.frames.append(Frame(self.resourceManager.fetch(string), t))
    
    def Step(self):
        t = time.time()
        if (t - self.lastTime) > self.frames[self.currentFrame].time:
            if self.currentFrame < len(self.frames) - 1:
                self.currentFrame += 1
            else:
                self.currentFrame = 0

        self.lastTime = t
        return self.frames[self.currentFrame]
