from math import *
from MathUtils.LinearAlgebra import Vector2D

camera_radian_per_pixel_x = 0.00181
camera_radian_per_pixel_y = -0.00107
camera_installation_angle = 0.2984
camera_installation_height = 0.45 # meters
robot_length = 0.64 # meters

def get_relative_position_to_robot(targert_height, pixel_x, pixel_y):
    target_theta = pixel_y*camera_radian_per_pixel_y + camera_installation_angle

    target_h = targert_height - camera_installation_height
    target_y = target_h / tan(target_theta)

    target_x = target_y * tan(pixel_x * camera_radian_per_pixel_x)

    return Vector2D([target_x, target_y + robot_length / 2])