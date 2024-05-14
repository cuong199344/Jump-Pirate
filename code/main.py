import sys

import pygame

from settings import *
from level import Level
from pytmx.util_pygame import load_pygame
from os.path import join
from support import *
from data import *
from debug import debug
from ui import UI
from overworld import Overworld

class Game:
    """
    Lớp chính điều khiển toàn bộ trò chơi Jump Pirate
    Lớp này khởi tạo và quản lý các thành phần chính của trò chơi, bao gồm:
        Màn hình hiển thị (display_surface)
        Clock để kiểm soát tốc độ khung hình (frame rate)
        Các tài nguyên (assets) như hình ảnh, âm thanh, dữ liệu
        Giai đoạn chơi hiện tại (current_stage), có thể là màn chơi (Level) hoặc màn hình overworld (Overworld)
        Âm nhạc nền (bg_music)
    * Phương thức
    switch_stage(target, unlock=0): Chuyển đổi giữa các giai đoạn chơi khác nhau (màn chơi, overworld)
    import_assets(self): Nhập các tài nguyên (hình ảnh, âm thanh) cần thiết cho trò chơi
    run(self): Vòng lặp chính của trò chơi, xử lý các sự kiện, cập nhật và hiển thị trò chơi mỗi khung hình
    check_game_over(self): Kiểm tra điều kiện kết thúc trò chơi (mất hết máu)
    """
    def __init__(self):
        """
        Hàm khởi tạo
        Khởi tạo trò chơi Jump Pirate và thiết lập các thành phần chính.
        Phương thức này được gọi khi khởi tạo một đối tượng `Game` mới. Nó thực hiện các bước sau để thiết lập trò chơi:
            Khởi tạo Pygame: Khởi động thư viện Pygame, nền tảng để xây dựng các trò chơi 2D
            Tạo màn hình hiển thị: Tạo cửa sổ trò chơi với kích thước được xác định bởi
                `WINDOW_WIDTH` và `WINDOW_HEIGHT`. Đặt tiêu đề cửa sổ thành "Jump Pirate"
            Khởi tạo Clock: Tạo đối tượng `Clock` để kiểm soát tốc độ khung hình (frame rate) của trò chơi,
                đảm bảo trải nghiệm mượt mà trên các máy tính khác nhau
            Nhập tài nguyên: Gọi phương thức `import_assets` để tải các hình ảnh, âm thanh và dữ liệu cần thiết cho trò
                chơi.
            Khởi tạo các thành phần chính:
                `ui`: Tạo đối tượng `UI` để quản lý giao diện người dùng (UI)
                `data`: Tạo đối tượng `Data` để lưu trữ các dữ liệu trò chơi
                `tmx_maps`: Tạo một từ điển lưu trữ các bản đồ Tiled Map Editor (TMX) của các màn chơi.
                `tmx_overworld`: Tải bản đồ TMX của màn hình overworld.
                `current_stage`: Khởi tạo màn chơi đầu tiên (`Level`) bằng cách truyền bản đồ TMX, hình ảnh, âm thanh,
                    dữ liệu trò chơi và phương thức
                `switch_stage` để chuyển đổi giữa các màn chơi.
            Phát nhạc nền: Phát nhạc nền lặp lại (`play(-1)`)
        """
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Jump Pirate")

        # Clock for frame rate
        self.clock = pygame.time.Clock()

        self.import_assets()
        self.text_font = pygame.font.Font('./font/Pixeltype.ttf', 60)
        self.ui = UI(self.font, self.ui_frames)
        self.data = Data(self.ui)
        self.tmx_maps = {
            0: load_pygame(join('.', 'data', 'levels', '1.tmx')),
            1: load_pygame(join('.', 'data', 'levels', '2.tmx')),
            2: load_pygame(join('.', 'data', 'levels', '3.tmx')),
        }
        self.tmx_overworld = load_pygame(join('.', 'data', 'overworld', 'overworld.tmx'))
        self.current_stage = Level(self.tmx_maps[0], self.level_frames, self.audio_files, self.data, self.switch_stage)

        # BG music
        # Đặt -1 đề loop
        self.bg_music.play(-1)
        self.bg_music.set_volume(0.3)

    def switch_stage(self, target, unlock=0):
        """
        Chuyển đổi giữa các giai đoạn chơi khác nhau trong trò chơi Jump Pirate
        Phương thức này được gọi để chuyển đổi giữa màn chơi (level) và màn hình overworld
            :param target: Xác định giai đoạn chơi
            :param unlock: Màn chơi được mở khóa khi chuyển đến overworld (chỉ áp dụng khi target là "overworld")
        """
        if target == 'level':
            self.current_stage = Level(self.tmx_maps[self.data.current_level], self.level_frames, self.audio_files,
                                       self.data, self.switch_stage)
        # overworld
        else:
            if unlock > 0:
                self.data.unlocked_level = unlock
            else:
                self.data.health -= 1
            self.current_stage = Overworld(self.tmx_overworld, self.data, self.overworld_frames, self.switch_stage)

    def import_assets(self):
        """
        Nhập các tài nguyên (hình ảnh, âm thanh) cần thiết cho trò chơi Jump Pirate
        Phương thức này thực hiện các tác vụ sau để chuẩn bị tài nguyên cho trò chơi:
            Nhập hình ảnh các đối tượng
            Nhập font chữ
            Nhập hình ảnh giao diện (UI)
            Nhập hình ảnh màn hình overworld
            Nhập âm thanh
            Nhập nhạc nền

        """
        # Load ảnh của các object cần thiết và lưu vào level_frames
        self.level_frames = {
            'flag': import_folder('.', 'graphics', 'level', 'flag'),
            'saw': import_folder('.', 'graphics', 'enemies', 'saw', 'animation'),
            'floor_spike': import_folder('.', 'graphics', 'enemies', 'floor_spikes'),
            'palms': import_sub_folders('.', 'graphics', 'level', 'palms'),
            'candle': import_folder('.', 'graphics', 'level', 'candle'),
            'window': import_folder('.', 'graphics', 'level', 'window'),
            'big_chain': import_folder('.', 'graphics', 'level', 'big_chains'),
            'small_chain': import_folder('.', 'graphics', 'level', 'small_chains'),
            'candle_light': import_folder('.', 'graphics', 'level', 'candle light'),
            'player': import_sub_folders('.', 'graphics', 'player'),
            'saw': import_folder('.', 'graphics', 'enemies', 'saw', 'animation'),
            'saw_chain': import_image('.', 'graphics', 'enemies', 'saw', 'saw_chain'),
            'helicopter': import_folder('.', 'graphics', 'level', 'helicopter'),
            'boat': import_folder('.', 'graphics', 'objects', 'boat'),
            'spike': import_image('.', 'graphics', 'enemies', 'spike_ball', 'Spiked Ball'),
            'spike_chain': import_image('.', 'graphics', 'enemies', 'spike_ball', 'spiked_chain'),
            'tooth': import_folder('.', 'graphics', 'enemies', 'tooth', 'run'),
            'shell': import_sub_folders('.', 'graphics', 'enemies', 'shell'),
            'pearl': import_image('.', 'graphics', 'enemies', 'bullets', 'pearl'),
            'items': import_sub_folders('.', 'graphics', 'items'),
            'particle': import_folder('.', 'graphics', 'effects', 'particle'),
            'water_top': import_folder('.', 'graphics', 'level', 'water', 'top'),
            'water_body': import_image('.', 'graphics', 'level', 'water', 'body'),
            'bg_tiles': import_folder_dict('.', 'graphics', 'level', 'bg', 'tiles'),
            'cloud_small': import_folder('.', 'graphics', 'level', 'clouds', 'small'),
            'cloud_large': import_image('.', 'graphics', 'level', 'clouds', 'large_cloud'),
            'fly': import_folder('.', 'graphics', 'enemies', 'fly', 'fly'),
        }

        self.font = pygame.font.Font(join('.', 'graphics', 'ui', 'runescape_uf.ttf'), 40)
        self.ui_frames = {
            'heart': import_folder('.', 'graphics', 'ui', 'heart'),
            'coin': import_image('.', 'graphics', 'ui', 'coin')
        }
        self.overworld_frames = {
            'palms': import_folder('.', 'graphics', 'overworld', 'palm'),
            'water': import_folder('.', 'graphics', 'overworld', 'water'),
            'path': import_folder_dict('.', 'graphics', 'overworld', 'path'),
            'icon': import_sub_folders('.', 'graphics', 'overworld', 'icon'),
        }

        self.audio_files = {
            'coin': pygame.mixer.Sound(join('.', 'audio', 'coin.wav')),
            'attack': pygame.mixer.Sound(join('.', 'audio', 'attack.wav')),
            'jump': pygame.mixer.Sound(join('.', 'audio', 'jump.wav')),
            'damage': pygame.mixer.Sound(join('.', 'audio', 'damage.wav')),
            'pearl': pygame.mixer.Sound(join('.', 'audio', 'pearl.wav')),
        }
        self.bg_music = pygame.mixer.Sound(join('.', 'audio', 'starlight_city.mp3'))
        self.bg_music.set_volume(0.5)
    def run(self):
        """
        Vòng lặp chính của trò chơi Jump Pirate, xử lý các sự kiện, cập nhật và hiển thị trò chơi.
        Phương thức này là vòng lặp chính điều khiển hoạt động của trò chơi. Nó chạy liên tục cho đến khi
            người chơi thoát game. Bên trong vòng lặp, các tác vụ sau được thực hiện mỗi khung hình:
                Kiểm tra tốc độ khung hình (frame rate)
                Xử lý sự kiện
                Kiểm tra điều kiện kết thúc trò chơi
                Cập nhật màn chơi hiện tại:
                Cập nhật giao diện người dùng (UI):
                Hiển thị khung hình:
        """
        while True:
            # Đặt frame rate để máy yếu chạy mượt và máy mạnh chạy tối đa
            dt = self.clock.tick() / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.data.health <= 0 or self.data.unlocked_level == 3:
                    if event.type == pygame.KEYDOWN:
                        pygame.quit()
                        sys.exit()


            self.current_stage.run(dt)
            self.ui.update(dt)
            self.check_game_over()

            pygame.display.update()

    def check_game_over(self):
        """
        Kiểm tra điều kiện kết thúc trò chơi Jump Pirate
        Phương thức này kiểm tra xem người chơi có hết máu (`self.data.health`) hay không. Nếu hết máu, trò chơi sẽ kết thúc
        """
        if self.data.health <= 0:
            self.display_surface.fill((94, 129, 162))

            self.score_message = self.text_font.render(f"Your score: {self.data.coins}", False, (111, 196, 169))
            self.score_message_rect = self.score_message.get_rect(center=(300, 250))

            self.gameover_message = self.text_font.render("Game Over", False, (111, 196, 169))
            self.gameover_message_rect = self.score_message.get_rect(center=(500, 400))

            self.over_message = self.text_font.render("PRESS ANY KEY TO EXIT THE GAME", False, (111, 196, 169))
            self.over_message_rect = self.score_message.get_rect(center=(700, 550))

            self.display_surface.blit(self.score_message, self.score_message_rect)
            self.display_surface.blit(self.gameover_message, self.gameover_message_rect)
            self.display_surface.blit(self.over_message, self.over_message_rect)

        if self.data.unlocked_level == 3:
            self.display_surface.fill((94, 129, 162))

            self.score_message = self.text_font.render(f"Your score: {self.data.coins}", False, (111, 196, 169))
            self.score_message_rect = self.score_message.get_rect(center=(300, 250))

            self.gameover_message = self.text_font.render("VICTORY !!!", False, (111, 196, 169))
            self.gameover_message_rect = self.score_message.get_rect(center=(500, 400))

            self.over_message = self.text_font.render("PRESS ANY KEY TO EXIT THE GAME", False, (111, 196, 169))
            self.over_message_rect = self.score_message.get_rect(center=(700, 550))

            self.display_surface.blit(self.score_message, self.score_message_rect)
            self.display_surface.blit(self.gameover_message, self.gameover_message_rect)
            self.display_surface.blit(self.over_message, self.over_message_rect)


if __name__ == "__main__":
    game = Game()
    game.run()
