import pygame
import heapq 
import random
import time 
#Constants 
WIDTH, HEIGHT = 1280, 720
GRID_SIZE = 80
WHITE = (255,255,255) #0-255
BLACK = (0, 0, 0)
FPS = 60
GAME_DURATION = 15
MOVE_INTERVAL = 0.15

# تجهيز Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chicken Ninja War")
                                                                                    
                                                                                    
# Load resources
def load_resources():                                                                     
    hit_sound = pygame.mixer.Sound("assets/hit.mp3") 
    sword_sound = pygame.mixer.Sound("assets/sword.mp3") 
    game_over_sound = pygame.mixer.Sound("assets/game_over.mp3")
    start_sound = pygame.mixer.Sound("assets/start.mp3")
    pygame.mixer.music.load("assets/background_music.mp3")
    five = pygame.mixer.Sound("assets/five.mp3")
    chicken_img = pygame.image.load("assets/chicken.png")
    ninja_img = pygame.image.load("assets/ninja.png") 
    start_bg = pygame.image.load("assets/start_bg.jpg")
    game_bg = pygame.image.load("assets/game_bg.jpg")
    game_over2 = pygame.image.load("assets/game_over2.jpg")

    return {
        "hit_sound": hit_sound,
        "sword_sound": sword_sound,
        "game_over_sound": game_over_sound,
        "start_sound": start_sound,
        "chicken_img": chicken_img,
        "ninja_img": ninja_img, 
        "start_bg": start_bg,
        "game_bg": game_bg,
        "five": five,
        "game_over2": game_over2                              
    }

resources = load_resources()

# Game variables                       
clock = pygame.time.Clock()
score = 0
kills = 0

# Ninja
ninja = {"x": WIDTH // 2, "y": HEIGHT - GRID_SIZE, "speed": 1} 

# Chicken settings
def create_chicken():
    return {"x": random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE,
            "y": random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE}

chickens = [create_chicken()] 


def draw_grid():
    for row in range(0, HEIGHT, GRID_SIZE):
        for col in range(0, WIDTH, GRID_SIZE):
            pygame.draw.rect(screen, WHITE, (col, row, GRID_SIZE, GRID_SIZE), 1)

def draw_elements():
    screen.blit(resources["game_bg"], (0,0))
    draw_grid()
    for chicken in chickens:
        screen.blit(resources["chicken_img"], (chicken["x"], chicken["y"]))
    screen.blit(resources["ninja_img"], (ninja["x"], ninja["y"])) 

def display_text(text, font_size, x, y):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, (x, y))

def draw_game_ui():
    draw_elements()
    display_text(f"Score: {score}", 40, 10, 10)
    time_left = max(0, GAME_DURATION - int(time.time() - start_time))
    display_text(f"Time: {time_left}", 40, 10, 50)
    pygame.display.flip()

def display_game_over():
    screen.blit(resources["game_over2"], (0, 0))
    display_text("THE END", 72, WIDTH // 2 - 100, HEIGHT // 3)
    display_text(f"Score: {score}", 36, WIDTH // 2 - 70, HEIGHT // 2)
    display_text(f"Kills: {kills}", 36, WIDTH // 2 - 70, HEIGHT // 1.5)
    pygame.display.flip()
    pygame.mixer.Sound.play(resources["game_over_sound"])

def start_screen():
    screen.blit(resources["start_bg"], (0, 0))
    display_text("PRESS ENTER ", 60, WIDTH // 2 - 155, HEIGHT // 1.5)
    display_text("TO START", 60, WIDTH // 2 - 110, HEIGHT // 1.34)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False

# A* Algorithm
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(start, goal): 
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        neighbors = [
            (current[0] + GRID_SIZE, current[1]),
            (current[0] - GRID_SIZE, current[1]),
            (current[0], current[1] + GRID_SIZE),
            (current[0], current[1] - GRID_SIZE)
        ]

        for neighbor in neighbors:
            if 0 <= neighbor[0] < WIDTH and 0 <= neighbor[1] < HEIGHT:
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  

def move_ninja_with_a_star(ninja, target_chicken): 
    start = (ninja["x"], ninja["y"]) 
    goal = (target_chicken["x"], target_chicken["y"])

    path = a_star(start, goal)

    if path:
        next_step = path[0]
        ninja["x"], ninja["y"] = next_step 

def can_hit(ninja, chicken):
    return ninja["x"] == chicken["x"] and ninja["y"] == chicken["y"] 

def game_loop():
    global score, kills, chickens, start_time
    running = True
    pygame.mixer.Sound.play(resources["start_sound"])  
    pygame.mixer.music.play(-1)

    start_time = time.time()
    last_move_time = time.time()
    target_chicken = None
    sound_played = False 

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not target_chicken or target_chicken not in chickens:
            if chickens:
                target_chicken = chickens[0]

        current_time = time.time()
        if target_chicken and current_time - last_move_time >= MOVE_INTERVAL:
            move_ninja_with_a_star(ninja, target_chicken) 
            last_move_time = current_time

            if can_hit(ninja, target_chicken): 
                pygame.mixer.Sound.play(resources["sword_sound"]) 
                pygame.mixer.Sound.play(resources["hit_sound"]) 
                chickens.remove(target_chicken)
                score += 10
                kills += 1
                chickens.append(create_chicken())

        elapsed_time = time.time() - start_time
        
 
        if int(elapsed_time) == 9 and not sound_played:
            pygame.mixer.Sound.play(resources["five"])
            sound_played = True  

        if elapsed_time > GAME_DURATION:
            display_game_over()  
            waiting_for_enter = True
            while waiting_for_enter:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        waiting_for_enter = False
                        running = False

        draw_game_ui()

    pygame.mixer.music.stop()

# Main program
if __name__ == "__main__":
    start_screen()
    game_loop()
    pygame.quit()
