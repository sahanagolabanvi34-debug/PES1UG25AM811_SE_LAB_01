import random
import pygame
from game.text_box import TextBox
 
class GameEngine:
    ROUND_DURATION_MS = 30_000

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.words = ["PYTHON", "PYGAME", "PLANET", "ROCKET", "GALAXY", "STREAM", "PUZZLE", "ALGORITHM"]
        self.secret_word = ""
        self.scrambled_word = ""
        self.hint_count = 0

        self.score = 0
        self.feedback_msg = "Unscramble the letters above!"
        self.feedback_color = (210, 215, 225)

        self.input_box = TextBox(width // 2 - 130, 210, 160, 46)
        self.submit_btn = pygame.Rect(width // 2 + 45, 210, 95, 46)
        self.hint_btn = pygame.Rect(width // 2 + 150, 210, 95, 46)
        self.undo_btn = pygame.Rect(width // 2 - 100, 270, 90, 38)
        self.clear_btn = pygame.Rect(width // 2 + 10, 270, 90, 38)
        self.tile_rects = []
        self.selected_tiles = set()
        self.answer_sources = []

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_word = pygame.font.SysFont(None, 52)
        self.font_msg = pygame.font.SysFont(None, 26)
        self.font_btn = pygame.font.SysFont(None, 24)

        self.next_round()

    def scramble_string(self, word):
        letters = list(word)
        while True:
            random.shuffle(letters)
            shuffled = "".join(letters)
            if shuffled != word or len(word) <= 1:
                return shuffled

    def next_round(self):
        self.secret_word = random.choice(self.words)
        self.scrambled_word = self.scramble_string(self.secret_word)
        self.hint_count = 0
        self.round_start_ticks = pygame.time.get_ticks()
        self.selected_tiles.clear()
        self.answer_sources.clear()
        tile_width = 44
        tile_gap = 8
        row_width = len(self.scrambled_word) * tile_width + (len(self.scrambled_word) - 1) * tile_gap
        start_x = (self.width - row_width) // 2
        self.tile_rects = [
            pygame.Rect(start_x + index * (tile_width + tile_gap), 130, tile_width, 42)
            for index in range(len(self.scrambled_word))
        ]
        self.input_box.clear()

    def select_tile(self, index):
        if index in self.selected_tiles or len(self.input_box.text) >= 15:
            return
        self.selected_tiles.add(index)
        self.answer_sources.append(index)
        self.input_box.text += self.scrambled_word[index]

    def undo_answer(self):
        if not self.input_box.text:
            return
        source = self.answer_sources.pop()
        self.input_box.text = self.input_box.text[:-1]
        if source is not None:
            self.selected_tiles.remove(source)

    def clear_answer(self):
        self.input_box.clear()
        self.answer_sources.clear()
        self.selected_tiles.clear()

    def reveal_hint(self):
        if self.hint_count < len(self.secret_word):
            self.hint_count += 1
            self.score = max(0, self.score - 1)

    def submit_guess(self):
        guess = self.input_box.text.strip().upper()
        if not guess:
            self.feedback_msg = "Type a word before submitting!"
            self.feedback_color = (240, 170, 50)
            return

        is_correct = (guess == self.secret_word)

        if is_correct:
            self.score += 1
            self.feedback_msg = f"CORRECT! '{self.secret_word}' is right."
            self.feedback_color = (80, 230, 110)
            self.next_round()
        else:
            self.feedback_msg = "WRONG GUESS! Try again."
            self.feedback_color = (240, 80, 80)
            self.clear_answer()

    def handle_event(self, event):
        previous_text = self.input_box.text
        self.input_box.handle_event(event)
        if len(self.input_box.text) < len(previous_text):
            self.answer_sources = self.answer_sources[:len(self.input_box.text)]
            self.selected_tiles = {
                source for source in self.answer_sources if source is not None
            }
        elif len(self.input_box.text) > len(previous_text):
            self.answer_sources.extend([None] * (len(self.input_box.text) - len(previous_text)))

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.submit_guess()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            interactive_rects = [
                self.submit_btn,
                self.hint_btn,
                self.undo_btn,
                self.clear_btn,
                *self.tile_rects,
            ]
            if any(rect.collidepoint(event.pos) for rect in interactive_rects):
                self.input_box.active = True

            if self.submit_btn.collidepoint(event.pos):
                self.submit_guess()
            elif self.hint_btn.collidepoint(event.pos):
                self.reveal_hint()
            elif self.undo_btn.collidepoint(event.pos):
                self.undo_answer()
            elif self.clear_btn.collidepoint(event.pos):
                self.clear_answer()
            else:
                for index, tile_rect in enumerate(self.tile_rects):
                    if tile_rect.collidepoint(event.pos):
                        self.select_tile(index)
                        break

    def update(self):
        elapsed_ms = pygame.time.get_ticks() - self.round_start_ticks
        if elapsed_ms >= self.ROUND_DURATION_MS:
            self.next_round()

    def render(self, screen):
        screen.fill((26, 30, 38))

        title_surf = self.font_title.render("Word Scramble Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 25))

        score_surf = self.font_msg.render(f"Score: {self.score}", True, (255, 220, 80))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 70))

        elapsed_ms = pygame.time.get_ticks() - self.round_start_ticks
        remaining_seconds = max(0, (self.ROUND_DURATION_MS - elapsed_ms + 999) // 1000)
        timer_color = (240, 80, 80) if remaining_seconds <= 5 else (210, 215, 225)
        timer_surf = self.font_msg.render(f"Time: {remaining_seconds}s", True, timer_color)
        screen.blit(timer_surf, (self.width // 2 - timer_surf.get_width() // 2, 98))

        for index, tile_rect in enumerate(self.tile_rects):
            selected = index in self.selected_tiles
            tile_color = (55, 62, 72) if selected else (42, 55, 70)
            text_color = (125, 130, 138) if selected else (100, 200, 255)
            pygame.draw.rect(screen, tile_color, tile_rect, border_radius=5)
            pygame.draw.rect(screen, (90, 100, 115), tile_rect, width=2, border_radius=5)
            letter_surf = self.font_msg.render(self.scrambled_word[index], True, text_color)
            screen.blit(letter_surf, letter_surf.get_rect(center=tile_rect.center))

        hinted_word = " ".join(
            self.secret_word[index] if index < self.hint_count else "_"
            for index in range(len(self.secret_word))
        )
        hint_surf = self.font_msg.render(hinted_word, True, (210, 215, 225))
        screen.blit(hint_surf, (self.width // 2 - hint_surf.get_width() // 2, 178))

        self.input_box.render(screen)

        pygame.draw.rect(screen, (50, 150, 85), self.submit_btn, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), self.submit_btn, width=2, border_radius=6)
        btn_text = self.font_btn.render("SUBMIT", True, (255, 255, 255))
        screen.blit(btn_text, (self.submit_btn.centerx - btn_text.get_width() // 2, self.submit_btn.centery - btn_text.get_height() // 2))

        pygame.draw.rect(screen, (55, 105, 155), self.hint_btn, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), self.hint_btn, width=2, border_radius=6)
        hint_btn_text = self.font_btn.render("HINT", True, (255, 255, 255))
        screen.blit(hint_btn_text, (self.hint_btn.centerx - hint_btn_text.get_width() // 2, self.hint_btn.centery - hint_btn_text.get_height() // 2))

        for button, label in ((self.undo_btn, "UNDO"), (self.clear_btn, "CLEAR")):
            pygame.draw.rect(screen, (70, 78, 90), button, border_radius=6)
            pygame.draw.rect(screen, (180, 185, 195), button, width=2, border_radius=6)
            button_text = self.font_btn.render(label, True, (255, 255, 255))
            screen.blit(button_text, button_text.get_rect(center=button.center))

        feedback_surf = self.font_msg.render(self.feedback_msg, True, self.feedback_color)
        screen.blit(feedback_surf, (self.width // 2 - feedback_surf.get_width() // 2, 330))
