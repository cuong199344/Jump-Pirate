import pygame

from settings import *
from timer import *
from os.path import join
from math import sin

class Player(pygame.sprite.Sprite):
    """
    Đại diện cho nhân vật chính của trò chơi
    Lớp này kế thừa từ `pygame.sprite.Sprite` để cung cấp các tính năng cơ bản của đối tượng hiển thị
    Nhân vật có thể di chuyển, nhảy, tấn công và tương tác với các đối tượng khác trong môi trường trò chơi
    * Phương thức
    input(): Kiểm tra input từ người chơi (bấm phím) để điều khiển hướng di chuyển và tấn công
    attack(): Thực hiện hành động tấn công của nhân vật
    move(dt): Cập nhật vị trí của nhân vật theo hướng di chuyển, trọng lực, nhảy và va chạm
    platform_move(dt): Di chuyển nhân vật cùng với nền di chuyển nếu đang đứng trên đó
    check_contact(): Kiểm tra xem nhân vật đang tiếp xúc với mặt phẳng nào
    collision(axis): Xử lý va chạm của nhân vật với các sprite khác theo trục được chỉ định
    def semi_collision(): Xử lý va chạm đặc biệt của nhân vật với các sprite trong nhóm `semi_collision_sprites`
    update_timers(): Cập nhật trạng thái của các bộ hẹn giờ cho các hành động của nhân vật.
    animate(dt): Cập nhật hình ảnh hoạt ảnh của nhân vật
    get_state(): Cập nhật trạng thái hoạt ảnh của nhân vật dựa trên thông tin di chuyển và va chạm
    get_damage(): Giảm máu của nhân vật khi bị va chạm với kẻ thù
    flicker(): Tạo hiệu ứng nhận sát thương cho nhân vật
    update(dt): Cập nhật trạng thái của nhân vật mỗi frame
    """
    def __init__(self, pos, groups, collision_sprites, semi_collision_sprites, frames, data, attack_sound, jump_sound):
        """
        Hàm khởi tạo
            :param pos: Vị trí ban đầu của nhân vật (x, y)
            :param groups: Danh sách các nhóm sprite để thêm nhân vật vào
            :param collision_sprites: Nhóm các sprite dùng để kiểm tra va chạm với nhân vật
            :param semi_collision_sprites: Nhóm các sprite dùng để kiểm tra va chạm đặc biệt với nhân vật (chẳng hạn như nền di chuyển)
            :param frames: Từ điển lưu trữ các khung hình hoạt ảnh theo trạng thái
            :param data: Dữ liệu trò chơi liên quan đến nhân vật (chẳng hạn như máu)
            :param attack_sound: Âm thanh phát ra khi nhân vật tấn công
            :param jump_sound: Âm thanh phát ra khi nhân vật nhảy
        """
        # general setup
        super().__init__(groups)
        self.z = Z_LAYERS['main']
        self.data = data

        # image
        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = "idle", True
        self.image = self.frames[self.state][self.frame_index]


        # rects
        self.rect = self.image.get_frect(topleft=pos)
        self.hitbox_rect = self.rect.inflate(-76, -36)
        # rect ở frame trước để xác định hướng đi của nhân vật
        self.old_rect = self.hitbox_rect.copy()

        # movement
        self.direction = vector()
        self.speed = 500
        self.gravity = 2000
        self.jump = False
        self.jump_height = 900
        self.jump_state = "on_ground"
        self.attacking = False

        # collision
        self.collision_sprites = collision_sprites
        self.semi_collision_sprites = semi_collision_sprites
        self.on_surface = {'floor': False, 'left': False, 'right': False}
        self.platform = None

        self.timers = {
            'wall jump': Timer(200),
            'wall slide block': Timer(200),
            'platform skip': Timer(100),
            'attack block': Timer(500),
            'hit': Timer(1000)
        }

        # audio
        self.attack_sound = attack_sound
        self.jump_sound = jump_sound
        self.jump_sound.set_volume(0.1)

    def input(self):
        """
        Xử lý input từ người chơi để điều khiển nhân vật.
        Phương thức này kiểm tra các phím bấm của người chơi và cập nhật trạng thái di chuyển, tấn công và nhảy của nhân vật.
        **Các phím điều khiển:**
            Phím mũi tên phải (RIGHT): Nhân vật di chuyển sang phải.
            Phím mũi tên trái (LEFT): Nhân vật di chuyển sang trái.
            Phím mũi tên xuống (DOWN): Kích hoạt bộ hẹn giờ `platform skip` để ngăn nhân vật bám lên nền di chuyển
                trong một khoảng thời gian nhất định.
            Phím X: Thực hiện hành động tấn công.
            Phím SPACE: Nhân vật nhảy.

        """
        # Kiểm tra input
        keys = pygame.key.get_pressed()
        input_vector = vector(0, 0)

        if not self.timers["wall jump"].active:
            if keys[pygame.K_RIGHT]:
                input_vector.x += 1
                self.facing_right = True

            if keys[pygame.K_LEFT]:
                input_vector.x -= 1
                self.facing_right = False

            if keys[pygame.K_DOWN]:
                self.timers['platform skip'].activate()

            if keys[pygame.K_x]:
                self.attack()

            self.direction.x = input_vector.normalize().x if input_vector else input_vector.x

        if keys[pygame.K_SPACE]:
            self.jump = True

        # double jump
        if not keys[pygame.K_SPACE] and self.jump_state == "jumped" and not all ((self.on_surface['floor'],self.on_surface['left'], self.on_surface['right'])):
            self.jump_state = "ready_for_double_jump"

    def attack(self):
        """
        Thực hiện hành động tấn công của nhân vật.
        Phương thức này cho phép nhân vật thực hiện hành động tấn công khi bộ hẹn giờ `self.timers['attack block']`
            không hoạt động.
        Nếu điều kiện được đáp ứng, phương thức sẽ:
            Thiết lập `self.attacking` thành True để kích hoạt hoạt ảnh tấn công.
            Khởi tạo lại chỉ số khung hình (`self.frame_index`) bằng 0 để bắt đầu trình tự hoạt ảnh tấn công.
            Kích hoạt bộ hẹn giờ `self.timers['attack block']` để ngăn chặn việc tấn công liên tục trong một khoảng
                thời gian nhất định.
            Phát âm thanh tấn công (`self.attack_sound`)
        """
        # chỉ được quyền attack khi mà timer['attack block'] không chạy
        # Khi attack sẽ chạy timer['attack block']
        if not self.timers['attack block'].active:
            self.attacking = True
            self.frame_index = 0
            self.timers['attack block'].activate()
            self.attack_sound.play()

    def move(self, dt):
        """
        Cập nhật vị trí của nhân vật theo hướng di chuyển, trọng lực, nhảy và va chạm.
            Phương thức này thực hiện các hành động sau để di chuyển nhân vật:
                Di chuyển theo phương ngang (horizontal):
                    Cập nhật vị trí trục X của hình chữ nhật bao quanh vùng va chạm `self.hitbox_rect` dựa trên hướng di
                        chuyển (`self.direction.x`), tốc độ (`self.speed`), và khoảng thời gian (`dt`).
                    Gọi phương thức `collision("horizontal")` để xử lý va chạm theo phương ngang.

            Di chuyển theo phương dọc (vertical):
                Kiểm tra điều kiện nhân vật đang nhảy (không chạm đất) và tiếp xúc với tường:
                    Nếu đúng, thiết lập vận tốc theo phương Y (`self.direction.y`) bằng 0 để nhân vật bám tường (wall slide).
                Nếu không:
                    Cập nhật vận tốc theo phương Y (`self.direction.y`) dựa trên trọng lực (`self.gravity`) và
                        khoảng thời gian (`dt`).
                    Cập nhật vị trí trục Y của hình chữ nhật bao quanh vùng va chạm `self.hitbox_rect` dựa trên vận tốc
                        theo phương Y (`self.direction.y`) và khoảng thời gian (`dt`).
                    Cập nhật lại vận tốc theo phương Y (`self.direction.y`) dựa trên trọng lực (`self.gravity`) và
                        khoảng thời gian (`dt`).

            Nhảy:
                Kiểm tra trạng thái nhảy (`self.jump`):
                    Nếu đang nhảy:
                        Nếu đang chạm đất:
                            Thiết lập vận tốc theo phương Y (`self.direction.y`) thành một giá trị âm để bật lên
                                (chiều cao nhảy phụ thuộc `self.jump_height`).
                            Kích hoạt bộ hẹn giờ `self.timers["wall slide block"]` để ngăn chặn bám tường ngay sau khi nhảy.
                            Giảm một chút vị trí Y của `self.hitbox_rect` để tránh kẹt nhân vật trên nền.
                            Cập nhật trạng thái nhảy (`self.jump_state`) thành "jumped" (đã nhảy).
                            Phát âm thanh nhảy (`self.jump_sound`).
                        Nếu đang bám tường (tiếp xúc với tường trái hoặc phải):
                            Kích hoạt bộ hẹn giờ `self.timers['wall jump']` để ngăn chặn việc nhảy bám tường liên tục.
                            Thiết lập vận tốc theo phương Y (`self.direction.y`) thành một giá trị âm để bật lên.
                            Thiết lập vận tốc theo phương X (`self.direction.x`) để tạo hiệu ứng hất sang trái hoặc phải
                                tuỳ thuộc tường đang bám.
                            Cập nhật trạng thái nhảy (`self.jump_state`) thành "jumped" (đã nhảy).
                            Phát âm thanh nhảy (`self.jump_sound`).
                        Nếu đang trong trạng thái "ready_for_double_jump" (có thể nhảy đôi):
                            Thiết lập vận tốc theo phương Y (`self.direction.y`) thành một giá trị âm để bật lên
                                (chiều cao nhảy phụ thuộc `self.jump_height`).
                            Kích hoạt bộ hẹn giờ `self.timers["wall slide block"]` để ngăn chặn bám tường ngay sau khi nhảy.
                            Giảm một chút vị trí Y của `self.rect` để tránh kẹt nhân vật trên nền.
                            Cập nhật trạng thái nhảy (`self.jump_state`) thành "double_jump" (đang nhảy đôi).
                            Phát âm thanh nhảy (`self.jump_sound`).
                Thiết lập trạng thái nhảy (`self.jump`) thành False sau khi xử lý xong các trường hợp nhảy.

            Va chạm:
                Gọi phương thức `collision("vertical")` để xử lý va chạm theo phương dọc.
                Gọi phương thức `semi_collision()` để xử lý va chạm đặc biệt với các sprite trong nhóm `semi_collision_sprites`.

            Cập nhật vị trí hiển thị của nhân vật:
                Cập nhật vị trí trung tâm của hình chữ nhật hiển thị `self.rect` dựa trên vị trí trung tâm của
                    hình chữ nhật va chạm `self.hitbox_rect`.
            :param dt: Thời gian trôi qua
        """
        # Di chuyển
        # horizontal
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision("horizontal")

        # vertical
        # Kiểm tra xem người chơi có đang trong air và tiếp xúc với tường hay không
        # wall slide
        if not self.on_surface['floor'] and any((self.on_surface['left'], self.on_surface['right'])) and not self.timers["wall slide block"].active:
            self.direction.y = 0
            self.hitbox_rect.y += self.gravity / 20 * dt
        else:
            self.direction.y += self.gravity / 2 * dt
            self.hitbox_rect.y += self.direction.y * dt
            self.direction.y += self.gravity / 2 * dt

        # jump
        if self.jump:
            if self.on_surface['floor']:
                self.direction.y = -self.jump_height
                self.timers["wall slide block"].active
                self.hitbox_rect.bottom -= 1
                # double jump
                self.jump_state = "jumped"
                self.jump_sound.play()
            # wall jump
            elif any((self.on_surface['left'], self.on_surface['right'])) and not self.timers["wall slide block"].active:
                self.timers['wall jump'].activate()
                self.direction.y = -self.jump_height
                self.direction.x = 1 if self.on_surface['left'] else -1
                # double jump
                self.jump_state = "jumped"
                self.jump_sound.play()
            # double jump
            elif self.jump_state == "ready_for_double_jump":
                self.direction.y = -self.jump_height
                self.timers["wall slide block"].active
                self.rect.bottom -= 1
                # double jump
                self.jump_state = "double_jump"
                self.jump_sound.play()
            self.jump = False

        self.collision("vertical")
        self.semi_collision()
        self.rect.center = self.hitbox_rect.center

    def platform_move(self, dt):
        """
        Di chuyển nhân vật cùng với nền di chuyển nếu đang đứng trên đó.
        Phương thức này kiểm tra xem nhân vật có đang đứng trên một nền di chuyển (`self.platform`) hay không.
        Nếu có, vị trí của nhân vật (`self.hitbox_rect`) sẽ được cập nhật theo hướng di chuyển (`self.platform.direction`),
            tốc độ (`self.platform.speed`) của nền di chuyển và khoảng thời gian (`dt`).
            :param dt: Thời gian trôi qua
        """
        if self.platform:
            self.hitbox_rect.topleft += self.platform.direction * self.platform.speed * dt

    def check_contact(self):
        """
        Kiểm tra xem nhân vật đang tiếp xúc với mặt phẳng nào (Dưới, trái phải)
        Phương thức này kiểm tra xem nhân vật đang tiếp xúc với các sprite trong nhóm `collision_sprites` và `semi_collision_sprites`
        để cập nhật thông tin về việc tiếp xúc với mặt phẳng (dưới, trái, phải) trong từ điển `self.on_surface`.
        """
        # Kiểm tra có đang tiếp xúc với mặt phẳng nào hay không (Dưới, trái phải)
        floor_rect = pygame.Rect(self.hitbox_rect.bottomleft, (self.hitbox_rect.width, 2))
        right_rect = pygame.Rect(self.hitbox_rect.topright + vector(0, self.hitbox_rect.height / 4),
                                 (2, self.hitbox_rect.height / 2))
        left_rect = pygame.Rect(self.hitbox_rect.topleft + vector(-2, self.hitbox_rect.height / 4),
                                (2, self.hitbox_rect.height / 2))

        collide_rects = [sprite.rect for sprite in self.collision_sprites]
        semi_collide_rect = [sprite.rect for sprite in self.semi_collision_sprites]
        # collision
        # Kiểm tra đụng độ cho toàn bộ sprite trong list trên
        self.on_surface['floor'] = True if floor_rect.collidelist(collide_rects) >= 0 or floor_rect.collidelist(semi_collide_rect) >= 0 and self.direction.y >= 0 else False
        self.on_surface['right'] = True if right_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface['left'] = True if left_rect.collidelist(collide_rects) >= 0 else False

        self.platform = None
        sprites = self.collision_sprites.sprites() + self.semi_collision_sprites.sprites()
        for sprite in [sprite for sprite in sprites if hasattr(sprite, 'moving')]:
            if sprite.rect.colliderect(floor_rect):
                self.platform = sprite

    def collision(self, axis):
        """
        Xử lý va chạm của nhân vật với các sprite khác theo trục được chỉ định
        Phương thức này kiểm tra va chạm của nhân vật với các sprite trong nhóm `collision_sprites` theo trục
            được cung cấp (`axis`).
        Nếu va chạm xảy ra, vị trí của nhân vật sẽ được điều chỉnh để tránh va chạm
            :param axis: Trục va chạm ("horizontal" hoặc "vertical")
        """
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if axis == "horizontal":
                    # left
                    if self.hitbox_rect.left <= sprite.rect.right and int(self.old_rect.left) >= int(sprite.old_rect.right):
                        self.hitbox_rect.left = sprite.rect.right
                    # right
                    if self.hitbox_rect.right >= sprite.rect.left and int(self.old_rect.right) <= int(sprite.old_rect.left):
                        self.hitbox_rect.right = sprite.rect.left
                else:
                    # top
                    if self.hitbox_rect.top <= sprite.rect.bottom and int(self.old_rect.top) >= int(sprite.old_rect.bottom):
                        self.hitbox_rect.top = sprite.rect.bottom
                        if hasattr(sprite, 'moving'):
                            self.hitbox_rect.top += 5
                    # bottom
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.old_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                    # reset mỗi khi xảy ra va chạm, ngăn không cho gravity tăng tự động
                    self.direction.y = 0

    def semi_collision(self):
        """
        Xử lý va chạm đặc biệt của nhân vật với các sprite trong nhóm `semi_collision_sprites`
        Phương thức này kiểm tra va chạm của nhân vật với các sprite trong nhóm `semi_collision_sprites`
        Khi ấn xuống ở platform, timer sẽ kích hoạt và làm cho platform không hoạt động nữa trong 1 khoảng thời gian
            và hoạt động lại sau một khoản thời gian của timer(khi mà timer của platform đó không hoạt động
        """
        # Mong muốn thực hiện khi mà timer 'platform skip' không active
        # Khi ấn xuống ở platform, timer sẽ kích hoạt và làm cho platform không hoạt động nữa trong 1 khoảng thời gian
        # và hoạt động lại sau một khoản thời gian của timer(khi mà timer của platform đó không hoạt động
        if not self.timers['platform skip'].active:
            for sprite in self.semi_collision_sprites:
                if sprite.rect.colliderect(self.hitbox_rect):
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.old_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                        if self.direction.y > 0:
                            self.direction.y = 0

    def update_timers(self):
        """
        Cập nhật trạng thái của các bộ hẹn giờ cho các hành động của nhân vật
        Phương thức này duyệt qua các bộ hẹn giờ trong từ điển `self.timers` và cập nhật trạng thái của chúng
            (chẳng hạn như đang hoạt động hay đã hết thời gian)
        """
        for timer in self.timers.values():
            timer.update()

    def animate(self, dt):
        """
        Cập nhật hình ảnh hoạt ảnh của nhân vật
        Phương thức này cập nhật khung hình hoạt ảnh hiện tại của nhân vật dựa trên trạng thái hoạt ảnh (`self.state`),
            chỉ số khung hình (`self.frame_index`), tốc độ hoạt ảnh (`ANIMATION_SPEED`), và khoảng thời gian (`dt`).
        Phương thức cũng điều chỉnh hướng hiển thị của hình ảnh hoạt ảnh theo hướng quay của
            nhân vật (`self.facing_right`)
            :param dt: Thời gian trôi qua
        """
        # làm animatrion cho các player
        self.frame_index += ANIMATION_SPEED * dt
        # Nếu mà frame index của hành động attack quá giới hạn thì sẽ lại về trạng thái idle
        if self.state == 'attack' and self.frame_index >= len(self.frames[self.state]):
             self.state = 'idle'
        # Cập nhật image bằng cách chọn 1 frame mới thông qua frames index ( int vì sau phép tính trên sẽ thành dạng float
        # ép kiểu int lại, chia lấy dư cho số lượng frames vì frame_index sẽ tăng mãi mãi và ta lặp lại hoạt ảnh bằng cách chia lấy du
        # khi đó frames được lấy ra chỉ nằm trong khoảng từ 0 đến index của frames cuối
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        # Đổi chiều nhân vật khi quay trái phải
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)

        if self.attacking and self.frame_index > len(self.frames[self.state]):
            self.attacking = False

    def get_state(self):
        """
        Cập nhật trạng thái hoạt ảnh của nhân vật dựa trên thông tin di chuyển và va chạm
        Phương thức này xác định trạng thái hoạt ảnh phù hợp cho nhân vật dựa trên các yếu tố sau:
            `self.on_surface`: Kiểm tra xem nhân vật đang tiếp xúc với mặt phẳng nào (dưới, trái, phải)
            `self.direction.y`: Xác định hướng di chuyển theo chiều dọc (lên, xuống)
            `self.attacking`: Kiểm tra xem nhân vật đang tấn công hay không

        Trạng thái hoạt ảnh được cập nhật cho `self.state`
        """
        if self.on_surface['floor']:
            if self.attacking:
                self.state = 'attack'
            else:
                self.state = 'idle' if self.direction.x == 0 else 'run'
        else:
            if self.attacking:
                self.state = 'air_attack'
            else:
                if any((self.on_surface['left'], self.on_surface['right'])):
                    self.state = 'wall'
                else:
                    self.state = 'jump' if self.direction.y < 0 else 'fall'

    def get_damage(self):
        """
        Giảm máu của nhân vật khi bị va chạm với kẻ thù
        Phương thức này giảm một đơn vị máu của nhân vật (`self.data.health`) và kích hoạt bộ hẹn giờ `self.timers['hit']`
            để quản lý hiệu ứng nhận sát thương (nhấp nháy hình ảnh)
        """
        if not self.timers['hit'].active:
            self.data.health -= 1
            self.timers['hit'].activate()

    def flicker(self):
        """
        Tạo hiệu ứng nhận sát thương cho nhân vật
        Phương thức này sử dụng hàm sin để tạo hiệu ứng nhấp nháy hình ảnh của nhân vật khi bị nhận sát thương.
        Hiệu ứng này chỉ được thực hiện khi bộ hẹn giờ `self.timers['hit']` đang hoạt động
        """
        # khi bị nhận sát thương thì sẽ có hiệu ứng nhận diện
        # Dùng sin để tạo hiệu ứng flicker liên tục
        if self.timers['hit'].active and sin(pygame.time.get_ticks() * 100) >= 0:
            white_mask = pygame.mask.from_surface(self.image)
            white_surf = white_mask.to_surface()
            white_surf.set_colorkey('black')
            self.image = white_surf

    def update(self, dt):
        """
        Cập nhật trạng thái của nhân vật mỗi frame
        Phương thức này được gọi mỗi frame để cập nhật toàn bộ trạng thái của nhân vật, bao gồm:
            Lưu trữ vị trí cũ
            Cập nhật các bộ hẹn giờ
            Kiểm tra input từ người chơi
            Di chuyển nhân vật
            Di chuyển cùng nền di chuyển
            Kiểm tra tiếp xúc với mặt phẳng
            Xác định trạng thái hoạt ảnh
            Cập nhật hình ảnh hoạt ảnh
            Hiệu ứng nhận sát thương
            :param dt: Thời gian trôi qua
        """
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()

        self.input()
        self.move(dt)
        self.platform_move(dt)
        self.check_contact()

        self.get_state()
        self.animate(dt)
        self.flicker()

