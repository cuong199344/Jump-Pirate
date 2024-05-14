from settings import *
from sprites import Sprite, MovingSprite, AnimatedSprite, Spike, Item, ParticleEffectSprite
from player import Player
from groups import AllSprites
from enemies import Tooth, Fly, Shell, Pearl

from random import uniform
class Level:
    """
    Đại diện cho một màn chơi trong game Jump Pirate.
    Lớp này chịu trách nhiệm quản lý các thành phần, đối tượng, logic va chạm và cập nhật của một màn chơi
    * Phương thức
    setup(tmx_map, level_frames, audio_files):Thiết lập level dựa trên dữ liệu từ TMX map, hình ảnh và âm thanh
    create_pearl(pos, direction): Tạo một sprite 'pearl' mới
    pearl_collision(): Xử lý va chạm giữa 'pearl' với các sprite khác (xóa 'pearl' khi va chạm)
    hit_collision(): Xử lý va chạm giữa người chơi với các sprite gây sát thương
    item_collision(): Xử lý va chạm giữa người chơi với các sprite item (kích hoạt item và xóa).
    attack_collision(): Xử lý va chạm giữa đòn tấn công của người chơi với các enemy 'fly', 'tooth' và 'pearl'
        (đảo ngược hướng di chuyển của enemy hoặc xóa 'pearl').
    check_constraint(): Kiểm tra các ràng buộc của người chơi trong màn chơi (giới hạn trái phải, rơi xuống hoặc chạm đích).
    run(dt): Cập nhật và hiển thị màn chơi.
    """
    def __init__(self, tmx_map, level_frames, audio_files, data, switch_stage):
        """
        Hàm khởi tạo
        Khởi tạo một đối tượng Level mới, đại diện cho một màn chơi trong game Jump Pirate
        Phương thức này được gọi khi tạo một đối tượng Level. Nó thực hiện các bước sau để thiết lập level:
            Lưu trữ tham chiếu đến các đối tượng cần thiết
            Khởi tạo các thuộc tính của level
            Xử lý dữ liệu level từ TMX map
            Khởi tạo các nhóm sprite
            Khởi tạo các thuộc tính khác
            Gọi phương thức setup để thiết lập chi tiết level dựa trên TMX map, hình ảnh và âm thanh
            Khởi tạo các âm thanh
            :param tmx_map: Đối tượng TMX map chứa dữ liệu cấu trúc của màn chơi
            :param level_frames: Từ điển chứa các frame ảnh đại diện cho các sprite trong màn chơi
            :param audio_files: Từ điển chứa các file âm thanh được sử dụng trong màn chơi
            :param data: Từ điển chứa các file âm thanh được sử dụng trong màn chơi
            :param switch_stage: Hàm để chuyển đổi giữa các màn chơi (overworld, level)
        """
        self.display_surface = pygame.display.get_surface()
        self.data = data
        self.switch_stage = switch_stage

        # level data
        self.level_width = tmx_map.width * TILE_SIZE
        # level height
        self.level_bottom = tmx_map.height * TILE_SIZE
        tmx_level_properties = tmx_map.get_layer_by_name('Data')[0].properties
        self.level_unlock = tmx_level_properties['level_unlock']

        if tmx_level_properties['bg']:
            bg_tile = level_frames['bg_tiles'][tmx_level_properties['bg']]
        else:
            bg_tile = None

        # groups
        self.all_sprites = AllSprites(
            width=tmx_map.width,
            height=tmx_map.height,
            bg_tile=bg_tile,
            top_limit=tmx_level_properties['top_limit'],
            clouds={'large': level_frames['cloud_large'], 'small': level_frames['cloud_small']},
            horizon_line=tmx_level_properties['horizon_line']
        )
        # Nhóm sprite kiểm tra đụng độ
        self.collision_sprites = pygame.sprite.Group()
        # Semi collision
        self.semi_collision_sprites = pygame.sprite.Group()

        self.damage_sprites = pygame.sprite.Group()

        # enemies
        self.tooth_sprites = pygame.sprite.Group()
        self.fly_sprites = pygame.sprite.Group()
        self.pearl_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()

        # frames
        self.pearl_surf = level_frames['pearl']
        self.particle_frames = level_frames['particle']

        self.setup(tmx_map, level_frames, audio_files)

        # audio
        self.coin_sound = audio_files['coin']
        self.coin_sound.set_volume(0.2)
        self.damage_sound = audio_files['damage']
        self.damage_sound.set_volume(0.5)
        self.pearl_sound = audio_files['pearl']
        self.pearl_sound.set_volume(1.5)

    def setup(self, tmx_map, level_frames, audio_files):
        """
        Thiết lập chi tiết cho level dựa trên dữ liệu từ TMX map, hình ảnh và âm thanh
        Phương thức này được gọi sau khi khởi tạo level để sắp xếp các thành phần (sprite, nhóm sprite) theo đúng
            cấu trúc của màn chơi
        Các bước thực hiện:
            Xử lý tile: Duyệt qua các layer 'BG', 'Terrain', 'FG', và 'Platforms' trong TMX map.
            Xử lý chi tiết nền: Duyệt qua các object trong layer 'BG details' của TMX map.
            Xử lý nhân vật và object: Duyệt qua các object trong layer 'Objects' của TMX map.
                Nếu object có tên là "player":
                    Khởi tạo đối tượng `Player` với đầy đủ các thuộc tính và phương thức cần thiết
                Nếu object có tên là "barrel", "crate", hoặc "door":
                    Tạo `Sprite` cho các object này và thêm vào nhóm `all_sprites` và `collision_sprites`
                Nếu là các object khác:
                    Xác định frame ảnh đại diện cho object dựa vào tên trong `level_frames`
                    Lật ngược animation cho object 'floor_spike' nếu được đánh dấu 'inverted' trong TMX map
                    Xác định các nhóm sprite phù hợp để thêm object (ví dụ: `semi_collision_sprites` cho 'palm')
                    Xác định layer (z-index) để hiển thị theo thứ tự
                    Tạo `AnimatedSprite` với tốc độ animation khác nhau (trừ trường hợp 'palm')
                Nếu object có tên là 'flag':
                    Lưu trữ vùng va chạm của cờ (để kiểm tra win condition)
            Xử lý object chuyển động: Duyệt qua các object trong layer 'Moving Objects' của TMX map
                Nếu object có tên là 'spike':
                    Khởi tạo đối tượng `Spike` với các thuộc tính
                    Thêm `Spike` vào nhóm `all_sprites` và `damage_sprites`
                    Vẽ thêm các chấm nối từ tâm đến đầu nhọn của 'spike' để dễ quan sát
                Nếu là các object chuyển động khác:
                    Xác định frame ảnh đại diện cho object
                    Xác định nhóm sprite phù hợp dựa vào thuộc tính 'platform' trong TMX map
                    Tính toán điểm bắt đầu và kết thúc của đường di chuyển
                    Xác định hướng di chuyển và tốc độ
                    Khởi tạo đối tượng `MovingSprite` để điều khiển chuyển động của object
                    Vẽ đường di chuyển của object (nếu cần thiết, ví dụ: 'saw')
            Xử lý enemy: Duyệt qua các object trong layer 'Enemies' của TMX map.
            Xử lý item: Duyệt qua các object trong layer 'Items' của TMX map.
            :param tmx_map: Đối tượng TMX map chứa dữ liệu cấu trúc của màn chơi
            :param level_frames: Từ điển chứa các frame ảnh đại diện cho các sprite trong màn chơi
            :param audio_files: Từ điển chứa các file âm thanh được sử dụng trong màn chơi
        """
        # Load tiles
        for layer in ['BG', 'Terrain', 'FG', 'Platforms']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == 'Terrain':
                    groups.append(self.collision_sprites)
                if layer == 'Platforms':
                    groups.append(self.semi_collision_sprites)
                match layer:
                    case 'BG':
                        z = Z_LAYERS['bg tiles']
                    case 'FG':
                        z = Z_LAYERS['bg tiles']
                    case _:
                        z = Z_LAYERS['main']
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, groups, z)

        # Load bg details
        for obj in tmx_map.get_layer_by_name('BG details'):
            # Nếu tên là static thì chỉ load object, nếu có tên thì sẽ load animation
            if obj.name == 'static':
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, z=Z_LAYERS['bg tiles'])
            else:
                AnimatedSprite((obj.x, obj.y), level_frames[obj.name], self.all_sprites, Z_LAYERS['bg tiles'])
                # light effect cho candle
                if obj.name == 'candle':
                    AnimatedSprite((obj.x, obj.y) + vector(-20, -20), level_frames['candle_light'], self.all_sprites,
                                   Z_LAYERS['bg tiles'])

        # Load player/object
        for obj in tmx_map.get_layer_by_name('Objects'):
            if obj.name == "player":
                self.player = Player(
                    pos=(obj.x, obj.y),
                    groups=self.all_sprites,
                    collision_sprites=self.collision_sprites,
                    semi_collision_sprites=self.semi_collision_sprites,
                    frames=level_frames['player'],
                    data=self.data,
                    attack_sound=audio_files['attack'],
                    jump_sound=audio_files['jump'],
                )
            else:
                if obj.name in ("barrel", "crate", "door"):
                    Sprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
                else:
                    # frames
                    # load các object và các frames tương tứng, riêng palm vì có nhiều biến thể nhưng chung một dạng là palm
                    # nên sẽ được load riêng
                    frames = level_frames[obj.name] if not 'palm' in obj.name else level_frames['palms'][obj.name]
                    # Kiểm tra xem spike có ở trên trần hay không
                    if obj.name == 'floor_spike' and obj.properties['inverted']:
                        # flip spike
                        frames = [pygame.transform.flip(frame, False, True) for frame in frames]

                    # groups
                    groups = [self.all_sprites]
                    # Nếu palm không phải bg thì cho có thể nhảy lên được
                    if obj.name in ('palm_small', 'palm_large'): groups.append(self.semi_collision_sprites)
                    if obj.name in ('saw', 'floor_spike'): groups.append(self.damage_sprites)

                    # z index
                    z = Z_LAYERS['main'] if not 'bg' in obj.name else Z_LAYERS['bg details']

                    # Làm cho các hoạt ảnh object có tốc độ khác nhau
                    animation_speed = ANIMATION_SPEED if not 'palm' in obj.name else ANIMATION_SPEED + uniform(-1, 1)
                    AnimatedSprite((obj.x, obj.y), frames, groups, z, animation_speed)
            if obj.name == 'flag':
                self.level_finish_rect = pygame.FRect((obj.x, obj.y), (obj.width, obj.height))

        # Load moving object
        for obj in tmx_map.get_layer_by_name('Moving Objects'):
            if obj.name == 'spike':
                Spike(
                    pos=(obj.x + obj.width / 2, obj.y + obj.height / 2),
                    surf=level_frames['spike'],
                    radius=obj.properties['radius'],
                    speed=obj.properties['speed'],
                    start_angle=obj.properties['start_angle'],
                    end_angle=obj.properties['end_angle'],
                    groups=(self.all_sprites, self.damage_sprites))
                # vẽ chấm từ tâm đến spike để giúp người chơi nhìn đễ hơn
                for radius in range(0, obj.properties['radius'], 20):
                    Spike(
                        pos=(obj.x + obj.width / 2, obj.y + obj.height / 2),
                        surf=level_frames['spike_chain'],
                        radius=radius,
                        speed=obj.properties['speed'],
                        start_angle=obj.properties['start_angle'],
                        end_angle=obj.properties['end_angle'],
                        groups=self.all_sprites,
                        z=Z_LAYERS['bg details'])
            else:
                frames = level_frames[obj.name]
                groups = (self.all_sprites, self.semi_collision_sprites) if obj.properties['platform'] else (
                self.all_sprites, self.damage_sprites)
                # Lấy điểm giữa (đầu và cuối) của vật di chuyển
                if obj.width > obj.height:  # horizontal
                    move_dir = 'x'
                    start_pos = (obj.x, obj.y + obj.height / 2)
                    end_pos = (obj.x + obj.width, obj.y + obj.height / 2)
                else:  # vertical
                    move_dir = 'y'
                    start_pos = (obj.x + obj.width / 2, obj.y)
                    end_pos = (obj.x + obj.width / 2, obj.y + obj.height)
                speed = obj.properties['speed']
                MovingSprite(frames, groups, start_pos, end_pos, move_dir, speed, obj.properties['flip'])
                if obj.name == 'saw':
                    # Kiểm tra hướng đi của saw để flip animation khi đi ngược lại
                    # Vẽ đường di chuyển của saw để người chơi biết cận trái phải hoặc trên dưới của vậy cản
                    # kiểm tra chiều ngang
                    if move_dir == 'x':
                        y = start_pos[1] - level_frames['saw_chain'].get_height() / 2
                        left, right = int(start_pos[0]), int(end_pos[0])
                        for x in range(left, right, 20):
                            Sprite((x, y), level_frames['saw_chain'], self.all_sprites, Z_LAYERS['bg details'])
                    # Kiểm tra chiều dọc
                    else:
                        x = start_pos[0] - level_frames['saw_chain'].get_width() / 2
                        top, bottom = int(start_pos[1]), int(end_pos[1])
                        for y in range(top, bottom, 20):
                            Sprite((x, y), level_frames['saw_chain'], self.all_sprites, Z_LAYERS['bg details'])

        # Load enemies
        for obj in tmx_map.get_layer_by_name('Enemies'):
            if obj.name == 'tooth':
                Tooth((obj.x, obj.y), level_frames['tooth'],
                      (self.all_sprites, self.damage_sprites, self.tooth_sprites), self.collision_sprites)
            if obj.name == 'shell':
                Shell(
                    pos=(obj.x, obj.y),
                    frames=level_frames['shell'],
                    # Để có thể đứng lên top shell thì groups chọn collison_sprites để sprites có collision
                    groups=(self.all_sprites, self.collision_sprites),
                    reverse=obj.properties['reverse'],
                    player=self.player,
                    # Lớp pearl chỉ được tạo khi có shell
                    create_pearl = self.create_pearl
                    )
            if obj.name == 'fly':
                Fly((obj.x, obj.y), level_frames['fly'],
                      (self.all_sprites, self.damage_sprites, self.fly_sprites), self.collision_sprites)

        # Load items
        for obj in tmx_map.get_layer_by_name('Items'):
            # Lấy vị trí nằm ở chính giữa 1 tile
            Item(obj.name, (obj.x + TILE_SIZE / 2, obj.y + TILE_SIZE / 2), level_frames['items'][obj.name],
                 (self.all_sprites, self.item_sprites), self.data)

        # Load water
        for obj in tmx_map.get_layer_by_name('Water'):
            rows = int(obj.height / TILE_SIZE)
            cols = int(obj.width / TILE_SIZE)
            for row in range(rows):
                for col in range(cols):
                    x = obj.x + col * TILE_SIZE
                    y = obj.y + row * TILE_SIZE
                    # Nếu là hàng đầu thì sẽ thêm animation, các hàng khác không cần
                    if row == 0:
                        AnimatedSprite((x, y), level_frames['water_top'], self.all_sprites, Z_LAYERS['water'])
                    else:
                        Sprite((x, y), level_frames['water_body'], self.all_sprites, Z_LAYERS['water'])

    def create_pearl(self, pos, direction):
        """
        Tạo một sprite 'pearl' mới và thêm vào level
        Phương thức này được gọi bởi enemy 'shell' để bắn ra 'pearl' theo hướng nhất định
            :param pos:
            :param direction:
        """
        Pearl(pos, (self.all_sprites, self.damage_sprites, self.pearl_sprites), self.pearl_surf, direction, 150)
        self.pearl_sound.play()

    def pearl_collision(self):
        """
        Xử lý va chạm giữa 'pearl' với các sprite khác trong level
        Phương thức này kiểm tra va chạm giữa tất cả các sprite trong nhóm `collision_sprites` với nhóm
            `pearl_sprites`. Khi va chạm xảy ra, 'pearl' sẽ bị xóa và tạo hiệu ứng hạt
        """
        # khi pearl gặp vật cản không phải người thì sẽ bị xóa
        for sprite in self.collision_sprites:
            sprite = pygame.sprite.spritecollide(sprite, self.pearl_sprites, True)
            if sprite:
                ParticleEffectSprite((sprite[0].rect.center), self.particle_frames, self.all_sprites)

    def hit_collision(self):
        """
        Xử lý va chạm giữa người chơi và các sprite gây sát thương trong level.
        Phương thức này kiểm tra va chạm giữa `hitbox_rect` của người chơi với các sprite trong nhóm `damage_sprites`.
        Khi va chạm xảy ra, người chơi sẽ nhận sát thương, âm thanh va chạm được phát và sprite gây sát thương có thể bị
            xóa (nếu là 'pearl' dính vào người chơi)
        """
        # Hàm kiểm tra khi người chơi bị gây sát thương
        for sprite in self.damage_sprites:
            if sprite.rect.colliderect(self.player.hitbox_rect):
                self.player.get_damage()
                self.damage_sound.play()
                # nếu mà pearl dính người chơi thì sẽ bị xóa đi
                if hasattr(sprite, 'pearl'):
                    sprite.kill()
                    ParticleEffectSprite((sprite.rect.center), self.particle_frames, self.all_sprites)

    def item_collision(self):
        """
        Xử lý va chạm giữa người chơi và các sprite item trong level.
        Phương thức này kiểm tra va chạm giữa `hitbox_rect` của người chơi với các sprite trong nhóm `item_sprites`.
        Khi va chạm xảy ra:
            Item va chạm sẽ được kích hoạt (thực hiện chức năng của nó).
            Item va chạm sẽ bị xóa khỏi level.
            Hiệu ứng hạt được tạo ra tại vị trí của item.
            Âm thanh thu thập coin được phát.
        :return:
        """
        # Kiểm ra xem người chơi có chạm vào items hay không, nếu có thì sẽ thực hiện điều ứng với items ố và làm nó biến mất
        if self.item_sprites:
            item_sprites = pygame.sprite.spritecollide(self.player, self.item_sprites, True)
            if item_sprites:
                item_sprites[0].activate()
                ParticleEffectSprite((item_sprites[0].rect.center), self.particle_frames, self.all_sprites)
                self.coin_sound.play()

    def attack_collision(self):
        """
        Xử lý va chạm tấn công giữa người chơi và các sprite enemy trong level
        Phương thức này kiểm tra va chạm giữa `hitbox_rect` của người chơi với các sprite trong nhóm `pearl_sprites`,
            `tooth_sprites` và `fly_sprites`. Khi va chạm xảy ra và đáp ứng các điều kiện sau:
            Người chơi đang tấn công
            Người chơi đang đối mặt với mục tiêu (được xác định dựa trên hướng di chuyển của người chơi và vị trí của mục tiêu).
        Phương thức sẽ thực hiện các hành động sau:
            Đảo ngược hướng di chuyển của mục tiêu enemy (khiến nó đi ngược lại)
        """
        # Có khả năng đánh fly và tooth để đi ngược lại, đánh pearl thì pearl sẽ mất
        for target in self.pearl_sprites.sprites() + self.tooth_sprites.sprites() + self.fly_sprites.sprites():
            # Chỉ thực hiện khi người chơi va chạm với vật, đang đánh và đối mặt với mục tiêu
            # Nếu vị trí của người chơi < vị trí vật và người chơi quay phải thì người chơi đang đối mặtvowisi mục tiêu và ngược lại
            facing_target = self.player.rect.centerx < target.rect.centerx and self.player.facing_right or \
                            self.player.rect.centerx > target.rect.centerx and not self.player.facing_right
            if target.rect.colliderect(self.player.rect) and self.player.attacking and facing_target:
                target.reverse()

    def check_constraint(self):
        """
        Kiểm tra các ràng buộc di chuyển của người chơi trong level
        Phương thức này đảm bảo người chơi không đi ra ngoài vùng hiển thị của level và xử lý các điều kiện thắng thua
        """
        # left right
        if self.player.hitbox_rect.left <= 0:
            self.player.hitbox_rect.left = 0
        if self.player.hitbox_rect.right >= self.level_width:
            self.player.hitbox_rect.right = self.level_width

        # bottom border
        if self.player.hitbox_rect.bottom > self.level_bottom:
            self.switch_stage('overworld', -1)

        # success
        if self.player.hitbox_rect.colliderect(self.level_finish_rect):
            print("success")
            self.switch_stage('overworld', self.level_unlock)

    def run(self, dt):
        """
        Cập nhật và hiển thị level
        Phương thức này thực hiện các hành động chính để chạy level, bao gồm:
            Tô nền cho màn hình hiển thị ("gray").
            Cập nhật tất cả sprite trong nhóm `all_sprites` dựa trên `dt` (delta time).
            Kiểm tra va chạm giữa "pearl" và các sprite khác, xử lý va chạm.
            Kiểm tra va chạm giữa người chơi và các sprite gây sát thương, xử lý sát thương.
            Kiểm tra va chạm giữa người chơi và các sprite item, xử lý item và hiệu ứng.
            Kiểm tra va chạm tấn công giữa người chơi và các enemy, xử lý hướng di chuyển của enemy.
            Kiểm tra các ràng buộc di chuyển của người chơi trong level.
            Vẽ tất cả sprite trong nhóm `all_sprites` với tâm là `hitbox_rect.center` của người chơi và
                theo `dt` (delta time) để tạo hiệu ứng mượt mà.
            :param dt: Thời gian trôi qua
        """
        self.display_surface.fill("gray")

        self.all_sprites.update(dt)
        self.pearl_collision()
        self.hit_collision()
        self.item_collision()
        self.attack_collision()
        self.check_constraint()

        self.all_sprites.draw(self.player.hitbox_rect.center, dt)



