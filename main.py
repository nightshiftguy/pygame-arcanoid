import pygame
from scripts.utils import load_image, load_images, read_csv, check_file_amount, Animation
from scripts.brickmap import Tilemap
from scripts.entities import Paddle, Ball, Texture, Brick
from scripts.uicontroller import UIController

class Game:
    def __init__(self):
        pygame.init()

        self.level_amount = check_file_amount('levels')
        self.levels_unlocked = [True]
        for i in range(self.level_amount-1):
            self.levels_unlocked.append(False)

        pygame.display.set_caption("arcanoid")
        self.screen = pygame.display.set_mode((768, 600))
        self.game_clock = pygame.time.Clock()
        self.ui_controller = UIController(self)

        self.state = 'menu'

        self.assets = {
            'ball' : load_image('Balls/Glossy/Ball_Green_Glossy-24x24.png'),
            'brick': load_images('Bricks/Colored/Plain'),
            'brick-damage': load_images('Bricks/Damage'),
            'paddle': load_image('Paddles/Style A/Paddle_A_Red_192x28.png'),
            'background-animation': Animation(self, load_images('Background'))
        }

        self.movement = 0        
        self.tilemap = Tilemap(self)
        self.entities = []
        self.entities.append(Texture(self, (0,0), 'background-animation', self.screen.get_size()))
        self.entities.append(Paddle(self, (300,570), (1,1)))
        self.entities.append(Ball(self, (0, 200), (0.5,0.5)))

    def unlock_next_level(self):
        for level_id, level in enumerate(self.levels_unlocked):
            if level==False:
                self.levels_unlocked[level_id]=True
                break

    def load_level(self, level_number):
        self.start_time = pygame.time.get_ticks()
        self.score=0
        self.lives=3
        self.movement_input = [False, False]
        self.won = False
        self.score=0
        for entity in self.entities[:]:
            if hasattr(entity, 'reset'):
                entity.reset()
        self.tilemap.read(read_csv('levels/'+str(level_number)+'.csv'))
    
    def getInput(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.movement_input[0]=True
        else:
            self.movement_input[0]=False

        if key[pygame.K_RIGHT]:
            self.movement_input[1]=True
        else:
            self.movement_input[1]=False

        self.movement = (self.movement_input[1] - self.movement_input[0], 0)

    def render(self):
        for entity in self.entities:
            if hasattr(entity, 'render'):
                entity.render(self.screen)

        font = pygame.font.SysFont(None, 30)
        lives_text = font.render(f"Lives: {self.lives}", True, (255,255,255))
        score_text = font.render(f"Score: {self.score}", True, (255,255,255))
        self.screen.blit(lives_text, (10, 10))
        self.screen.blit(score_text, (150, 10))


    def update(self):
        if pygame.time.get_ticks() - self.start_time < 500:
            return
        for asset in self.assets.values():
            if hasattr(asset, 'update'):
                asset.update()
        for entity in self.entities:
            if hasattr(entity, 'update'):
                entity.update(self.dt)

    def run(self):
        running = True
        while running:
            self.events = pygame.event.get()
            self.dt = self.game_clock.tick()
            if self.state == 'menu':
                self.ui_controller.update_menu()
                self.ui_controller.render_menu()
            elif self.state == 'gameover':
                self.ui_controller.render_gameover()
            elif self.state == 'playing':
                if not any(isinstance(entity, Brick) for entity in self.entities):
                    self.won = True
                    self.unlock_next_level()
                    self.state = 'gameover'
                if self.lives<=0:
                    self.state = 'gameover'
                self.screen.fill((0,0,0))

                self.update()
                self.render()
                self.getInput()
            for event in self.events:
                if event.type == pygame.QUIT:
                    running = False
            pygame.display.update()
        pygame.quit()

Game().run()