import pygame
from settings import ROOM_WIDTH, ROOM_HEIGHT, ROOM_COLORS

class Room:
    def __init__(self, room_x_index, room_y_index, color):
        self.room_x_index = room_x_index # Grid index, not pixel
        self.room_y_index = room_y_index # Grid index, not pixel
        self.color = color
        # Calculate the room's bounds in world coordinates
        self.world_rect = pygame.Rect(
            room_x_index * ROOM_WIDTH,
            room_y_index * ROOM_HEIGHT,
            ROOM_WIDTH,
            ROOM_HEIGHT
        )

    def draw(self, surface, camera_offset_x, camera_offset_y):
        # Adjust draw position based on camera
        # This room's top-left corner in screen coordinates
        screen_x = self.world_rect.x - camera_offset_x
        screen_y = self.world_rect.y - camera_offset_y
        
        # Only draw if the room is visible on the screen
        # This is a basic visibility check; more complex culling could be added
        if screen_x < surface.get_width() and screen_x + ROOM_WIDTH > 0 and \
           screen_y < surface.get_height() and screen_y + ROOM_HEIGHT > 0:
            pygame.draw.rect(surface, self.color, (screen_x, screen_y, ROOM_WIDTH, ROOM_HEIGHT))
            # Optional: Draw a border to distinguish rooms
            pygame.draw.rect(surface, (0,0,0), (screen_x, screen_y, ROOM_WIDTH, ROOM_HEIGHT), 1)

if __name__ == '__main__':
    # Example usage (requires a Pygame screen setup to run)
    pygame.init()
    screen = pygame.display.set_mode((ROOM_WIDTH, ROOM_HEIGHT))
    pygame.display.set_caption("Room Test")
    
    # Create a sample room
    test_room = Room(0, 0, ROOM_COLORS[0])
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((255,255,255)) # White background
        test_room.draw(screen, 0, 0) # Draw room with no camera offset
        pygame.display.flip()
        
    pygame.quit()
