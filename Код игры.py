import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Математический дождь")

# Приятная цветовая палитра
BACKGROUND = (245, 245, 255)  # Светло-голубой фон
PRIMARY = (106, 13, 173)  # Фиолетовый
SECONDARY = (142, 68, 173)  # Светло-фиолетовый
ACCENT = (231, 76, 60)  # Красный для ошибок
SUCCESS = (46, 204, 113)  # Зелёный для успеха
TEXT_COLOR = (44, 62, 80)  # Тёмно-синий текст
WHITE = (255, 255, 255)
SHADOW = (0, 0, 0, 30)  # Тень для кнопок

# Шрифты
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)
medium_font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 24)  # Маленький шрифт для кнопки выхода
game_over_font = pygame.font.Font(None, 28)  # Шрифт для текста на финальном экране

best_score = 0
initial_speed = 5  # Начальная скорость падения

# --- Водяной знак ---
watermark_font = pygame.font.Font(None, 48)
watermark_text = "by Akul"

def draw_watermark(alpha=35, color=None):
    """Рисует полупрозрачный водяной знак по центру экрана."""
    if color is None:
        color = PRIMARY
    surf = watermark_font.render(watermark_text, True, color)
    surf.set_alpha(alpha)
    rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(surf, rect)
# --------------------

class Slider:
    def __init__(self, x, y, width, min_value, max_value, initial_value):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.dragging = False
        self.handle_radius = 12

    def handle_position(self):
        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        x = self.rect.x + int(ratio * self.rect.width)
        return (x, self.rect.centery)

    def draw(self):
        # Линия слайдера
        pygame.draw.rect(screen, (200, 200, 200), self.rect, border_radius=10)

        # Заполненная часть
        filled_rect = self.rect.copy()
        filled_rect.width = int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        pygame.draw.rect(screen, PRIMARY, filled_rect, border_radius=10)

        # Ручка слайдера
        handle_pos = self.handle_position()
        pygame.draw.circle(screen, SECONDARY, handle_pos, self.handle_radius)
        pygame.draw.circle(screen, WHITE, handle_pos, self.handle_radius - 3)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                handle_pos = self.handle_position()
                if ((event.pos[0] - handle_pos[0]) ** 2 + (
                        event.pos[1] - handle_pos[1]) ** 2) ** 0.5 <= self.handle_radius:
                    self.dragging = True
                elif self.rect.collidepoint(event.pos):
                    self.dragging = True
                    self.update_value(event.pos[0])

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.update_value(event.pos[0])

    def update_value(self, mouse_x):
        x = max(self.rect.x, min(mouse_x, self.rect.x + self.rect.width))
        ratio = (x - self.rect.x) / self.rect.width
        self.value = self.min_value + ratio * (self.max_value - self.min_value)

class FallingAnswer:
    def __init__(self, text, x, y, speed):
        self.text = text
        self.x = x
        self.y = y
        self.speed = speed
        self.rect = pygame.Rect(x, y, 60, 60)
        self.alpha = 255
        self.pulse = 0

    def move(self):
        self.y += self.speed
        self.rect.y = self.y
        self.pulse = (self.pulse + 1) % 60

    def draw(self):
        # Лёгкая пульсация
        size_scale = 1 + 0.05 * (1 if self.pulse < 30 else -1)
        current_rect = self.rect.inflate(int(self.rect.width * (size_scale - 1)),
                                         int(self.rect.height * (size_scale - 1)))

        # Тень
        shadow_rect = current_rect.copy()
        shadow_rect.y += 3
        shadow_surface = pygame.Surface(current_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, SHADOW, shadow_surface.get_rect(), border_radius=10)
        screen.blit(shadow_surface, shadow_rect)

        # Основной прямоугольник
        pygame.draw.rect(screen, PRIMARY, current_rect, border_radius=10)
        pygame.draw.rect(screen, SECONDARY, current_rect, 2, border_radius=10)

        # Текст
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=current_rect.center)
        screen.blit(text_surface, text_rect)

def draw_button(rect, text, color, hover=False, font_size=None):
    # Тень
    shadow_rect = rect.copy()
    shadow_rect.y += 4
    shadow_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, SHADOW, shadow_surface.get_rect(), border_radius=15)
    screen.blit(shadow_surface, shadow_rect)

    # Основная кнопка
    current_color = color if not hover else tuple(min(255, c + 20) for c in color)
    pygame.draw.rect(screen, current_color, rect, border_radius=15)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=15)

    # Текст
    if font_size:
        button_font = pygame.font.Font(None, font_size)
    else:
        button_font = font
    text_surface = button_font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def generate_question(operations):
    while True:
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operation = random.choice(operations)
        if operation == '-' and num1 < num2:
            num1, num2 = num2, num1
        question = f"{num1} {operation} {num2}"
        answer = eval(question)
        if answer >= 0:
            return question, answer

def generate_choices(correct_answer):
    choices = [correct_answer]
    while len(choices) < 5:
        offset = random.randint(1, 5)
        wrong_answer = correct_answer + offset if random.choice([True, False]) else correct_answer - offset
        if wrong_answer != correct_answer and wrong_answer > 0 and wrong_answer not in choices:
            choices.append(wrong_answer)
    random.shuffle(choices)
    return choices

def update_best_score(score):
    global best_score
    if score > best_score:
        best_score = score

def show_game_over_screen(score, reason="lives"):
    global best_score
    update_best_score(score)

    # Полупрозрачный фон
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # Водяной знак поверх затемнения
    draw_watermark(alpha=45, color=(255, 255, 255))

    # Карточка результата
    card_rect = pygame.Rect(200, 120, 400, 360)
    pygame.draw.rect(screen, WHITE, card_rect, border_radius=20)
    pygame.draw.rect(screen, PRIMARY, card_rect, 3, border_radius=20)

    game_over_surface = large_font.render("Игра окончена!", True, ACCENT)
    game_over_rect = game_over_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
    screen.blit(game_over_surface, game_over_rect)

    score_surface = medium_font.render(f"Счёт: {score}", True, TEXT_COLOR)
    score_rect = score_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(score_surface, score_rect)

    best_surface = font.render(f"Лучший счёт: {best_score}", True, SUCCESS)
    best_rect = best_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    screen.blit(best_surface, best_rect)

    # Разбиваем текст на две строки
    hint_line1 = "Нажмите любую клавишу"
    hint_line2 = "для продолжения..."

    hint_surface1 = game_over_font.render(hint_line1, True, TEXT_COLOR)
    hint_rect1 = hint_surface1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    screen.blit(hint_surface1, hint_rect1)

    hint_surface2 = game_over_font.render(hint_line2, True, TEXT_COLOR)
    hint_rect2 = hint_surface2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 125))
    screen.blit(hint_surface2, hint_rect2)

    pygame.display.flip()

    # Ждём нажатия клавиши
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

def settings_menu():
    global initial_speed

    speed_slider = Slider(WIDTH // 2 - 150, 300, 300, 1, 10, initial_speed)

    while True:
        screen.fill(BACKGROUND)

        # Градиент фона
        gradient = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(HEIGHT):
            alpha = int(30 * (1 - i / HEIGHT))
            pygame.draw.line(gradient, (PRIMARY[0], PRIMARY[1], PRIMARY[2], alpha),
                             (0, i), (WIDTH, i))
        screen.blit(gradient, (0, 0))

        # Водяной знак
        draw_watermark()

        # Заголовок
        title_surface = large_font.render("Настройки", True, PRIMARY)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, 150))
        screen.blit(title_surface, title_rect)

        # Надпись "Сложность"
        difficulty_surface = medium_font.render("Сложность", True, TEXT_COLOR)
        difficulty_rect = difficulty_surface.get_rect(center=(WIDTH // 2, 250))
        screen.blit(difficulty_surface, difficulty_rect)

        # Слайдер скорости
        speed_slider.draw()

        # Значение скорости
        speed_value_surface = font.render(f"Скорость: {speed_slider.value:.1f}", True, TEXT_COLOR)
        speed_value_rect = speed_value_surface.get_rect(center=(WIDTH // 2, 350))
        screen.blit(speed_value_surface, speed_value_rect)

        # Кнопка "Назад"
        back_button = pygame.Rect(WIDTH // 2 - 100, 450, 200, 50)
        mouse_pos = pygame.mouse.get_pos()
        draw_button(back_button, "Назад", SECONDARY, back_button.collidepoint(mouse_pos))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    initial_speed = speed_slider.value
                    return
            speed_slider.handle_event(event)

        pygame.display.flip()

def game_loop(operations):
    clock = pygame.time.Clock()
    score = 0
    lives = 3
    question, correct_answer = generate_question(operations)
    choices = generate_choices(correct_answer)
    animation_timer = 0

    falling_answers = []
    base_speed = initial_speed  # Используем настройку скорости
    for i, choice in enumerate(choices):
        y = random.randint(-500, -100)
        while True:
            x = random.randint(200, 600 - 100)
            new_rect = pygame.Rect(x, y, 60, 60)
            if not any(new_rect.colliderect(answer.rect) for answer in falling_answers):
                break
        falling_answers.append(FallingAnswer(str(choice), x, y, base_speed))

    running = True
    speed_increase_counter = 0
    while running:
        screen.fill(BACKGROUND)

        # Лёгкий градиент фона
        gradient = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        for i in range(100):
            alpha = int(50 * (1 - i / 100))
            pygame.draw.line(gradient, (PRIMARY[0], PRIMARY[1], PRIMARY[2], alpha),
                             (0, i), (WIDTH, i))
        screen.blit(gradient, (0, 0))

        # Водяной знак
        draw_watermark()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if exit_button.collidepoint(mouse_pos):
                    update_best_score(score)  # Сохраняем счёт при выходе
                    return
                for answer in falling_answers[:]:
                    if answer.rect.collidepoint(mouse_pos):
                        if int(answer.text) == correct_answer:
                            score += 1
                            speed_increase_counter += 1
                            animation_timer = 20
                            if speed_increase_counter % 5 == 0:
                                base_speed += 1
                                for ans in falling_answers:
                                    ans.speed = base_speed
                            question, correct_answer = generate_question(operations)
                            choices = generate_choices(correct_answer)
                            falling_answers = []
                            for i, choice in enumerate(choices):
                                y = random.randint(-500, -100)
                                while True:
                                    x = random.randint(200, 600 - 100)
                                    new_rect = pygame.Rect(x, y, 60, 60)
                                    if not any(new_rect.colliderect(answer.rect) for answer in falling_answers):
                                        break
                                falling_answers.append(FallingAnswer(str(choice), x, y, base_speed))
                        else:
                            lives -= 1
                            falling_answers.remove(answer)
                            if lives == 0:
                                show_game_over_screen(score, reason="lives")
                                return

        # Верхняя панель
        panel_rect = pygame.Rect(0, 0, WIDTH, 100)
        pygame.draw.rect(screen, PRIMARY, panel_rect)
        pygame.draw.rect(screen, SECONDARY, panel_rect, 3)

        # Вопрос
        question_surface = font.render(f"Вопрос: {question}", True, WHITE)
        question_rect = question_surface.get_rect(midleft=(20, 35))
        screen.blit(question_surface, question_rect)

        # Счёт
        score_surface = font.render(f"Счёт: {score}", True, WHITE)
        score_rect = score_surface.get_rect(center=(WIDTH - 180, 25))
        screen.blit(score_surface, score_rect)

        # Панель здоровья
        health_surface = font.render(f"Здоровье: {lives}", True, WHITE)
        health_rect = health_surface.get_rect(center=(WIDTH - 180, 65))
        screen.blit(health_surface, health_rect)

        # Кнопка выхода
        exit_button = pygame.Rect(WIDTH - 120, HEIGHT - 50, 100, 30)
        draw_button(exit_button, "Выход", ACCENT, font_size=24)

        # Рисуем падающие ответы
        for answer in falling_answers[:]:
            answer.move()
            answer.draw()

            if answer.y > HEIGHT:
                if int(answer.text) == correct_answer:
                    lives -= 1
                    if lives == 0:
                        show_game_over_screen(score, reason="lives")
                        return
                    else:
                        question, correct_answer = generate_question(operations)
                        choices = generate_choices(correct_answer)
                        falling_answers = []
                        for i, choice in enumerate(choices):
                            y = random.randint(-500, -100)
                            while True:
                                x = random.randint(200, 600 - 100)
                                new_rect = pygame.Rect(x, y, 60, 60)
                                if not any(new_rect.colliderect(answer.rect) for answer in falling_answers):
                                    break
                            falling_answers.append(FallingAnswer(str(choice), x, y, base_speed))
                else:
                    falling_answers.remove(answer)

        # Анимация успеха
        if animation_timer > 0:
            animation_timer -= 1
            success_surface = large_font.render("+1", True, SUCCESS)
            success_rect = success_surface.get_rect(center=(WIDTH // 2, 150))
            screen.blit(success_surface, success_rect)

        pygame.display.flip()
        clock.tick(30)

def main_menu():
    global best_score
    while True:
        screen.fill(BACKGROUND)

        # Градиент фона
        gradient = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(HEIGHT):
            alpha = int(30 * (1 - i / HEIGHT))
            pygame.draw.line(gradient, (PRIMARY[0], PRIMARY[1], PRIMARY[2], alpha),
                             (0, i), (WIDTH, i))
        screen.blit(gradient, (0, 0))

        # Водяной знак
        draw_watermark()

        # Заголовок с тенью
        title_shadow = large_font.render("Математический дождь", True, (100, 100, 100))
        title_shadow_rect = title_shadow.get_rect(center=(WIDTH // 2 + 3, 103))
        screen.blit(title_shadow, title_shadow_rect)

        title_surface = large_font.render("Математический дождь", True, PRIMARY)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)

        # Лучший счёт
        best_score_surface = medium_font.render(f"Лучший счёт: {best_score}", True, SUCCESS)
        best_score_rect = best_score_surface.get_rect(center=(WIDTH // 2, 160))
        screen.blit(best_score_surface, best_score_rect)

        # Кнопки выбора сложности
        button_width, button_height = 220, 60
        buttons = [
            (pygame.Rect(WIDTH // 2 - button_width // 2, 220, button_width, button_height), "Сложение", PRIMARY),
            (pygame.Rect(WIDTH // 2 - button_width // 2, 300, button_width, button_height), "Вычитание", PRIMARY),
            (pygame.Rect(WIDTH // 2 - button_width // 2, 380, button_width, button_height), "Умножение", PRIMARY),
            (pygame.Rect(WIDTH // 2 - button_width // 2, 460, button_width, button_height), "Все сразу", SECONDARY),
            (pygame.Rect(WIDTH // 2 - button_width // 2, 540, button_width, button_height), "Настройки", SUCCESS)
        ]

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True

        for button_rect, text, color in buttons:
            hover = button_rect.collidepoint(mouse_pos)
            draw_button(button_rect, text, color, hover)

            if mouse_click and hover:
                if text == "Сложение":
                    game_loop(['+'])
                elif text == "Вычитание":
                    game_loop(['-'])
                elif text == "Умножение":
                    game_loop(['*'])
                elif text == "Все сразу":
                    game_loop(['+', '-', '*'])
                elif text == "Настройки":
                    settings_menu()

        pygame.display.flip()

if __name__ == "__main__":
    main_menu()