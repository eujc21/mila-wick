import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, health=100):
        super().__init__()
        self.x = x  # World x-coordinate
        self.y = y  # World y-coordinate
        # It's generally better to have image and rect attributes for a Sprite
        # self.image will be defined in subclasses or needs a placeholder here
        # self.rect will also be defined in subclasses, typically using self.x, self.y
        # For now, let's assume subclasses will handle image and rect creation.
        
        self.health = health
        self.max_health = health
        self.alive = True
        
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0 # Ensure health doesn't go below 0
            self.alive = False
            self.kill() # kill() is a method from pygame.sprite.Sprite to remove it from all groups
            
    def update(self, dt): # dt for delta time, common in game loops
        pass # To be overridden in subclasses for specific update logic
