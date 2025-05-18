from pygame import *
from random import randint
from time import time as get_time

# Константы
SPRITE_SIZE = 65
SCREEN_SIZE = (700, 500)
WHITE = (255, 255, 255)

font.init()

# Функция для отображения текста
def show_text(x, y, text, color, fsize=30):
    label = font.SysFont('Arial', fsize).render(text, True, color)
    window.blit(label, (x, y))

# Класс для счетчиков
class Counter: 
    def __init__(self, x, y, text, font_size=20):
        self.pos = (x, y)
        self.text = text
        self.count = 0
        self.font = font.SysFont('Arial', font_size)
        self.render()

    def render(self):
        self.image = self.font.render(self.text + str(self.count), True, WHITE)

    def show(self):
        window.blit(self.image, self.pos)

# Создание счетчиков
missed_count = Counter(10, 10, 'Пропущено: ')
kill_count = Counter(10, 52, 'Убито: ')
lives_count = Counter(10, 94, 'Жизни: ')
lives_count.count = 3

# Базовый класс для спрайтов
class GameSprite(sprite.Sprite):
    def __init__(self, x, y, image_name, speed, scale=1):
        super().__init__()
        self.image = transform.scale(image.load(image_name), (SPRITE_SIZE // scale, SPRITE_SIZE // scale))
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def show(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# Класс для врагов
class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= SCREEN_SIZE[1]:
            missed_count.count += 1
            missed_count.render()
            self.rect.y = 0
            self.rect.x = randint(0, SCREEN_SIZE[0] - SPRITE_SIZE)
        self.show()

# Класс для пули
class Bullet(GameSprite):
    def __init__(self, x, y, image_name, speed, scale):
        super().__init__(x, y, image_name, speed, scale)
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()

# Класс для босса
class Boss(GameSprite):
    def __init__(self, x, y, image_name, speed):
        super().__init__(x, y, image_name, speed, scale=1)
        self.last_shoot_time = 0
        self.health = 3  # Добавляем здоровье боссу
        self.phrase = "Ты не пройдешь мге!"

    def update(self):
        # Двигаем босса из стороны в сторону
        if self.rect.x <= 0 or self.rect.x >= SCREEN_SIZE[0] - SPRITE_SIZE:
            self.speed = -self.speed
        self.rect.x += self.speed

        # Стреляем в игрока
        if get_time() - self.last_shoot_time >= 1:
            self.shoot()
            self.last_shoot_time = get_time()

        self.show()
        #Отображение фразы
        show_text(self.rect.x - 40, self.rect.y - 30, self.phrase, WHITE, 15)

    def shoot(self):
        boss_bullet = Bullet(self.rect.x + SPRITE_SIZE//2 - 5, self.rect.y + SPRITE_SIZE, 'bullet.png', -5, 4)
        boss_bullets.add(boss_bullet)

# Класс для игрока
class Player(GameSprite):
    def __init__(self, x, y, image_name, speed):
        super().__init__(x, y, image_name, speed)
        self.last_shoot_time = 0
        self.amount_bullets = 50
        self.max_bullets = 50
        self.reloading = False
        self.reload_time = 3 # секунды
        self.reload_start_time = 0
        self.hidden = False  # Флаг для отслеживания невидимости
        self.hide_timer = 0  # Таймер для отслеживания времени невидимости

    def move(self):
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < SCREEN_SIZE[0] - SPRITE_SIZE:
            self.rect.x += self.speed
        #Проверяем не в перезарядке ли мы и есть ли у нас пули для стрельбы
        if keys[K_SPACE] and self.amount_bullets > 0 and not self.reloading:
            if get_time() - self.last_shoot_time >= 0.2:
                self.shoot()
                self.last_shoot_time = get_time()
        #Начало перезарядки
        if keys[K_r] and self.amount_bullets < self.max_bullets and not self.reloading:
            self.start_reloading()
        # Активация невидимости по нажатию клавиши "s"
        if keys[K_s] and not self.hidden:
            self.hide()

    def show(self):
        if not self.hidden:
            window.blit(self.image, (self.rect.x, self.rect.y))
        show_text(SCREEN_SIZE[0] - 200, 15, f'Пули: {self.amount_bullets}', WHITE, 20)
        if self.reloading:
            show_text(self.rect.x, self.rect.y + 40, 'Перезарядка...', WHITE, 20)
            if get_time() - self.reload_start_time >= self.reload_time:
                self.finish_reloading()
        # Если игрок невидим, показываем таймер
        if self.hidden:
            remaining_time = int(5 - (get_time() - self.hide_timer))
            show_text(self.rect.x, self.rect.y + 40, f'Невидимость: {remaining_time}', WHITE, 20)
            # Проверяем, не закончилось ли время невидимости
            if get_time() - self.hide_timer >= 5:
                self.unhide()

    def shoot(self):
        bullet = Bullet(self.rect.x + SPRITE_SIZE//2 - 5, self.rect.y, 'bullet.png', 7, 4)
        bullets.add(bullet)
        self.amount_bullets -= 1
        mixer.Sound('hitsound.wav').play()

    def start_reloading(self):
        self.reloading = True
        self.reload_start_time = get_time()

    def finish_reloading(self):
        self.reloading = False
        self.amount_bullets = self.max_bullets

    def hide(self):
        self.hidden = True
        self.hide_timer = get_time()

    def unhide(self):
        self.hidden = False

# Класс для астероидов
class Asteroid(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= SCREEN_SIZE[1]:
            self.rect.y = 0
            self.rect.x = randint(0, SCREEN_SIZE[0] - SPRITE_SIZE)

# Создание групп спрайтов
bullets = sprite.Group()
asteroids = sprite.Group()
enemies = sprite.Group()
boss_bullets = sprite.Group()

# Создание экземпляров спрайтов
player = Player(320, 430, "1.png", 5)
boss = Boss(320, 50, 'boss.jpg', 2) # Создаем босса

# Количество врагов для первого уровня
num_enemies_level1 = 2
# Количество астероидов для первого уровня
num_asteroids_level1 = 1

# Создаем врагов для первого уровня
for _ in range(num_enemies_level1):
    enemies.add(Enemy(randint(0, SCREEN_SIZE[0] - SPRITE_SIZE), -50, '2.jpg', 2))
# Создаем астероиды для первого уровня
for _ in range(num_asteroids_level1):
    asteroids.add(Asteroid(randint(0, SCREEN_SIZE[0] - SPRITE_SIZE), -50, '07d7f8bad583b8d24b97109f436b719e.jpg', 3))

# Настройка окна
window = display.set_mode(SCREEN_SIZE)
display.set_caption('Космическая стрелялка')

# Загрузка фона
bg = transform.scale(image.load("galaxy.jpg"), SCREEN_SIZE)

# Настройка музыки
mixer.init()
mixer.music.load('tick-tock-made-with-Voicemod.mp3')
mixer.music.set_volume(0.1)
mixer.music.play(-1)

# Игровой цикл
clock = time.Clock()
game = True
finish = False
mini_boss_fight = True # Добавим флаг для мини-босса

# Переменная для отслеживания текущего уровня
current_level = 1

# Функция для перехода на следующий уровень
def next_level():
    global current_level, enemies, asteroids

    current_level += 1
    enemies.empty()
    asteroids.empty()

    if current_level == 2:
        # Увеличиваем сложность второго уровня (больше врагов и астероидов)
        num_enemies_level2 = 4
        num_asteroids_level2 = 2
        for _ in range(num_enemies_level2):
            enemies.add(Enemy(randint(0, SCREEN_SIZE[0] - SPRITE_SIZE), -50, '2.jpg', 3))  # Увеличиваем скорость
        for _ in range(num_asteroids_level2):
            asteroids.add(Asteroid(randint(0, SCREEN_SIZE[0] - SPRITE_SIZE), -50, '07d7f8bad583b8d24b97109f436b719e.jpg', 4))  # Увеличиваем скорость
    elif current_level == 3:
        # Переход на уровень с боссом
        pass  # Босс уже создан

# Функция перезапуска игры
def restart_game():
    global finish, kill_count, missed_count, lives_count, player, bullets, asteroids, enemies, boss, boss_bullets, current_level, mini_boss_fight

    finish = False
    current_level = 1
    mini_boss_fight = True # Возвращаем мини-босса

    kill_count.count = 0
    kill_count.render()
    missed_count.count = 0
    missed_count.render()
    lives_count.count = 3
    lives_count.render()

    player.rect.x = 320
    player.rect.y = 430
    player.amount_bullets = 50

    boss.rect.x = 320
    boss.rect.y = 50
    boss.health = 3  # Восстанавливаем здоровье босса

    bullets.empty()
    asteroids.empty()
    enemies.empty()
    boss_bullets.empty()

    # Создаем врагов для первого уровня
    for _ in range(num_enemies_level1):
        enemies.add(Enemy(randint(0, SCREEN_SIZE[0] - SPRITE_SIZE), -50, '2.jpg', 2))
    # Создаем астероиды для первого уровня
    for _ in range(num_asteroids_level1):
        asteroids.add(Asteroid(randint(0, SCREEN_SIZE[0] - SPRITE_SIZE), -50, '07d7f8bad583b8d24b97109f436b719e.jpg', 3))

# Основной игровой цикл
while game:
    clock.tick(60)

    for e in event.get():
        if e.type == QUIT:
            game = False
        if e.type == KEYDOWN:
            if e.key == K_r and finish:
                restart_game()

    if not finish:
        window.blit(bg, (0, 0))
        player.show()
        player.move()
        missed_count.show()
        kill_count.show()
        lives_count.show()

        enemies.update()
        asteroids.update()
        # Обновляем босса только на уровне 3
        if current_level == 3:
            boss.update()

        bullets.update()
        bullets.draw(window)
        asteroids.draw(window)
        # Рисуем пули босса только на уровне 3
        if current_level == 3:
            boss_bullets.update() # Обновляем пули босса
            boss_bullets.draw(window) # Рисуем пули босса

        # Проверка столкновений врагов и пуль
        collisions = sprite.groupcollide(enemies, bullets, False, True)
        for enemy in collisions:
            enemy.rect.y = -50
            enemy.rect.x = randint(0, SCREEN_SIZE[0] - SPRITE_SIZE)
            kill_count.count += 1
            kill_count.render()

        # Мини-босс файт в начале игры
        if mini_boss_fight:
            boss.update()  # Обновляем босса
            boss_bullets.update() # Обновляем пули босса
            boss_bullets.draw(window)  # Рисуем пули босса

            boss_hits = sprite.spritecollide(boss, bullets, True)
            if boss_hits:
                boss.health -= 1
                if boss.health <= 0:
                    mini_boss_fight = False  # Отключаем мини-босса после победы

        # Проверяем столкновения пуль игрока с боссом
        if current_level == 3:
            boss_hits = sprite.spritecollide(boss, bullets, True)
            if boss_hits:
                boss.health -= 1  # Уменьшаем здоровье босса при попадании
                if boss.health <= 0:
                    finish = True
                    show_text(SCREEN_SIZE[0] // 2 - 100, SCREEN_SIZE[1] // 2, "ПОБЕДА!!!", WHITE, 50)

        # Проверяем столкновения игрока с врагами, астероидами и пулями босса (если игрок не невидим)
        if not player.hidden:
            if sprite.spritecollide(player, enemies, True) or \
               sprite.spritecollide(player, asteroids, True) or \
               sprite.spritecollide(player, boss_bullets, True):
                lives_count.count -= 1
                lives_count.render()
                if lives_count.count <= 0:
                    finish = True
                    show_text(SCREEN_SIZE[0] // 2 - 100, SCREEN_SIZE[1] // 2, "ПРОИГРЫШ!!!", WHITE, 50)
                else:
                    # Перемещаем игрока в безопасное место после столкновения
                    player.rect.x = 320
                    player.rect.y = 430

        if missed_count.count >= 10:
            finish = True
            show_text(SCREEN_SIZE[0] // 2 - 100, SCREEN_SIZE[1] // 2, "ПРОИГРЫШ!!!", WHITE, 50)

        # Условие для перехода на следующий уровень (например, убито определенное количество врагов)
        if kill_count.count >= 5 and current_level < 3 and not mini_boss_fight:
            next_level()

    else:
        show_text(SCREEN_SIZE[0] // 2 - 100, SCREEN_SIZE[1] // 2 - 50, "Игра окончена!", WHITE, 35)
        show_text(SCREEN_SIZE[0] // 2 - 100, SCREEN_SIZE[1] // 2 + 50, "Нажмите R, чтобы начать заново", WHITE, 25)

    display.update()