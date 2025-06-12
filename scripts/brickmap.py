import csv
from scripts.entities import Brick

class Tilemap:
    def __init__(self, game):
        self.game = game

    def read(self, map):
        OFFSET_Y = 40
        TILE_HEIGHT = 32
        TILE_WIDTH = [64, 128]
        for row_idx, row in enumerate(map):
            for col_idx, tile in enumerate(row):
                if tile != -1:
                    x = col_idx * TILE_WIDTH[0]
                    y = row_idx * TILE_HEIGHT + OFFSET_Y
                    if tile <14:
                        self.game.entities.append(Brick(self.game, (x, y), (TILE_WIDTH[0], TILE_HEIGHT), tile))     
                    elif tile >= 14:
                        self.game.entities.append(Brick(self.game, (x, y), (TILE_WIDTH[1], TILE_HEIGHT), tile))