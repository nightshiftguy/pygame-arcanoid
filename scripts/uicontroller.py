import pygame

class Button:
    def __init__(self, game, position, size, text, level_id):
        self.game = game
        self.position = list(position)
        self.size = list(size)
        self.text = text
        self.level_id = level_id
        
    def render(self, mouse):
        self.game.screen
        if self.game.levels_unlocked[self.level_id]:
            self.color = (100, 100, 255) if self.rect().collidepoint(mouse) else (50, 50, 200)
        else:
            self.color = (100, 100, 255)
        pygame.draw.rect(self.game.screen, self.color, self.rect())
        self.game.screen.blit(self.text, (self.rect().x + 10, self.rect().y + 10))

    def rect(self):
        return pygame.Rect(self.position, self.size)
    
    def is_clicked(self, mouse, click):
        return self.game.levels_unlocked[self.level_id] and self.rect().collidepoint(mouse) and click[0]

class UIController:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 40)
        self.mouse = pygame.mouse.get_pos()
        self.click = pygame.mouse.get_pressed()
        
        self.level_buttons=[]
        self.PADDING_TOP=100
        self.PADDING_LEFT=100
        for level_id, unlocked in enumerate(self.game.levels_unlocked):
            text = self.font.render("Level "+str(level_id+1), True, (255, 255, 255))
            self.level_buttons.append(
                Button(self.game, (self.PADDING_LEFT, self.PADDING_TOP+100+level_id*70), (200, 50), text, level_id)
            )

    def render_gameover(self):
        msg = "You Win!" if self.game.won else "Game Over"
        text = self.font.render(msg, True, (255, 255, 255))
        self.game.screen.blit(text, (self.game.screen.get_width()//2 - text.get_width()//2, self.game.screen.get_height()//2))
        for event in self.game.events:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.game.state = "menu"

    def render_menu(self):
        self.game.screen.fill((0, 0, 0))
        title = self.font.render("Select Level", True, (255, 255, 255))
        self.game.screen.blit(title, (100, self.PADDING_TOP))

        for button in self.level_buttons:
            button.render(self.mouse)

    def update_menu(self):
        self.mouse = pygame.mouse.get_pos()
        self.click = pygame.mouse.get_pressed()
        for level_num, button in enumerate(self.level_buttons):
            if button.is_clicked(self.mouse, self.click):
                self.game.load_level(level_num+1)
                self.game.state = 'playing'
