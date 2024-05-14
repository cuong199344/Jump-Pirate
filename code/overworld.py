from settings import *
from sprites import Sprite, AnimatedSprite, Node, Icon, PathSprite
from groups import WorldSprites
from random import randint

class Overworld:
    """
    Đại diện cho màn hình chính (overworld) của game, nơi nhân vật di chuyển giữa các màn chơi
    *Phương thức:
        setup(tmx_map, overworld_frames): Thiết lập overworld
        create_path_sprites(self): Tạo các sprite đường đi
        input(self): Xử lý input từ người chơi để di chuyển nhân vật giữa các nút
        move(self, direction): Di chuyển nhân vật đến nút được chọn
        get_current_node(self):Lấy nút hiện tại mà nhân vật đang đứng trên
        run(self, dt): Cập nhật và hiển thị overworld
    """
    def __init__(self, tmx_map, data, overworld_frames, switch_stage):
        """
        Hàm khởi tạo
            :param tmx_map: Bản đồ Tiled của overworld
            :param data: Dữ liệu trò chơi liên quan đến overworld (chẳng hạn như level hiện tại)
            :param overworld_frames: Từ điển chứa các khung hình hoạt ảnh của overworld
            :param switch_stage: Hàm dùng để chuyển đổi giữa các màn chơi (overworld và màn chơi chính)
        """
        self.display_surface = pygame.display.get_surface()
        self.data = data
        self.switch_stage = switch_stage

        # groups
        self.all_sprites = WorldSprites(data)
        self.node_sprites = pygame.sprite.Group()

        self.setup(tmx_map, overworld_frames)

        self.current_node = [node for node in self.node_sprites if node.level == 0][0]

        # path
        self.path_frames = overworld_frames['path']
        self.create_path_sprites()
    def setup(self, tmx_map, overworld_frames):
        """
        Thiết lập màn hình overworld.
        Phương thức này thiết lập các thành phần cần thiết để hiển thị màn hình overworld dựa vào dữ liệu từ
            TMX map và các khung hình hoạt ảnh được cung cấp
        Duyệt qua các lớp nền ('main' và 'top') trong TMX map để tạo các sprite nền
            bằng lớp `Sprite`
        Duyệt qua tất cả ô trong lớp 'Objects' để tạo các sprite tương ứng:
            Nếu đối tượng là 'palm' (cây cọ), sử dụng lớp `AnimatedSprite` để tạo hoạt ảnh
            Nếu đối tượng là 'grass' (cỏ), sử dụng lớp `Sprite` với lớp nền 'bg details'
            Các đối tượng khác sử dụng lớp `Sprite` với lớp nền 'bg tiles'
        Xử lý các đường đi ('Paths'):
            Tạo một từ điển `self.paths` để lưu trữ thông tin đường đi
            Duyệt qua các đối tượng đường đi trong lớp 'Paths' để lấy tọa độ các điểm mốc và điểm bắt đầu, kết thúc của đường đi
        Xử lý các nút di chuyển ('Nodes'):
            Duyệt qua các đối tượng nút di chuyển trong lớp 'Nodes'
            Nếu là nút di chuyển của màn chơi hiện tại (kiểm tra qua thuộc tính `current_level` trong `data`),
                tạo biểu tượng người chơi (lớp `Icon`) tại vị trí nút
            Đối với các nút di chuyển khác, tạo sprite nút (lớp `Node`) với thông tin level, đường đi khả dụng
            :param tmx_map: Bản đồ Tiled của overworld
            :param overworld_frames: Từ điển chứa các khung hình hoạt ảnh của overworld
        """
        # Khởi và load các vật cần thiết
        # tiles
        for layer in ['main', 'top']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, Z_LAYERS['bg tiles'])

        # water
        for col in range(tmx_map.width):
            for row in range(tmx_map.height):
                AnimatedSprite((col * TILE_SIZE, row * TILE_SIZE), overworld_frames['water'], self.all_sprites,
                               Z_LAYERS['bg'])

        # objects
        for obj in tmx_map.get_layer_by_name('Objects'):
            # Vì palm có hoạt ảnh nên là dùng Animated sprite
            if obj.name == 'palm':
                AnimatedSprite((obj.x, obj.y), overworld_frames['palms'], self.all_sprites, Z_LAYERS['main'],
                               randint(4, 6))
            else:
                key = 'bg details' if obj.name == 'grass' else 'bg tiles'
                z = Z_LAYERS[f'{key}']
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, z)

        # paths
        self.paths = {}
        for obj in tmx_map.get_layer_by_name('Paths'):
            pos = [(int(p.x + TILE_SIZE / 2), int(p.y + TILE_SIZE / 2)) for p in obj.points]
            start = obj.properties['start']
            end = obj.properties['end']
            self.paths[end] = {'pos': pos, 'start': start}

        # nodes & player
        for obj in tmx_map.get_layer_by_name('Nodes'):

            # player
            if obj.name == 'Node' and obj.properties['stage'] == self.data.current_level:
                self.icon = Icon((obj.x + TILE_SIZE / 2, obj.y + TILE_SIZE / 2), self.all_sprites,
                                 overworld_frames['icon'])

            # nodes
            if obj.name == 'Node':
                available_paths = {k: v for k, v in obj.properties.items() if k in ('left', 'right', 'up', 'down')}
                Node(
                    pos=(obj.x, obj.y),
                    surf=overworld_frames['path']['node'],
                    groups=(self.all_sprites, self.node_sprites),
                    level=obj.properties['stage'],
                    data=self.data,
                    paths=available_paths)

    def create_path_sprites(self):
        """
        Tạo sprite đường đi
        Phương thức này tạo các sprite để hiển thị đường đi (path) giữa các nút di chuyển
            (node) trên màn hình overworld
        Khởi tạo từ điển `path_tiles` để lưu trữ các ô tạo thành đường đi cho từng cặp nút.
        Duyệt qua các đường đi (`self.paths`):
            Lấy danh sách các điểm mốc (`pos`) của đường đi hiện tại
            Xác định nút bắt đầu (`start_node`) và nút kết thúc (`end_node`) dựa vào thuộc tính
                `start` trong dữ liệu đường đi
            Thêm nút bắt đầu vào danh sách `path_tiles` cho đường đi hiện tại
            Duyệt qua từng cặp điểm mốc liên tiếp:
                Tính hướng di chuyển (`path_dir`) giữa hai điểm mốc
                Xác định ô bắt đầu (`start_tile`) trên lưới dựa trên vị trí điểm mốc đầu
                Kiểm tra hướng di chuyển để xác định các ô cần thêm vào đường đi:
                    Nếu di chuyển ngang (`path_dir.x` khác 0), lặp qua các ô theo hướng đó
                        cho đến khi gặp điểm mốc kế tiếp
                    Nếu di chuyển dọc (`path_dir.y` khác 0), lặp qua các ô theo hướng đó
                        cho đến khi gặp điểm mốc kế tiếp
                Thêm nút kết thúc vào danh sách `path_tiles` cho đường đi hiện tại.
        Duyệt qua các đường đi đã xử lý (`path_tiles`):
            Duyệt qua từng ô trong danh sách đường đi:
                Kiểm tra nếu ô đang xét không phải là ô đầu tiên hoặc ô cuối cùng
                    (để tránh tính toán hướng chéo ở hai đầu mút)
                Tính toán hướng chéo dựa trên sự khác biệt giữa vị trí ô trước đó,
                    ô đang xét và ô tiếp theo
                Chọn sprite đường đi phù hợp dựa trên hướng chéo tính toán được
                Tạo một `PathSprite` với vị trí, sprite, nhóm sprite và level tương ứng
        """
        # Tạo đường đi
        # get tiles from path
        nodes = {node.level: vector(node.grid_pos) for node in self.node_sprites}
        path_tiles = {}
        for path_id, data in self.paths.items():
            path = data['pos']
            start_node, end_node = nodes[data['start']], nodes[path_id]
            path_tiles[path_id] = [start_node]
            # Giữa start node và end node thì giờ ta sẽ append những node ở giữa
            # Convert them into tiles on a grid
            for index, points in enumerate(path):
                # chỉ lấy khi index < len(path) - 1
                if index < len(path) - 1:
                    start, end = vector(points), vector(path[index + 1])
                    # Kiểm tra hướng đi
                    path_dir = (end - start) / TILE_SIZE
                    start_tile = vector(int(start[0] / TILE_SIZE), int(start[1] / TILE_SIZE))
                    # Chiều ngang
                    if path_dir.x:
                        # Hướng
                        dir_x = 1 if path_dir.x > 0 else -1
                        for x in range(dir_x, int(path_dir.x) + dir_x, dir_x):
                            path_tiles[path_id].append(start_tile + vector(x, 0))
                    # Chiều dọc
                    if path_dir.y:
                        # Hướng
                        dir_y = 1 if path_dir.y > 0 else -1
                        for y in range(dir_y, int(path_dir.y) + dir_y, dir_y):
                            path_tiles[path_id].append(start_tile + vector(0, y))
            path_tiles[path_id].append(end_node)

        # create sprites
        for key, path in path_tiles.items():
            for index, tile in enumerate(path):
                if index > 0 and index < len(path) - 1:
                    prev_tile = path[index - 1] - tile
                    next_tile = path[index + 1] - tile

                    if prev_tile.x == next_tile.x:
                        surf = self.path_frames['vertical']
                    elif prev_tile.y == next_tile.y:
                        surf = self.path_frames['horizontal']
                    else:
                        if prev_tile.x == -1 and next_tile.y == -1 or prev_tile.y == -1 and next_tile.x == -1:
                            surf = self.path_frames['tl']
                        elif prev_tile.x == 1 and next_tile.y == 1 or prev_tile.y == 1 and next_tile.x == 1:
                            surf = self.path_frames['br']
                        elif prev_tile.x == -1 and next_tile.y == 1 or prev_tile.y == 1 and next_tile.x == -1:
                            surf = self.path_frames['bl']
                        elif prev_tile.x == 1 and next_tile.y == -1 or prev_tile.y == -1 and next_tile.x == 1:
                            surf = self.path_frames['tr']
                        else:
                            surf = self.path_frames['horizontal']

                    PathSprite(
                        pos=(tile.x * TILE_SIZE, tile.y * TILE_SIZE),
                        surf=surf,
                        groups=self.all_sprites,
                        level=key)

    def input(self):
        """
        Xử lý đầu vào từ người chơi trên màn hình overworld.
        Phương thức này kiểm tra các phím được bấm và di chuyển biểu tượng người chơi
            (icon) đến nút di chuyển mong muốn, hoặc chuyển sang màn chơi chính (level)
        """
        keys = pygame.key.get_pressed()
        if self.current_node and not self.icon.path:
            if keys[pygame.K_DOWN] and self.current_node.can_move('down'):
                self.move('down')
            if keys[pygame.K_LEFT] and self.current_node.can_move('left'):
                self.move('left')
            if keys[pygame.K_RIGHT] and self.current_node.can_move('right'):
                self.move('right')
            if keys[pygame.K_UP] and self.current_node.can_move('up'):
                self.move('up')
            if keys[pygame.K_RETURN]:
                self.data.current_level = self.current_node.level
                self.switch_stage('level')

    def move(self, direction):
        """
        Di chuyển biểu tượng người chơi đến nút di chuyển được chọn.

        Phương thức này di chuyển biểu tượng người chơi (icon) đến nút di chuyển ở hướng
            được cung cấp (`direction`).
            :param direction: Hướng di chuyển
        """
        path_key = int(self.current_node.paths[direction][0])
        # reverse the path
        path_reverse = True if self.current_node.paths[direction][-1] == 'r' else False
        path = self.paths[path_key]['pos'][:] if not path_reverse else self.paths[path_key]['pos'][::-1]
        self.icon.start_move(path)

    def get_current_node(self):
        """
        Cập nhật nút di chuyển hiện tại
        Phương thức này kiểm tra xem biểu tượng người chơi (icon) đang va chạm với một nút di chuyển nào trong nhóm
            `self.node_sprites` và cập nhật thuộc tính `self.current_node` nếu có
        """
        nodes = pygame.sprite.spritecollide(self.icon, self.node_sprites, False)
        if nodes:
            self.current_node = nodes[0]

    def run(self, dt):
        """
        Cập nhật và hiển thị màn hình overworld
        Phương thức này thực hiện các hành động cần thiết để cập nhật và hiển thị màn hình overworld mỗi khung hình
            :param dt: Thời gian trôi qua
        """
        self.input()
        self.get_current_node()
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.icon.rect.center)
