import pygame.draw

from settings import *
from sprites import Sprite, Cloud
from timer import Timer
from random import randint, choice

class AllSprites(pygame.sprite.Group):
    """
    Nhóm chứa tất cả các sprite trong level
    Lớp này kế thừa từ `pygame.sprite.Group` và quản lý việc cập nhật, hiển thị các sprite có trên màn hình
    * Phương thức
    `camera_constraint()`: Giới hạn camera trong biên level
    `draw_sky()`: Vẽ nền trời
    `draw_large_cloud(self, dt)`: Vẽ mây lớn
    `create_cloud(self)`: Tạo một mây nhỏ ngẫu nhiên
    `draw(self, target_pos, dt)`: Vẽ tất cả sprite trong nhóm
        Cập nhật camera theo vị trí mục tiêu (`target_pos`)
        Kiểm tra loại nền (trời hoặc gạch)
        Nếu là nền trời:
            Cập nhật bộ hẹn giờ tạo mây
            Vẽ nền trời và di chuyển mây lớn
        Sắp xếp các sprite theo thứ tự z (từ xa đến gần) trước khi vẽ
        Vẽ từng sprite lên bề mặt hiển thị với sự dịch chuyển của camera (`offset`)
    """

    def __init__(self, width, height, clouds, horizon_line, bg_tile=None, top_limit=0):
        """
        Hàm khởi tạo
            :param width, height: Số ô ngang và dọc của level trong Tiled map
            :param clouds: Từ điển chứa các ảnh sprite của mây (mây lớn và mây nhỏ)
            :param horizon_line: Vị trí đường chân trời
            :param bg_tile: Ảnh sprite của nền gạch (nếu có)
            :param top_limit: Giới hạn trên cùng của level
        """
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector()
        self.width, self.height = width * TILE_SIZE, height * TILE_SIZE
        self.borders = {
            'left': 0,
            'right': -self.width + WINDOW_WIDTH,
            'bottom': -self.height + WINDOW_HEIGHT,
            'top': top_limit
        }
        # Kiểm tra xem có cần bg hay không
        self.sky = not bg_tile
        self.horizon_line = horizon_line

        # Tạo bg ứng với màu bg trong object Data
        if bg_tile:
            for col in range(width):
                for row in range(-int(top_limit / TILE_SIZE) - 1, height):
                    x, y = col * TILE_SIZE, row * TILE_SIZE
                    Sprite((x, y), bg_tile, self, -1)
        # sky
        else:
            self.large_cloud = clouds['large']
            self.small_clouds = clouds['small']
            self.cloud_direction = -1

            # large cloud
            self.large_cloud_speed = 50
            self.large_cloud_x = 0
            # Tạo mây lớn chiều ngang màn hình
            self.large_cloud_tiles = int(self.width / self.large_cloud.get_width()) + 2
            self.large_cloud_width, self.large_cloud_height = self.large_cloud.get_size()

            # small clouds
            # Dùng timer để tạo mây
            # Tạo nhiều cloud
            self.cloud_timer = Timer(2500, self.create_cloud, True)
            self.cloud_timer.activate()
            for cloud in range(20):
                pos = (randint(0, self.width), randint(self.borders['top'], self.horizon_line))
                surf = choice(self.small_clouds)
                Cloud(pos, surf, self)

    def camera_constraint(self):
        """
        Giới hạn camera trong biên level.
        Phương thức này đảm bảo camera không cho người chơi đi ra ngoài level bằng cách điều chỉnh vị trí camera
            (biến `offset`) dựa trên các giới hạn của level (`self.borders`)
        """
        # offset luôn chạy hướng ngc lại so với người chơi, nếu đi xa sang bên phải thì offset ngày càng nhỏ
        # offset nên dc là chính nó khi nó < 0 => người chơi k gần cạnh trái, ngc lại thì đặt là 0 để người chơi không vượt qua được
        # Giới hạn phải thì sẽ phải công thêm chiều dài map

        self.offset.x = self.offset.x if self.offset.x < self.borders['left'] else self.borders['left']
        self.offset.x = self.offset.x if self.offset.x > self.borders['right'] else self.borders['right']
        self.offset.y = self.offset.y if self.offset.y > self.borders['bottom'] else self.borders['bottom']
        self.offset.y = self.offset.y if self.offset.y < self.borders['top'] else self.borders['top']

    def draw_sky(self):
        """
        Vẽ nền trời cho level.
        Phương thức này vẽ nền trời cho level nếu level được thiết lập là có nền trời (`self.sky` là `True`)
        """
        # Vẽ sky
        self.display_surface.fill('#ddc6a1')
        # Đường chân trời chia trời và đất
        # horizon line
        horizon_pos = self.horizon_line + self.offset.y
        sea_rect = pygame.FRect(0, horizon_pos, WINDOW_WIDTH, WINDOW_HEIGHT - horizon_pos)
        pygame.draw.rect(self.display_surface, '#92a9ce', sea_rect)

        # horizon line
        pygame.draw.line(self.display_surface, '#f5f1de', (0, horizon_pos), (WINDOW_WIDTH, horizon_pos), 4)

    def draw_large_cloud(self, dt):
        """
        Vẽ mây lớn trên nền trời
        Phương thức này vẽ mây lớn di chuyển ngang trên nền trời của level
            :param dt: Thời gian trôi qua
        """
        self.large_cloud_x += self.cloud_direction * self.large_cloud_speed * dt
        # Kiểm tra nếu như hết mây sẽ lặp lại
        if self.large_cloud_x <= -self.large_cloud_width:
            self.large_cloud_x = 0
        for cloud in range(self.large_cloud_tiles):
            # Mong muốn large_cloud nằm trên đường chân trời
            left = self.large_cloud_x + self.large_cloud_width * cloud + self.offset.x
            top = self.horizon_line - self.large_cloud_height + self.offset.y
            self.display_surface.blit(self.large_cloud, (left, top))

    def create_cloud(self):
        """
        Tạo một sprite mây nhỏ ngẫu nhiên (phương thức riêng tư)
        Phương thức nội bộ này được sử dụng để tạo và thêm một sprite mây nhỏ mới vào nhóm `AllSprites`
        Vị trí và ảnh hiển thị của mây nhỏ được chọn ngẫu nhiên
        """
        pos = (randint(self.width + 500, self.width + 600), randint(self.borders['top'], self.horizon_line))
        surf = choice(self.small_clouds)
        Cloud(pos, surf, self)

    def draw(self, target_pos, dt):
        """
        Vẽ tất cả sprite trong nhóm lên bề mặt hiển thị
        Phương thức này chịu trách nhiệm vẽ tất cả các sprite có trong nhóm `AllSprites` lên bề mặt hiển thị chính
            (`self.display_surface`).
        Vị trí hiển thị của các sprite được điều chỉnh dựa trên camera (tương đối với vị trí mục tiêu `target_pos`)
            :param target_pos: Vị trí mục tiêu (tuple of x, y). Vị trí này thường là vị trí của người chơi,
                dựa vào đó camera sẽ điều chỉnh để giữ người chơi ở trung tâm màn hình
            :param dt: Thời gian trôi qua
        """
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)
        self.camera_constraint()

        if self.sky:
            self.cloud_timer.update()
            self.draw_sky()
            self.draw_large_cloud(dt)

        # Sắp xếp theo z, từ đó giúp cho điều kiển phần tử nào được vẽ trước, phần tử nào được vẽ sau
        for sprite in sorted(self, key=lambda sprite: sprite.z):
            offset_pos = sprite.rect.topleft + self.offset
            self.display_surface.blit(sprite.image, offset_pos)


class WorldSprites(pygame.sprite.Group):
    """
    Nhóm chứa tất cả các sprite trong thế giới game (overworld)
    Lớp này kế thừa từ `pygame.sprite.Group` và quản lý việc vẽ các sprite lên màn hình
    Các sprite được phân loại theo thứ tự hiển thị (`z`) và được sắp xếp để tạo hiệu ứng phối cản
    * Phương thức
    `draw(target_pos)`: Vẽ tất cả sprite trong nhóm lên bề mặt hiển thị
    """
    def __init__(self, data):
        """
        Hàm khởi tạo
            :param data: Dữ liệu trò chơi được dùng để thiết lập các sprite ban đầu
        """
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.data = data
        self.offset = vector()

    def draw(self, target_pos):
        """
        Vẽ tất cả sprite trong nhóm lên bề mặt hiển thị, phân loại theo lớp nền (background) và lớp chính (main)
        Phương thức này chịu trách nhiệm vẽ toàn bộ các sprite có trong nhóm `WorldSprites` lên bề mặt hiển thị chính
            (`self.display_surface`), đồng thời gắn camera và vị trú người chơi di chuyển
        Các sprite được phân loại và sắp xếp theo thứ tự hiển thị (`z`) để tạo hiệu ứng lớp (layering effect)
            :param target_pos: Vị trí mục tiêu (tuple of x, y). Vị trí này thường là vị trí của người chơi,
                dựa vào đó camera sẽ điều chỉnh để giữ người chơi ở trung tâm màn hình
        """
        # Camera
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)

        # chia thành 2 phần background và main

        # background
        # Mỗi khi unlock được một stage mới thì node tượng trương so stage đó sẽ hiện lên
        for sprite in sorted(self, key=lambda sprite: sprite.z):
            if sprite.z < Z_LAYERS['main']:
                if sprite.z == Z_LAYERS['path']:
                    if sprite.level <= self.data.unlocked_level:
                        self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
                else:
                    self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
        # main
        # Sắp xếp theo y để tạo được hiệu ứng trước sau
        for sprite in sorted(self, key=lambda sprite: sprite.rect.centery):
            if sprite.z == Z_LAYERS['main']:
                if hasattr(sprite, 'icon'):
                    self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset + vector(0, -28))
                else:
                    self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)

