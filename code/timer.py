from pygame.time import get_ticks


class Timer:
    """
    Lớp quản lý thời gian với các chức năng:
        Bật/tắt timer
        Cập nhật và kiểm tra thời gian trôi qua
        Chạy hàm được truyền vào khi hết thời gian
    * Phương thức:
    activate(): Bật timer.
    deactivate(): Tắt timer.
    update(): Cập nhật timer và kiểm tra thời gian trôi qua.
    """
    def __init__(self, duration, func=None, repeat=False, autostart=False):
        """
        Khởi tạo timer với các thông số
        duration: Khoảng thời gian cần chạy
        func: Hàm sẽ thực hiện khi hết thời gian
        start_time: Thời gian bắt đầu
        active: Có đang hoạt động hay không
        repeat: Có lặp lại hay không
        autostart: Có tự chạy khi vừa tạo hay không
            :param duration: Khoảng thời gian cần chạy
            :param func: Hàm được truyền vào để thực hiện khi hết duration
            :param repeat: Có muốn lặp lại hay không
            :param autostart: Tự động chạy khi khởi tạo, không cần gọi hàm bật
        """
        self.duration = duration
        self.func = func
        self.start_time = 0
        self.active = False
        self.repeat = repeat
        self.autostart = autostart
        if self.autostart:
            self.activate()

    def activate(self):
        """
        Hàm bật
        Chuyển hoạt động của timer sang True
        Lấy thời gian bắt đầu bằng hàm get_ticks()
        * get_ticks(): Lấy thời gian kể từ khi init
        """
        self.active = True
        self.start_time = get_ticks()

    def deactivate(self):
        """
        Hàm tắt
        Tắt hoạt động của timer
        Đặt lại thời gian bắt đầu bằng 0
        Nếu có lặp lại thì sẽ gọi hàm bật (activate) để chạy tiếp tục
        """
        self.active = False
        self.start_time = 0
        if self.repeat:
            self.activate()

    def update(self):
        """
        Hàm cập nhật
        Lấy thời gian hiện tại bằng hàm get_ticks()
        Xác định xem khoảng thời gian trôi qua đã vượt quá duration chưa
        Nếu rồi thì sẽ thực hiện hàm được truyền vô qua self.func() và dừng cập nhật thông qua hàm tắt (deactivate)
        * get_ticks(): Lấy thời gian kể từ khi init
        """
        current_time = get_ticks()
        if current_time - self.start_time >= self.duration:
            if self.func and self.start_time != 0:
                self.func()
            self.deactivate()
