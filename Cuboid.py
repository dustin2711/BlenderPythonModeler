from copy import *
import bpy

from mathutils import Vector

rounding = 0.001


class Blueprint:

    @staticmethod
    def roundfloat(value, roundTo=rounding):
        return round(value / roundTo) * roundTo

    def render(self):
        raise NotImplementedError("Render method was not implemented.")


class BlueprintContainer(Blueprint):

    def __init__(self):
        self.children: list[Blueprint] = []

    def add_child(self, child: Blueprint):
        self.children.append(child)

    def add_children(self, children: list[Blueprint]):
        self.children.extend(children)

    def render(self):
        for child in self.children:
            child.render()


class Cuboid(Blueprint):
    """Use this to specify a cuboid that will be rendered."""

    def __init__(self, left=0, right=1, bot=0, top=1, back=0, front=1):
        self._left = left
        self._right = right
        self._bot = bot
        self._top = top
        self._back = back
        self._front = front

    # 6 main values

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, value: float):
        self._left = self.roundfloat(value)

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, value: float):
        self._right = self.roundfloat(value)

    @property
    def bot(self):
        return self._bot

    @bot.setter
    def bot(self, value: float):
        self._bot = self.roundfloat(value)

    @property
    def top(self):
        return self._top

    @top.setter
    def top(self, value: float):
        self._top = self.roundfloat(value)

    @property
    def back(self):
        return self._back

    @back.setter
    def back(self, value: float):
        self._back = self.roundfloat(value)

    @property
    def front(self):
        return self._front

    @front.setter
    def front(self, value: float):
        self._front = self.roundfloat(value)

    # Size

    @property
    def height(self):
        return self._top - self._bot

    @height.setter
    def height(self, value: float):
        """Changes top so that height is as given."""
        self._top = self.roundfloat(self._bot + value)

    # @property height:
    #     get: return self.top - self.bot
    #     set: self.top = self.round(self.bot + value)

    # height = property(
    #     lambda self: self.top - self.bot,
    #     lambda self, value: self.top := self.round(self.bot + value) # setattr would work...
    # )

    @property
    def width(self):
        return self._right - self._left

    @width.setter
    def width(self, value: float):
        """Changes right so that width is as given."""
        self._right = self.roundfloat(self._left + value)

    @property
    def depth(self):
        return self._front - self._back

    @depth.setter
    def depth(self, value: float):
        """Changes front so that depth is as given."""
        self._front = self.roundfloat(self._back + value)

    # Corners

    @property
    def frontrighttop(self):
        return Vector((self._front, self._right, self._top))

    @frontrighttop.setter
    def frontrighttop(self, value: Vector):
        self.front = value.x
        self.right = value.y
        self.top = value.z

    @property
    def backrightbot(self):
        return Vector((self.back, self.right, self.bot))

    @backrightbot.setter
    def backrightbot(self, value: Vector):
        self.back = value.x
        self.right = value.y
        self.bot = value.z

    @property
    def frontleftbot(self):
        return Vector((self.front, self.left, self.bot))

    @frontleftbot.setter
    def frontleftbot(self, value: Vector):
        self.front = value.x
        self.left = value.y
        self.bot = value.z

    @property
    def backleftbot(self):
        return Vector((self.back, self.left, self.bot))

    @backleftbot.setter
    def backleftbot(self, value: Vector):
        self.back = value.x
        self.left = value.y
        self.bot = value.z

    @property
    def backlefttop(self):
        return Vector((self.back, self.left, self.top))

    @backlefttop.setter
    def backlefttop(self, value: Vector):
        self.back = value.x
        self.left = value.y
        self.top = value.z

    @property
    def frontrightbot(self):
        return Vector((self.front, self.right, self.bot))

    @frontrightbot.setter
    def frontrightbot(self, value: Vector):
        self.front = value.x
        self.right = value.y
        self.bot = value.z

    @property
    def frontlefttop(self):
        return Vector((self.front, self.left, self.top))

    @frontlefttop.setter
    def frontlefttop(self, value: Vector):
        self.front = value.x
        self.left = value.y
        self.top = value.z

    @property
    def backrighttop(self):
        return Vector((self.back, self.right, self.top))

    @backrighttop.setter
    def backrighttop(self, value: Vector):
        self.back = value.x
        self.right = value.y
        self.top = value.z

    # Functions

    def render(self):  # -> bpy.types.Object:
        # Calculate dimensions of the cuboid
        dimensions = self.frontrighttop - self.backleftbot
        # Create cuboid mesh
        bpy.ops.mesh.primitive_cube_add(
            size=1, enter_editmode=False, align="WORLD", location=(0, 0, 0)
        )
        cuboid_obj = bpy.context.object

        # Scale cuboid to match dimensions
        cuboid_obj.scale = dimensions

        # Move cuboid to start point
        cuboid_obj.location = self.backleftbot + dimensions / 2

        return cuboid_obj

    def copy(self):
        return Cuboid(
            self._left, self._right, self._bot, self._top, self._back, self._front
        )
        # return deepcopy(self)

    def __str__(self):
        return f"Cube: {self._left} to {self._right}, {self._bot} to {self._top}, {self._back} to {self._front}"

    def __repr__(self):
        return self.__str__()

    def copy(self):
        return deepcopy(self)
