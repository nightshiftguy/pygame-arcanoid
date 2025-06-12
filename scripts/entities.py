import pygame
import math
from scripts.utils import Animation

class Entity:
    def __init__(self, game, e_type, position, size, subtype=None):
        self.game = game
        self.type = e_type
        self.position = list(position)
        self.size = size
        self.subtype = subtype
 
class Visible:
    def render(self, surf):
            asset = self.game.assets[self.type]
            if isinstance(asset, list):
                surf.blit(asset[self.subtype], self.position)
            else:
                surf.blit(asset, self.position)

class Physical:
    def rect(self):
        return pygame.Rect(self.position, self.size)
    
    def check_collision(self, physical_obj):
        if physical_obj != self and isinstance(physical_obj, Physical):
            return self.rect().colliderect(physical_obj.rect())
        return False
    
class Resetable:
    def reset(self):
        pass

class Destructable:
    def destroy(self):
        if self in self.game.entities:
            self.game.entities.remove(self)

class Texture(Entity, Visible):
    def __init__(self, game, position, e_type, size):
        super().__init__(game, e_type, position, size, subtype=None)

    def render(self, surf):
        image = self.game.assets[self.type]
        if type(image) == Animation:
            image = image.img()
        image_width, image_height = image.get_width(), image.get_height()

        temp_surface = pygame.Surface(self.size, pygame.SRCALPHA)

        for x in range(self.size[0] // image_width+1):
            for y in range(self.size[1] // image_height+1):
                temp_surface.blit(image.copy(), (x * image_width, y * image_height))

        surf.blit(temp_surface, self.position)

class MoveableEntity(Entity , Resetable):
    def __init__(self, game, e_type, position, velocity, size):
        super().__init__(game, e_type, position, size)
        self.velocity = list(velocity)
        self.initial_velocity = list(velocity).copy()
        self.initial_position=list(position)

    def update(self, dt):
        acceleration = 0.06
        if self.game.movement[0] != 0:
            self.velocity[0] += acceleration * self.game.movement[0]
        else:
            self.velocity[0] *= 0.5
        self.velocity[0] = max(min(self.velocity[0], self.initial_velocity[0]), -self.initial_velocity[0])
        self.position[0] += self.velocity[0] * dt

    def reset(self):
        self.position = self.initial_position.copy()
        

class Paddle(MoveableEntity, Physical, Visible):
    def __init__(self, game, position, velocity):
        width = game.assets['paddle'].get_width()
        height = game.assets['paddle'].get_height()
        super().__init__(game, 'paddle', position, velocity, (width, height))

    def update(self, dt):
        super().update(dt)
        screen_w = self.game.screen.get_width()
        if self.position[0] < 0:
            self.position[0] = 0
        elif self.position[0] + self.size[0] > screen_w:
            self.position[0] = screen_w - self.size[0]

class Brick(Entity, Physical, Visible, Destructable):
    def __init__(self, game, position, size, subtype):
        assert (subtype>=0 and subtype<=4) or (subtype>=13 and subtype<=16), "Brick subtype out of range"
        super().__init__(game, 'brick', position, size, subtype)
        self.hitpoints=self.subtype+1
        self.was_hit=False

    def render(self, surf):
        super().render(surf)
        if self.was_hit:
            damage_overlay = self.game.assets['brick-damage']
            surf.blit(damage_overlay[self.hitpoints-1], self.position)
    
    def hit(self):
        self.game.score+=10
        self.was_hit=True
        self.hitpoints-=1
        if self.hitpoints<=0:
            self.destroy()

    def reset(self):
        self.destroy()

class Ball(MoveableEntity, Physical, Visible):
    def __init__(self, game, position, initial_velocity):
        width = game.assets['ball'].get_width()
        height = game.assets['ball'].get_height()
        super().__init__(game, 'ball', position, initial_velocity, (width, height))
        self.max_angle = 75

    def update(self, dt):
        #x
        self.position[0] += self.velocity[0] * dt
        screen_w = self.game.screen.get_width()

        if self.rect().left < 0 and self.velocity[0] < 0:
            self.position[0] = 0
            self.velocity[0] *= -1

        if self.rect().right > screen_w and self.velocity[0] > 0:
            self.position[0] = screen_w - self.size[0]
            self.velocity[0] *= -1

        for entity in self.game.entities[:]:
            if self.check_collision(entity):
                if entity.type == 'brick':
                    if self.velocity[0] > 0:
                        self.position[0] = entity.rect().left - self.size[0]
                    else:
                        self.position[0] = entity.rect().right
                    self.velocity[0] *= -1
                    entity.hit()
                break

        #y
        self.position[1] += self.velocity[1] * dt

        if self.rect().top < 0 and self.velocity[1] < 0:
            self.position[1] = 0
            self.velocity[1] *= -1

        if self.rect().bottom > self.game.screen.get_height() and self.velocity[1] > 0:
            self.game.lives-=1
            self.game.start_time = pygame.time.get_ticks()
            self.reset()

        for entity in self.game.entities[:]:
            if self.check_collision(entity):
                if entity.type == 'paddle':
                    paddle_center = entity.rect().centerx
                    offset = self.rect().centerx - paddle_center
                    #normalized = offset_from_paddle_center + normalized_paddle_velocity + normalized_ball_velocity 
                    normalized = offset / (entity.rect().width / 2) * 0.4 + (entity.velocity[0] / entity.initial_velocity[0]) * 0.4 + 0.2 * self.velocity[0]/self.initial_velocity[0]*1.41 
                    angle = math.radians(normalized * self.max_angle)
                    abs_angle = max(math.radians(5), min(abs(angle), math.radians(75)))
                    angle = math.copysign(abs_angle, angle)
                    self.velocity[0] = self.initial_velocity[0] * math.sin(angle)
                    self.velocity[1] = -abs(self.initial_velocity[1] * math.cos(angle))
                elif entity.type == 'brick':
                    if self.velocity[1] > 0:
                        self.position[1] = entity.rect().top - self.size[1]
                    else:
                        self.position[1] = entity.rect().bottom
                    self.velocity[1] *= -1
                    entity.hit()
                break                

    def reset(self):
        self.position = self.initial_position.copy()
        self.velocity = self.initial_velocity.copy()

    def render(self, surf):
        asset = self.game.assets['ball']
        surf.blit(asset, self.position)