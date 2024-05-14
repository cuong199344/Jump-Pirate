from settings import *
from sprites import AnimatedSprite
from random import randint
from timer import Timer


class UI:
    """
    Lớp này quản lý các thành phần giao diện người dùng (UI) cho trò chơi

    * Phương thức
    create_hearts(self, amount): Tạo và thêm `amount` sprite trái tim vào nhóm `sprites`, đại diện cho sức khỏe người chơi.
    display_text(self): Hiển thị số lượng xu hiện tại và biểu tượng xu trên màn hình.
    show_coins(self, amount): Cập nhật số lượng xu được hiển thị.
    update(self, dt): Cập nhật các yếu tố UI dựa trên thời gian delta (`dt`). Điều này thường bao gồm hoạt hình và vẽ.
    """
    def __init__(self, font, frames):
        """
        Hàm khởi tạo
            :param font: Đối tượng phông chữ được sử dụng để hiển thị các yếu tố văn bản trong UI
            :param frames: Từ điển chứa các khung hình hoạt hình cho các yếu tố UI. Khóa nên tương ứng với tên phần tử
        """
        self.display_surface = pygame.display.get_surface()
        self.sprites = pygame.sprite.Group()
        self.font = font

        # hearts
        self.heart_frames = frames['heart']
        self.heart_surf_width = self.heart_frames[0].get_width()
        self.heart_padding = 5
        self.create_hearts(5)

        # coins
        self.coin_amount = 0
        self.coin_timer = Timer(1000)
        self.coin_surf = frames['coin']

    def create_hearts(self, amount):
        """
        Hàm tạo và hiển trị trái tim
        Tạo và hiển thị các sprite trái tim đại diện cho sức khỏe người chơi
        Phương thức này xóa tất cả các sprite hiện có và tạo `amount` sprite trái tim mới,  với vị trí được tính toán
            dựa trên các thuộc tính của lớp
            :param amount: Số lượng trái tim cần tạo và hiển thị
        """
        # Tạo hình trái tim để hiển thị thành máu của người chơi
        # Trước khi tạo heart mới sẽ xóa toàn bộ heart cũ
        for sprite in self.sprites:
            sprite.kill()
        for heart in range(amount):
            # Muốn heart được mở rộng theo chiều ngang
            x = 10 + heart * (self.heart_surf_width + self.heart_padding)
            y = 10
            Heart((x, y), self.heart_frames, self.sprites)

    def display_text(self):
        """
        Hàm hiển thị số lượng xu hiện tại
        Hiển thị số lượng xu hiện tại và biểu tượng xu trên màn hình
        Phương thức này hiển thị số lượng xu đã thu thập được dưới dạng văn bản và biểu tượng xu trên bề mặt hiển thị UI
        """
        # Hiển thị chữ
        text_surf = self.font.render(str(self.coin_amount), False, 'white')
        text_rect = text_surf.get_frect(topleft=(16, 34))
        self.display_surface.blit(text_surf, text_rect)

        # Hiển thị hình đồng xu
        coin_rect = self.coin_surf.get_frect(center=text_rect.midbottom).move(0, 10)
        self.display_surface.blit(self.coin_surf, coin_rect)

    def show_coins(self, amount):
        """
        Hàm cập nhật số lượng xu
        Cập nhật số lượng xu hiển thị trên màn hình.
        Phương thức này cập nhật thuộc tính `coin_amount` của lớp với giá trị được cung cấp, có thể ảnh hưởng đến cách
            hiển thị số lượng xu và biểu tượng xu trên UI
            :param amount: Số lượng xu cần hiện
        """
        self.coin_amount = amount

    def update(self, dt):
        """
        Hàm cập nhật
        Cập nhật và hiển thị các thành phần giao diện người dùng (UI)
        Phương thức này thực hiện các hành động sau để cập nhật UI:
            Cập nhật trạng thái của các sprite UI (ví dụ như hoạt ảnh) dựa trên thời gian trôi qua `dt`
            Vẽ tất cả các sprite UI lên bề mặt hiển thị chính
            Hiển thị số lượng xu hiện tại và biểu tượng xu
            :param dt: Thời gian trôi qua
        """
        self.sprites.update(dt)
        self.sprites.draw(self.display_surface)
        self.display_text()


class Heart(AnimatedSprite):
    """
    Đại diện cho một sprite trái tim hoạt hình trong giao diện người dùng (UI).
    Lớp này kế thừa từ `AnimatedSprite` để cung cấp các tính năng hoạt ảnh cơ bản.
    Ngoài ra, lớp `Heart` có thêm thuộc tính `active` để theo dõi trạng thái hoạt động (hiện thị hoạt ảnh) của trái tim.
    * Phương thức
    animate(dt):  Cập nhật chỉ số khung hình và thay đổi hình ảnh của sprite trái tim dựa trên dt (khoảng thời gian)
    update(dt): Mô tả cách phương thức này kiểm tra trạng thái hoạt động và thực hiện hành động cập nhật tương ứng
    """
    def __init__(self, pos, frames, groups):
        """
        Hàm khởi tạo
            :param pos: Vị trí ban đầu của sprite trái tim (x, y)
            :param frames: Danh sách các Surface đại diện cho từng khung hình hoạt ảnh của trái tim
            :param groups: Một hoặc nhiều nhóm sprite để thêm sprite trái tim vào
        """
        super().__init__(pos, frames, groups)
        self.active = False

    def animate(self, dt):
        """
        Hàm hoạt họa
        Cập nhật hoạt ảnh của trái tim.
        Phương thức này tính toán khung hình hoạt ảnh tiếp theo dựa trên tốc độ hoạt ảnh (`ANIMATION_SPEED`)
            và khoảng thời gian (`dt`) kể từ lần cập nhật trước.
        Nếu cần thiết, phương thức cũng cập nhật hình ảnh của sprite trái tim và xử lý khi hoạt ảnh hoàn thành
            :param dt: Thời gian trôi qua
        """
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.active = False
            self.frame_index = 0

    def update(self, dt):
        """
        Hàm cập nhật
        Cập nhật trạng thái và hành vi của trái tim.
        Phương thức này kiểm tra trạng thái hoạt động (`active`) của trái tim và thực hiện các hành động tương ứng:
            Nếu hoạt động (`active == True`), gọi phương thức `animate` để cập nhật hoạt ảnh của trái tim
                dựa trên khoảng thời gian (`dt`).
            Nếu không hoạt động (`active == False`), tạo ra xác suất ngẫu nhiên (1/2000) để kích hoạt trạng thái
                hoạt động và bắt đầu hoạt ảnh.
            :param dt: Thời gian trôi qua
        """
        if self.active:
            self.animate(dt)
        else:
            if randint(0, 2000) == 1:
                self.active = True