
class Data:
    """
    Lớp lưu trữ thông tin trạng thái trò chơi và người chơi

    Lớp này lưu trữ các thông số quan trọng của người chơi và trò chơi, chẳng hạn như số tiền xu (coin), máu (health),
        level đã mở khóa (unlocked_level) và level hiện tại (current_level). Ngoài ra, lớp này có thể tương tác
        với giao diện người dùng (UI) để hiển thị thông tin cập nhật
    * Phương thức
    `coins` (thuộc tính chỉ đọc/ghi):
        `get`: Lấy số tiền xu hiện tại
        `set`: Cập nhật số tiền xu và thông báo cho UI hiển thị giá trị mới
    `health` (thuộc tính chỉ đọc/ghi):
        `get`: Lấy số máu hiện tại
        `set`: Cập nhật số máu và thông báo cho UI hiển thị số máu mới bằng cách tạo lại các biểu tượng máu tim
    """
    # Tạo lớp data lưu trữ thông số của người chơi
    def __init__(self, ui):
        """
        Hàm khởi tạo
            :param ui: Tham chiếu đến đối tượng quản lý giao diện người dùng (UI) để tương tác và hiển thị thông tin
        """
        self.ui = ui
        self._coins = 0
        self._health = 5
        self.ui.create_hearts(self._health)

        self.unlocked_level = 0
        self.current_level = 0

    @property
    def coins(self):
        """
        Lấy số tiền xu hiện tại của người chơi
        Thuộc tính này cho phép truy cập số tiền xu mà người chơi đang sở hữu
            :return: Số tiền xu hiện tại của người chơi
        """
        # Đọc coin
        return self._coins

    @coins.setter
    def coins(self, value):
        """
        Cập nhật số tiền xu của người chơi và thông báo cho UI hiển thị giá trị mới
        Phương thức này thiết lập lại giá trị của thuộc tính `_coins` (riêng tư) để cập nhật số tiền xu của người chơi
            :param value: Số tiền xu mới cần thiết lập
        """
        # Thêm coin
        self._coins = value
        self.ui.show_coins(self.coins)

    @property
    def health(self):
        """
        Lấy số máu hiện tại của người chơi
        Thuộc tính này cho phép truy cập số máu (máu tim) hiện tại của người chơi
            :return: Số máu (máu tim) hiện tại của người chơi
        """
        # Đọc health
        return self._health

    @health.setter
    def health(self, value):
        """
        Cập nhật số máu của người chơi và thông báo cho UI hiển thị các biểu tượng máu (tim) tương ứng.

        Phương thức này thiết lập lại giá trị của thuộc tính `_health` (riêng tư) để cập nhật số máu của người chơi.
            Ngoài ra, phương thức này gọi đến phương thức `create_hearts` của đối tượng UI được tham chiếu
            để tạo lại các biểu tượng máu tim trên giao diện người dùng,
            phản ánh chính xác số máu hiện tại.
            :param value: Số máu mới cần thiết lập
        """
        # tạo hearth
        self._health = value
        self.ui.create_hearts(value)


