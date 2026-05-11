
from pygame import *
from random import randint
from time import time as timer

window = display.set_mode((700, 500))
display.set_caption("Шутер")

# новый фон
background = transform.scale(image.load("space_bg.jpg"), (700, 500))

win_height = 500
win_width = 700
clock = time.Clock()

score = 0
lost = 0
level = 1
player_health = 5

mixer.init()
mixer.music.load("space.ogg")
mixer.music.set_volume(0.1)
mixer.music.play()

shoot = mixer.Sound("fire.ogg")
shoot.set_volume(0.25)

boss_spawned = False

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__()

        self.image = transform.scale(image.load(player_image), (size_x, size_y))

        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):

    def update(self):
        keys = key.get_pressed()

        if keys[K_a] and self.rect.x > 0:
            self.rect.x -= self.speed

        if keys[K_d] and self.rect.x < win_width - 60:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet("bullet.png", self.rect.centerx, self.rect.top, 15, 20, 10)
        bullets.add(bullet)


class Enemy(GameSprite):

    def update(self):
        self.rect.y += self.speed

        global lost
        global player_health

        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0

            lost += 1
            player_health -= 1


class Bullet(GameSprite):

    def update(self):
        self.rect.y -= self.speed

        if self.rect.y < 0:
            self.kill()


# БОСС
class Boss(GameSprite):

    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)

        self.health = 30
        self.direction = "left"

    def update(self):

        if self.direction == "left":
            self.rect.x -= self.speed

            if self.rect.x <= 0:
                self.direction = "right"

        else:
            self.rect.x += self.speed

            if self.rect.x >= win_width - 180:
                self.direction = "left"

    def draw_health(self):
        boss_hp = font2.render("Boss HP: " + str(self.health), 1, (255, 0, 0))
        window.blit(boss_hp, (500, 10))


ship = Player("rocket.png", 310, win_height - 101, 80, 100, 5)

bullets = sprite.Group()
monsters = sprite.Group()

for i in range(5):
    monster = Enemy("ufo.png", randint(80, win_width - 80), -40, 80, 50, randint(1, 2))
    monsters.add(monster)


asteroids = sprite.Group()

for i in range(3):
    asteroid = Enemy("asteroid.png", randint(30, win_width - 30), -40, 80, 50, randint(1, 4))
    asteroids.add(asteroid)


boss_group = sprite.Group()


font.init()
font2 = font.Font(None, 40)

win = font2.render("YOU WIN", True, (0, 255, 0))
lose = font2.render("YOU LOSE", True, (255, 0, 0))

game = True
finish = False

num_fire = 0
rel_time = False


while game:

    for e in event.get():
        if e.type == QUIT:
            game = False

        elif e.type == KEYDOWN:

            if e.key == K_SPACE:

                if num_fire < 5 and rel_time == False:

                    num_fire += 1
                    shoot.play()
                    ship.fire()

                if num_fire >= 5 and rel_time == False:

                    last_time = timer()
                    rel_time = True


    if finish != True:

        window.blit(background, (0, 0))

        # ТЕКСТ
        score_count = font2.render("Score: " + str(score), 1, (255,255,255))
        window.blit(score_count, (10,10))

        lost_count = font2.render("Lost: " + str(lost), 1, (255,255,255))
        window.blit(lost_count, (10,40))

        level_text = font2.render("Level: " + str(level), 1, (0,255,0))
        window.blit(level_text, (10,70))

        hp_text = font2.render("HP: " + str(player_health), 1, (255,50,50))
        window.blit(hp_text, (10,100))


        ship.reset()
        ship.update()

        bullets.update()
        bullets.draw(window)

        monsters.update()
        monsters.draw(window)

        asteroids.update()
        asteroids.draw(window)


        # уровни
        if score >= 10:
            level = 2

            for monster in monsters:
                monster.speed = 4

        if score >= 20:
            level = 3

            for monster in monsters:
                monster.speed = 6


        # спавн босса
        if score >=30 and boss_spawned == False:

            boss = Boss("boss.png", 250, 50, 180, 120, 5)
            boss_group.add(boss)

            boss_spawned = True


        boss_group.update()
        boss_group.draw(window)

        for b in boss_group:
            b.draw_health()


        if rel_time:

            now_timer = timer()

            if now_timer - last_time < 5:

                reload = font2.render("WAIT RELOAD...", 5, (150,0,0))
                window.blit(reload, (250,460))

            else:

                num_fire = 0
                rel_time = False


        

        collides = sprite.groupcollide(monsters, bullets, True, True)

        for i in collides:

            score += 1

            monster = Enemy(
                "ufo.png",
                randint(80, win_width - 80),
                -40,
                80,
                50,
                randint(1, level + 2)
            )

            monsters.add(monster)

        collides = sprite.groupcollide(asteroids, bullets, True, True)

        for i in collides:

            score += 1

            asteroid = Enemy(
                "asteroid.png",
                randint(80, win_width - 80),
                -40,
                80,
                50,
                randint(1, level + 2)
            )

            asteroids.add(asteroid)
        


        # попадание по боссу
        for boss in boss_group:

            boss_hit = sprite.spritecollide(boss, bullets, True)

            for hit in boss_hit:

                boss.health -= 1

                if boss.health <= 0:

                    boss.kill()
                    finish = True
                    window.blit(win, (250,250))


        # столкновение
        if sprite.spritecollide(ship, monsters, False):

            player_health -= 1

            for monster in monsters:
                monster.rect.y = -100


        if sprite.spritecollide(ship, asteroids, False):

            player_health -= 1

            for asteroid in asteroids:
                asteroid.rect.y = -100


        if player_health <= 0 or lost >= 10:

            finish = True
            window.blit(lose, (250,250))


    display.update()
    clock.tick(60)
