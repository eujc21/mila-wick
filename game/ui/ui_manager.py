import pygame

class UIManager:
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def update(self, dt):
        for element in self.elements:
            if hasattr(element, 'update'):
                element.update(dt)

    def draw(self):
        for element in self.elements:
            if hasattr(element, 'draw'):
                element.draw(self.screen)

    def handle_event(self, event):
        for element in self.elements:
            if hasattr(element, 'handle_event'):
                element.handle_event(event)
