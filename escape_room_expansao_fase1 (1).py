import pygame
import math
import random
import sys

# ============================================================
# ESCAPE ROOM 2D - MANSÃO DOS MISTÉRIOS (EDITION DELUXE)
# ============================================================

pygame.init()
pygame.font.init()

SCREEN_W, SCREEN_H = 1100, 700
WORLD_W, WORLD_H = 3000, 1900
FPS = 60

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Escape Room 2D - Mansão dos Mistérios")
clock = pygame.time.Clock()

# ------------------------------------------------------------
# PALETA DE CORES
# ------------------------------------------------------------
COLOR_BG = (10, 12, 16)
COLOR_WHITE = (245, 245, 250)
COLOR_GRAY_LIGHT = (175, 180, 190)
COLOR_GRAY_DARK = (28, 30, 38)
COLOR_FLOOR_A = (48, 43, 41)
COLOR_FLOOR_B = (56, 50, 47)
COLOR_WALL = (28, 30, 38)
COLOR_WALL_BORDER = (65, 70, 85)

COLOR_PURPLE = (112, 76, 190)
COLOR_PURPLE_LIGHT = (160, 120, 240)
COLOR_SKIN = (238, 180, 135)
COLOR_HAIR = (45, 28, 22)

COLOR_RED = (215, 65, 78)
COLOR_GREEN = (60, 200, 115)
COLOR_GREEN_DARK = (32, 105, 67)
COLOR_YELLOW = (245, 196, 70)
COLOR_GOLD = (230, 175, 45)
COLOR_WOOD = (95, 58, 38)
COLOR_WOOD_LIGHT = (135, 82, 50)
COLOR_PAPER = (225, 212, 175)

font_micro = pygame.font.Font(None, 18)
font_small = pygame.font.Font(None, 22)
font_main = pygame.font.Font(None, 28)
font_big = pygame.font.Font(None, 42)
font_title = pygame.font.Font(None, 64)


# ============================================================
# SISTEMA DE CONQUISTAS (ACHIEVEMENTS)
# ============================================================

class AchievementManager:
    def __init__(self):
        self.achievements = {
            "first_step": {"title": "Primeiros Passos", "desc": "Moveu o personagem pela primeira vez", "unlocked": False},
            "sprint": {"title": "Atleta", "desc": "Usou a corrida (LSHIFT)", "unlocked": False},
            "gold_key": {"title": "Caçador de Tesouros", "desc": "Encontrou a Chave Dourada", "unlocked": False},
            "red_key": {"title": "Mestre da Vermelha", "desc": "Encontrou a Chave Vermelha", "unlocked": False},
            "read_note": {"title": "Investigador", "desc": "Leu o bilhete misterioso", "unlocked": False},
            "safe": {"title": "Hacker de Cofre", "desc": "Abriu o cofre trancado", "unlocked": False},
            "open_door": {"title": "Explorador", "desc": "Abriu uma porta trancada", "unlocked": False},
            "escape": {"title": "Mestre do Escape", "desc": "Escapou com sucesso da mansão", "unlocked": False},
            "clock": {"title": "Pontual", "desc": "Resolveu o relógio antigo", "unlocked": False},
            "symbols": {"title": "Leitor de Símbolos", "desc": "Abriu o painel secreto", "unlocked": False},
            "power": {"title": "De Volta à Luz", "desc": "Restaurou a energia", "unlocked": False},
            "evidence": {"title": "Detetive", "desc": "Encontrou todas as evidências", "unlocked": False},
        }
        self.notifications = []

    def unlock(self, key):
        if key in self.achievements and not self.achievements[key]["unlocked"]:
            self.achievements[key]["unlocked"] = True
            title = self.achievements[key]["title"]
            self.notifications.append({"title": title, "timer": 240})

    def update(self):
        for notif in self.notifications[:]:
            notif["timer"] -= 1
            if notif["timer"] <= 0:
                self.notifications.remove(notif)

    def draw_notifications(self, surface):
        y_offset = 70
        for notif in self.notifications:
            box = pygame.Rect(SCREEN_W - 320, y_offset, 300, 50)
            pygame.draw.rect(surface, (20, 25, 35), box, border_radius=8)
            pygame.draw.rect(surface, COLOR_GOLD, box, 2, border_radius=8)

            txt_header = font_micro.render("🏆 CONQUISTA DESBLOQUEADA!", True, COLOR_GOLD)
            txt_title = font_small.render(notif["title"], True, COLOR_WHITE)

            surface.blit(txt_header, (box.x + 12, box.y + 8))
            surface.blit(txt_title, (box.x + 12, box.y + 26))

            y_offset += 60


# ============================================================
# CÂMERA
# ============================================================

class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def update(self, target_rect):
        self.x += (target_rect.centerx - SCREEN_W / 2 - self.x) * 0.08
        self.y += (target_rect.centery - SCREEN_H / 2 - self.y) * 0.08

        self.x = max(0.0, min(float(WORLD_W - SCREEN_W), self.x))
        self.y = max(0.0, min(float(WORLD_H - SCREEN_H), self.y))

    def apply(self, rect):
        return rect.move(-int(self.x), -int(self.y))

    def apply_pos(self, pos):
        return pos[0] - int(self.x), pos[1] - int(self.y)


# ============================================================
# PERSONAGEM DO JOGO
# ============================================================

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 38, 50)
        self.base_speed = 3.8
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.is_sprinting = False

        self.facing = "down"
        self.angle = 90.0
        self.walk_time = 0.0
        self.moving = False

    def handle_input(self, achievement_mgr):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1

        if dx != 0 or dy != 0:
            achievement_mgr.unlock("first_step")

        self.is_sprinting = keys[pygame.K_LSHIFT] and (dx != 0 or dy != 0) and self.stamina > 5
        if self.is_sprinting:
            self.stamina = max(0.0, self.stamina - 0.6)
            achievement_mgr.unlock("sprint")
        else:
            self.stamina = min(self.max_stamina, self.stamina + 0.3)

        return dx, dy

    def move(self, dx, dy, world):
        self.moving = dx != 0 or dy != 0
        current_speed = self.base_speed * (1.5 if self.is_sprinting else 1.0)

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        if dx > 0: self.facing, self.angle = "right", 0.0
        elif dx < 0: self.facing, self.angle = "left", 180.0
        if dy > 0: self.facing, self.angle = "down", 90.0
        elif dy < 0: self.facing, self.angle = "up", 270.0

        # Eixo X
        self.rect.x += int(dx * current_speed)
        col_x = world.get_collision(self.rect)
        if col_x:
            if dx > 0: self.rect.right = col_x.left
            if dx < 0: self.rect.left = col_x.right

        # Eixo Y
        self.rect.y += int(dy * current_speed)
        col_y = world.get_collision(self.rect)
        if col_y:
            if dy > 0: self.rect.bottom = col_y.top
            if dy < 0: self.rect.top = col_y.bottom

        if self.moving:
            self.walk_time += 0.25 if self.is_sprinting else 0.15
        else:
            self.walk_time = 0.0

    def draw(self, surface, camera):
        r = camera.apply(self.rect)
        bobbing = int(math.sin(self.walk_time) * 3) if self.moving else 0

        # Sombra
        shadow_rect = pygame.Rect(r.x + 4, r.bottom - 6, r.width - 8, 10)
        pygame.draw.ellipse(surface, (12, 12, 16), shadow_rect)

        # Pernas
        leg_offset = int(math.sin(self.walk_time) * 4) if self.moving else 0
        pygame.draw.line(surface, COLOR_GRAY_DARK, (r.centerx - 6, r.bottom - 12), (r.centerx - 7 + leg_offset, r.bottom + 2), 6)
        pygame.draw.line(surface, COLOR_GRAY_DARK, (r.centerx + 6, r.bottom - 12), (r.centerx + 7 - leg_offset, r.bottom + 2), 6)

        # Corpo
        body_rect = pygame.Rect(r.x + 3, r.y + 18 + bobbing, 32, 26)
        pygame.draw.rect(surface, COLOR_PURPLE, body_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_PURPLE_LIGHT, body_rect, 2, border_radius=6)

        # Cabeça
        head_rect = pygame.Rect(r.centerx - 13, r.y + bobbing, 26, 24)
        pygame.draw.ellipse(surface, COLOR_SKIN, head_rect)

        # Cabelo
        hair_rect = pygame.Rect(r.centerx - 14, r.y - 2 + bobbing, 28, 18)
        pygame.draw.arc(surface, COLOR_HAIR, hair_rect, math.pi, 2 * math.pi, 6)

        # Olhos
        ex, ey = r.centerx, r.y + 12 + bobbing
        if self.facing == "left": ex -= 5
        elif self.facing == "right": ex += 5
        pygame.draw.circle(surface, COLOR_BG, (ex - 4, ey), 2)
        pygame.draw.circle(surface, COLOR_BG, (ex + 4, ey), 2)


# ============================================================
# MUNDO E PORTAS INTERATIVAS
# ============================================================

class Door:
    def __init__(self, x, y, w, h, door_id, required_key_id):
        self.rect = pygame.Rect(x, y, w, h)
        self.door_id = door_id
        self.required_key_id = required_key_id
        self.is_open = False


class World:
    def __init__(self):
        self.walls = [
            pygame.Rect(0, 0, WORLD_W, 50),
            pygame.Rect(0, WORLD_H - 50, WORLD_W, 50),
            pygame.Rect(0, 0, 50, WORLD_H),
            pygame.Rect(WORLD_W - 50, 0, 50, WORLD_H),

            pygame.Rect(800, 50, 40, 500),
            pygame.Rect(800, 700, 40, 750),
            pygame.Rect(1600, 50, 40, 500),
            pygame.Rect(1600, 700, 40, 750),

            pygame.Rect(50, 800, 450, 40),
            pygame.Rect(650, 800, 150, 40),
            # Parede que separa a mansão antiga da nova ala leste; abertura é o portão.
            pygame.Rect(2350, 50, 40, 630),
            pygame.Rect(2350, 840, 40, 1010),
            # Divisórias internas com duas entradas livres: cada sala tem uma passagem
            # ampla pelo lado norte, em vez de ficar completamente cercada por paredes.
            pygame.Rect(2500, 900, 65, 35),
            pygame.Rect(2635, 900, 125, 35),
            pygame.Rect(2795, 900, 75, 35),
            pygame.Rect(2905, 900, 95, 35),
            pygame.Rect(2500, 935, 35, 295),
            pygame.Rect(2760, 935, 35, 295),
            pygame.Rect(2535, 1230, 75, 35),
            pygame.Rect(2700, 1230, 60, 35),
            pygame.Rect(2795, 1230, 65, 35),
            pygame.Rect(2940, 1230, 60, 35),
        ]

        self.doors = [
            Door(800, 550, 40, 150, "door_library", "gold_key"),
            Door(1600, 550, 40, 150, "door_exit_hall", "red_key"),
            Door(500, 800, 150, 40, "door_basement", None),
            Door(2350, 680, 40, 160, "door_east_wing", "red_key"),
        ]
        self.doors[2].is_open = True

        self.furniture = [
            pygame.Rect(150, 150, 280, 70),
            pygame.Rect(520, 150, 90, 300),
            pygame.Rect(200, 920, 300, 75),
            pygame.Rect(1000, 180, 320, 80),
            pygame.Rect(1800, 180, 350, 75),
            # Novos móveis/obstáculos da ala leste
            pygame.Rect(1850, 1000, 230, 55),
            pygame.Rect(2140, 1180, 65, 180),
            pygame.Rect(950, 1080, 180, 55),
        ]

    def get_collision(self, rect):
        for obstacle in self.walls + self.furniture:
            if rect.colliderect(obstacle):
                return obstacle

        for door in self.doors:
            if not door.is_open and rect.colliderect(door.rect):
                return door.rect
        return None

    def draw(self, surface, camera):
        surface.fill(COLOR_FLOOR_A)

        tile_size = 60
        start_x = int(camera.x // tile_size) * tile_size
        start_y = int(camera.y // tile_size) * tile_size

        for x in range(start_x, int(camera.x + SCREEN_W) + tile_size, tile_size):
            for y in range(start_y, int(camera.y + SCREEN_H) + tile_size, tile_size):
                if ((x // tile_size) + (y // tile_size)) % 2 == 0:
                    r = pygame.Rect(x - camera.x, y - camera.y, tile_size, tile_size)
                    pygame.draw.rect(surface, COLOR_FLOOR_B, r)

        for f in self.furniture:
            r = camera.apply(f)
            draw_furniture(surface, r)

        for w in self.walls:
            r = camera.apply(w)
            pygame.draw.rect(surface, COLOR_WALL, r)
            pygame.draw.rect(surface, COLOR_WALL_BORDER, r, 2)

        for door in self.doors:
            r = camera.apply(door.rect)
            if not door.is_open:
                pygame.draw.rect(surface, COLOR_WOOD, r, border_radius=4)
                pygame.draw.rect(surface, COLOR_GOLD if door.required_key_id == "gold_key" else COLOR_RED, r, 3, border_radius=4)
            else:
                pygame.draw.rect(surface, (20, 22, 28), r, border_radius=4)

        labels = [
            ("SALA INICIAL", 250, 90),
            ("CORREDOR DE PASSAGEM", 1050, 90),
            ("BIBLIOTECA PRINCIPAL", 1850, 90),
            ("PORÃO DE SEGREDOS", 300, 870),
            ("ALA LESTE: LABORATÓRIO", 2520, 960),
            ("RELÓGIO ANTIGO", 2550, 1010),
            ("SÓTÃO SUBTERRÂNEO", 2800, 1270),
        ]
        for title, x, y in labels:
            font_img = font_small.render(title, True, (130, 135, 145))
            surface.blit(font_img, (x - camera.x, y - camera.y))


# ============================================================
# UTILS DE RENDERIZAÇÃO
# ============================================================

def draw_real_key(surface, center_pos, color):
    cx, cy = center_pos
    pygame.draw.circle(surface, color, (cx - 8, cy), 7, 3)
    pygame.draw.line(surface, color, (cx - 1, cy), (cx + 12, cy), 3)
    pygame.draw.line(surface, color, (cx + 8, cy), (cx + 8, cy + 6), 3)
    pygame.draw.line(surface, color, (cx + 12, cy), (cx + 12, cy + 6), 3)


def draw_safe(surface, rect):
    """Cofre metálico ilustrado, com porta, dobradiças, teclado e maçaneta."""
    shadow = rect.move(4, 5)
    pygame.draw.rect(surface, (12, 12, 15), shadow, border_radius=8)
    pygame.draw.rect(surface, (65, 72, 83), rect, border_radius=8)
    pygame.draw.rect(surface, (155, 165, 177), rect, 3, border_radius=8)
    door = rect.inflate(-12, -12)
    pygame.draw.rect(surface, (43, 50, 61), door, border_radius=5)
    pygame.draw.rect(surface, (105, 116, 130), door, 2, border_radius=5)
    for yy in (rect.y + 17, rect.bottom - 20):
        pygame.draw.rect(surface, (190, 195, 202), (rect.x + 5, yy, 5, 9), border_radius=2)
    dial = (rect.right - 22, rect.centery + 4)
    pygame.draw.circle(surface, (19, 22, 28), dial, 10)
    pygame.draw.circle(surface, COLOR_GOLD, dial, 7, 2)
    pygame.draw.line(surface, COLOR_GOLD, (dial[0], dial[1]-5), (dial[0], dial[1]+5), 2)
    pygame.draw.line(surface, COLOR_GOLD, (dial[0]-5, dial[1]), (dial[0]+5, dial[1]), 2)
    keypad = pygame.Rect(rect.x + 13, rect.y + 17, 20, 24)
    pygame.draw.rect(surface, (15, 20, 26), keypad, border_radius=3)
    for ky in range(3):
        for kx in range(2):
            pygame.draw.circle(surface, (105, 205, 150), (keypad.x+6+kx*8, keypad.y+6+ky*7), 2)


def draw_furniture(surface, rect):
    """Desenha móveis diferentes conforme tamanho/formato, evitando blocos lisos."""
    r = rect
    pygame.draw.ellipse(surface, (15, 13, 14), (r.x+3, r.bottom-9, r.width-6, 13))
    if r.width >= 250 and r.height < 100:  # sofá ou mesa comprida
        pygame.draw.rect(surface, (54, 32, 28), r, border_radius=10)
        pygame.draw.rect(surface, (126, 72, 49), r.inflate(-8, -8), border_radius=8)
        pygame.draw.rect(surface, (160, 103, 68), (r.x+8, r.y+6, r.width-16, max(12, r.height//3)), border_radius=5)
        pygame.draw.line(surface, (65, 37, 28), (r.x+12, r.bottom-8), (r.right-12, r.bottom-8), 3)
        for xx in (r.x+14, r.right-20):
            pygame.draw.rect(surface, (40, 25, 20), (xx, r.bottom-5, 7, 9), border_radius=2)
    elif r.height >= 180:  # estante/armário
        pygame.draw.rect(surface, (50, 30, 23), r, border_radius=5)
        pygame.draw.rect(surface, (125, 74, 42), r.inflate(-7, -7), border_radius=3)
        for yy in range(r.y+22, r.bottom-8, 45):
            pygame.draw.line(surface, (49, 28, 20), (r.x+6, yy), (r.right-6, yy), 5)
            for j in range(3):
                bx = r.x+10+j*max(18, (r.width-25)//3)
                bw = max(9, min(17, r.width//7))
                book = pygame.Rect(bx, yy-19, bw, 18)
                pygame.draw.rect(surface, [(125,42,46),(46,78,95),(181,135,56),(65,105,73)][j], book, border_radius=2)
                pygame.draw.line(surface, (220,190,125), (bx+3, yy-15), (bx+bw-3, yy-15), 1)
        pygame.draw.rect(surface, (176, 119, 71), r, 3, border_radius=5)
    else:  # mesa baixa
        pygame.draw.rect(surface, (53, 32, 24), r, border_radius=6)
        pygame.draw.rect(surface, (142, 87, 49), r.inflate(-7, -7), border_radius=5)
        pygame.draw.line(surface, (190, 135, 85), (r.x+10, r.y+10), (r.right-10, r.y+10), 2)
        for xx in (r.x+12, r.right-18):
            pygame.draw.rect(surface, (55, 34, 25), (xx, r.bottom-4, 6, 10), border_radius=2)


def draw_item_sprite(surface, rect, kind):
    """Ícones desenhados em estilo pixel-art, cada objeto com silhueta própria."""
    x, y, w, h = rect
    cx, cy = rect.center
    if kind == 'fuse':
        pygame.draw.ellipse(surface, (20, 20, 24), (x-3, y+h-5, w+6, 8))
        body = pygame.Rect(x+3, y+5, w-6, h-10)
        pygame.draw.rect(surface, (224, 225, 207), body, border_radius=5)
        pygame.draw.rect(surface, (95, 105, 115), body, 2, border_radius=5)
        pygame.draw.rect(surface, COLOR_GOLD, (cx-4, y+7, 8, h-14), border_radius=2)
        pygame.draw.rect(surface, (165, 175, 185), (x, y+7, 5, h-14), border_radius=2)
        pygame.draw.rect(surface, (165, 175, 185), (x+w-5, y+7, 5, h-14), border_radius=2)
    elif kind == 'battery':
        pygame.draw.rect(surface, (25, 27, 32), (x-3, y+2, w+6, h-2), border_radius=4)
        pygame.draw.rect(surface, (53, 145, 78), (x, y+5, w, h-7), border_radius=3)
        pygame.draw.rect(surface, (170, 180, 175), (x+3, y, w-6, 6), border_radius=2)
        pygame.draw.rect(surface, (230, 230, 205), (x+6, y+8, w-12, 4))
        pygame.draw.line(surface, (235, 235, 220), (cx, y+14), (cx, y+21), 2)
    elif kind == 'medkit':
        pygame.draw.ellipse(surface, (20, 15, 17), (x-3, y+h-5, w+6, 8))
        pygame.draw.rect(surface, (220, 225, 220), rect, border_radius=5)
        pygame.draw.rect(surface, (135, 145, 145), rect, 2, border_radius=5)
        pygame.draw.rect(surface, (205, 42, 52), (cx-4, y+5, 8, h-10), border_radius=1)
        pygame.draw.rect(surface, (205, 42, 52), (x+5, cy-4, w-10, 8), border_radius=1)
        pygame.draw.line(surface, (255,255,255), (x+5,y+5),(x+10,y+5),2)
    elif kind == 'tools':
        pygame.draw.rect(surface, (35, 38, 44), (x-2,y+5,w+4,h-8), border_radius=4)
        pygame.draw.rect(surface, (110, 65, 36), (x,y+8,w,h-11), border_radius=3)
        pygame.draw.arc(surface, (180, 185, 190), (x+5,y-3,w-10,16), math.pi, 2*math.pi, 3)
        pygame.draw.line(surface, (180,190,195),(x+8,y+10),(x+8,y+h-7),4)
        pygame.draw.line(surface, (205,75,65),(x+8,y+10),(x+17,y+3),4)
        pygame.draw.line(surface, (205,205,190),(x+18,y+10),(x+23,y+h-8),3)
    elif kind == 'document':
        pygame.draw.rect(surface, (35, 25, 18), (x+3,y+4,w,h), border_radius=2)
        pygame.draw.rect(surface, (230, 215, 173), rect, border_radius=2)
        pygame.draw.rect(surface, (143, 113, 72), rect, 2, border_radius=2)
        for yy in (y+8,y+14,y+20):
            pygame.draw.line(surface, (120,90,57), (x+5,yy),(x+w-5,yy),1)
        pygame.draw.circle(surface, (160,45,40),(x+w-7,y+7),3)
    elif kind == 'clock':
        pygame.draw.rect(surface, (65, 36, 22), rect.inflate(4,4), border_radius=5)
        pygame.draw.rect(surface, (145, 89, 45), rect, border_radius=4)
        face = pygame.Rect(x+7,y+5,w-14,h-10)
        pygame.draw.ellipse(surface, (221, 199, 145), face)
        pygame.draw.ellipse(surface, (80, 45, 25), face, 2)
        for a in range(12):
            ang = a*math.tau/12
            px,py = cx+math.cos(ang)*(w*.30), cy+math.sin(ang)*(h*.30)
            pygame.draw.circle(surface,(80,50,28),(int(px),int(py)),1)
        pygame.draw.line(surface,(55,35,25),(cx,cy),(cx,cy-12),2)
        pygame.draw.line(surface,(55,35,25),(cx,cy),(cx+9,cy+4),2)
    elif kind == 'panel':
        pygame.draw.rect(surface, (31, 35, 45), rect, border_radius=4)
        pygame.draw.rect(surface, (155, 125, 210), rect, 3, border_radius=4)
        for i, col in enumerate(((105,145,255),(245,200,80),(105,220,150))):
            pygame.draw.circle(surface, col, (x+13+i*15,cy), 5)
            pygame.draw.circle(surface, (230,230,240), (x+13+i*15,cy), 5, 1)
        pygame.draw.line(surface, (120,130,150),(x+7,y+9),(x+w-7,y+9),2)
    elif kind == 'generator':
        pygame.draw.ellipse(surface, (14,16,19),(x-4,y+h-5,w+8,12))
        pygame.draw.rect(surface, (43, 62, 70), rect, border_radius=6)
        pygame.draw.rect(surface, (105, 135, 145), rect, 3, border_radius=6)
        pygame.draw.rect(surface, (20,28,34),(x+8,y+8,w-16,h-18),border_radius=3)
        pygame.draw.circle(surface, (205, 75, 45),(x+17,y+19),5)
        pygame.draw.circle(surface, (75, 205, 125),(x+31,y+19),5)
        pygame.draw.arc(surface, (185, 195, 195),(x+17,y+27,w-30,h-33),0,math.pi,2)
        pygame.draw.line(surface, (205, 175, 80),(x+12,y+h-7),(x+w-12,y+h-7),3)
    elif kind == 'switch':
        pygame.draw.rect(surface, (38, 40, 44), rect.inflate(8,8), border_radius=4)
        pygame.draw.rect(surface, (160, 115, 55), rect, border_radius=3)
        pygame.draw.line(surface, (225, 220, 195),(x+5,y+h-5),(x+w-5,y+5),4)
        pygame.draw.circle(surface, (215, 65, 55),(x+w-5,y+5),4)


# ============================================================
# CRIATURA: patrulha, perseguição e busca
# ============================================================

class Creature:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 36, 44)
        self.spawn = (x, y)
        self.state = "patrol"
        self.speed = 1.45
        self.target = (x + 180, y)
        self.patrol_points = [(x, y), (x + 180, y), (x + 180, y + 150), (x, y + 150)]
        self.patrol_index = 1
        self.last_seen = (x, y)
        self.search_timer = 0

    def update(self, player, world, hidden=False):
        if hidden:
            self.state = "search"
            self.search_timer = max(self.search_timer, 45)
        else:
            dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
            if dist < 270:
                self.state = "chase"
                self.last_seen = player.rect.center
                self.search_timer = 150
            elif self.state == "chase":
                self.state = "search"
            if self.state == "search":
                self.search_timer -= 1
                if self.search_timer <= 0:
                    self.state = "patrol"
        if self.state == "patrol":
            tx, ty = self.patrol_points[self.patrol_index]
            if math.hypot(tx-self.rect.centerx, ty-self.rect.centery) < 12:
                self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)
                tx, ty = self.patrol_points[self.patrol_index]
        elif self.state == "chase":
            tx, ty = player.rect.center
        else:
            tx, ty = self.last_seen
        dx, dy = tx - self.rect.centerx, ty - self.rect.centery
        length = math.hypot(dx, dy)
        if length > 3:
            dx, dy = dx / length * self.speed, dy / length * self.speed
            oldx, oldy = self.rect.x, self.rect.y
            self.rect.x += round(dx)
            if world.get_collision(self.rect): self.rect.x = oldx
            self.rect.y += round(dy)
            if world.get_collision(self.rect): self.rect.y = oldy

    def draw(self, surface, camera):
        r = camera.apply(self.rect)
        color = (150, 35, 45) if self.state == "chase" else (95, 45, 55)
        pygame.draw.ellipse(surface, color, r)
        pygame.draw.circle(surface, (255, 70, 65), (r.x + 10, r.y + 15), 3)
        pygame.draw.circle(surface, (255, 70, 65), (r.x + 25, r.y + 15), 3)
        pygame.draw.line(surface, (20, 10, 15), (r.x+9, r.bottom-10), (r.right-8, r.bottom-10), 3)


# ============================================================
# GERENCIADOR DE JOGO (ENGINE)
# ============================================================

class GameEngine:
    def __init__(self):
        self.camera = Camera()
        self.world = World()
        self.player = Player(180, 1200)
        self.achievements = AchievementManager()

        # Objetos no Mapa
        self.key_gold = pygame.Rect(600, 950, 30, 30)
        self.note = pygame.Rect(1010, 930, 44, 52)  # Na sala central, acessível antes de abrir o cofre
        self.safe_box = pygame.Rect(1300, 1050, 85, 70)
        self.key_red = pygame.Rect(1450, 1120, 30, 30)  # No chão, afastada do cofre para ser coletável
        self.exit_door = pygame.Rect(2900, 1650, 45, 160)
        self.east_wing_unlocked = False
        # Novos enigmas e itens da ala leste / laboratório
        self.clock_obj = pygame.Rect(2580, 1040, 55, 55)
        self.symbol_panel = pygame.Rect(2820, 1040, 55, 55)
        self.generator = pygame.Rect(2820, 1370, 75, 65)
        self.fuse_item = pygame.Rect(2460, 1100, 25, 25)
        self.battery_item = pygame.Rect(2650, 1390, 25, 25)
        self.medkit_item = pygame.Rect(2870, 1130, 28, 28)
        self.tools_item = pygame.Rect(2720, 1430, 30, 30)
        self.document_item = pygame.Rect(2860, 1450, 30, 36)
        self.hidden_switch = pygame.Rect(2600, 1270, 22, 22)
        self.creature = Creature(2660, 1500)
        self.health = 100
        self.battery = 100.0
        self.has_fuse = False
        self.has_battery = False
        self.has_medkit = False
        self.has_tools = False
        self.power_restored = False
        self.clock_solved = False
        self.symbols_solved = False
        self.secret_passage_open = False
        self.hidden = False
        self.evidence = set()
        self.final_choice_open = False
        self.ending = None
        self.damage_cooldown = 0

        # Flags
        self.has_gold_key = False
        self.has_red_key = False
        self.read_note = False
        self.safe_unlocked = False

        self.in_cutscene = True
        self.in_credits = False

        self.inventory_open = False
        self.active_puzzle = None
        self.puzzle_code_input = ""
        self.note_open = False
        self.game_won = False

        self.message_text = "Você acordou em uma mansão trancada..."
        self.message_timer = 300

    def show_message(self, text, duration=240):
        self.message_text = text
        self.message_timer = duration

    def trigger_interaction(self):
        if self.in_cutscene or self.inventory_open or self.active_puzzle or self.game_won or self.in_credits:
            return

        p_center = self.player.rect.center

        # Itens de sobrevivência e pistas: priorizados antes de objetos grandes.
        def near(obj, radius=82):
            return math.hypot(p_center[0] - obj.centerx, p_center[1] - obj.centery) < radius

        if not self.has_fuse and near(self.fuse_item):
            self.has_fuse = True
            self.show_message("Você encontrou um fusível. Leve-o ao gerador!")
            return
        if not self.has_battery and near(self.battery_item):
            self.has_battery = True
            self.battery = min(100, self.battery + 35)
            self.show_message("Pilhas encontradas: bateria da lanterna recarregada!")
            return
        if not self.has_medkit and near(self.medkit_item):
            self.has_medkit = True
            self.health = min(100, self.health + 35)
            self.show_message("Você encontrou um kit médico. Pressione M para usá-lo depois de sofrer dano.")
            return
        if not self.has_tools and near(self.tools_item):
            self.has_tools = True
            self.show_message("Você encontrou ferramentas. Agora pode abrir o painel de manutenção.")
            return
        if near(self.document_item):
            if "diario" not in self.evidence:
                self.evidence.add("diario")
                self.show_message("Diário: 'O relógio marca 10:10; os símbolos seguem Lua, Sol, Lua. Os últimos dígitos do cofre são 2-9.'")
            else:
                self.show_message("O diário descreve os experimentos do antigo dono.")
            if len(self.evidence) >= 3:
                self.achievements.unlock("evidence")
            return
        if near(self.clock_obj):
            if not self.clock_solved:
                self.active_puzzle = "CLOCK"
                self.puzzle_code_input = ""
            else:
                self.show_message("O relógio está ajustado para 10:10.")
            return
        if near(self.symbol_panel):
            if not self.symbols_solved:
                self.active_puzzle = "SYMBOLS"
                self.puzzle_code_input = ""
            else:
                self.show_message("O painel de símbolos já está desbloqueado.")
            return
        if near(self.generator):
            if self.power_restored:
                self.show_message("O gerador está funcionando.")
            elif self.has_fuse:
                self.active_puzzle = "POWER"
                self.puzzle_code_input = ""
            else:
                self.show_message("Falta um fusível para ligar o gerador.")
            return
        if near(self.hidden_switch):
            self.secret_passage_open = True
            self.show_message("Você acionou uma alavanca! Uma passagem secreta se abriu.")
            self.evidence.add("passagem")
            return

        # Portas
        for door in self.world.doors:
            if not door.is_open and math.hypot(p_center[0] - door.rect.centerx, p_center[1] - door.rect.centery) < 100:
                if door.door_id == "door_east_wing":
                    if self.has_gold_key and self.has_red_key:
                        door.is_open = True
                        self.east_wing_unlocked = True
                        self.show_message("A ala leste foi liberada! Explore o laboratório e o sótão subterrâneo.")
                        self.achievements.unlock("open_door")
                    else:
                        self.show_message("A porta da ala leste exige as chaves dourada e vermelha.")
                    return
                if door.required_key_id == "gold_key" and self.has_gold_key:
                    door.is_open = True
                    self.show_message("Você abriu a porta com a Chave Dourada!")
                    self.achievements.unlock("open_door")
                    return
                elif door.required_key_id == "red_key" and self.has_red_key:
                    door.is_open = True
                    self.show_message("Você abriu a porta com a Chave Vermelha!")
                    self.achievements.unlock("open_door")
                    return
                else:
                    self.show_message("A porta está trancada. Encontre a chave correspondente!")
                    return

        # Chave Dourada
        if not self.has_gold_key and math.hypot(p_center[0] - self.key_gold.centerx, p_center[1] - self.key_gold.centery) < 80:
            self.has_gold_key = True
            self.show_message("Você pegou a CHAVE DOURADA!")
            self.achievements.unlock("gold_key")
            return

        # Papel com código: continua no cenário e pode ser examinado novamente.
        if math.hypot(p_center[0] - self.note.centerx, p_center[1] - self.note.centery) < 90:
            self.note_open = True
            if not self.read_note:
                self.read_note = True
                self.show_message("Você leu o folheto! O código é 4729.")
                self.achievements.unlock("read_note")
            return

        # Chave vermelha: verificar ANTES do cofre para não bloquear a coleta.
        # Ela só aparece depois que o cofre é aberto e fica no chão, ao lado dele.
        if self.safe_unlocked and not self.has_red_key and math.hypot(p_center[0] - self.key_red.centerx, p_center[1] - self.key_red.centery) < 85:
            self.has_red_key = True
            self.show_message("Você pegou a CHAVE VERMELHA! Ela está no inventário.")
            self.achievements.unlock("red_key")
            return

        # Cofre
        if math.hypot(p_center[0] - self.safe_box.centerx, p_center[1] - self.safe_box.centery) < 95:
            if not self.safe_unlocked:
                self.active_puzzle = "SAFE"
                self.puzzle_code_input = ""
            else:
                self.show_message("O cofre está aberto. Procure a chave vermelha no chão!")
            return

        # Porta Final
        if math.hypot(p_center[0] - self.exit_door.centerx, p_center[1] - self.exit_door.centery) < 110:
            if self.has_gold_key and self.has_red_key and self.east_wing_unlocked:
                self.game_won = True
                if self.clock_solved and self.symbols_solved and self.power_restored and len(self.evidence) >= 3:
                    self.ending = "verdadeiro"
                    self.show_message("Final verdadeiro: você revelou o segredo da mansão.")
                elif self.evidence:
                    self.ending = "secreto"
                else:
                    self.ending = "normal"
                self.achievements.unlock("escape")
            else:
                self.show_message("Encontre as duas chaves e libere o portão da ala leste!")

    def handle_puzzle_input(self, event):
        if event.key == pygame.K_ESCAPE:
            self.active_puzzle = None
            return
        if self.active_puzzle == "CLOCK":
            if event.key == pygame.K_RETURN:
                if self.puzzle_code_input == "1010":
                    self.clock_solved = True
                    self.active_puzzle = None
                    self.show_message("Relógio ajustado! Um compartimento secreto se abriu.")
                    self.achievements.unlock("clock")
                    self.evidence.add("relogio")
                else:
                    self.show_message("Horário incorreto. A pista indica 10:10.")
                    self.puzzle_code_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self.puzzle_code_input = self.puzzle_code_input[:-1]
            elif event.unicode.isdigit() and len(self.puzzle_code_input) < 4:
                self.puzzle_code_input += event.unicode
            return
        if self.active_puzzle == "SYMBOLS":
            if event.key == pygame.K_RETURN:
                if self.puzzle_code_input.upper() == "LSL":
                    self.symbols_solved = True
                    self.active_puzzle = None
                    self.show_message("Sequência correta! O painel liberou o acesso ao laboratório.")
                    self.achievements.unlock("symbols")
                    self.evidence.add("simbolos")
                else:
                    self.show_message("Sequência errada. Consulte o diário: Lua, Sol, Lua.")
                    self.puzzle_code_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self.puzzle_code_input = self.puzzle_code_input[:-1]
            elif event.unicode.upper() in "LS" and len(self.puzzle_code_input) < 3:
                self.puzzle_code_input += event.unicode.upper()
            return
        if self.active_puzzle == "POWER":
            if event.key == pygame.K_RETURN:
                if self.puzzle_code_input == "314":
                    self.power_restored = True
                    self.has_fuse = False
                    self.active_puzzle = None
                    self.show_message("Energia restaurada! A iluminação da ala leste voltou.")
                    self.achievements.unlock("power")
                    self.evidence.add("energia")
                else:
                    self.show_message("Sequência incorreta. A etiqueta do gerador diz 3-1-4.")
                    self.puzzle_code_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self.puzzle_code_input = self.puzzle_code_input[:-1]
            elif event.unicode.isdigit() and len(self.puzzle_code_input) < 3:
                self.puzzle_code_input += event.unicode
            return
        if event.key == pygame.K_BACKSPACE:
            self.puzzle_code_input = self.puzzle_code_input[:-1]
        elif event.key == pygame.K_RETURN:
            if self.puzzle_code_input == "4729":
                self.safe_unlocked = True
                self.active_puzzle = None
                self.show_message("Cofre aberto! A Chave Vermelha está dentro.")
                self.achievements.unlock("safe")
            else:
                self.show_message("Código incorreto!")
                self.puzzle_code_input = ""
        elif event.unicode.isdigit() and len(self.puzzle_code_input) < 4:
            self.puzzle_code_input += event.unicode

    def update(self):
        if self.in_cutscene or self.in_credits or self.note_open:
            return

        if self.message_timer > 0:
            self.message_timer -= 1
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
        if self.battery > 0 and not self.in_cutscene:
            self.battery = max(0, self.battery - 0.012)

        if not self.active_puzzle and not self.inventory_open and not self.game_won and not self.note_open:
            dx, dy = self.player.handle_input(self.achievements)
            self.player.move(dx, dy, self.world)

        # A criatura ronda o laboratório; esconder-se com H interrompe a detecção.
        self.creature.update(self.player, self.world, self.hidden)
        if self.hidden:
            self.hidden = False
        elif self.creature.rect.colliderect(self.player.rect) and self.damage_cooldown <= 0:
            self.health = max(0, self.health - 15)
            self.damage_cooldown = 90
            self.show_message("A criatura atingiu você! Pressione H perto de móveis para se esconder.")
            if self.health <= 0:
                self.ending = "capturado"
                self.game_won = True

        self.camera.update(self.player.rect)
        self.achievements.update()

    def render_lighting(self):
        dark_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        dark_surf.fill((8, 10, 15, 220))

        p_screen = self.camera.apply_pos(self.player.rect.center)
        angle_rad = math.radians(self.player.angle)

        cone_surface = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        poly_points = [p_screen]
        spread = 35.0
        distance = 260.0 if self.battery > 0 else 95.0

        for a in range(int(-spread), int(spread) + 1, 5):
            rad = angle_rad + math.radians(a)
            px = p_screen[0] + math.cos(rad) * distance
            py = p_screen[1] + math.sin(rad) * distance
            poly_points.append((px, py))

        if len(poly_points) > 2:
            pygame.draw.polygon(cone_surface, (255, 240, 200, 160), poly_points)

        pygame.draw.circle(cone_surface, (255, 245, 220, 180), p_screen, 75 if self.battery > 0 else 28)
        dark_surf.blit(cone_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        screen.blit(dark_surf, (0, 0))

    def render_ui(self):
        pygame.draw.rect(screen, COLOR_GRAY_DARK, (0, 0, SCREEN_W, 60))
        pygame.draw.line(screen, COLOR_WALL_BORDER, (0, 60), (SCREEN_W, 60), 2)

        screen.blit(font_main.render("MANSÃO DOS MISTÉRIOS", True, COLOR_WHITE), (20, 18))

        # BARRA DE VIGOR
        pygame.draw.rect(screen, (15, 15, 20), (320, 22, 160, 16), border_radius=4)
        stamina_w = int((self.player.stamina / self.player.max_stamina) * 156)
        if stamina_w > 0:
            col_st = COLOR_YELLOW if self.player.stamina > 20 else COLOR_RED
            pygame.draw.rect(screen, col_st, (322, 24, stamina_w, 12), border_radius=3)
        screen.blit(font_micro.render("VIGOR (LSHIFT)", True, COLOR_GRAY_LIGHT), (320, 8))

        screen.blit(font_small.render("[E] Interagir | [TAB] Inventário | [H] Esconder", True, COLOR_GRAY_LIGHT), (500, 20))
        pygame.draw.rect(screen, (15, 15, 20), (720, 42, 110, 10), border_radius=3)
        pygame.draw.rect(screen, COLOR_RED, (722, 44, int(106 * self.health / 100), 6), border_radius=3)
        screen.blit(font_micro.render(f"VIDA {self.health}%", True, COLOR_WHITE), (720, 8))
        pygame.draw.rect(screen, (15, 15, 20), (850, 42, 100, 10), border_radius=3)
        pygame.draw.rect(screen, COLOR_YELLOW, (852, 44, int(96 * self.battery / 100), 6), border_radius=3)
        screen.blit(font_micro.render(f"LANTERNA {int(self.battery)}%", True, COLOR_WHITE), (850, 8))

        # Indicadores de Chaves no topo da UI
        pygame.draw.circle(screen, COLOR_GOLD if self.has_gold_key else COLOR_GRAY_DARK, (980, 30), 12)
        pygame.draw.circle(screen, COLOR_RED if self.has_red_key else COLOR_GRAY_DARK, (1030, 30), 12)

        # Mensagem
        if self.message_timer > 0 and not self.game_won:
            msg_box = pygame.Rect(SCREEN_W // 2 - 300, SCREEN_H - 80, 600, 45)
            pygame.draw.rect(screen, COLOR_GRAY_DARK, msg_box, border_radius=10)
            pygame.draw.rect(screen, COLOR_PURPLE_LIGHT, msg_box, 2, border_radius=10)
            txt = font_small.render(self.message_text, True, COLOR_WHITE)
            screen.blit(txt, txt.get_rect(center=msg_box.center))

        # Notificações de Conquistas
        self.achievements.draw_notifications(screen)

    def render_cutscene(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H))
        overlay.fill((5, 6, 10))
        screen.blit(overlay, (0, 0))

        txt_t = font_title.render("A MANSÃO ABANDONADA", True, COLOR_GOLD)
        screen.blit(txt_t, txt_t.get_rect(center=(SCREEN_W // 2, 120)))

        lines = [
            "Você acordou preso no porão sombrio desta mansão.",
            "Para escapar, você precisa explorar os cômodos e achar as chaves.",
            "",
            "CONTROLES DO JOGO:",
            "• WASD / Setas : Movimentar o personagem",
            "• LSHIFT        : Correr (consome Vigor)",
            "• Tecla E       : Interagir com portas, cofres e itens",
            "• Tecla TAB     : Abrir / Fechar Inventário",
            "• Tecla H       : Esconder-se perto de móveis",
            "• Tecla M       : Usar kit médico do inventário",
            "• Teclas L/S    : Sequência de símbolos (Lua/Sol)",
            "",
            "DICA: Fique atento às portas trancadas entre as salas!"
        ]

        y_offset = 200
        for line in lines:
            if "CONTROLES" in line:
                color = COLOR_PURPLE_LIGHT
                f = font_main
            elif "DICA" in line:
                color = COLOR_YELLOW
                f = font_small
            else:
                color = COLOR_WHITE
                f = font_small

            txt = f.render(line, True, color)
            screen.blit(txt, txt.get_rect(center=(SCREEN_W // 2, y_offset)))
            y_offset += 32

        pulse = int(120 + 135 * abs(math.sin(pygame.time.get_ticks() * 0.004)))
        btn_color = (pulse, pulse, 50)
        btn = font_big.render("Pressione [ ESPAÇO ] para Começar", True, btn_color)
        screen.blit(btn, btn.get_rect(center=(SCREEN_W // 2, 590)))

        btn_cred = font_small.render("Pressione [ C ] para ver os Créditos", True, COLOR_GRAY_LIGHT)
        screen.blit(btn_cred, btn_cred.get_rect(center=(SCREEN_W // 2, 640)))

    def render_credits(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H))
        overlay.fill((8, 10, 15))
        screen.blit(overlay, (0, 0))

        txt_t = font_title.render("CRÉDITOS DO JOGO", True, COLOR_GOLD)
        screen.blit(txt_t, txt_t.get_rect(center=(SCREEN_W // 2, 100)))

        credits_text = [
            ("DESENVOLVIMENTO & PROGRAMAÇÃO", COLOR_PURPLE_LIGHT),
            ("Criado com Pygame em Python", COLOR_WHITE),
            ("", COLOR_WHITE),
            ("DESIGN DE ARTE & ILUMINAÇÃO", COLOR_PURPLE_LIGHT),
            ("Gráficos Procedurais 2D Dinâmicos", COLOR_WHITE),
            ("", COLOR_WHITE),
            ("SISTEMAS & PUZZLES", COLOR_PURPLE_LIGHT),
            ("Escape Room 2D Engine", COLOR_WHITE),
            ("", COLOR_WHITE),
            ("AGRADECIMENTOS ESPECIAIS", COLOR_GOLD),
            ("A todos os jogadores e entusiastas de jogos indie!", COLOR_WHITE)
        ]

        y = 200
        for line, color in credits_text:
            if line != "":
                txt = font_main.render(line, True, color)
                screen.blit(txt, txt.get_rect(center=(SCREEN_W // 2, y)))
            y += 35

        btn = font_big.render("Pressione [ ESC ] para Voltar", True, COLOR_YELLOW)
        screen.blit(btn, btn.get_rect(center=(SCREEN_W // 2, 620)))

    def render_inventory(self):
        if not self.inventory_open: return

        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(SCREEN_W // 2 - 250, SCREEN_H // 2 - 180, 500, 360)
        pygame.draw.rect(screen, COLOR_GRAY_DARK, panel, border_radius=16)
        pygame.draw.rect(screen, COLOR_WALL_BORDER, panel, 3, border_radius=16)

        title = font_big.render("INVENTÁRIO DE ITENS", True, COLOR_WHITE)
        screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 40)))

        items = [
            ("Chave Dourada", self.has_gold_key, COLOR_GOLD),
            ("Chave Vermelha", self.has_red_key, COLOR_RED),
            ("Bilhete", self.read_note, COLOR_PAPER),
            ("Fusível", self.has_fuse, COLOR_YELLOW),
            ("Pilhas", self.has_battery, COLOR_GREEN),
            ("Kit médico", self.has_medkit, COLOR_RED),
            ("Ferramentas", self.has_tools, COLOR_GRAY_LIGHT),
        ]

        for i, (name, unlocked, col) in enumerate(items):
            col_i, row_i = i % 3, i // 3
            slot = pygame.Rect(panel.x + 20 + col_i * 155, panel.y + 85 + row_i * 125, 140, 105)
            pygame.draw.rect(screen, (15, 17, 23), slot, border_radius=10)
            pygame.draw.rect(screen, col if unlocked else COLOR_WALL_BORDER, slot, 2, border_radius=10)

            status_txt = "POSSUI" if unlocked else "???"
            txt_n = font_small.render(name, True, COLOR_WHITE if unlocked else COLOR_GRAY_LIGHT)
            txt_s = font_micro.render(status_txt, True, COLOR_GREEN if unlocked else COLOR_RED)

            screen.blit(txt_n, txt_n.get_rect(center=(slot.centerx, slot.y + 35)))
            screen.blit(txt_s, txt_s.get_rect(center=(slot.centerx, slot.y + 72)))

    def render_puzzle(self):
        if not self.active_puzzle: return

        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(SCREEN_W // 2 - 180, SCREEN_H // 2 - 150, 360, 300)
        pygame.draw.rect(screen, COLOR_GRAY_DARK, panel, border_radius=16)

        puzzle_titles = {"SAFE": "COFRE TRANCADO", "CLOCK": "RELÓGIO ANTIGO", "SYMBOLS": "PAINEL DE SÍMBOLOS", "POWER": "GERADOR ELÉTRICO"}
        title = font_big.render(puzzle_titles.get(self.active_puzzle, "ENIGMA"), True, COLOR_WHITE)
        screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 40)))

        display_box = pygame.Rect(panel.centerx - 70, panel.y + 120, 140, 50)
        pygame.draw.rect(screen, (10, 12, 16), display_box, border_radius=8)

        code_str = (self.puzzle_code_input + "____")[:4]
        txt_code = font_title.render(" ".join(code_str), True, COLOR_GOLD)
        screen.blit(txt_code, txt_code.get_rect(center=display_box.center))
        hints = {"SAFE": "Junte o folheto (4-7) e o diário (2-9)", "CLOCK": "Ajuste o horário: 1010", "SYMBOLS": "Lua, Sol, Lua: digite LSL", "POWER": "Etiqueta do gerador: 314"}
        hint = font_small.render(hints.get(self.active_puzzle, "Digite e pressione ENTER"), True, COLOR_GRAY_LIGHT)
        screen.blit(hint, hint.get_rect(center=(panel.centerx, panel.y + 215)))
        close_hint = font_micro.render("ESC para fechar", True, COLOR_GRAY_LIGHT)
        screen.blit(close_hint, close_hint.get_rect(center=(panel.centerx, panel.bottom - 20)))

    def render_note(self):
        if not self.note_open:
            return
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 205))
        screen.blit(overlay, (0, 0))

        paper = pygame.Rect(SCREEN_W // 2 - 190, SCREEN_H // 2 - 210, 380, 420)
        pygame.draw.rect(screen, (80, 65, 43), paper.move(7, 8), border_radius=5)
        pygame.draw.rect(screen, (225, 212, 175), paper, border_radius=5)
        pygame.draw.rect(screen, (155, 132, 91), paper, 3, border_radius=5)

        # Bordas e marcas envelhecidas do papel
        for i in range(8):
            x = paper.x + 18 + i * 45
            pygame.draw.line(screen, (195, 177, 133), (x, paper.y + 8), (x + 4, paper.y + 15), 2)
            pygame.draw.line(screen, (195, 177, 133), (x, paper.bottom - 15), (x + 4, paper.bottom - 8), 2)

        title = font_big.render("BILHETE MISTERIOSO", True, (70, 48, 30))
        screen.blit(title, title.get_rect(center=(paper.centerx, paper.y + 55)))
        lines = [
            ("Se encontrou este papel...", font_small),
            ("procure o cofre escondido.", font_small),
            ("", font_small),
            ("Primeira parte da senha:", font_main),
            ("4  -  7  -  ?  -  ?", font_title),
            ("Leia o diário na ala leste para completar.", font_small),
        ]
        y = paper.y + 125
        for line, f in lines:
            if line:
                color = (145, 35, 30) if "4  -  7" in line else (80, 54, 34)
                txt = f.render(line, True, color)
                screen.blit(txt, txt.get_rect(center=(paper.centerx, y)))
            y += 42
        hint = font_small.render("[E] ou [ESC] para fechar", True, (70, 48, 30))
        screen.blit(hint, hint.get_rect(center=(paper.centerx, paper.bottom - 35)))

    def draw(self):
        if self.in_credits:
            self.render_credits()
            return

        if self.in_cutscene:
            self.render_cutscene()
            return

        if self.game_won:
            screen.fill(COLOR_BG)
            ending_titles = {"normal": "VOCÊ ESCAPOU!", "secreto": "FINAL SECRETO DESBLOQUEADO!", "verdadeiro": "FINAL VERDADEIRO: O SEGREDO REVELADO!", "capturado": "A CRIATURA TE CAPTUROU..."}
            ending_text = ending_titles.get(self.ending, "VOCÊ ESCAPOU COM SUCESSO!")
            txt = font_big.render(ending_text, True, COLOR_GOLD if self.ending != "capturado" else COLOR_RED)
            screen.blit(txt, txt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 50)))

            unlocked_count = sum(1 for a in self.achievements.achievements.values() if a["unlocked"])
            total_count = len(self.achievements.achievements)
            txt_ach = font_main.render(f"Conquistas Desbloqueadas: {unlocked_count}/{total_count}", True, COLOR_WHITE)
            screen.blit(txt_ach, txt_ach.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 30)))

            btn = font_small.render("Pressione [ C ] para ver os Créditos", True, COLOR_GRAY_LIGHT)
            screen.blit(btn, btn.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 100)))
            return

        self.world.draw(screen, self.camera)

        # Desenhar Chave Dourada se não foi pega
        if not self.has_gold_key:
            draw_real_key(screen, self.camera.apply_pos(self.key_gold.center), COLOR_GOLD)

        # Folheto claramente visível no cenário, com linhas e símbolo de pista.
        r = self.camera.apply(self.note)
        pygame.draw.rect(screen, (24, 20, 17), r.move(3, 4), border_radius=3)
        pygame.draw.rect(screen, COLOR_PAPER, r, border_radius=3)
        pygame.draw.rect(screen, (155, 132, 91), r, 2, border_radius=3)
        pygame.draw.line(screen, (130, 95, 55), (r.x + 7, r.y + 12), (r.right - 7, r.y + 12), 2)
        pygame.draw.line(screen, (130, 95, 55), (r.x + 7, r.y + 20), (r.right - 7, r.y + 20), 2)
        pygame.draw.line(screen, (130, 95, 55), (r.x + 7, r.y + 28), (r.right - 7, r.y + 28), 2)
        mark = font_micro.render("?", True, (145, 35, 30))
        screen.blit(mark, mark.get_rect(center=(r.centerx, r.bottom - 7)))

        r = self.camera.apply(self.safe_box)
        draw_safe(screen, r)

        # Chave vermelha visível no chão após abrir o cofre.
        if self.safe_unlocked and not self.has_red_key:
            key_pos = self.camera.apply_pos(self.key_red.center)
            draw_real_key(screen, key_pos, COLOR_RED)

        # Dicas contextuais deixam claro quais objetos aceitam interação.
        p_center = self.player.rect.center
        nearby = None
        if not self.has_gold_key and math.hypot(p_center[0] - self.key_gold.centerx, p_center[1] - self.key_gold.centery) < 90:
            nearby = ("[E] Pegar chave dourada", self.camera.apply(self.key_gold))
        elif math.hypot(p_center[0] - self.note.centerx, p_center[1] - self.note.centery) < 100:
            nearby = ("[E] Examinar folheto", self.camera.apply(self.note))
        elif self.safe_unlocked and not self.has_red_key and math.hypot(p_center[0] - self.key_red.centerx, p_center[1] - self.key_red.centery) < 100:
            nearby = ("[E] Pegar chave vermelha", self.camera.apply(self.key_red))
        elif math.hypot(p_center[0] - self.safe_box.centerx, p_center[1] - self.safe_box.centery) < 110:
            nearby = ("[E] Examinar cofre", self.camera.apply(self.safe_box))
        # Contexto de interação dos novos objetos.
        for obj, label, visible in [
            (self.fuse_item, "[E] Pegar fusível", not self.has_fuse),
            (self.battery_item, "[E] Pegar pilhas", not self.has_battery),
            (self.medkit_item, "[E] Pegar kit médico", not self.has_medkit),
            (self.tools_item, "[E] Pegar ferramentas", not self.has_tools),
            (self.document_item, "[E] Ler diário", True),
            (self.clock_obj, "[E] Examinar relógio", True),
            (self.symbol_panel, "[E] Examinar símbolos", True),
            (self.generator, "[E] Interagir com gerador", True),
            (self.hidden_switch, "[E] Acionar alavanca secreta", True),
        ]:
            if visible and math.hypot(p_center[0]-obj.centerx, p_center[1]-obj.centery) < 90:
                nearby = (label, self.camera.apply(obj))
                break
        if nearby:
            prompt = font_small.render(nearby[0], True, COLOR_WHITE)
            prompt_bg = prompt.get_rect(midbottom=(SCREEN_W // 2, SCREEN_H - 95)).inflate(20, 12)
            pygame.draw.rect(screen, (20, 25, 35), prompt_bg, border_radius=7)
            pygame.draw.rect(screen, COLOR_YELLOW, prompt_bg, 2, border_radius=7)
            screen.blit(prompt, prompt.get_rect(center=prompt_bg.center))

        r = self.camera.apply(self.exit_door)
        door_col = (48, 105, 70) if self.has_red_key and self.has_gold_key else (105, 38, 42)
        pygame.draw.rect(screen, (25, 20, 20), r.move(3, 4), border_radius=4)
        pygame.draw.rect(screen, door_col, r, border_radius=4)
        pygame.draw.rect(screen, (170, 125, 75), r, 3, border_radius=4)
        pygame.draw.rect(screen, (65, 40, 29), r.inflate(-12, -12), 2, border_radius=3)
        pygame.draw.circle(screen, COLOR_GOLD, (r.right-10, r.centery), 4)
        pygame.draw.circle(screen, (35, 25, 20), (r.right-10, r.centery), 2)

        # Itens ilustrados individualmente (chaves, fusível, pilhas, kit, ferramentas, diário).
        for obj, visible, kind in [
            (self.fuse_item, not self.has_fuse, 'fuse'),
            (self.battery_item, not self.has_battery, 'battery'),
            (self.medkit_item, not self.has_medkit, 'medkit'),
            (self.tools_item, not self.has_tools, 'tools'),
            (self.document_item, True, 'document'),
        ]:
            if visible:
                rr = self.camera.apply(obj)
                draw_item_sprite(screen, rr, kind)
        for obj, kind in [(self.clock_obj, 'clock'), (self.symbol_panel, 'panel'), (self.generator, 'generator'), (self.hidden_switch, 'switch')]:
            rr = self.camera.apply(obj)
            draw_item_sprite(screen, rr, kind)
        if self.secret_passage_open:
            rr = self.camera.apply(pygame.Rect(2165, 1100, 90, 100))
            pygame.draw.rect(screen, (15, 18, 22), rr, border_radius=4)
            pygame.draw.rect(screen, COLOR_GREEN, rr, 2, border_radius=4)
        self.creature.draw(screen, self.camera)
        self.player.draw(screen, self.camera)

        self.render_lighting()
        self.render_ui()
        self.render_inventory()
        self.render_puzzle()
        self.render_note()


# ============================================================
# LOOP PRINCIPAL
# ============================================================

def main():
    engine = GameEngine()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if engine.in_credits:
                    if event.key == pygame.K_ESCAPE:
                        engine.in_credits = False
                    continue

                if engine.in_cutscene:
                    if event.key == pygame.K_SPACE:
                        engine.in_cutscene = False
                    elif event.key == pygame.K_c:
                        engine.in_credits = True
                    continue

                if engine.game_won:
                    if event.key == pygame.K_c:
                        engine.in_credits = True
                    continue

                if engine.note_open:
                    if event.key in (pygame.K_ESCAPE, pygame.K_e, pygame.K_SPACE):
                        engine.note_open = False
                    continue

                if engine.active_puzzle:
                    engine.handle_puzzle_input(event)
                else:
                    if event.key == pygame.K_e:
                        engine.trigger_interaction()
                    elif event.key == pygame.K_TAB:
                        engine.inventory_open = not engine.inventory_open
                    elif event.key == pygame.K_h:
                        # Esconder-se atrás de móveis próximos reduz a detecção da criatura.
                        near_furniture = any(engine.player.rect.inflate(100, 100).colliderect(f) for f in engine.world.furniture)
                        if near_furniture:
                            engine.hidden = True
                            engine.show_message("Você se escondeu por um instante.")
                        else:
                            engine.show_message("Aproxime-se de um móvel para se esconder.")
                    elif event.key == pygame.K_m:
                        if engine.has_medkit and engine.health < 100:
                            engine.health = min(100, engine.health + 40)
                            engine.has_medkit = False
                            engine.show_message("Kit médico utilizado. Vida restaurada.")

        engine.update()
        engine.draw()

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()