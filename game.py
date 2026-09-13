
import pygame
import random
import sys


WIDTH, HEIGHT = 800, 600
FPS = 60

GRAVITY = 0.45
FLAP_STRENGTH = -8.5
MAX_FALL_SPEED = 10

PIPE_WIDTH = 70
PIPE_GAP = 170
PIPE_SPEED = 3
PIPE_FREQUENCY_MS = 1500 

GROUND_HEIGHT = 80

SKY_BLUE = (113, 197, 207)
GROUND_BROWN = (50, 50, 50)
GROUND_GREEN = (0, 0, 0)
PIPE_GREEN = (13, 71, 120)
PIPE_GREEN_DARK = (13, 51, 92)
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
RED = (220, 50, 50)
TITLE_COLOR = (255, 220, 0)       
TITLE_OUTLINE = 205, 217, 251
GAMEOVER_COLOR = RED               
HINT_COLOR = 205, 217, 251                 
                


class Bird:
    
    ANIMATION_SPEED_MS = 100

    def __init__(self, frames=None):
        self.x = WIDTH // 3
        self.y = HEIGHT // 2
        self.radius = 16
        self.velocity = 0
        self.alive = True
        self.angle = 0

        
        self.frames = frames
        self.frame_index = 0
        self.animation_timer = 0

    def flap(self):
        if self.alive:
            self.velocity = FLAP_STRENGTH

    def update(self, dt):
        self.velocity += GRAVITY
        if self.velocity > MAX_FALL_SPEED:
            self.velocity = MAX_FALL_SPEED
        self.y += self.velocity

        self.angle = max(-25, min(70, self.velocity * 4))

        if self.frames:
            self.animation_timer += dt
            if self.animation_timer >= self.ANIMATION_SPEED_MS:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)

    def get_rect(self):
        if self.frames:
            img_rect = self.frames[self.frame_index].get_rect(center=(self.x, self.y))
            return img_rect.inflate(-8, -8)  
        return pygame.Rect(
            self.x - self.radius, self.y - self.radius,
            self.radius * 2, self.radius * 2
        )

    def draw(self, screen):
        if self.frames:
            current_frame = self.frames[self.frame_index]
            rotated = pygame.transform.rotate(current_frame, -self.angle)
            rect = rotated.get_rect(center=(self.x, self.y))
            screen.blit(rotated, rect)
            return

        body_surf = pygame.Surface((self.radius * 2 + 10, self.radius * 2 + 10), pygame.SRCALPHA)
        center = (self.radius + 5, self.radius + 5)

    
    
class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = PIPE_WIDTH
        margin = 60
        self.gap_y = random.randint(margin + PIPE_GAP // 2,
                                     HEIGHT - GROUND_HEIGHT - margin - PIPE_GAP // 2)
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def off_screen(self):
        return self.x + self.width < 0

    def top_rect(self):
        height = self.gap_y - PIPE_GAP // 2
        return pygame.Rect(self.x, 0, self.width, height)

    def bottom_rect(self):
        y = self.gap_y + PIPE_GAP // 2
        height = (HEIGHT - GROUND_HEIGHT) - y
        return pygame.Rect(self.x, y, self.width, height)

    def draw(self, screen):
        for rect in (self.top_rect(), self.bottom_rect()):
            pygame.draw.rect(screen, PIPE_GREEN, rect)
            pygame.draw.rect(screen, PIPE_GREEN_DARK, rect, 3)

        cap_h = 24
        top = self.top_rect()
        cap_top = pygame.Rect(self.x - 4, top.height - cap_h, self.width + 8, cap_h)
        pygame.draw.rect(screen, PIPE_GREEN, cap_top)
        pygame.draw.rect(screen, PIPE_GREEN_DARK, cap_top, 3)

        bottom = self.bottom_rect()
        cap_bottom = pygame.Rect(self.x - 4, bottom.y, self.width + 8, cap_h)
        pygame.draw.rect(screen, PIPE_GREEN, cap_bottom)
        pygame.draw.rect(screen, PIPE_GREEN_DARK, cap_bottom, 3)

    def collides_with(self, bird_rect):
        return bird_rect.colliderect(self.top_rect()) or bird_rect.colliderect(self.bottom_rect())


"""É o que dá a sensação de movimento"""

def draw_ground(screen, offset):
    ground_y = HEIGHT - GROUND_HEIGHT
    pygame.draw.rect(screen, GROUND_BROWN, (0, ground_y, WIDTH, GROUND_HEIGHT))
    pygame.draw.rect(screen, GROUND_GREEN, (0, ground_y, WIDTH, 10))

    stripe_w = 30
    x = -offset % stripe_w
    while x < WIDTH:
        pygame.draw.line(screen, GROUND_GREEN, (x, ground_y + 10), (x - 15, ground_y + GROUND_HEIGHT), 4)
        x += stripe_w


def draw_text_center(screen, text, font, color, y, outline_color=BLACK):
    surf = font.render(text, True, color)
    outline = font.render(text, True, outline_color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        screen.blit(outline, outline.get_rect(center=(rect.centerx + dx, rect.centery + dy)))
    screen.blit(surf, rect)


def draw_panel(screen, rect):
    """Painel semi-transparente com cantos arredondados, usado atrás de textos/menus."""
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)


def draw_start_screen(screen, fonts, title_img=None):
    font_big, font_medium, font_small = fonts

    panel_rect = pygame.Rect(0, 0, 320, 170)
    panel_rect.center = (WIDTH // 2, HEIGHT // 2 - 30)
    draw_panel(screen, panel_rect)

    if title_img:
        img_rect = title_img.get_rect(center=(WIDTH // 2, panel_rect.top + 55))
        screen.blit(title_img, img_rect)
    else:
        quit

def draw_gameover_screen(screen, fonts, score, best_score, gameover_img=None):
    font_big, font_medium, font_small = fonts

    panel_rect = pygame.Rect(0, 0, 320, 220)
    panel_rect.center = (WIDTH // 2, HEIGHT // 2 - 10)
    draw_panel(screen, panel_rect)

    if gameover_img:
        img_rect = gameover_img.get_rect(center=(WIDTH // 2, panel_rect.top + 45))
        screen.blit(gameover_img, img_rect)
    else:
        draw_text_center(screen, "GAME OVER", font_big, GAMEOVER_COLOR, panel_rect.top + 40)

    draw_text_center(screen, f"Pontuação: {score}", font_medium, HINT_COLOR, panel_rect.top + 80)
    draw_text_center(screen, f"Recorde: {best_score}", font_small, HINT_COLOR, panel_rect.top + 55)


def main():
    pygame.init()

    try:
        pygame.mixer.init()
        audio_ready = True
    except pygame.error as e:
        print(f"[Aviso] Não foi possível iniciar o áudio: {e}")
        audio_ready = False

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flappy Bird Clone")
    clock = pygame.time.Clock()

    font_big = pygame.font.SysFont("arial", 48, bold=True)
    font_medium = pygame.font.SysFont("arial", 28, bold=True)
    font_small = pygame.font.SysFont("arial", 20)

    BIRD_SIZE = (60, 60)  
    bird_frames = None
    try:
        bird_frames = [
            pygame.transform.scale(
                pygame.image.load(f"imagens/pombovoo{i}.png").convert_alpha(), BIRD_SIZE
            )
            for i in (1, 2, 3)
        ]
        background_img = pygame.transform.scale(
            pygame.image.load("imagens/backgroundflappybird.png").convert(), (WIDTH, HEIGHT)
        )
    except (pygame.error, FileNotFoundError) as e:
        print(f"Imagem não encontrada")

    try:
        title_img = pygame.image.load("imagens/title.png").convert_alpha()
    except (pygame.error, FileNotFoundError):
        pass
    try:
        gameover_img = pygame.image.load("imagens/gameover2.png").convert_alpha()
    except (pygame.error, FileNotFoundError):
        pass

    """Áudio do jogo"""

    def load_sound(path):
        if not audio_ready:
            return None
        try:
            return pygame.mixer.Sound(path)
        except (pygame.error, FileNotFoundError):
            return None

    flap_sound = load_sound("sons/flap.wav")
    score_sound = load_sound("sons/score.wav")
    hit_sound = load_sound("sons/hit.wav")

    def play_sound(sound):
        if sound:
            sound.play()

   
    PIPE_EVENT = pygame.USEREVENT + 1

    def reset_game():
        bird = Bird(bird_frames)
        pipes = []
        pygame.time.set_timer(PIPE_EVENT, PIPE_FREQUENCY_MS)
        return bird, pipes, 0

    bird, pipes, score = reset_game()
    best_score = 0
    ground_offset = 0
    state = "start"  

    while True:
        dt = clock.tick(FPS) 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    if state == "start":
                        state = "playing"
                        bird.flap()
                        play_sound(flap_sound)
                    elif state == "playing":
                        bird.flap()
                        play_sound(flap_sound)
                    elif state == "gameover":
                        pass
                if event.key == pygame.K_r and state == "gameover":
                    bird, pipes, score = reset_game()
                    state = "start"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == "start":
                    state = "playing"
                    bird.flap()
                    play_sound(flap_sound)
                elif state == "playing":
                    bird.flap()
                    play_sound(flap_sound)
                elif state == "gameover":
                    bird, pipes, score = reset_game()
                    state = "start"

            if event.type == PIPE_EVENT and state == "playing":
                pipes.append(Pipe(WIDTH + 20))

       
        if state == "playing":
            bird.update(dt)
            ground_offset += PIPE_SPEED

            for pipe in pipes:
                pipe.update()

                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    pipe.passed = True
                    score += 1
                    play_sound(score_sound)

            pipes = [p for p in pipes if not p.off_screen()]

            bird_rect = bird.get_rect()
            ground_y = HEIGHT - GROUND_HEIGHT

            hit_ground_or_ceiling = bird.y + bird.radius >= ground_y or bird.y - bird.radius <= 0
            hit_pipe = any(p.collides_with(bird_rect) for p in pipes)

            if hit_ground_or_ceiling or hit_pipe:
                state = "gameover"
                bird.alive = False
                best_score = max(best_score, score)
                play_sound(hit_sound)
                pygame.time.set_timer(PIPE_EVENT, 0)


        if background_img:
            screen.blit(background_img, (0, 0))
        
        for pipe in pipes:
            pipe.draw(screen)

        draw_ground(screen, ground_offset)
        bird.draw(screen)

        """Placar"""
        
        score_surf = font_big.render(str(score), True, WHITE)
        outline_surf = font_big.render(str(score), True, (205, 217, 251))
        score_rect = score_surf.get_rect(center=(WIDTH // 2, 60))
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            screen.blit(outline_surf, outline_surf.get_rect(center=(score_rect.centerx + dx, score_rect.centery + dy)))
        screen.blit(score_surf, score_rect)

        if state == "start":
            draw_start_screen(screen, (font_big, font_medium, font_small), title_img)

        if state == "gameover":
            draw_gameover_screen(screen, (font_big, font_medium, font_small), score, best_score, gameover_img)

        pygame.display.flip()


if __name__ == "__main__":
    main()