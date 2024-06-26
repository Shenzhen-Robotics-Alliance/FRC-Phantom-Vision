import pygame, sys, math, logging
from networktables import NetworkTables


robot_width = 0.5  # meters
robot_length = 0.5  # meters
SERVER = "onbot-jetson.local"
# SERVER = "localhost"


logging.basicConfig(level=logging.DEBUG)
NetworkTables.startClient(SERVER)
NetworkTables.initialize()
robot_pos_x = NetworkTables.getTable("Vision").getEntry("robot_pos_x")
robot_pos_y = NetworkTables.getTable("Vision").getEntry("robot_pos_y")
robot_rot = NetworkTables.getTable("Vision").getEntry("robot_rotation")
tags_visibility_table = NetworkTables.getTable("Vision").getEntry("tags_visibility")

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
field_image = pygame.image.load("dashboard/2024_Field_Dark.png")
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

navigation_tags = [(1, 15.079471999999997, 0.24587199999999998), (2, 16.185134, 0.883666), (3, 16.579342, 4.982717999999999), (4, 16.579342, 5.547867999999999), (5, 14.700757999999999, 8.2042), (6, 1.8415, 8.2042), (7, -0.038099999999999995, 5.547867999999999), (8, -0.038099999999999995, 4.982717999999999), (9, 0.356108, 0.883666), (10, 1.4615159999999998, 0.24587199999999998), (11, 11.904726, 3.7132259999999997), (12, 11.904726, 4.49834), (13, 11.220196, 4.105148), (14, 5.320792, 4.105148), (15, 4.641342, 4.49834), (16, 4.641342, 3.7132259999999997)]
def draw_field_and_tags_as_background():
    # Draw the field image
    window.blit(field_image, (0, 0))

    # Draw the navigation tags (outside the main loop)
    font = pygame.font.Font(None, 36)

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
    return (robot_pos_x.getDouble(0), robot_pos_y.getDouble(0))


def get_robot_rotation() -> float:
    '''
    returns: the facing of the robot, in radian. zero is facing front and positive is counter-clockwise
    '''
    return robot_rot.getDouble(0)

def get_tags_visibility() -> list[bool]:
    '''
    returns: a boolean array marking, the visibilities of tags. Starting from tag id 1, True is visible.
    '''
    return tags_visibility_table.getBooleanArray([False for i in range(16)])

def mark_visible_tags(robot_head:tuple):
    '''
    Marks the visible tags with a straight, dotted line in gray that connects the robot's head (given its coordinate)
    and the tag's position (in navigation_tags).

    Parameters:
        window: Pygame display surface where the robot and tags are being drawn.
        robot_head: Tuple of pixel coordinates (x, y) for the robot's head position.
    '''
    visible_tags = get_tags_visibility()  # Assuming this function returns a list of boolean values for tag visibility

    # Draw a line for each visible tag
    for index, (_, field_x, field_y) in enumerate(navigation_tags):
        if visible_tags[index]:
            tag_pixel_position = field_to_pixel((field_x, field_y), WINDOW_WIDTH, WINDOW_HEIGHT)
            # Draw a dotted line from robot_head to tag_pixel_position
            draw_dotted_line(window, robot_head, tag_pixel_position, (255, 255, 0), 1)

def draw_dotted_line(surface, start_pos, end_pos, color, width=3):
    '''
    Draws a dotted line between two points.

    Parameters:
        surface: The pygame surface on which to draw.
        start_pos: Starting position tuple (x, y).
        end_pos: Ending position tuple (x, y).
        color: Color of the line.
        width: Width of the line.
    '''
    x1, y1 = start_pos
    x2, y2 = end_pos
    distance = math.hypot(x2 - x1, y2 - y1)
    dots = int(distance / width * 2)  # Number of dots, 10 pixels apart
    for n in range(dots):
        x = x1 + n * (x2 - x1) / dots
        y = y1 + n * (y2 - y1) / dots
        pygame.draw.circle(surface, color, (int(x), int(y)), width)


# Function to draw the robot on the dashboard
ROBOT_DISPLAY_LENGTH_METERS = 0.7
ROBOT_DISPLAY_WIDTH_METERS = 0.6
def draw_robot(robot_pos, robot_rotation) -> tuple:
    '''
    returns: the position of the dot, that represents the robot's head
    '''

    robot_rotation *= -1
     # Calculate the robot's pixel position
    pixel_pos = field_to_pixel(robot_pos, WINDOW_WIDTH, WINDOW_HEIGHT)

    # Dimensions of the robot rectangle in pixels
    pixel_width = field_to_pixel((ROBOT_DISPLAY_LENGTH_METERS, 0), WINDOW_WIDTH, WINDOW_HEIGHT)[0] - field_to_pixel((0, 0), WINDOW_WIDTH, WINDOW_HEIGHT)[0]
    pixel_length = field_to_pixel((0, ROBOT_DISPLAY_WIDTH_METERS), WINDOW_WIDTH, WINDOW_HEIGHT)[1] - field_to_pixel((0, 0), WINDOW_WIDTH, WINDOW_HEIGHT)[1]

    # Calculate rectangle corners before rotation
    rect_corners = [
        (-pixel_width / 2, -pixel_length / 2),
        (pixel_width / 2, -pixel_length / 2),
        (pixel_width / 2, pixel_length / 2),
        (-pixel_width / 2, pixel_length / 2)
    ]

    # Rotate corners and translate to actual position
    rotated_corners = [
        (math.cos(robot_rotation) * x - math.sin(robot_rotation) * y + pixel_pos[0],
         math.sin(robot_rotation) * x + math.cos(robot_rotation) * y + pixel_pos[1])
        for x, y in rect_corners
    ]

    # Draw robot rectangle
    pygame.draw.polygon(window, (255, 0, 0), rotated_corners)

    # Calculate midpoint of the front edge for the "head" dot
    front_mid = (
        (rotated_corners[1][0] + rotated_corners[2][0]) / 2,
        (rotated_corners[1][1] + rotated_corners[2][1]) / 2
    )

    # Draw head dot
    pygame.draw.circle(window, (0, 255, 0), (int(front_mid[0]), int(front_mid[1])), 5)  # 5 pixels radius for the dot

    return (int(front_mid[0]), int(front_mid[1]))

fps = 60
clock = pygame.time.Clock()
try:
    while True:
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
        draw_field_and_tags_as_background()
        NetworkTables.flush()

        mark_visible_tags(draw_robot(get_robot_field_position(), get_robot_rotation()))
        # if not NetworkTables.isConnected():
        #     print("<-- trying to connect to server -->")
        # draw_robot((5, 5), 0)

        # Update the display
        pygame.display.update()

        clock.tick(fps)
except KeyboardInterrupt:
    print("user interrupt, exiting...")