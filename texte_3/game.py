import pygame
import sqlite3
import random

# Configurações
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
PLAYER_SIZE = 50
ITEM_SIZE = 40
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
TRANSPARENT_BLACK = (0, 0, 0, 128)
TIME_LIMIT = 60  # segundos

# Inicializa o Pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Carregar e tocar música
pygame.mixer.music.load('principal.mp3')  # Substitua pelo caminho do seu arquivo de música
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Carregar o som do efeito
try:
    coin_sound = pygame.mixer.Sound('coins.mp3')  # Substitua pelo caminho do seu arquivo de efeito
    coin_sound.set_volume(0.5)  # Configura o volume do som do efeito
    print("Som do efeito carregado com sucesso.")
except pygame.error as e:
    print(f"Erro ao carregar o som do efeito: {e}")
    pygame.quit()
    exit()

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Jogo de Coleta')

# Carregar imagens
try:
    player_image = pygame.image.load('pec.png')
    player_image = pygame.transform.scale(player_image, (PLAYER_SIZE, PLAYER_SIZE))
    print("Imagem do jogador carregada com sucesso.")
except pygame.error as e:
    print(f"Erro ao carregar a imagem do jogador: {e}")
    pygame.quit()
    exit()

try:
    item_image = pygame.image.load('item.png')
    item_image = pygame.transform.scale(item_image, (ITEM_SIZE, ITEM_SIZE))
    print("Imagem do item carregada com sucesso.")
except pygame.error as e:
    print(f"Erro ao carregar a imagem do item: {e}")
    pygame.quit()
    exit()

try:
    menu_image = pygame.image.load('OIG3.jpeg')
    menu_image = pygame.transform.scale(menu_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
    print("Imagem do menu carregada com sucesso.")
except pygame.error as e:
    print(f"Erro ao carregar a imagem do menu: {e}")
    pygame.quit()
    exit()

# Configuração do jogador e item
player = pygame.Rect(150, 150, PLAYER_SIZE, PLAYER_SIZE)
item = pygame.Rect(0, 0, ITEM_SIZE, ITEM_SIZE)
player_speed = 5
score = 0
item_color = RED

maze_walls = [
    pygame.Rect(100, 100, 600, 20),
    pygame.Rect(100, 100, 20, 400),
    pygame.Rect(100, 480, 600, 20),
    pygame.Rect(680, 100, 20, 400),
    pygame.Rect(200, 200, 20, 200),
    pygame.Rect(300, 100, 20, 200),
    pygame.Rect(400, 300, 20, 200),
    pygame.Rect(500, 200, 20, 200),
]

# Funções e lógica do jogo seguem aqui...

def setup_database():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    level INTEGER
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS rankings (
                    id INTEGER PRIMARY KEY,
                    player_name TEXT,
                    score INTEGER
                )''')
    conn.commit()
    conn.close()

def update_score(player_name, score):
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute('INSERT INTO rankings (player_name, score) VALUES (?, ?)', (player_name, score))
    conn.commit()
    conn.close()

def get_rankings():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute('SELECT player_name, score FROM rankings ORDER BY score DESC LIMIT 10')
    rankings = c.fetchall()
    conn.close()
    return rankings

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def is_position_valid(rect):
    if (rect.left < 100 or rect.right > WINDOW_WIDTH - 100 or
        rect.top < 100 or rect.bottom > WINDOW_HEIGHT - 100):
        return False
    for wall in maze_walls:
        if rect.colliderect(wall):
            return False
    return True

def place_item_within_bounds():
    while True:
        x = random.randint(100, WINDOW_WIDTH - ITEM_SIZE - 100)
        y = random.randint(100, WINDOW_HEIGHT - ITEM_SIZE - 100)
        item_rect = pygame.Rect(x, y, ITEM_SIZE, ITEM_SIZE)
        if is_position_valid(item_rect):
            return item_rect

def draw_transparent_rect(surface, color, rect):
    temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    temp_surface.fill(color)
    surface.blit(temp_surface, rect)

def show_menu():
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)
    menu_running = True

    while menu_running:
        screen.blit(menu_image, (0, 0))
        draw_transparent_rect(screen, TRANSPARENT_BLACK, pygame.Rect(150, 100, 500, 300))
        draw_text('Pick coins', font, WHITE, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100)
        draw_text('1. Iniciar Novo Jogo', small_font, WHITE, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        draw_text('2. Ver Ranking', small_font, WHITE, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40)
        draw_text('3. Sair', small_font, WHITE, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 'start_game'
                elif event.key == pygame.K_2:
                    return 'view_ranking'
                elif event.key == pygame.K_3:
                    pygame.quit()
                    return 'quit'

        pygame.display.flip()

def show_rankings():
    font = pygame.font.Font(None, 36)
    rankings = get_rankings()
    menu_running = True

    while menu_running:
        screen.fill(WHITE)
        draw_text('Ranking', font, BLACK, screen, WINDOW_WIDTH // 2, 50)
        y_offset = 100
        for i, (name, score) in enumerate(rankings):
            draw_text(f'{i + 1}. {name} - {score}', font, BLACK, screen, WINDOW_WIDTH // 2, y_offset)
            y_offset += 30
        draw_text('Pressione Q para voltar ao menu', font, BLACK, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    menu_running = False

        pygame.display.flip()

def get_player_name():
    font = pygame.font.Font(None, 48)
    input_box = pygame.Rect(WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT // 2 - 20, 280, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = True
    text = ''
    clock = pygame.time.Clock()
    
    while True:
        screen.fill(WHITE)
        txt_surface = font.render(text, True, color)
        width = max(280, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)
        draw_text('Digite seu nome:', font, BLACK, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return text
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        color = color_active if active else color_inactive
        pygame.display.flip()
        clock.tick(30)

def show_game_over(score, player_name):
    if not pygame.font.get_init():
        pygame.font.init()
    
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)
    game_over_running = True

    while game_over_running:
        screen.fill(WHITE)
        draw_text('Tempo Esgotado!', font, BLACK, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100)
        draw_text(f'Pontuação Final: {score}', small_font, BLACK, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        draw_text(f'Nome do Jogador: {player_name}', small_font, BLACK, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40)
        draw_text('Pressione Q para voltar ao menu', small_font, BLACK, screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    game_over_running = False

        pygame.display.flip()

def main():
    setup_database()

    while True:
        menu_choice = show_menu()

        if menu_choice == 'quit':
            break
        elif menu_choice == 'start_game':
            player_name = get_player_name()
            if not player_name:
                continue

            global player, item, score, start_time
            player = pygame.Rect(150, 150, PLAYER_SIZE, PLAYER_SIZE)
            item = place_item_within_bounds()
            start_time = pygame.time.get_ticks()
            score = 0

            clock = pygame.time.Clock()
            running = True
            font = pygame.font.Font(None, 36)

            print("Jogo iniciado.")

            while running:
                current_time = pygame.time.get_ticks()
                elapsed_time = (current_time - start_time) / 1000
                time_left = TIME_LIMIT - elapsed_time

                if time_left <= 0:
                    running = False
                    print("Tempo esgotado!")

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        print("Jogo encerrado pelo usuário.")

                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    player.x -= player_speed
                if keys[pygame.K_RIGHT]:
                    player.x += player_speed
                if keys[pygame.K_UP]:
                    player.y -= player_speed
                if keys[pygame.K_DOWN]:
                    player.y += player_speed

                if (player.left < 100 or player.right > WINDOW_WIDTH - 100 or
                    player.top < 100 or player.bottom > WINDOW_HEIGHT - 100):
                    running = False
                    print("O jogador saiu dos limites permitidos.")

                if any(player.colliderect(wall) for wall in maze_walls):
                    running = False
                    print("O jogador colidiu com a parede.")

                if player.colliderect(item):
                    score += 1
                    coin_sound.play()  # Toca o som do efeito de coleta
                    item = place_item_within_bounds()
                    print(f"Item coletado! Pontuação: {score}")

                screen.fill(WHITE)
                screen.blit(player_image, (player.x, player.y))
                screen.blit(item_image, (item.x, item.y))

                for wall in maze_walls:
                    pygame.draw.rect(screen, BLUE, wall)

                draw_text(f'Score: {score}', font, RED, screen, WINDOW_WIDTH // 2, 20)
                draw_text(f'Tempo: {int(time_left)}', font, RED, screen, WINDOW_WIDTH // 2, 50)
                pygame.display.flip()
                clock.tick(30)

            update_score(player_name, score)
            print(f"Pontuação do jogador: {score} salva no banco de dados.")
            show_game_over(score, player_name)
        elif menu_choice == 'view_ranking':
            show_rankings()

    pygame.quit()

if __name__ == "__main__":
    main()
