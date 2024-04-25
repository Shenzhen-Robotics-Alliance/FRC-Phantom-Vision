import logging
from networktables import NetworkTables

from MathUtils.LinearAlgebra import *
from MathUtils.cameraprofiles import CameraProfile
from apriltagdetection import AprilTagCamera


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


robot_odometry_position = Vector2D((7.2,4.8))
robot_odometry_rotation = Rotation2D(0)
robot_visual_position = -1
robot_odometry_position_last_navigation = Vector2D()
visible_tags = []

def get_robot_position_via_navigation_tag(id:int, tag_relative_position_to_robot:Vector2D, robot_facing:Rotation2D):
    tag_field_position = tags_on_field[id].position_on_field
    tag_relative_position_to_robot_field_oriented = tag_relative_position_to_robot.multiply_by(robot_facing).multiply_by(Rotation2D(math.radians(90)))
    robot_relative_position_to_tag_field_oriented = tag_relative_position_to_robot_field_oriented.multiply_by_scalar(-1)
    return robot_relative_position_to_tag_field_oriented.add_by(tag_field_position)

def process_results(camera_resolution:tuple, cameras:list[AprilTagCamera], camera_profiles:list[CameraProfile]):
    global robot_visual_position, visible_tags
    # TODO: if different estimates deviates too much from one another, we think the results are not trustable
    estimationSums = Vector2D()
    visible_tags = []
    for camera_id in range(len(cameras)):
        camera = cameras[camera_id]
        camera_profile = camera_profiles[camera_id]
        tags = camera.tags
        for tag in tags:
            if tag.tag_id not in tags_on_field:
                continue
            visible_tags.append(tag.tag_id)
            relative_position = camera_profile.get_relative_position_to_robot(tags_on_field[tag.tag_id].height, tag.center[0]-camera_resolution[0]/2, tag.center[1]-camera_resolution[1]/2)
            estimate = get_robot_position_via_navigation_tag(tag.tag_id, relative_position, robot_odometry_rotation)
            estimationSums = estimationSums.add_by(estimate)
    if len(tags) == 0:
        robot_visual_position = None
    else:
        robot_visual_position = estimationSums.multiply_by_scalar(1/len(tags))
    # print("robot visual pos: ", robot_visual_position)


logging.basicConfig(level=logging.DEBUG)
NetworkTables.initialize()
NetworkTables.startServer(listenAddress="0.0.0.0")
robot_pos_x = NetworkTables.getTable("Vision").getEntry("robot_pos_x")
robot_pos_y = NetworkTables.getTable("Vision").getEntry("robot_pos_y")
tags_visibility_table = NetworkTables.getTable("Vision").getEntry("tags_visibility")

odomoter_pos_x_entry = NetworkTables.getTable("Vision").getEntry("odometer_x")
odometer_pos_y_entry = NetworkTables.getTable("Vision").getEntry("odometer_pos_y")
robot_rot_entry = NetworkTables.getTable("Vision").getEntry("robot_rotation")

def pull_odometry_data_from_networktable():
    global robot_odometry_position, robot_odometry_rotation
    robot_odometry_position = Vector2D((
        odomoter_pos_x_entry.getDouble(robot_odometry_position.get_x()),
        odometer_pos_y_entry.getDouble(robot_odometry_position.get_y()) 
    ))
    robot_odometry_rotation = Rotation2D(robot_rot_entry.getDouble(robot_odometry_rotation.get_radian()))

def send_results_to_networktable():
    tags_visibility = [False for i in range(16)]
    for i in visible_tags:
        tags_visibility[i-1] = True
    tags_visibility_table.setBooleanArray(tags_visibility)

    if robot_visual_position is None:
        robot_pos_x.setDouble(robot_odometry_position.get_x())
        robot_pos_y.setDouble(robot_odometry_position.get_y())
    else:
        robot_pos_x.setDouble(robot_visual_position.get_x())
        robot_pos_y.setDouble(robot_visual_position.get_y())