from MathUtils.LinearAlgebra import *


class TagOnField:
    def __init__(self, position_on_field:Vector2D, height:float):
        self.position_on_field = position_on_field
        self.height = height

tags_on_field = {} # id:TagOnField

# Given dataset from 
tags_data = [
    (1, 593.68, 9.68, 53.38),
    (2, 637.21, 34.79, 53.38),
    (3, 652.73, 196.17, 57.13),
    (4, 652.73, 218.42, 57.13),
    (5, 578.77, 323.00, 53.38),
    (6, 72.5, 323.00, 53.38),
    (7, -1.50, 218.42, 57.13),
    (8, -1.50, 196.17, 57.13),
    (9, 14.02, 34.79, 53.38),
    (10, 57.54, 9.68, 53.38),
    (11, 468.69, 146.19, 52.00),
    (12, 468.69, 177.10, 52.00),
    (13, 441.74, 161.62, 52.00),
    (14, 209.48, 161.62, 52.00),
    (15, 182.73, 177.10, 52.00),
    (16, 182.73, 146.19, 52.00)
]

# Function to convert inches to meters
def inches_to_meters(value):
    return value * 0.0254

# Populating the tags_on_field dictionary
rst = []
for id, x, y, z in tags_data:
    rst.append((id, inches_to_meters(x), inches_to_meters(y)))
    tags_on_field[id] = TagOnField(Vector2D([inches_to_meters(x), inches_to_meters(y)]), inches_to_meters(z))

print(rst)

def get_robot_position_via_navigation_tag(id:int, tag_relative_position_to_robot:Vector2D, robot_facing:Rotation2D):
    tag_field_position = tags_on_field[id].position
    tag_relative_position_to_robot_field_oriented = tag_relative_position_to_robot.multiply_by(robot_facing)
    robot_relative_position_to_tag_field_oriented = tag_relative_position_to_robot_field_oriented.multiply_by(-1)
    return robot_relative_position_to_tag_field_oriented.add_by(tag_field_position)

