import pygame

pygame.init()
font = pygame.font.Font(None, 30)


def debug(info, y=10, x=10):
    """
    Tạo phần hiển trị thông tin cần thiết lên màn hình nằm mục đích sửa lỗi
        :param info: thông tin muốn được in lên màn hình
        :param y: cố định là 10
        :param x: cố định là 10
        :return: Vẽ ra thông tin muốn hiển thị lên màn hình
    """
    display_surface = pygame.display.get_surface()
    debug_surf = font.render(str(info), True, 'White')
    debug_rect = debug_surf.get_rect(topleft=(x, y))
    pygame.draw.rect(display_surface, 'Black', debug_rect)
    display_surface.blit(debug_surf, debug_rect)
