import pygame
import os
import csv

BASE_IMG_PATH = 'data/images/'
BASE_DATA_PATH = 'data/'

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    img.set_colorkey((255,0,255))
    return img

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

def read_csv(path, delimiter=",", as_int=True):
    result = []
    with open(BASE_DATA_PATH + path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        for row in reader:
            if as_int:
                result.append([int(cell) for cell in row])
            else:
                result.append([cell.strip() for cell in row])
    return result

def check_file_amount(path):
    return sum(1 for f in os.listdir(BASE_DATA_PATH+path))

class Animation:
    def __init__(self, game, images, img_duration=1000, loop=True):
        self.game = game
        self.images=images
        self.img_duration = img_duration
        self.loop = loop
        self.done = False
        self.frame = 0
        self.timer = 0

    def update(self):
        if self.done:
            return

        self.timer += self.game.dt
        if self.timer >= self.img_duration:
            self.timer = 0
            self.frame += 1
            if self.frame >= len(self.images):
                if self.loop:
                    self.frame = 0
                else:
                    self.frame = len(self.images) - 1
                    self.done = True

    def img(self):
        return self.images[int(self.frame)]
        
    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)