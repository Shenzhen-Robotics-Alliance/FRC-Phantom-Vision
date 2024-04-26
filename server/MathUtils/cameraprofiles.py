from math import *
from MathUtils.LinearAlgebra import *



class CameraProfile:
    def __init__(self, horizontal_project_ratio:float, vertical_projection_ratio:float, camera_installation_angle:float, camera_installation_height:float, camera_position_on_robot:Vector2D, camera_facing:Rotation2D):
        self.horizontal_projection_ratio = horizontal_project_ratio
        self.vevertical_projection_ratio = vertical_projection_ratio
        self.camera_installation_angle = camera_installation_angle
        self.camera_installation_height = camera_installation_height
        self.camera_position_on_robot = camera_position_on_robot
        Vector2D([0,0.35])

        self.camera_facing = camera_facing

    def get_relative_position_to_robot(self, targert_height, pixel_x, pixel_y):
        target_theta = atan(pixel_y * self.vevertical_projection_ratio) + self.camera_installation_angle

        target_h = targert_height - self.camera_installation_height
        target_y = target_h / tan(target_theta)

        # TODO: improve this algorithm
        target_x = target_y * pixel_x * self.horizontal_projection_ratio
        print("px:", pixel_x)

        return Vector2D([target_x, target_y]).add_by(self.camera_position_on_robot).multiply_by(self.camera_facing)