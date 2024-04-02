import numpy as np
from MathUtils.AngleUtils import *

class Vector2D:
    def __init__(self, *args):
        if len(args) == 0:
            self.array = np.array([0, 0])
        elif len(args) == 1:
            self.array = np.array(args[0])
        elif len(args) == 2:
            heading, magnitude = args
            self.array = np.array([math.cos(heading) * magnitude, math.sin(heading) * magnitude])
        else:
            raise ValueError("Expected at most two arguments, got more.")

    def get_value(self) -> list:
        """
        Get the value of the vector.

        Returns:
        - np.ndarray: A numpy array representing the vector with two elements [x, y].
        """
        return self.array.tolist()

    def get_x(self) -> float:
        """
        Get the x-coordinate of the vector.

        Returns:
        - float: The x-coordinate of the vector.
        """
        return self.array[0]

    def get_y(self) -> float:
        """
        Get the y-coordinate of the vector.

        Returns:
        - float: The y-coordinate of the vector.
        """
        return self.array[1]

    def update(self, new_vector: 'Vector2D') -> None:
        """
        Update the vector with a new value.

        Parameters:
        - new_vector: A numpy array representing the new value of the vector with two elements [x, y].
        """
        self.array = new_vector.array

    def multiply_by(self, transformation: 'Transformation2D') -> 'Vector2D':
        """
        Multiply the vector by a transformation.

        Parameters:
        - transformation: A 2x2 numpy array representing the transformation matrix.

        Returns:
        - Vector2D: The resulting vector after multiplication.
        """
        return transformation.multiply(self)

    def multiply_by_scalar(self, scaler: float) -> 'Vector2D':
        """
        Scale the vector by a scalar value.

        Parameters:
        - scaler: The scalar value to multiply the vector by.

        Returns:
        - Vector2D: The resulting vector after scaling.
        """
        return Vector2D(scaler * self.array)

    def add_by(self, adder: 'Vector2D') -> 'Vector2D':
        """
        Add another vector to the current vector.

        Parameters:
        - adder: A numpy array representing the vector to add.

        Returns:
        - Vector2D: The resulting vector after addition.
        """
        return Vector2D(self.array + adder.array)

    def get_heading(self) -> float:
        """
        Get the heading angle of the vector.

        Returns:
        - float: The heading angle of the vector in radians.
        """
        return np.arctan2(self.array[1], self.array[0])

    def get_magnitude(self) -> float:
        """
        Get the magnitude of the vector.

        Returns:
        - float: The magnitude of the vector.
        """
        return np.linalg.norm(self.array)

    def __eq__(self, other: 'Vector2D') -> bool:
        """
        Check if two vectors are equal.

        Parameters:
        - other: Another Vector2D object for comparison.

        Returns:
        - bool: True if the vectors are equal, False otherwise.
        """
        return np.array_equal(self.array, other.array)

    def __str__(self) -> str:
        """
        Get the string representation of the vector.

        Returns:
        - str: The string representation of the vector.
        """
        return f"vector with value:\n {self.array}"


class Transformation2D:
    @staticmethod
    def get_original_space() -> np.ndarray:
        """
        Get the original unstressed space transformation.

        Returns:
        - np.ndarray: The original unstressed space transformation as a 2x2 numpy array.
        """
        return np.eye(2)

    def __init__(self, *args: list) -> None:
        """
        Initialize a 2D transformation.

        Parameters:
        - args: Variable-length argument list. It can be empty, a 2x2 numpy array representing the initial value,
                or two Vector2D objects representing the iHat and jHat vectors.
        """
        if len(args) == 0:
            self.array = Transformation2D.get_original_space()
        elif len(args) == 1:
            self.array = np.array(args[0])
        elif len(args) == 2:
            self.array = np.array([list(args[0]), list[args[1]]])
        else:
            raise ValueError("Expected at most two arguments, got more.")

    def set_value(self, value:list) -> None:
        """
        Set the value of the transformation.

        Parameters:
        - value: A 2x2 numpy array representing the transformation matrix.
        """
        self.array = np.array(value)

    def get_value(self) -> list:
        """
        Get the value of the transformation.

        Returns:
        - np.ndarray: A 2x2 numpy array representing the transformation matrix.
        """
        return self.array.tolist()

    def multiply(self, vector: 'Vector2D') -> 'Vector2D':
        """
        Apply the transformation to a given vector.

        Parameters:
        - vector: A numpy array representing the vector to transform.

        Returns:
        - np.ndarray: The transformed vector.
        """
        return Vector2D(np.dot(self.array, vector.array))

    def get_determinant(self) -> float:
        """
        Calculate the determinant of the transformation matrix.

        Returns:
        - float: The determinant of the transformation matrix.
        """
        return np.linalg.det(self.array)

    def get_reversal(self) -> 'Transformation2D':
        """
        Get the reversal of the transformation.

        Returns:
        - np.ndarray: The reversal of the transformation as a 2x2 numpy array.
        """
        return Transformation2D(np.linalg.inv(self.array))

    def __str__(self) -> str:
        """
        Get the string representation of the transformation.

        Returns:
        - str: The string representation of the transformation.
        """
        return f"transformation with value: \n {self.array}"

    def __eq__(self, other: 'Transformation2D') -> bool:
        """
        Check if two transformations are equal.

        Parameters:
        - other: Another Transformation2D object for comparison.

        Returns:
        - bool: True if the transformations are equal, False otherwise.
        """
        return np.array_equal(self.array, other.array)

class Rotation2D(Transformation2D):
    def __init__(self, radian):
        radian = simplify_angle(radian)
        iHat = [np.cos(radian), np.sin(radian)]
        jHat = [np.cos(radian + np.pi / 2), np.sin(radian + np.pi / 2)]
        
        super().__init__([iHat, jHat])
        self.radian = radian

    def get_radian(self):
        return self.radian

    def add(self, another_rotation):
        return Rotation2D(simplify_angle(self.get_radian() + another_rotation.get_radian()))

    def __str__(self):
        return f"rotation with radian: {self.get_radian()} \nand vector value: {super().__str__()}"

