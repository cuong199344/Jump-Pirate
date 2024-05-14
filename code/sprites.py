from settings import *
from math import sin, cos, radians
from random import randint, choice

class Sprite(pygame.sprite.Sprite):
    """
    Sprite là một yếu tố trực quan có thể được vẽ trên màn hình và có khả năng tương tác với các sprite khác.
    Lớp cơ sở này cung cấp chức năng cốt lõi để quản lý vị trí, hình ảnh và phát hiện va chạm của sprite
    * Phương thức
    Kế thừa các phương thức từ pygame.sprite.Sprite
    """

    def __init__(self, pos, surf=pygame.Surface((TILE_SIZE, TILE_SIZE)), groups=None, z=Z_LAYERS['main']):
        """
        Hàm khởi tạo
            :param pos: Vị trí ban đầu (x, y) của sprite trên màn hình
            :param surf: Bề mặt hình ảnh để sử dụng cho sprite. Mặc định là một bề mặt trống với kích thước TILE_SIZE
            :param groups: Danh sách (pygame.sprite.Group) các nhóm mà sprite này thuộc về. Mặc định là None
            :param z: Lớp Z của sprite để sắp xếp theo độ sâu. Mặc định là lớp Z 'main' được định nghĩa trong biến riêng biệt Z_LAYERS
        """
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.old_rect = self.rect.copy()
        self.z = z

class AnimatedSprite(Sprite):
    """
    AnimatedSprite cung cấp chức năng bổ sung để tự động thay đổi hình ảnh của sprite theo thời gian, tạo hiệu ứng hoạt hình
    Lớp này là một lớp sprite mở rộng từ lớp Sprite cơ bản, được sử dụng để tạo các sprite hoạt hình.
    * Phương thức
    animate(dt): Cập nhật chỉ số khung hình và hình ảnh của sprite dựa trên thời gian trôi qua (dt).
    update(dt): Gọi phương thức animate để cập nhật sprite.
    """

    # Sprite làm animatrion cho các object
    def __init__(self, pos, frames, groups, z=Z_LAYERS['main'], animation_speed=ANIMATION_SPEED):
        """
        Hàm khởi tạo
            :param pos: Vị trí ban đầu (x, y) của sprite trên màn hình
            :param frames: Danh sách các bề mặt hình ảnh đại diện cho các khung hình hoạt hình
            :param groups: Danh sách (pygame.sprite.Group) các nhóm mà sprite này thuộc về. Mặc định là None
            :param z: Lớp Z của sprite để sắp xếp theo độ sâu trong khi vẽ. Mặc định là lớp Z 'main' được định nghĩa
                trong biến riêng biệt Z_LAYERS
            :param animation_speed: Tốc độ hoạt hình, điều chỉnh tốc độ thay đổi khung hình (giá trị cao hơn = tốc độ
                hoạt hình nhanh hơn). Mặc định là ANIMATION_SPEED
        """
        # self.frames: list of surface, chọn 1 surface dựa vào frame index
        self.frames, self.frame_index = frames, 0
        super().__init__(pos, self.frames[self.frame_index], groups, z)
        self.animation_speed = animation_speed

    def animate(self, dt):
        """
        Hàm hoạt họa
        Cập nhật chỉ số khung hình và hình ảnh của sprite dựa trên thời gian trôi qua.
        Phương thức này điều chỉnh hoạt ảnh của sprite bằng cách cập nhật chỉ số khung hình (`frame_index`) và hình ảnh
            (`image`) dựa trên tốc độ hoạt hình (`animation_speed`) và thời gian trôi qua (`dt`).
        Chỉ số khung hình được tăng lên theo thời gian, nhưng được giới hạn trong phạm vi số lượng khung hình
            (`len(self.frames)`) bằng cách chia lấy dư.
        Hình ảnh hiện tại của sprite được cập nhật bằng cách chọn khung hình tương ứng với chỉ số khung hình hiện tại từ
            danh sách khung hình (`self.frames`).
            :param dt: Thời gian trôi qua
        """
        # Tăng frames index dựa theo animation_speed và dt ( mong muốn animation chạy với tốc độ giống nhau)
        self.frame_index += self.animation_speed * dt
        # Cập nhật image bằng cách chọn 1 frame mới thông qua frames index ( int vì sau phép tính trên sẽ thành dạng float
        # ép kiểu int lại, chia lấy dư cho số lượng frames vì frame_index sẽ tăng mãi mãi và ta lặp lại hoạt ảnh bằng cách chia lấy du
        # khi đó frames được lấy ra chỉ nằm trong khoảng từ 0 đến index của frames cuối
        self.image = self.frames[int(self.frame_index % len(self.frames))]

    def update(self, dt):
        """
        Hàm cập nhật
        Cập nhật sprite
        Phương thức này gọi phương thức `animate` để cập nhật chỉ số khung hình và hình ảnh của sprite.
        Ngoài ra, nó có thể thực hiện các hành động cập nhật khác cho sprite, tùy thuộc vào logic của trò chơi.
            :param dt: Thời gian trôi qua
        """
        self.animate(dt)

class Item(AnimatedSprite):
    """
    Lớp Item mở rộng chức năng hoạt hình của AnimatedSprite để tạo ra các vật phẩm hoạt hình
    Vật phẩm có thể có các loại khác nhau, mỗi loại mang lại hiệu ứng khác nhau cho người chơi
    * Phương thức
    activate(self): Kích hoạt hiệu ứng của vật phẩm
    """

    def __init__(self, item_type, pos, frames, groups, data):
        """
        Hàm khởi tạo
            :param item_type: Kiểu của vật phẩm
            :param pos: Vị trí ban đầu (x, y) của vật phẩm trên màn hình
            :param frames: Danh sách các bề mặt hình ảnh đại diện cho các khung hình hoạt hình của vật phẩm
            :param groups: Danh sách (pygame.sprite.Group) các nhóm mà sprite này thuộc về. Mặc định là None
            :param data: Tham chiếu đến một đối tượng lưu trữ dữ liệu trò chơi
        """
        super().__init__(pos, frames, groups)
        self.rect.center = pos
        self.item_type = item_type
        self.data = data

    def activate(self):
        """
        Hàm kích hoạt
        Kích hoạt hiệu ứng của vật phẩm
        Phương thức này kiểm tra loại của vật phẩm (`self.item_type`) và cập nhật dữ liệu trò chơi (`self.data`) theo hiệu ứng của vật phẩm đó.
        Các loại vật phẩm được hỗ trợ:
            'gold': Tăng 5 tiền vàng.
            'silver': Tăng 1 tiền vàng.
            'diamond': Tăng 20 tiền vàng.
            'skull': Giảm 1 máu.
            'potion': Tăng 1 máu.
        """
        if self.item_type == 'gold':
            self.data.coins += 5
        if self.item_type == 'silver':
            self.data.coins += 1
        if self.item_type == 'diamond':
            self.data.coins += 50
        if self.item_type == 'skull':
            self.data.health -= 1
        if self.item_type == 'potion':
            self.data.health += 1

class ParticleEffectSprite(AnimatedSprite):
    """
    ParticleEffectSprite được sử dụng để tạo các hiệu ứng hình ảnh động ngắn, giống như các hạt bay hoặc vụ nổ
    Lớp này là một lớp kế thừa từ AnimatedSprite, đại diện cho các hiệu ứng hạt trong trò chơi
    Hiệu ứng chỉ chạy một lần và tự hủy sau khi hoàn thành animation
    * Phương thức
    animate(self, dt): Cập nhật chỉ số khung hình và hình ảnh của hiệu ứng hạt, nhưng chỉ chạy một lần đến hết animation
     rồi tự hủy
    """

    def __init__(self, pos, frames, groups):
        """
        Hàm khởi tạo
            :param pos: Vị trí ban đầu (x, y) của hiệu ứng hạt trên màn hình
            :param frames: Danh sách các bề mặt hình ảnh đại diện cho các khung hình hoạt hình của hiệu ứng hạt
            :param groups: Danh sách (pygame.sprite.Group) các nhóm mà sprite này thuộc về. Mặc định là None
        """
        super().__init__(pos, frames, groups)
        self.rect.center = pos
        self.z = Z_LAYERS['fg']

    def animate(self, dt):
        """
        Hàm hoạt họa
        Phương thức này tạo hiệu ứng hạt ngắn và tự hủy
        Phương thức này điều chỉnh hoạt ảnh của hiệu ứng hạt bằng cách cập nhật chỉ số khung hình (`frame_index`)
            và hình ảnh (`image`) dựa trên tốc độ hoạt hình (`animation_speed`) và thời gian trôi qua (`dt`)
        Khác với `AnimatedSprite` thông thường, phương thức này chỉ cho phép hiệu ứng chạy một lần
        Chỉ số khung hình được tăng lên theo thời gian, nhưng được kiểm tra để đảm bảo không vượt quá số lượng
            khung hình (`len(self.frames)`).
        Nếu chỉ số khung hình nhỏ hơn số lượng khung hình, hình ảnh hiện tại của hiệu ứng được cập nhật bằng cách chọn
            khung hình tương ứng.
        Ngược lại, nếu chỉ số khung hình vượt quá số lượng khung hình, phương thức sẽ gọi `self.kill()`, xóa hiệu ứng khỏi
            các nhóm sprite (`groups`) mà nó thuộc về.
            :param dt: Thời gian trôi qua
            :return:
        """
        # chỉ chạy sprite một lần rồi mất
        self.frame_index += self.animation_speed * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

class MovingSprite(AnimatedSprite):
    """
    MovingSprite mở rộng chức năng hoạt hình của AnimatedSprite để tạo ra các sprite di chuyển theo đường thẳng có hướng
    Lớp này là một lớp kế thừa từ AnimatedSprite, đại diện cho các sprite di chuyển trong trò chơi.
    * Phương thức
    check_border(self): Kiểm tra xem sprite đã di chuyển đến cuối đường ranh giới (end_pos) chưa, sau đó đảo ngược hướng
        di chuyển nếu cần. Cập nhật thuộc tính reverse để kiểm tra lật hình nếu flip là True.
    update(self, dt): Cập nhật trạng thái của sprite mỗi khung hình, bao gồm:
        Sao chép vị trí cũ (old_rect)
        Cập nhật vị trí mới dựa trên hướng di chuyển (direction), tốc độ (speed), và thời gian trôi qua (dt)
        Kiểm tra va chạm biên (check_border)
        Cập nhật hoạt hình (animate)
        Lật hình ảnh theo hướng di chuyển nếu flip là True (sử dụng thông tin từ reverse)
    """

    def __init__(self, frames, groups, start_pos, end_pos, move_dir, speed, flip=False):
        """
        Hàm khởi tạo
            :param frames: Danh sách các bề mặt hình ảnh đại diện cho các khung hình hoạt hình của sprite
            :param groups: Danh sách (pygame.sprite.Group) các nhóm mà sprite này thuộc về. Mặc định là None
            :param start_pos: Vị trí ban đầu (x, y) của sprite trên màn hình
            :param end_pos: Vị trí kết thúc (x, y) của sprite trên màn hình (để xác định hướng di chuyển)
            :param move_dir: Hướng di chuyển ("x" - ngang, "y" - dọc)
            :param speed: Tốc độ di chuyển của sprite
            :param flip: Xác định có lật hình ảnh sprite theo hướng di chuyển không. Mặc định là False
        """
        super().__init__(start_pos, frames, groups)
        if move_dir == 'x':
            self.rect.midleft = start_pos
        else:
            self.rect.midtop = start_pos
        self.start_pos = start_pos
        self.end_pos = end_pos

        # Movement
        self.moving = True
        self.speed = speed
        self.direction = vector(1, 0) if move_dir == 'x' else vector(0, 1)
        self.move_dir = move_dir

        self.flip = flip
        self.reverse = {'x': False, 'y': False}

    def check_border(self):
        """
        Hàm kiểm tra viền
        Phương thức này kiểm tra xem sprite đã di chuyển đến giới hạn được xác định bởi
            `end_pos` (`vị trí kết thúc`) chưa, dựa trên hướng di chuyển (`move_dir`).
        Nếu sprite đã chạm đến giới hạn, hướng di chuyển (`direction`) sẽ được đảo ngược để di chuyển theo hướng đối diện.
        Vị trí của sprite (`rect`) cũng được điều chỉnh để đảm bảo sprite không vượt qua giới hạn.
        Nếu `flip` là True (lật hình ảnh theo hướng di chuyển), thuộc tính `reverse`
            sẽ được cập nhật để xác định hướng lật hình ảnh dựa trên hướng di chuyển hiện tại.
        """
        if self.move_dir == 'x':
            # Kiểm tra xem gặp điểm đầu hoặc cuối để đổi chiều
            # Kiểm tra xem vật di chuyển ngang gặp giới hạn phải chưa
            if self.rect.right >= self.end_pos[0] and self.direction.x == 1:
                self.direction.x = -1
                self.rect.right = self.end_pos[0]
            # Kiểm tra xem vật di chuyển ngang gặp giới hạn trái chưa
            if self.rect.left <= self.start_pos[0] and self.direction.x == -1:
                self.direction.x = 1
                self.rect.left = self.start_pos[0]
            # Kiểm tra xem object có quay đầu không
            self.reverse['x'] = True if self.direction.x < 0 else False
        else:
            # Kiểm tra xem vật di chuyển dọc gặp giới hạn dưới chưa
            if self.rect.bottom >= self.end_pos[1] and self.direction.y == 1:
                self.direction.y = -1
                self.rect.bottom = self.end_pos[1]
            # Kiểm tra xem vật di chuyển dọc gặp giới hạn trên chưa
            if self.rect.top <= self.start_pos[1] and self.direction.y == -1:
                self.direction.y = 1
                self.rect.top = self.start_pos[1]
            # Kiểm tra xem object có quay đầu không
            self.reverse['y'] = True if self.direction.y > 0 else False

    def update(self, dt):
        """
        Hàm cập nhật
        Cập nhật trạng thái của sprite mỗi khung hình, bao gồm:
            Sao chép vị trí cũ (`old_rect`).
            Cập nhật vị trí mới dựa trên hướng di chuyển (`direction`), tốc độ (`speed`), và thời gian trôi qua (`dt`).
            Kiểm tra va chạm biên (`check_border`).
            Cập nhật hoạt hình (`animate`).
            Lật hình ảnh theo hướng di chuyển nếu `flip` là True (sử dụng thông tin từ `reverse`)
            :param dt: Thời gian trôi qua
        """
        self.old_rect = self.rect.copy()
        self.rect.topleft += self.direction * self.speed * dt
        self.check_border()

        self.animate(dt)
        if self.flip:
            self.image = pygame.transform.flip(self.image, self.reverse['x'], self.reverse['y'])

class Spike(Sprite):
    """
    Đại diện cho một gai nhọn di chuyển theo đường tròn cung
    Lớp này kế thừa từ `Sprite` để cung cấp các tính năng cơ bản của đối tượng hiển thị.
    Một Spike được định nghĩa bởi tâm (`center`), bán kính (`radius`), tốc độ (`speed`), góc bắt đầu (`start_angle`),
        góc kết thúc (`end_angle`) của cung tròn, và có thể tùy chọn đặt độ sâu hiển thị (`z`)
    * Phương thức
    update(self, dt): Cập nhật trạng thái của sprite mỗi khung hình
    """
    def __init__(self, pos, surf, groups, radius, speed, start_angle, end_angle, z=Z_LAYERS['main']):
        """
        Hàm khởi tạo
            :param pos: Tọa độ tâm của gai nhọn (x, y)
            :param surf: Surface của gai nhọn được hiển thị
            :param groups: Một hoặc nhiều nhóm sprite để thêm gai nhọn vào
            :param radius: Bán kính của cung tròn
            :param speed: Tốc độ quay của gai nhọn (góc trên giây)
            :param start_angle: Góc bắt đầu của cung tròn (độ)
            :param end_angle: Góc kết thúc của cung tròn (độ). Nếu bằng -1, gai nhọn sẽ quay toàn bộ vòng tròn
            :param z: Độ sâu hiển thị của gai nhọn. Mặc định là `Z_LAYERS['main']`
        """
        self.center = pos
        self.radius = radius
        self.speed = speed
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.angle = self.start_angle
        self.direction = 1
        self.full_circle = True if self.end_angle == -1 else False

        # trigonometry
        y = self.center[1] + sin(radians(self.angle)) * self.radius
        x = self.center[0] + cos(radians(self.angle)) * self.radius

        super().__init__((x, y), surf, groups, z)

    def update(self, dt):
        """
        Hàm cập nhật
        Cập nhật vị trí và hướng của gai nhọn
        Phương thức này tính toán góc mới của gai nhọn dựa trên tốc độ quay (`speed`), hướng quay (`direction`),
            và khoảng thời gian (`dt`)
            :param dt: Thời gian trôi qua
        """
        # cập nhật góc
        self.angle += self.direction * self.speed * dt

        if not self.full_circle:
            if self.angle >= self.end_angle:
                self.direction = -1
            if self.angle < self.start_angle:
                self.direction = 1

        y = self.center[1] + sin(radians(self.angle)) * self.radius
        x = self.center[0] + cos(radians(self.angle)) * self.radius
        self.rect.center = (x, y)

class Cloud(Sprite):
    """
    Đại diện cho một đám mây di chuyển ngang qua màn hình.
    Lớp này kế thừa từ `Sprite` để cung cấp các tính năng cơ bản của đối tượng hiển thị.
    Một đám mây được tạo với vị trí (`pos`), Surface của đám mây (`surf`), các nhóm sprite để thêm vào (`groups`),
        và tùy chọn đặt độ sâu hiển thị (`z`).
    * Phương thức
    update(self, dt): Cập nhật trạng thái của sprite mỗi khung hình
    """
    def __init__(self, pos, surf, groups, z=Z_LAYERS['clouds']):
        """
        Hàm khởi tạo
        Phương thức này tạo một đám mây mới với các thông số được cung cấp
            :param pos: Vị trí ban đầu của đám mây (x, y)
            :param surf: Surface của đám mây được hiển thị
            :param groups: Một hoặc nhiều nhóm sprite để thêm đám mây vào
            :param z: Độ sâu hiển thị của đám mây. Mặc định là `Z_LAYERS['clouds']`
        """
        super().__init__(pos, surf, groups, z)
        self.speed = randint(50, 120)
        self.direction = -1
        self.rect.midbottom = pos

    def update(self, dt):
        """
        Cập nhật vị trí của đám mây trên màn hình.
        Phương thức này tính toán dịch chuyển ngang của đám mây dựa trên tốc độ (`speed`), hướng di chuyển (`direction`)
            , và khoảng thời gian (`dt`). Vị trí mới được cập nhật thông qua tọa độ X của hình chữ nhật
            bao quanh đám mây (`self.rect.x`)
            :param dt: Thời gian trôi qua
        """
        self.rect.x += self.direction * self.speed * dt

        if self.rect.right <= 0:
            self.kill()

class Node(pygame.sprite.Sprite):
    """
    Đại diện cho một nút (node) trong trò chơi, biểu thị vị trí của các màn chơi.
    Lớp này kế thừa từ `pygame.sprite.Sprite` để cung cấp các tính năng cơ bản của đối tượng hiển thị
    * Phương thức
    can_move(self, direction): Kiểm tra xem người chơi có thể di chuyển đến nút theo hướng đã cho hay không
    """
    # Node: vị trí của các màn chơi
    def __init__(self, pos, surf, groups, level, data, paths):
        """
        Hàm khởi tạo
            :param pos: Vị trí ban đầu của nút (x, y)
            :param surf: Surface của nút được hiển thị
            :param groups: Một hoặc nhiều nhóm sprite để thêm nút vào
            :param level: Mức độ của màn chơi tương ứng với nút
            :param data: Dữ liệu trò chơi liên quan đến nút
            :param paths: Từ điển chứa các đường dẫn di chuyển từ nút này đến các nút khác (khóa là hướng di chuyển,
                giá trị là thông tin đường dẫn)
        """
        super().__init__(groups)
        self.image = surf
        # lấy điểm ở giữa vì hình ảnh node sẽ được biểu thị thành hình tròn
        self.rect = self.image.get_frect(center=(pos[0] + TILE_SIZE / 2, pos[1] + TILE_SIZE / 2))
        self.z = Z_LAYERS['path']
        self.level = level
        self.data = data
        self.paths = paths

        self.grid_pos = (int(pos[0] / TILE_SIZE), int(pos[1] / TILE_SIZE))

    def can_move(self, direction):
        """
        Kiểm tra xem người chơi có thể di chuyển đến nút theo hướng đã cho hay không.
        Phương thức này kiểm tra hai điều kiện:
            1. Hướng di chuyển có hợp lệ hay không (có tồn tại đường dẫn trong `self.paths`).
            2. Mức độ của màn chơi đích có được mở khóa hay không (dựa trên `self.data.unlocked_level`).
        Trả về `True` nếu người chơi có thể di chuyển, `False` nếu không
            :param direction: Hướng di chuyển
        """
        # Giới hạn khu vực mà người chơi có thể đi và chỉ được đi vào khi người chơi đã mở được khu vực đó
        if direction in list(self.paths.keys()) and int(self.paths[direction][0][0]) <= self.data.unlocked_level:
            return True

class Icon(pygame.sprite.Sprite):
    """
    Đại diện cho một biểu tượng di chuyển trên màn hình trò chơi
    Lớp này kế thừa từ `pygame.sprite.Sprite` để cung cấp các tính năng cơ bản của đối tượng hiển thị
    Một biểu tượng có thể di chuyển theo đường dẫn được cung cấp và có trạng thái hoạt ảnh khác nhau
    * Phương thức

    """
    def __init__(self, pos, groups, frames):
        """
        Hàm khởi tạo
            :param pos: Vị trí ban đầu của biểu tượng (x, y)
            :param groups: Một hoặc nhiều nhóm sprite để thêm biểu tượng vào
            :param frames: Từ điển lưu trữ các khung hình hoạt ảnh theo trạng thái
        """
        super().__init__(groups)
        self.icon = True
        self.path = None
        self.direction = vector()
        self.speed = 500

        # image
        self.frames, self.frame_index = frames, 0
        self.state = 'idle'
        self.image = self.frames[self.state][self.frame_index]
        self.z = Z_LAYERS['main']

        # rect
        self.rect = self.image.get_frect(center=pos)

    def start_move(self, path):
        """
        Hàm bắt đầu di chuyển
        Bắt đầu di chuyển biểu tượng theo đường dẫn được cung cấp
        Phương thức này thiết lập đường dẫn di chuyển cho biểu tượng:
            Vị trí bắt đầu được đặt tại điểm đầu tiên của đường dẫn
            Danh sách các điểm đến được lưu trữ trong `self.path`
            Phương thức `find_path` được gọi để tính toán hướng di chuyển ban đầu
            :param path: Danh sách các điểm đến theo thứ tự di chuyển (tọa độ các điểm)
        """
        self.rect.center = path[0]
        self.path = path[1:]
        self.find_path()

    def find_path(self):
        """
        Tính toán hướng di chuyển dựa trên điểm đến tiếp theo trong đường dẫn.
        Phương thức này kiểm tra xem còn điểm đến trong đường dẫn (`self.path`) hay không.
        Nếu có, phương thức sẽ tính toán hướng di chuyển theo trục X hoặc Y để đến điểm đó.
        Nếu không còn điểm đến, hướng di chuyển được đặt thành vectơ rỗng
        """
        if self.path:
            # vertical
            if self.rect.centerx == self.path[0][0]:
                self.direction = vector(0, 1 if self.path[0][1] > self.rect.centery else - 1)
            # horizontal
            else:
                self.direction = vector(1 if self.path[0][0] > self.rect.centerx else - 1, 0)
        else:
            self.direction = vector()

    def point_collision(self):
        """
        Kiểm tra va chạm giữa đối tượng và điểm đầu tiên trên đường đi.

        Hàm này kiểm tra xem tâm của hình chữ nhật (được biểu thị bởi thuộc tính `rect` của đối tượng) có vượt qua
            tọa độ x và y của điểm đầu tiên trên đường đi (được lưu trữ trong phần tử đầu tiên của danh sách `path`)
            hay không. Kiểm tra dựa vào hướng di chuyển của đối tượng (được biểu thị bởi thuộc tính `direction`).
        Nếu có va chạm theo trục Y:
            Nếu đối tượng đang đi lên (direction.y == 1) và tâm y của hình chữ nhật lớn hơn hoặc bằng tọa độ y của
                điểm đầu tiên, thì sẽ điều chỉnh tâm y của hình chữ nhật bằng tọa độ y của điểm đầu tiên.
            Xóa bỏ điểm đầu tiên khỏi danh sách `path`
            Gọi hàm `find_path` để tìm đường đi mới
        Nếu có va chạm theo trục X:
            Logic tương tự như trên trục Y, nhưng kiểm tra tọa độ x và hướng di chuyển theo trục x.

        """
        if self.direction.y == 1 and self.rect.centery >= self.path[0][1] or \
                self.direction.y == -1 and self.rect.centery <= self.path[0][1]:
            self.rect.centery = self.path[0][1]
            del self.path[0]
            self.find_path()

        if self.direction.x == 1 and self.rect.centerx >= self.path[0][0] or \
                self.direction.x == -1 and self.rect.centerx <= self.path[0][0]:
            self.rect.centerx = self.path[0][0]
            del self.path[0]
            self.find_path()

    def animate(self, dt):
        """
        Kiểm tra va chạm với điểm đến và cập nhật vị trí, đường dẫn di chuyển.
        Phương thức này kiểm tra xem biểu tượng đã đến điểm đến theo tọa độ X hoặc Y hay chưa,
            dựa trên hướng di chuyển (`self.direction`) và vị trí hiện tại (`self.rect.center`).
        Nếu biểu tượng đã đến điểm đến:
            Cập nhật vị trí biểu tượng theo tọa độ Y của điểm đến.
            Xóa điểm đến khỏi danh sách đường dẫn (`self.path`).
            Gọi phương thức `find_path` để tính toán hướng di chuyển mới dựa trên điểm đến tiếp theo (nếu có).
            :param dt: Thời gian trôi qua
        """
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]

    def get_state(self):
        """
        Cập nhật trạng thái hoạt ảnh của biểu tượng dựa trên hướng di chuyển

        Phương thức này kiểm tra hướng di chuyển (`self.direction`) của biểu tượng và thiết lập trạng thái hoạt ảnh
            (`self.state`) phù hợp:
                'idle'`: Biểu tượng không di chuyển (hướng di chuyển bằng vectơ rỗng)
                'right'`: Biểu tượng di chuyển sang phải (hướng di chuyển có giá trị dương trên trục X)
                'left'`: Biểu tượng di chuyển sang trái (hướng di chuyển có giá trị âm trên trục X)
                'down'`: Biểu tượng di chuyển xuống dưới (hướng di chuyển có giá trị dương trên trục Y)
                'up'`: Biểu tượng di chuyển lên trên (hướng di chuyển có giá trị âm trên trục Y)
        """
        self.state = 'idle'
        if self.direction == vector(1, 0):
            self.state = 'right'
        if self.direction == vector(-1, 0):
            self.state = 'left'
        if self.direction == vector(0, 1):
            self.state = 'down'
        if self.direction == vector(0, -1):
            self.state = 'up'

    def update(self, dt):
        """
        Cập nhật trạng thái, vị trí và hoạt ảnh của biểu tượng
        Kiểm tra đường dẫn di chuyển (`self.path`):
            Nếu có đường dẫn (`self.path` không rỗng):
                Gọi phương thức `point_collision` để kiểm tra va chạm với điểm đến.
                Cập nhật vị trí biểu tượng dựa trên hướng di chuyển (`self.direction`), tốc độ (`self.speed`),
                    và khoảng thời gian (`dt`).
        Cập nhật trạng thái hoạt ảnh (`self.state`) dựa trên hướng di chuyển (gọi phương thức `get_state`).
        Cập nhật khung hình hoạt ảnh hiện tại (`self.animate`) dựa trên khoảng thời gian (`dt`)
            :param dt: Thời gian trôi qua
        """
        if self.path:
            self.point_collision()
            self.rect.center += self.direction * self.speed * dt
        self.get_state()
        self.animate(dt)

class PathSprite(Sprite):
    """
    Đại diện cho một đối tượng sprite trên đường dẫn di chuyển trong trò chơi.
    Lớp này kế thừa từ `pygame.sprite.Sprite` để cung cấp các tính năng cơ bản của đối tượng hiển thị.
    Các đối tượng sprite đường dẫn thường được sử dụng để đánh dấu các vị trí trên màn hình có thể di chuyển đến được
    """
    def __init__(self, pos, surf, groups, level):
        """
        Hàm khởi tạo
            :param pos: Vị trí ban đầu của đối tượng sprite đường dẫn (x, y)
            :param surf: Surface của đối tượng sprite đường dẫn được hiển thị
            :param groups: Một hoặc nhiều nhóm sprite để thêm đối tượng sprite đường dẫn vào
            :param level: Mức độ của màn chơi được liên kết với đối tượng sprite đường dẫn
        """
        super().__init__(pos, surf, groups, Z_LAYERS['path'])
        self.level = level
