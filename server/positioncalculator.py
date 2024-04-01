from math import *
from MathUtils.LinearAlgebra import Vector2D

horizontal_projection_ratio = 0.0019083090502545134
vertical_projection_ratio = -0.0018938381148259048
camera_installation_angle = radians(30)
camera_installation_height = 0

def get_relative_position_to_robot(targert_height, pixel_x, pixel_y):
    target_theta = atan(pixel_y * vertical_projection_ratio) + camera_installation_angle

    target_h = targert_height - camera_installation_height
    target_y = target_h / tan(target_theta)

    target_x = target_y * pixel_x * horizontal_projection_ratio
    print("px:", pixel_x)

    return Vector2D([target_x, target_y])