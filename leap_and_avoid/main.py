import pygame
import random
import sys

pygame.init()

# Screen setup
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Leap and Avoid Vertical")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 48)

# Constants
GRAVITY = 0.5
JUMP_STRENGTH = -13
PLAYER_RADIUS = 12
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20
FPS = 60

# Create spike image dynamically (red triangle)
def create_spike_image():
    surf = pygame.Surface((40, 20), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (255, 0, 0), [(0, 20), (20, 0), (40, 20)])
    return surf

# Create coin image dynamically (yellow circle)
def create_coin_image():
    surf = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 215, 0), (10, 10), 10)
    return surf

spike_img = create_spike_image()
coin_img = create_coin_image()

# Particle for jump effect
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(2, 4)
        self.color = (200, 200, 200)
        self.life = 20
        self.vel_x = random.uniform(-1, 1)
        self.vel_y = random.uniform(-2, 0)

    def update(self):
        self.life -= 1
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.1  # gravity

    def draw(self, surface):
        if self.life > 0:
            alpha = max(0, int(255 * (self.life / 20)))
            surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (self.radius, self.radius), self.radius)
            surface.blit(surf, (self.x - self.radius, self.y - self.radius))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_RADIUS*2, PLAYER_RADIUS*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), (PLAYER_RADIUS, PLAYER_RADIUS), PLAYER_RADIUS)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - PLATFORM_HEIGHT - PLAYER_RADIUS))
        self.vel_y = 0
        self.coins_collected = 0
        self.score = 0
        self.particles = []

    def update(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5

        # Wrap around horizontally
        if self.rect.right > WIDTH:
            self.rect.left = 0
        if self.rect.left < 0:
            self.rect.right = WIDTH

        # Scroll world upward if player goes higher than 1/3 screen height
        if self.rect.top < HEIGHT // 3:
            scroll_amount = int(abs(self.vel_y))
            self.score += scroll_amount
            for plat in platforms:
                plat.rect.y += scroll_amount
            for enemy in enemies:
                enemy.rect.y += scroll_amount
            for coin in coins:
                coin.rect.y += scroll_amount

        # Remove particles that died
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

        # Game over if player falls below screen
        if self.rect.top > HEIGHT:
            game_over()

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        for p in self.particles:
            p.draw(surface)

    def add_jump_particles(self):
        for _ in range(8):
            self.particles.append(Particle(self.rect.centerx, self.rect.bottom))

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width=PLATFORM_WIDTH, height=PLATFORM_HEIGHT, color=(30,180,30)):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.color = color
        self.width = width
        self.height = height
        self.draw_platform()

    def draw_platform(self):
        pygame.draw.rect(self.image, self.color, (0, 0, self.width, self.height), border_radius=8)
        lighter = (min(self.color[0]+30,255), min(self.color[1]+40,255), min(self.color[2]+30,255))
        pygame.draw.rect(self.image, lighter, (3, 3, self.width - 6, self.height - 6), border_radius=8)

    def update(self):
        if self.rect.top > HEIGHT:
            self.kill()
            new_platform()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = spike_img
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = random.choice([-1, 1])
        self.speed = 1.5

    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.direction *= -1
        if self.rect.top > HEIGHT:
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = coin_img
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        if self.rect.top > HEIGHT:
            self.kill()

def new_platform():
    x = random.randint(0, WIDTH - PLATFORM_WIDTH)
    y = random.randint(-50, 0)
    platform = Platform(x, y)
    platforms.add(platform)
    all_sprites.add(platform)

    # Add enemies and coins only after 2 seconds
    if pygame.time.get_ticks() - start_time > 2000:
        if random.random() < 0.2:
            enemy = Enemy(x + 20, y - 20)
            enemies.add(enemy)
            all_sprites.add(enemy)
        if random.random() < 0.3:
            coin = Coin(x + random.randint(10, PLATFORM_WIDTH - 10), y - 30)
            coins.add(coin)
            all_sprites.add(coin)

def game_over():
    global game_over_flag
    game_over_flag = True

def reset_game():
    global start_time, game_over_flag
    player.rect.center = (WIDTH // 2, HEIGHT - PLATFORM_HEIGHT - PLAYER_RADIUS)
    player.vel_y = 0
    player.score = 0
    player.coins_collected = 0
    platforms.empty()
    enemies.empty()
    coins.empty()
    all_sprites.empty()
    all_sprites.add(player)

    # Add starting big green platform at bottom
    start_platform = Platform( (WIDTH - 200)//2, HEIGHT - PLATFORM_HEIGHT, width=200, height=PLATFORM_HEIGHT, color=(40, 200, 40))
    platforms.add(start_platform)
    all_sprites.add(start_platform)

    # Add some platforms above
    for i in range(5):
        plat = Platform(random.randint(0, WIDTH - PLATFORM_WIDTH), HEIGHT - PLATFORM_HEIGHT - (i+1)*100)
        platforms.add(plat)
        all_sprites.add(plat)

    start_time = pygame.time.get_ticks()
    game_over_flag = False

# Initialize game elements
player = Player()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Add starting big green platform at bottom
start_platform = Platform( (WIDTH - 200)//2, HEIGHT - PLATFORM_HEIGHT, width=200, height=PLATFORM_HEIGHT, color=(40, 200, 40))
platforms.add(start_platform)
all_sprites.add(start_platform)

# Add some platforms above
for i in range(5):
    plat = Platform(random.randint(0, WIDTH - PLATFORM_WIDTH), HEIGHT - PLATFORM_HEIGHT - (i+1)*100)
    platforms.add(plat)
    all_sprites.add(plat)

start_time = pygame.time.get_ticks()
game_over_flag = False

# Main game loop
while True:
    clock.tick(FPS)
    screen.fill((0, 0, 0))  # Black background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over_flag:
                # Check if player is on platform or bottom platform to jump
                player.rect.y += 2
                hits = pygame.sprite.spritecollide(player, platforms, False)
                player.rect.y -= 2
                if hits:
                    player.vel_y = JUMP_STRENGTH
                    player.add_jump_particles()
            if event.key == pygame.K_r and game_over_flag:
                reset_game()

    if not game_over_flag:
        all_sprites.update()

        # Collision with platforms (player falling onto platform)
        hits = pygame.sprite.spritecollide(player, platforms, False)
        if hits:
            lowest = hits[0]
            for plat in hits:
                if plat.rect.bottom > lowest.rect.bottom:
                    lowest = plat
            if player.vel_y > 0 and player.rect.bottom <= lowest.rect.bottom + 15:
                player.rect.bottom = lowest.rect.top
                player.vel_y = 0

        # Collision with enemies
        if pygame.sprite.spritecollide(player, enemies, False):
            game_over()

        # Collect coins
        coin_hits = pygame.sprite.spritecollide(player, coins, True)
        for coin in coin_hits:
            player.coins_collected += 1

        # Spawn new platforms as old ones move down
        while len(platforms) < 6:
            new_platform()

        # Draw everything
        all_sprites.draw(screen)
        player.draw(screen)

        # Score display
        score_text = font.render(f"Score: {-player.rect.top}", True, (255, 255, 255))
        coins_text = font.render(f"Coins: {player.coins_collected}", True, (255, 215, 0))
        screen.blit(score_text, (10, 10))
        screen.blit(coins_text, (10, 40))

    else:
        # Game Over screen
        go_text = big_font.render("Game Over", True, (255, 50, 50))
        restart_text = font.render("Press R to Restart", True, (255, 255, 255))
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 60))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))

    pygame.display.flip()
