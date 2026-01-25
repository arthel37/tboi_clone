import random
from collections import deque
from room import Room

class Level:
    def __init__(self, level_num):
        print('Tworzenie obiektu poziomu...')
        self.level_num = level_num
        self.target_room_count = 5 + (level_num * 2)
        self.map = {}
        self.generate_level()

    def generate_level(self):
        print('\tTworzenie poziomu...')
        attempt = 0
        while True:
            attempt += 1
            self.map = self._generate_map()
            self._connect_rooms()
            dead_ends = self._get_dead_ends()
            
            print(f'Próba {attempt}: znaleziono {len(dead_ends)} martwych zaułków')
            
            if len(dead_ends) >= 3:
                try: 
                    self._assign_special_rooms(dead_ends)
                    break
                except Exception as e:
                    print(f'Błąd podczas przypisywania pokoi: {e}')
                    continue
        print('\tZakończono tworzenie poziomu.')


    def _generate_map(self):
        print('\t\tTworzenie mapy...')
        temp_map = {}
        temp_map[(0, 0)] = Room(0, 0, "start")

        occupied_coords = [(0, 0)]

        while len(temp_map) < self.target_room_count:
            current_x, current_y = random.choice(occupied_coords)
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            direction = random.choice(directions)
            
            new_x = current_x + direction[0]
            new_y = current_y + direction[1]
            
            if (new_x, new_y) not in temp_map:
                neighbours = 0
                for dx, dy in directions:
                    if (new_x + dx, new_y + dy) in temp_map:
                        neighbours += 1
                if neighbours <= 2:
                    new_room = Room(new_x, new_y, 'normal')
                    temp_map[(new_x, new_y)] = new_room
                    occupied_coords.append((new_x, new_y))
        
        print('\t\tZakończono tworzenie mapy.')
        return temp_map
        
    def _connect_rooms(self):
        print('\t\tTworzenie drzwi...')
        for coords, room in self.map.items():
            x, y = coords
            if (x, y - 1) in self.map: 
                room.doors['top'] = True
            if (x, y + 1) in self.map: 
                room.doors['bottom'] = True
            if (x - 1, y) in self.map: 
                room.doors['left'] = True
            if (x + 1, y) in self.map: 
                room.doors['right'] = True

    def _get_dead_ends(self):
        print('\t\tSzukanie martwych zaułków...')
        dead_ends = []
        for room in self.map.values():
            if room.room_type == 'start':
                continue
            door_count = sum(room.doors.values())
            if door_count == 1:
                dead_ends.append(room)
        return dead_ends

    def _assign_special_rooms(self, dead_ends):
        print('\t\tPrzypisywanie pokojów specjalnych...')
        start_room = self.map[(0, 0)]
        self._calculate_distances(start_room)

        dead_ends.sort(key=lambda x: x.distance, reverse=True)

        boss_room = dead_ends.pop(0)
        boss_room.room_type = 'boss'

        random.shuffle(dead_ends)
        
        item_room = dead_ends.pop(0)
        item_room.room_type = 'item'

        shop_room = dead_ends.pop(0)
        shop_room.room_type = 'shop'

    def _calculate_distances(self, start_room):
        print('\t\t\tSzukanie najdalszego martwego zaułka od startu...')
        for room in self.map.values():
            room.distance = -1
        
        start_room.distance = 0
        queue = deque([start_room])

        while queue:
            curr_room = queue.popleft()
            directions = {'top': (0, -1), 'bottom': (0, 1), 'left': (-1, 0), 'right': (1, 0)}

            for direction, (dx, dy) in directions.items():
                if curr_room.doors[direction]:
                    neighbour_coords = (curr_room.x + dx, curr_room.y + dy)
                    if neighbour_coords in self.map:
                        neighbour = self.map[neighbour_coords]
                        if neighbour.distance == -1:
                            neighbour.distance = curr_room.distance + 1
                            queue.append(neighbour)
