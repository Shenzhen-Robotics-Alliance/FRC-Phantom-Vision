import pygame, sys, requests

# SERVER_URL = "http://onbot-jetson.local:5801"
SERVER_URL = "http://localhost:5801"

# Initialize Pygame
pygame.init()

# Set the dimensions of the field image
FIELD_WIDTH = 7680
FIELD_HEIGHT = 3812

# Calculate the aspect ratio
aspect_ratio = FIELD_WIDTH / FIELD_HEIGHT

# Choose a window height and calculate the width based on the aspect ratio
WINDOW_HEIGHT = 600
WINDOW_WIDTH = int(WINDOW_HEIGHT * aspect_ratio)

# Load the field image and scale it to fit the window
field_image = pygame.image.load("client/2024_Field_Dark.png")
field_image = pygame.transform.scale(field_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

# Create the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("FRC Robot Dashboard")

def field_to_pixel(field_coord, window_width, window_height):
    # Calculate the scaling factors for x and y coordinates
    scale_x = window_width / 16.54
    scale_y = window_height / 8.21

    # Convert field coordinate to pixel coordinate
    pixel_x = int(field_coord[0] * scale_x)
    pixel_y = window_height - int(field_coord[1] * scale_y)  # Pygame's origin is at the top-left

    return pixel_x, pixel_y

# Draw the field image
window.blit(field_image, (0, 0))

# Draw the navigation tags (outside the main loop)
font = pygame.font.Font(None, 36)
navigation_tags = [(1, 15.079471999999997, 0.24587199999999998), (2, 16.185134, 0.883666), (3, 16.579342, 4.982717999999999), (4, 16.579342, 5.547867999999999), (5, 14.700757999999999, 8.2042), (6, 1.8415, 8.2042), (7, -0.038099999999999995, 5.547867999999999), (8, -0.038099999999999995, 4.982717999999999), (9, 0.356108, 0.883666), (10, 1.4615159999999998, 0.24587199999999998), (11, 11.904726, 3.7132259999999997), (12, 11.904726, 4.49834), (13, 11.220196, 4.105148), (14, 5.320792, 4.105148), (15, 4.641342, 4.49834), (16, 4.641342, 3.7132259999999997)]

for tag_id, field_x, field_y in navigation_tags:
    pixel_x, pixel_y = field_to_pixel((field_x, field_y), WINDOW_WIDTH, WINDOW_HEIGHT)
    # Render text
    text = font.render(str(tag_id).zfill(2), True, (0, 0, 255))
    # Create a white rectangle to serve as background for text
    text_rect = text.get_rect(center=(pixel_x, pixel_y))
    # Limit the border of the labels to be inside the window
    text_rect.centerx = max(text_rect.width // 2, min(text_rect.centerx, WINDOW_WIDTH - text_rect.width // 2))
    text_rect.centery = max(text_rect.height // 2, min(text_rect.centery, WINDOW_HEIGHT - text_rect.height // 2))
    pygame.draw.rect(window, (255, 255, 255), text_rect)  # Draw white background
    window.blit(text, text_rect.topleft)  # Draw text

def get_robot_field_position() -> tuple:
    '''
    returns: the field position of the robot, in (x,y) and in meters
    '''
    response = requests.get(SERVER_URL + '/robot_pos')
    print(response.text.split()[0], response.text.split()[1])

    return (float(response.text.split()[0]), float(response.text.split()[1]))

def get_robot_rotation() -> float:
    '''
    returns: the facing of the robot, in radian. zero is facing front and positive is counter-clockwise
    '''
    response = requests.get(SERVER_URL + '/robot_rot')
    print(response.text)
    
    return float(response.text)

# Main loop
while True:
    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    get_robot_field_position()
    get_robot_rotation()

    # Update the display
    pygame.display.update()