from settings import *
from os import walk
from os.path import join


def import_image(*path, alpha=True, format='png'):
    """
    Tải ảnh từ một vị trí cụ thể
        :param path: Đường dẫn đến ảnh
        :param alpha: Xác định giữ nguyên độ trong suốt của ảnh hay không (định dạng RGBA)
        :param format: Định dạng ảnh mong muốn
        :return: Bề mặt ảnh được tải và chuyển đổi
    """
    full_path = join(*path) + f'.{format}'
    return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()


def import_folder(*path):
    """
    Tải tất cả ảnh từ một thư mục theo thứ tự được sắp xếp
        :param path: Đường dẫn đến thư mục chứa ảnh
        :return: Danh sách các bề mặt ảnh được tải và chuyển đổi
    """
    frames = []
    for folder_path, subfolders, image_names in walk(join(*path)):
        for image_name in sorted(image_names, key=lambda name: int(name.split('.')[0])):
            full_path = join(folder_path, image_name)
            frames.append(pygame.image.load(full_path).convert_alpha())
    return frames


def import_folder_dict(*path):
    """
    Tải tất cả ảnh từ một thư mục, lưu trữ chúng trong một từ điển với tên ảnh là khóa và bề mặt ảnh được tải là giá trị
        :param path: Đường dẫn đến thư mục chứa ảnh
        :return: Từ điển chứa tên ảnh làm khóa và bề mặt ảnh tương ứng làm giá trị
    """
    frame_dict = {}
    for folder_path, _, image_names in walk(join(*path)):
        for image_name in image_names:
            full_path = join(folder_path, image_name)
            surface = pygame.image.load(full_path).convert_alpha()
            frame_dict[image_name.split('.')[0]] = surface
    return frame_dict


def import_sub_folders(*path):
    """
    Tải ảnh từ một thư mục và các thư mục con của nó, tạo một từ điển với tên thư mục con làm khóa và danh sách ảnh từ mỗi thư mục con làm giá trị
        :param path: Đường dẫn đến thư mục gốc
        :return: Từ điển chứa tên thư mục con làm khóa và danh sách ảnh được tải từ mỗi thư mục con làm giá trị
    """
    frame_dict = {}
    for _, sub_folders, __ in walk(join(*path)):
        if sub_folders:
            for sub_folder in sub_folders:
                frame_dict[sub_folder] = import_folder(*path, sub_folder)
    return frame_dict
