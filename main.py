from pygame import *
import random

# Инициализация Pygame
init()
mixer.init()

# Окно игры
window = display.set_mode((700, 500))
display.set_caption('Арканоид')

# Музыка и звуки
mixer.music.load('space.ogg')
mixer.music.play(-1)
shot = mixer.Sound('fire.ogg')

# Шрифты
font = font.SysFont(None, 36)

# Фон
background = transform.scale(image.load("galaxy.jpg"), (700, 500))

# Глобальные переменные
missed_ufos = 0
destroyed_ufos = 0
game_result = None  # None, "win", "lose"


class GameSprite(sprite.Sprite):
    def __init__(self, image_path, x, y, speed, size=(70, 70)):
        super().__init__()
        self.image = transform.scale(image.load(image_path), size)
        self.speed = speed
        self.rect = self.image.get_rect(center=(x, y))

    def reset(self):
        window.blit(self.image, self.rect.topleft)


class Player(GameSprite):
    def __init__(self, image_path, x, y, speed):
        super().__init__(image_path, x, y, speed)
        self.bullet_available = True

    def update(self):
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < 630:
            self.rect.x += self.speed
        if keys[K_w] and self.rect.y > 0:
            self.rect.y -= self.speed
        if keys[K_s] and self.rect.y < 430:
            self.rect.y += self.speed
        if keys[K_SPACE]:
            self.fire()

    def fire(self):
        if self.bullet_available:
            shells.add(Bullet("bullet.png", self.rect.centerx, self.rect.top, 15))
            shot.play()
            self.bullet_available = False

    def reload(self):
        self.bullet_available = True


class Enemy(GameSprite):
    def __init__(self, image_path, x, y, speed):
        super().__init__(image_path, x, y, speed, (90, 70))

    def respawn(self):
        self.rect.x = random.randint(5, 630)
        self.rect.y = random.randint(-100, -5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > 500:
            self.respawn()
            return True
        return False


class Bullet(GameSprite):
    def __init__(self, image_path, x, y, speed):
        super().__init__(image_path, x, y, speed, (20, 20))

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < -10:
            self.kill()
            player.reload()


class Asteroid(GameSprite):
    def __init__(self, image_path, x, y, speed, direction):
        super().__init__(image_path, x, y, speed, (50, 50))
        self.direction = direction
        self.respawn()

    def respawn(self):
        if self.direction == "down":
            self.rect.x = random.randint(0, 650)
            self.rect.y = random.randint(-100, -5)
        elif self.direction == "right":
            self.rect.x = random.randint(-100, -5)
            self.rect.y = random.randint(0, 450)
        elif self.direction == "left":
            self.rect.x = random.randint(700, 750)
            self.rect.y = random.randint(0, 450)

    def update(self):
        if self.direction == "down":
            self.rect.y += self.speed
            if self.rect.y > 500:
                self.respawn()
        elif self.direction == "right":
            self.rect.x += self.speed
            if self.rect.x > 700:
                self.respawn()
        elif self.direction == "left":
            self.rect.x -= self.speed
            if self.rect.x < -50:
                self.respawn()


# Создание объектов
player = Player("rocket.png", 300, 420, 5)
shells = sprite.Group()
asteroids = sprite.Group()
ufoses = sprite.Group()

for i in range(5):
    ufoses.add(Enemy("ufo.png", random.randint(5, 620), random.randint(-100, -5), 1))

for i in range(3):
    asteroids.add(Asteroid("asteroid.png", 0, 0, random.randint(2, 3), random.choice(["down", "right", "left"])))


clock = time.Clock()
running = True

while running:
    window.blit(background, (0, 0))

    for e in event.get():
        if e.type == QUIT:
            running = False

    player.update()
    ufoses.update()
    shells.update()
    asteroids.update()

    ufoses.draw(window)
    asteroids.draw(window)
    shells.draw(window)
    player.reset()

    # Проверка столкновений пуль с врагами
    for bullet in shells:
        hit_enemies = sprite.spritecollide(bullet, ufoses, False)
        if hit_enemies:
            bullet.kill()
            hit_enemies[0].respawn()
            destroyed_ufos += 1
            player.reload()

    # Проверка условий поражения или победы
    if sprite.spritecollideany(player, asteroids) or missed_ufos > 20:
        game_result = "lose"
        running = False
    elif destroyed_ufos > 50:
        game_result = "win"
        running = False

    # Проверка выхода врагов за границу экрана
    for enemy in ufoses:
        if enemy.update():
            missed_ufos += 1

    # Отображение статистики
    window.blit(font.render(f"Пропущено: {missed_ufos}", True, (255, 255, 255)), (10, 40))
    window.blit(font.render(f"Счет: {destroyed_ufos}", True, (255, 255, 255)), (10, 10))

    display.update()
    clock.tick(60)

# Экран окончания игры
game_over = True
while game_over:
    for e in event.get():
        if e.type == QUIT:
            game_over = False

    window.blit(background, (0, 0))

    # Значение по умолчанию
    text = font.render("Игра окончена", True, (255, 255, 255))

    if game_result == "lose":
        text = font.render("Поражение", True, (255, 0, 0))
    elif game_result == "win":
        text = font.render("Победа!", True, (0, 255, 0))

    window.blit(text, (270, 250))
    display.update()
    clock.tick(60)
