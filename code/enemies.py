from settings import *
from random import choice
from timer import Timer


class Tooth(pygame.sprite.Sprite):
	"""
	Lớp mô phỏng Tooth - một loại kẻ thù trong game
	Lớp này kế thừa từ `pygame.sprite.Sprite` để tạo ra một đối tượng enemy (kẻ thù) đại diện cho Tooth.
		Tooth di chuyển qua lại trên màn hình và đổi hướng khi chạm vào cạnh màn hình hoặc các vật thể va chạm được cung cấp
	* Phương thức
	reverse(self): Đảo ngược hướng di chuyển của Tooth (nếu bộ đếm hit_timer cho phép)
	update(self, dt): Cập nhật trạng thái của Tooth (animation, di chuyển, đổi hướng)
	"""
	def __init__(self, pos, frames, groups, collision_sprites):
		"""
		Hàm khởi tạo
			:param pos: Vị trí ban đầu của Tooth trên màn hình (x, y)
			:param frames: Danh sách các khung hình animation (hoạt ảnh) của Tooth
			:param groups: Nhóm sprite (đối tượng) mà Tooth sẽ được thêm vào (dùng cho việc quản lý hiển thị và cập nhật)
			:param collision_sprites: Danh sách các sprite (đối tượng) dùng để kiểm tra va chạm của Tooth
		"""
		super().__init__(groups)
		self.frames, self.frame_index = frames, 0
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_frect(topleft=pos)
		self.z = Z_LAYERS['main']

		self.direction = choice((-1, 1))
		self.collision_rects = [sprite.rect for sprite in collision_sprites]
		self.speed = 200

		self.hit_timer = Timer(250)

	def reverse(self):
		"""
		Đảo ngược hướng di chuyển của Tooth (nếu bộ đếm hit_timer cho phép).
		Phương thức này đảo ngược hướng di chuyển (`direction`) của Tooth sang trái hoặc phải (-1 hoặc 1),
			nhưng chỉ thực hiện khi bộ đếm `hit_timer` không còn hoạt động (không còn tính giờ)
		"""
		if not self.hit_timer.active:
			self.direction *= -1
			self.hit_timer.activate()

	def update(self, dt):
		"""
		Cập nhật trạng thái của Tooth - một loại kẻ thù trong game
		Phương thức này cập nhật vị trí, animation (hoạt ảnh) và hướng di chuyển của Tooth
			:param dt: Khoảng thời gian trôi qua kể từ lần cập nhật trước (delta time)
		"""
		self.hit_timer.update()

		# animate
		self.frame_index += ANIMATION_SPEED * dt
		self.image = self.frames[int(self.frame_index % len(self.frames))]
		# Flip animation khi đổi hướng
		self.image = pygame.transform.flip(self.image, True, False) if self.direction < 0 else self.image

		# move
		self.rect.x += self.direction * self.speed * dt

		# reverse direction
		# Tạo FRect ở dưới chân bên phải và trái để kiểm tra xem kẻ thù đã tới cạnh chưa
		floor_rect_right = pygame.FRect(self.rect.bottomright, (1,1))
		floor_rect_left = pygame.FRect(self.rect.bottomleft, (-1,1))

		# Tạo FReact ở đầu nhân vật và thêm 2 phần ở trái và phải
		wall_rect = pygame.FRect(self.rect.topleft + vector(-1,0), (self.rect.width + 2, 1))

		# Nếu FRect ở dưới chân không va chạm gì hết có nghĩa là kẻ thù đã đến rìa mặt đất và sẽ quay đầu
		# Nều FRect ở trên đầu va chạm với tường thì sẽ làm cho kẻ thù quay đầu
		if floor_rect_right.collidelist(self.collision_rects) < 0 and self.direction > 0 or\
			floor_rect_left.collidelist(self.collision_rects) < 0 and self.direction < 0 or\
			wall_rect.collidelist(self.collision_rects) != -1:
			self.direction *= -1


class Fly(pygame.sprite.Sprite):
	"""
	Lớp mô phỏng Fly - một loại kẻ thù bay trong game
	Lớp này kế thừa từ `pygame.sprite.Sprite` để tạo ra một đối tượng enemy (kẻ thù) đại diện cho Fly.
		Fly bay qua lại trên màn hình và đổi hướng khi chạm vào tường hoặc các vật thể va chạm được cung cấp
	"""
	def __init__(self, pos, frames, groups, collision_sprites):
		"""
		Hàm khởi tạo
			:param pos: Vị trí ban đầu của Fly trên màn hình (x, y)
			:param frames: Danh sách các khung hình animation (hoạt ảnh) của Fly
			:param groups: Nhóm sprite (đối tượng) mà Fly sẽ được thêm vào (dùng cho việc quản lý hiển thị và cập nhật)
			:param collision_sprites: Danh sách các sprite (đối tượng) dùng để kiểm tra va chạm của Fly
		"""
		super().__init__(groups)
		self.frames, self.frame_index = frames, 0
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_frect(topleft=pos)
		self.z = Z_LAYERS['main']

		self.direction = choice((-1, 1))
		self.collision_rects = [sprite.rect for sprite in collision_sprites]
		self.speed = 300

		self.hit_timer = Timer(250)

	def reverse(self):
		"""
		Đảo ngược hướng di chuyển của Fly (nếu bộ đếm hit_timer cho phép).
		Phương thức này đảo ngược hướng di chuyển (`direction`) của Fly sang trái hoặc phải (-1 hoặc 1),
			nhưng chỉ thực hiện khi bộ đếm `hit_timer` không còn hoạt động (không còn tính giờ)
		"""
		if not self.hit_timer.active:
			self.direction *= -1
			self.hit_timer.activate()

	def update(self, dt):
		"""
		Cập nhật trạng thái của Fly - một loại kẻ thù trong game
		Phương thức này cập nhật vị trí, animation (hoạt ảnh) và hướng di chuyển của Fly
			:param dt: Khoảng thời gian trôi qua kể từ lần cập nhật trước (delta time)
		"""
		self.hit_timer.update()

		# animate
		self.frame_index += ANIMATION_SPEED * dt
		self.image = self.frames[int(self.frame_index % len(self.frames))]
		self.image = pygame.transform.flip(self.image, True, False) if self.direction > 0 else self.image

		# move
		self.rect.x += self.direction * self.speed * dt

		# reverse direction
		# Tạo FRect ở bên phải và trái để kiểm tra xem kẻ thù có chạm tường hay vật thể gì không
		wall_rect_right = pygame.FRect(self.rect.midright, (1,1))
		wall_rect_left = pygame.FRect(self.rect.midleft, (-1,1))
		# wall_rect = pygame.FRect(self.rect.topleft + vector(-1,0), (self.rect.width + 2, 1))
		# Nếu là FRect va chạm gì đó có nghĩa là kẻ thù đã chạm tường và sẽ quay đầu
		if wall_rect_right.collidelist(self.collision_rects) > 0 and self.direction > 0 or\
			wall_rect_left.collidelist(self.collision_rects) > 0 and self.direction < 0:
		#    wall_rect.collidelist(self.collision_rects) != -1:
			self.direction *= -1


class Shell(pygame.sprite.Sprite):
	"""
	Lớp mô phỏng Shell - một loại kẻ thù trong game
	Lớp này kế thừa từ `pygame.sprite.Sprite` để tạo ra một đối tượng enemy (kẻ thù) đại diện cho Shell. Shell có thể
		bắn ngọc (pearl) theo hướng quay của nó
	* Phương thức
	state_management(): Quản lý trạng thái hoạt động của Shell ("idle" hoặc "fire").
	update(dt): Cập nhật trạng thái của Shell (animation, trạng thái, bắn ngọc).
	"""
	def __init__(self, pos, frames, groups, reverse, player, create_pearl):
		"""
		Hàm khởi tạo
			:param pos: Vị trí ban đầu của Shell trên màn hình (x, y)
			:param frames: Từ điển chứa các khung hình animation (hoạt ảnh) của Shell theo trạng thái ("idle" hoặc "fire")
			:param groups: Nhóm sprite (đối tượng) mà Shell sẽ được thêm vào (dùng cho việc quản lý hiển thị và cập nhật)
			:param reverse: Kiểm tra xem Shell có cần quay ngược các animation và hướng bắn hay không.
				True để quay ngược, False để giữ nguyên
			:param player: Tham chiếu đến đối tượng người chơi
			:param create_pearl: Hàm dùng để tạo ra một viên ngọc (pearl)
		"""
		super().__init__(groups)
		# Nếu mà Shell có reverse thì sẽ quay shell theo hướng ngược lại và đặt hướng đạn theo hướng quay
		if reverse:
			self.frames = {}
			for key, surfs in frames.items():
				self.frames[key] = [pygame.transform.flip(surf, True, False) for surf in surfs]
			self.bullet_direction = -1
		else:
			self.frames = frames
			self.bullet_direction = 1

		self.frame_index = 0
		self.state = "idle"
		self.image = self.frames[self.state][self.frame_index]
		self.rect = self.image.get_frect(topleft=pos)
		self.old_rect = self.rect.copy()
		self.z = Z_LAYERS["main"]
		self.player = player
		self.shoot_timer = Timer(3000)
		self.has_fired = False
		self.create_pearl = create_pearl

	def state_management(self):
		"""
		Quản lý trạng thái hoạt động của Shell ("idle" hoặc "fire")
		Phương thức này kiểm tra xem Shell có nên chuyển sang trạng thái "fire" (bắn ngọc) hay không dựa trên
			vị trí của người chơi so với Shell
		"""
		# Quản lí trạng thái: idle hoặc là fire
		# fire:
		# 1. Nếu người chơi nằm trong vòng tấn công
		# 2. Người chơi nằm ngang với shell
		# 3. Người chơi nằm ở trước mặt shell ( nếu shell quay phải thì sẽ bắn nếu người chơi nằm bên phải và ngược lại)
		player_pos, shell_pos = vector(self.player.hitbox_rect.center), vector(self.rect.center)
		# Kiểm tra trong vòng
		# Nếu mà hướng đạn bên phải và tạo độ x của người chơi lớn hơn tạo độ x của shell thì sẽ là nằm trước mặt
		player_near = shell_pos.distance_to(player_pos) < 500
		# Kiểm tra trước mặt
		player_front = shell_pos.x < player_pos.x if self.bullet_direction > 0 else shell_pos.x > player_pos.x
		# Kiểm tra nằm ở cùng hàng ngang
		player_level = abs(shell_pos.y - player_pos.y) < 30

		# Nếu thỏa các điều kiện trên và shell không nằm trong thời gian bắn thì sẽ được bắn
		if player_near and player_front and player_level and not self.shoot_timer.active:
			self.state = 'fire'
			self.frame_index = 0
			self.shoot_timer.activate()

	def update(self, dt):
		"""
		Cập nhật trạng thái của Shell
		Phương thức này cập nhật animation (hoạt ảnh), trạng thái và hành động bắn ngọc của Shell
			:param dt: Thời gian trôi qua
		"""
		self.shoot_timer.update()
		self.state_management()

		# animation / attack
		self.frame_index += ANIMATION_SPEED * dt
		# Mong muốn animation là sau khi fire xong sẽ quay về idle
		if self.frame_index < len(self.frames[self.state]):
			self.image = self.frames[self.state][int(self.frame_index)]

			# fire
			# Mong muốn bắn pearl ở frame thứ 3 của animation và khi mà đang ở trạng thái không bắn
			if self.state == 'fire' and int(self.frame_index) == 3 and not self.has_fired:
				self.create_pearl(self.rect.center, self.bullet_direction)
				self.has_fired = True

		else:
			self.frame_index = 0
			if self.state == 'fire':
				self.state = 'idle'
				self.has_fired = False


class Pearl(pygame.sprite.Sprite):
	"""
	Lớp mô phỏng Pearl - đạn được bắn ra từ Shell
	Lớp này kế thừa từ `pygame.sprite.Sprite` để tạo ra một Pearl (đạn) di chuyển trên màn hình
		Pearl di chuyển theo hướng được bắn ra từ Shell cho đến khi hết thời gian tồn tại
	* Phương thức
	reverse(self): Đảo ngược hướng bay của Pearl (nếu bộ đếm 'reverse' cho phép)
	update(self, dt): Cập nhật trạng thái của viên ngọc (di chuyển, kiểm tra thời gian tồn tại)
	"""
	def __init__(self, pos, groups, surf, direction, speed):
		"""
		Hàm khởi tạo
			:param pos: Vị trí ban đầu của pearl trên màn hình (x, y)
			:param groups:  Nhóm sprite (đối tượng) mà pearl sẽ được thêm vào (dùng cho việc quản lý hiển thị và cập nhật)
			:param surf: Hình ảnh đại diện cho pearl
			:param direction: Hướng bay của pearl (-1: trái, 1: phải)
			:param speed: Tốc độ bay của pearl
		"""
		self.pearl = True
		super().__init__(groups)
		self.image = surf
		self.rect = self.image.get_frect(center=pos + vector(50 * direction, 0))
		self.direction = direction
		self.speed = speed
		self.z = Z_LAYERS['main']
		self.timers = {
			'lifetime': Timer(5000),
			'reverse': Timer(250)
		}
		self.timers['lifetime'].activate()

	def reverse(self):
		"""
		Đảo ngược hướng di chuyển của Pearl (nếu bộ đếm hit_timer cho phép).
		Phương thức này đảo ngược hướng di chuyển (`direction`) của pearl sang trái hoặc phải (-1 hoặc 1),
			nhưng chỉ thực hiện khi bộ đếm `hit_timer` không còn hoạt động (không còn tính giờ)
		"""
		if not self.timers['reverse'].active:
			self.direction *= -1
			self.timers['reverse'].activate()

	def update(self, dt):
		"""
		Cập nhật trạng thái của Pearl
		Phương thức này cập nhật vị trí và kiểm tra tuổi thọ của Pearl
			:param dt: Thời gian trôi qua
		"""
		for timer in self.timers.values():
			timer.update()

		# Pearl sẽ di chuyển theo hướng được bắn ra
		self.rect.x += self.direction * self.speed * dt
		# Sau khi pearl được bắn một khoảng thời gian thì sẽ xóa đi pearl (Trigger bằng việt timers['lifetime'] không chạy nữa
		if not self.timers['lifetime'].active:
			self.kill()