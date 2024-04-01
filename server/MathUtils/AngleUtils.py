import math
def simplify_angle(radian):
    """
    Simplify an angle into the range 0-360 degrees.

    Parameters:
    - radian (float): The angle to simplify, in radians.

    Returns:
    - float: The simplified angle, in radians and in the range 0 < x < 2*pi.
    """
    if math.isnan(radian) or math.isinf(radian) or abs(radian) > 10e7:
        raise ValueError("invalid radian: " + str(radian))
    radian = math.copysign(radian % (math.pi * 2), radian)
    if radian < 0:
        radian += math.pi * 2
    return radian

def get_actual_difference(current_rotation, targeted_rotation):
    """
    Get the shortest rotational distance (and its direction) needed to get from the current to targeted rotation.

    Parameters:
    - current_rotation (float): The current rotation, in radians.
    - targeted_rotation (float): The desired rotation, in radians.

    Returns:
    - float: The shortest distance between the two points, in radians, where positive is counter-clockwise.
    """
    loop_length = math.pi * 2
    current_rotation = simplify_angle(current_rotation)
    targeted_rotation = simplify_angle(targeted_rotation)
    difference = targeted_rotation - current_rotation
    if difference > loop_length / 2:
        return -(loop_length - difference)  # go the other way around
    if difference < -loop_length / 2:
        return loop_length + difference  # go the other way around
    return difference

def find_mid_point(rotation1, rotation2):
    """
    Get the midpoint between two points.

    Parameters:
    - rotation1 (float): The first rotation, in radians.
    - rotation2 (float): The second rotation, in radians.

    Returns:
    - float: The midpoint between the two rotations, in radians.
    """
    return simplify_angle(rotation1 + get_actual_difference(rotation1, rotation2))