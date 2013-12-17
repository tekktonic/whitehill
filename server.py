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
import pickle, numpy, time
from numpy import ceil, floor, array

pixels_per_bin = 16

def normalize(vector):
    """This represents the direction of a vector (not so much the magnitude).
       There are nine directions a vector can point in this engine:
       
       NW N NE       (-1,-1)  (0,-1)  (1,-1)
       W  .  E  -->  (-1, 0)  (0, 0)  (1, 0)
       SW S SE       (-1, 1)  (0, 1)  (1, 1)
       """
    x, y = vector
    if x > 0: x = 1
    if x < 0: x = -1
    if y > 0: y = 1
    if y < 0: y = -1
    return array((x, y))

class Box():
    """Conceptually, a Box is a convex polygon. It is implemented as a bit map
       where 1s are contained in the polygon and 0s are not. This allows
       individual pixel designation of things like collision boxes.
       There might be better (cheaper but still powerful) ways of doing this."""
    def __init__(self, array):
        self.array = numpy.array(array, dtype='b')
        self.size = numpy.array(self.array.shape)
    
    def union(self, otherbox):
        return Box(numpy.logical_or(self.array, otherbox.array))
    
    def collides(self, otherbox):
        return numpy.logical_and(self.array, otherbox.array).any()

class Entity():
    """An entity represents anything on the world map which falls into any of
       the following categories:
       
       - It can move
       - It can block other entities from moving
       - The player can interact with it based on player position
       
       So essentially every visual thing is an entity except for the world map
       background and menus/overlays."""
    def __init__(self, spritename, world, position, zlayer, size, collisionbox):
        self.spritename = spritename
        self.world = world
        # The position is the absolute pixel placement of the upperleft most
        # corner of the entity.
        self.position = position
        # Used for movement. Speed is in pixels per second
        self.speed = 24
        self.direction = array((0, 0))
        
        # The z layer is an integer (positive or negative)
        self.zlayer = zlayer
        
        self.size = size
        self.collisionbox = collisionbox
        
        self.world.add_entity(self)
    
    @property
    def velocity(self):
        return self.direction * self.speed
    
    @property
    def binpos(self):
        return self.position // pixels_per_bin
    
    @property
    def binsize(self):
        # The binsize is the maximum number of bins the entity can fill at once,
        # given any pixel position. If the sprite for this entity extends
        # outside of the binsize, the sprite may not be properly drawn.
        return self.size // pixels_per_bin + 1
    
    def move(self, direction, velocity):
        self.direction = direction
        self.velocity = velocity
    
    def sorting_key(self):
        """Gives a key to sort the entity first by z layer, then by its "base".
           The "base" is just the lowest y position occupied by the entity."""
        x, y = self.position
        width, height = self.size
        return (self.zlayer, y + height)

class WorldMap():
    def __init__(self, binsize):
        self.binsize = binsize
        width, height = binsize
        assert width >= 50 # screenwidth in bins
        assert height >= 40 # screenheight in bins
        self.entity_map = numpy.empty((width, height), dtype='O')
        self.previous_time = time.time()
        
    def entity_submap(self, binpos, binsize):
        x, y = binpos
        width, height = binsize
        selfwidth, selfheight = self.binsize
        if x < 0:
            width += x
            x = 0
        elif x + width > selfwidth:
            width = selfwidth - x
        if y < 0:
            height += y
            y = 0
        elif y + height > selfheight:
            height = selfheight - y
        return self.entity_map[x:x+width,y:y+height]
        
    def add_entity(self, entity):
        for row in self.entity_submap(entity.position, entity.binsize):
            for i, entity_list in enumerate(row):
                if entity_list is None:
                    row[i] = [entity]
                else:
                    entity_list.append(entity)
    
    def remove_entity(self, entity):
        for row in self.entity_submap(entity.position, entity.binsize):
            for i, entity_list in enumerate(row):
                assert entity_list
                entity_list.remove(entity)
    
    def move_entity(self, entity, timestep):
        # In the case that we have velocity, first remove the entity
        # from the map before calculating how far it moves. 
        self.remove_entity(entity)
        
        # Now we test to see exactly when the entity's path is
        # obstructed (if ever). We do this by first considering
        # all bins that the entity could pass through in this
        # timestep.
        direction = entity.direction
        delta = direction * int(timestep * entity.speed)
        distance = max(numpy.abs(delta))
        dx, dy = delta
        
        old_x, old_y = entity.position
        new_x, new_y = entity.position + delta
        size_x, size_y = entity.size
        
        if dx > 0:
            x = old_x
            width = new_x - old_x + size_x
        else:
            x = new_x
            width = old_x - new_x + size_x
        if dy > 0:
            y = old_y
            height = new_y - old_y + size_y
        else:
            y = new_y
            height = old_y - new_y + size_y
        # Position and size of collision_array:
        binbox_binpos = array((x, y)) // pixels_per_bin
        binbox_size = array((width, height)) // pixels_per_bin + 1
        
        # Now that we know which bins are involved, we can create a
        # big array showing which pixels in those bins (and at
        # the current z layer) are currently blocking.
        array_size_x, array_size_y = binbox_size * pixels_per_bin
        collision_array = numpy.zeros((array_size_x, array_size_y))
        
        x, y = binbox_binpos
        width, height = binbox_size
        possibly_colliding_entities = set()
        for row in self.entity_submap(entity.position, entity.binsize):
            for i, entity_list in enumerate(row):
                if not entity_list:
                    continue
                for other_entity in entity_list:
                    if entity.zlayer == other_entity.zlayer:
                        possibly_colliding_entities.append(other_entity)
        
        for other_entity in possibly_colliding_entities:
            box = other_entity.collisionbox
            width, height = box.size
            x, y = other_entity.position - binbox_binpos * pixels_per_bin
            # Now that we have found a collision box, we must add it to
            # the collision array at the correct offset.
            ## TODO: check bounds
            collision_array[x:x + width, y:y + height] += box.array
        
        # Now we can move our entity's bounding box along its trajectory one
        # pixel at a time to find out when exactly it begins to collide.
        for i in range(distance):
            box = entity.collisionbox
            width, height = box.size
            x, y = (entity.position + i * direction -
                      binbox_binpos * pixels_per_bin)
            mapwidth, mapheight = self.binsize * pixels_per_bin
            if x < 0 or y < 0 or x+width >= mapwidth or y+height >= mapheight:
                break # collision with map boundaries
            collision_area = collision_array[x:x+width, y:y+height]
            if numpy.logical_and(collision_area, box).any():
                break # Here we have found a collision, stop moving
            entity.position += direction
        
        # Add our entity back onto the map in its new position
        self.add_entity(entity)
        
    def move_all(self):
        # The timestep is the time since the last movement calculation.
        this_time = time.time()
        timestep = this_time - self.previous_time
        
        # Note: possible future optimization: we may not need to worry about
        # moving things that no player currently can possibly see.
        
        # Now we iterate through all items on the map which have nonzero
        # velocity. We determine how far they can move in the timestep. If their
        # path is unobstructed, this is (time * velocity). If their path is
        # obstructed, they simply stop at the point of collision.
        
        moved_entities = set()
        width, height = self.binsize
        
        for i in range(width):
            for j in range(height):
                entity_list = self.entity_map[i][j]
                if entity_list is None:
                    entity_list = []
                    self.entity_map[i][j] = entity_list
                for entity in entity_list:
                    if entity.velocity.any() and entity not in moved_entities:
                        self.move_entity(entity, timestep)
                        moved_entities.add(entity)
        
        self.previous_time = this_time
        
    def get_view(self, position):
        """Returns all bins covered by a screen at the given position.
        
        Each bin is 16-by-16 pixels.
        The screen is 800x640 pixels which means that it covers 50 horizontal
        and 40 vertical bins when aligned. When not aligned, it covers 51
        horizontal and 41 vertical bins, so we'll go ahead and notify it of
        that many bins.
        
        Arguments:
        
            position: upperleft pixel position
        """
        x, y = floor(position / pixels_per_bin)
        map_slice = self.entity_map[x:x+51, y:y+41]
        entities = set()
        for item in map_slice:
            entities.add(item)
        
        # Now we want to sort the entities first by z layer, then by the y
        # position of their "base" (y position plus height).
        entities = sorted(entities, key=Entity.sorting_key)
        
        # What the client wants to know is: which sprite corresponds to which
        # entity? Each sprite/entity should share some sort of ID. This lets the
        # client decide how to animate and avoid allocating new sprite objects
        # all the time. The sprite ID is just the hash of the entity object.
        
        # Now consider the sprites objects which the client hasn't created yet.
        # We need to send the name of the sprite (which determines the
        # subdirectory in which we find images for that sprite).
        
        def relevant_info(entity):
            hash_ = hash(entity)
            name = entity.spritename
            relative_position = entity.position - position
            return (hash_, name, relative_position)
        
        return pickle.pickle(map(entities, relevant_info))

def test():
    world = WorldMap(binsize=array((50, 40)))

    player = Entity(spritename="player",
                    world=world,
                    position=array((0,0)),
                    zlayer=1,
                    size=array((16,16)),
                    collisionbox=Box(numpy.ones((16,16))))
    player.direction = array((1, 1)) # looking SE
    player.speed = 1
    time.sleep(1.0)
    world.move_all()
    print(player.position)
