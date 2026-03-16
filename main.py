import json
import random
import re
import sys
import pygame

pygame.init()

# =====================================
# Blank Drop English - Difficulty Edition
# =====================================

# ---------- Files ----------
QUESTION_FILE = "intern_questions.json"

# ---------- Load questions ----------
try:
    with open(QUESTION_FILE, "r", encoding="utf-8-sig") as f:
        all_questions = json.load(f)
except FileNotFoundError:
    print(f"Error: {QUESTION_FILE} not found.")
    pygame.quit()
    sys.exit()
except json.JSONDecodeError as e:
    print("JSON read error:", e)
    pygame.quit()
    sys.exit()

if not all_questions:
    print("No questions found.")
    pygame.quit()
    sys.exit()

# ---------- Screen ----------
WIDTH, HEIGHT = 1100, 760
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blank Drop English - The Intern Edition")
clock = pygame.time.Clock()

# ---------- Fonts ----------
font_kor = pygame.font.SysFont("malgungothic", 30)
font_eng = pygame.font.SysFont("arial", 34)
font_ui = pygame.font.SysFont("arial", 26)
font_big = pygame.font.SysFont("arial", 54)
font_mid = pygame.font.SysFont("arial", 34)

# ---------- Colors ----------
WHITE = (245, 245, 245)
BLACK = (30, 30, 30)
NAVY = (53, 95, 155)
YELLOW = (245, 210, 70)
GREEN = (45, 170, 90)
RED = (220, 70, 70)
GRAY = (230, 230, 230)
DARK_GRAY = (90, 90, 90)
BLUE = (70, 130, 180)

# ---------- Helpers ----------
PREPOSITIONS = {
    "in", "on", "at", "to", "for", "with", "about", "from",
    "into", "over", "after", "before", "between", "by", "of",
    "out", "up", "off", "under", "through"
}

def draw_text(text, font, color, x, y):
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))

def draw_center_text(text, font, color, cx, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(cx, y))
    screen.blit(surf, rect)

def classify_question(q):
    # If level already exists in JSON, trust it
    if "level" in q and str(q["level"]).strip():
        return str(q["level"]).strip().lower()

    answer = str(q.get("answer", "")).strip().lower()
    english = str(q.get("english", "")).strip()
    word_count = len(re.findall(r"[A-Za-z']+", english))

    if answer in PREPOSITIONS or len(answer) <= 4 or word_count <= 6:
        return "easy"
    elif len(answer) <= 7 or word_count <= 10:
        return "medium"
    else:
        return "hard"

def split_questions_by_level(question_list):
    easy, medium, hard = [], [], []
    for q in question_list:
        level = classify_question(q)
        if level == "easy":
            easy.append(q)
        elif level == "hard":
            hard.append(q)
        else:
            medium.append(q)
    return easy, medium, hard

easy_questions, medium_questions, hard_questions = split_questions_by_level(all_questions)

if not easy_questions:
    easy_questions = all_questions[:]
if not medium_questions:
    medium_questions = all_questions[:]
if not hard_questions:
    hard_questions = all_questions[:]

# ---------- Game state ----------
game_state = "menu"   # menu / playing / game_over / clear
difficulty = None
questions = []
used_indices = set()
current_question = None

score = 0
lives = 3
combo = 0
user_input = ""
feedback = ""
feedback_color = BLACK
feedback_timer = 0
fall_speed = 1.0

block_x = 90
block_y = 70
block_w = 920
block_h = 150

def set_difficulty(level_name):
    global difficulty, questions, fall_speed
    difficulty = level_name

    if level_name == "easy":
        questions = easy_questions[:]
        fall_speed = 0.4
    elif level_name == "medium":
        questions = medium_questions[:]
        fall_speed = 0.6
    else:
        questions = hard_questions[:]
        fall_speed = 0.85

def pick_new_question():
    global current_question, block_y, game_state

    if len(used_indices) >= len(questions):
        game_state = "clear"
        current_question = None
        return

    available = [i for i in range(len(questions)) if i not in used_indices]
    idx = random.choice(available)
    used_indices.add(idx)
    current_question = questions[idx]
    block_y = 70

def start_game(level_name):
    global score, lives, combo, user_input, feedback, feedback_timer
    global used_indices, game_state

    set_difficulty(level_name)
    score = 0
    lives = 3
    combo = 0
    user_input = ""
    feedback = ""
    feedback_timer = 0
    used_indices = set()
    game_state = "playing"
    pick_new_question()

def restart_same_level():
    if difficulty:
        start_game(difficulty)

def back_to_menu():
    global game_state, difficulty, current_question, user_input, feedback
    game_state = "menu"
    difficulty = None
    current_question = None
    user_input = ""
    feedback = ""

def check_answer():
    global score, combo, feedback, feedback_color, feedback_timer, user_input, fall_speed

    if not current_question:
        return

    answer = str(current_question.get("answer", "")).strip().lower()
    typed = user_input.strip().lower()

    if typed == answer:
        combo += 1
        gained = 10 + min(combo - 1, 5)
        score += gained
        feedback = f"Correct! +{gained}"
        feedback_color = GREEN
        feedback_timer = 45
        user_input = ""

        # small difficulty-based acceleration
        if difficulty == "easy":
            fall_speed += 0.02
        elif difficulty == "medium":
            fall_speed += 0.04
        else:
            fall_speed += 0.06

        pick_new_question()
    else:
        combo = 0
        feedback = f"Wrong! Answer: {answer}"
        feedback_color = RED
        feedback_timer = 60
        user_input = ""

def miss_question():
    global lives, combo, feedback, feedback_color, feedback_timer, game_state, user_input

    if not current_question:
        return

    lives -= 1
    combo = 0
    feedback = f"Missed! Answer: {current_question['answer']}"
    feedback_color = RED
    feedback_timer = 60
    user_input = ""

    if lives <= 0:
        game_state = "game_over"
    else:
        pick_new_question()

# ---------- Main loop ----------
running = True

while running:
    clock.tick(60)
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if game_state == "menu":
                if event.key == pygame.K_1:
                    start_game("easy")
                elif event.key == pygame.K_2:
                    start_game("medium")
                elif event.key == pygame.K_3:
                    start_game("hard")

            elif game_state == "playing":
                if event.key == pygame.K_RETURN:
                    check_answer()
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    if len(event.unicode) == 1 and event.unicode.isprintable():
                        user_input += event.unicode

            elif game_state in ("game_over", "clear"):
                if event.key == pygame.K_r:
                    restart_same_level()
                elif event.key == pygame.K_m:
                    back_to_menu()

    # ---------- Menu ----------
    if game_state == "menu":
        draw_center_text("BLANK DROP ENGLISH", font_big, NAVY, WIDTH // 2, 130)
        draw_center_text("The Intern Edition", font_mid, DARK_GRAY, WIDTH // 2, 185)

        pygame.draw.rect(screen, GRAY, (260, 250, 580, 250), border_radius=18)
        pygame.draw.rect(screen, BLACK, (260, 250, 580, 250), 2, border_radius=18)

        draw_center_text("Select Difficulty", font_mid, BLACK, WIDTH // 2, 305)
        draw_center_text("1 - Easy", font_mid, GREEN, WIDTH // 2, 365)
        draw_center_text("2 - Medium", font_mid, BLUE, WIDTH // 2, 420)
        draw_center_text("3 - Hard", font_mid, RED, WIDTH // 2, 475)

        draw_center_text(
            f"Questions: easy {len(easy_questions)} / medium {len(medium_questions)} / hard {len(hard_questions)}",
            font_ui,
            DARK_GRAY,
            WIDTH // 2,
            560
        )
        draw_center_text("Press 1, 2, or 3 to start", font_ui, BLACK, WIDTH // 2, 610)

    # ---------- Playing ----------
    elif game_state == "playing":
        if current_question:
            block_y += fall_speed
            if block_y >= HEIGHT - 190:
                miss_question()

        pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, 72))
        draw_text(f"Score: {score}", font_ui, BLACK, 28, 20)
        draw_text(f"Lives: {lives}", font_ui, BLACK, 165, 20)
        draw_text(f"Combo: {combo}", font_ui, BLACK, 285, 20)
        draw_text(f"Used: {len(used_indices)}/{len(questions)}", font_ui, BLACK, 435, 20)
        draw_text(f"Difficulty: {difficulty.title()}", font_ui, BLACK, 650, 20)
        draw_text("Type the missing ONE word and press Enter", font_ui, DARK_GRAY, 835, 20)

        if current_question:
            korean = str(current_question["korean"])
            english = str(current_question["english"])

            pygame.draw.rect(screen, NAVY, (block_x, int(block_y), block_w, block_h), border_radius=14)
            pygame.draw.rect(screen, BLACK, (block_x, int(block_y), block_w, block_h), 2, border_radius=14)

            draw_text(korean, font_kor, WHITE, block_x + 24, int(block_y) + 24)
            draw_text(english, font_eng, YELLOW, block_x + 24, int(block_y) + 82)

        pygame.draw.rect(screen, GRAY, (180, HEIGHT - 105, 740, 58), border_radius=10)
        pygame.draw.rect(screen, BLACK, (180, HEIGHT - 105, 740, 58), 2, border_radius=10)
        draw_text("Your answer: " + user_input, font_ui, BLACK, 205, HEIGHT - 90)

        if feedback_timer > 0:
            draw_center_text(feedback, font_ui, feedback_color, WIDTH // 2, HEIGHT - 140)
            feedback_timer -= 1

    # ---------- Game over ----------
    elif game_state == "game_over":
        draw_center_text("GAME OVER", font_big, RED, WIDTH // 2, HEIGHT // 2 - 80)
        draw_center_text(f"Difficulty: {difficulty.title()}", font_ui, DARK_GRAY, WIDTH // 2, HEIGHT // 2 - 25)
        draw_center_text(f"Final Score: {score}", font_mid, BLACK, WIDTH // 2, HEIGHT // 2 + 20)
        draw_center_text("Press R to restart / M for menu", font_ui, DARK_GRAY, WIDTH // 2, HEIGHT // 2 + 85)

    # ---------- Clear ----------
    elif game_state == "clear":
        draw_center_text("STAGE CLEAR!", font_big, GREEN, WIDTH // 2, HEIGHT // 2 - 80)
        draw_center_text(f"Difficulty: {difficulty.title()}", font_ui, DARK_GRAY, WIDTH // 2, HEIGHT // 2 - 25)
        draw_center_text(f"Final Score: {score}", font_mid, BLACK, WIDTH // 2, HEIGHT // 2 + 20)
        draw_center_text(
            f"You finished all {len(questions)} questions.",
            font_ui,
            BLUE,
            WIDTH // 2,
            HEIGHT // 2 + 65
        )
        draw_center_text("Press R to restart / M for menu", font_ui, DARK_GRAY, WIDTH // 2, HEIGHT // 2 + 110)

    pygame.display.flip()

pygame.quit()
sys.exit()