"""
To use this script, fun these VSCode commands from "Blender Development" extension:
1. Blender: Start (one time at start)
2. Blender: Run Script (each time to execute script)
"""

import sys

# from varname import nameof # Doesnt work with blender :(

sys.path.append("E:/Coding/BlueprintCreator")
import bpy
from mathutils import Vector
from enum import Enum

from Cuboid import *

import bmesh


def clear_objects():
    objects = bpy.context.scene.objects
    # # Find and delete all objects with names starting with "Cube"
    # cube_objs = [
    #     obj for obj in bpy.context.scene.objects if obj.name.startswith("Cube")
    # ]
    bpy.ops.object.select_all(action="DESELECT")
    for objext in objects:
        objext.select_set(True)
    bpy.ops.object.delete()


# Clear existing blender objects
clear_objects()

left = Vector((0, -1, 0))
right = Vector((0, 1, 0))
up = Vector((0, 0, 1))
down = Vector((0, 0, -1))
forward = Vector((1, 0, 0))
backward = Vector((-1, 0, 0))


class Side(Enum):
    BotTop = 0
    """Bot and top. """
    LeftRight = 1
    """Left and right. """
    BackFront = 2
    """Back and front. """


rounding = 0.001


class Blueprint:
    def __init__(self, name=""):
        self.name = name if name else "Blueprint"
        self.parent: Blueprint = None
        """The parent blueprint (if available). """
        self.blender_object: bpy.types.Object = None
        """The created Blender object. This is None if create() was not called yet. """

    @staticmethod
    def roundfloat(value, roundTo=rounding):
        return round(value / roundTo) * roundTo

    def create(self, parent=None):
        """Creates a Blender object from this blueprint.
        Also sets the parent if it is available."""

        # Set parent if given
        if parent:
            self.parent = parent

        self._create()

        # Set name
        self.blender_object.name = self.name
        # if self.parent:
        #     self.blender_object.name = self.parent.name + "." + self.name

        # Set parent if available
        if self.parent and self.parent.blender_object:
            self.blender_object.parent = self.parent.blender_object

    def _create(self):
        """
        Private create method.
        Creates an empty node if not overriden.
        """
        self.blender_object = bpy.data.objects.new(self.name, None)
        bpy.context.scene.collection.objects.link(self.blender_object)


class BlueprintContainer(Blueprint):
    """Parent of multiple blueprint children."""

    def __init__(self, name="BlueprintContainer"):
        super().__init__(name)

        self.children: list[Blueprint] = []

    def add_child(self, child: Blueprint):
        self.children.append(child)

    def add_children(self, children: list[Blueprint]):
        self.children.extend(children)

    def create(self):
        super().create()

        for child in self.children:
            child.create(self)


class Cuboid(Blueprint):
    """Use this to specify a cuboid that will be rendered."""

    def __init__(self, name="Cuboid", left=0, right=1, bot=0, top=1, back=0, front=1):
        super().__init__(name)
        self._left = left
        self._right = right
        self._bot = bot
        self._top = top
        self._back = back
        self._front = front

    def move(self, x=0, y=0, z=0):
        self._left += y
        self._right += y
        self._back += x
        self._front += x
        self._bot += z
        self._top += z

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
        """Changes  so that height is as given."""
        """Changes top (if positive) or bot (if negative) so that width is as given."""
        if value < 0:
            self._bot = self.roundfloat(self._top + value)
        else:
            self._top = self.roundfloat(self._bot + value)

    @property
    def width(self):
        return self._right - self._left

    @width.setter
    def width(self, value: float):
        """Changes right (if positive) or left (if negative) so that width is as given."""
        if value < 0:
            self._left = self.roundfloat(self._right + value)
        else:
            self._right = self.roundfloat(self._left + value)

    @property
    def depth(self):
        return self._front - self._back

    @depth.setter
    def depth(self, value: float):
        """Changes front (if positive) or back (if negative) so that width is as given."""
        if value < 0:
            self._back = self.roundfloat(self._front + value)
        else:
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

    def _create(self):
        dimensions = self.frontrighttop - self.backleftbot
        location = self.backleftbot + dimensions / 2

        bpy.ops.mesh.primitive_cube_add(
            size=1,
            enter_editmode=False,
            align="WORLD",
            location=location,
            scale=dimensions,
        )

        self.blender_object = bpy.context.object

    def __str__(self):
        return f"Cube: {self._left} to {self._right}, {self._bot} to {self._top}, {self._back} to {self._front}"

    def __repr__(self):
        return self.__str__()

    def copy(self, name):
        cuboid = deepcopy(self)
        cuboid.name = name
        return cuboid


class Box(BlueprintContainer):

    def __init__(
        self,
        name="Box",
        back=0,
        left=0,
        bot=0,
        depth=1,
        width=1,
        height=1,
        thickness=0.01,
        big_side=Side.LeftRight,  # The side where both planks have full size (the beautiful side)
        small_side=Side.BotTop,  # The side where both planks have no max size in neither direction (the not so beautiful side)
    ):
        """Creates a box out of 6 cuboid with the outer given size and the given thickness for each side."""
        super().__init__(name)

        if big_side == small_side:
            raise ValueError("Outer and inner side must differ.")

        backleftbot = Vector((back, left, bot))

        botTopHaveMaxWidth = big_side == Side.BotTop or (
            big_side == Side.BackFront and small_side == Side.LeftRight
        )
        botTopHaveMaxDepth = big_side == Side.BotTop or (
            big_side == Side.LeftRight and small_side == Side.BackFront
        )
        leftRightHaveMaxDepth = big_side == Side.LeftRight or (
            big_side == Side.BotTop and small_side == Side.BackFront
        )
        leftRightHaveMaxHeight = big_side == Side.LeftRight or (
            big_side == Side.BackFront and small_side == Side.BotTop
        )
        backFrontHaveMaxWidth = big_side == Side.BackFront or (
            big_side == Side.BotTop and small_side == Side.LeftRight
        )
        backFrontHaveMaxHeight = big_side == Side.BackFront or (
            big_side == Side.LeftRight and small_side == Side.BotTop
        )

        # Bot part
        botpart = Cuboid("botpart")
        botpart.backleftbot = backleftbot
        botpart.height = thickness
        botpart.width = width
        botpart.depth = depth
        if not botTopHaveMaxWidth:
            botpart.left += thickness
            botpart.right -= thickness
        if not botTopHaveMaxDepth:
            botpart.back += thickness
            botpart.front -= thickness

        # Left part
        leftpart = Cuboid("leftpart")
        leftpart.backleftbot = backleftbot
        leftpart.width = thickness
        leftpart.front = depth
        leftpart.height = height
        if not leftRightHaveMaxHeight:
            leftpart.bot += thickness
            leftpart.top -= thickness
        if not leftRightHaveMaxDepth:
            leftpart.back += thickness
            leftpart.front -= thickness

        # Back part
        backpart = Cuboid("backpart")
        backpart.backleftbot = backleftbot
        backpart.depth = thickness
        backpart.width = width
        backpart.height = height
        if not backFrontHaveMaxWidth:
            backpart.left += thickness
            backpart.right -= thickness
        if not backFrontHaveMaxHeight:
            backpart.bot += thickness
            backpart.top -= thickness

        # Right part
        rightpart = leftpart.copy("rightpart")
        rightpart.move(y=width - thickness)

        # Top part
        toppart = botpart.copy("toppart")
        toppart.move(z=height - thickness)

        # Bot part
        frontpart = backpart.copy("frontpart")
        frontpart.move(x=depth - thickness)

        self.add_children([botpart, leftpart, rightpart, toppart, backpart, frontpart])


# # Box parameters
# thickness = 0.02
# width = 0.80
# depth = 0.50
# height = 0.30

# box1 = Box(
#     "Box1",
#     0,
#     0,
#     0,
#     depth,
#     width,
#     height,
#     thickness,
#     big_side=Side.BotTop,
#     small_side=Side.LeftRight,
# )
# box1.create()

# box2 = Box(
#     "Box2",
#     0,
#     1,
#     0,
#     depth,
#     width,
#     height,
#     thickness,
#     big_side=Side.LeftRight,
#     small_side=Side.BotTop,
# )
# box2.create()

# box3 = Box(
#     "Box3",
#     0,
#     2,
#     0,
#     depth,
#     width,
#     height,
#     thickness,
#     big_side=Side.BackFront,
#     small_side=Side.BotTop,
# )
# box3.create()


def create_frame_part(width, height, thickness):
    # Create a new mesh
    mesh = bpy.data.meshes.new(name="FramePartMesh")
    obj = bpy.data.objects.new(name="FramePart", object_data=mesh)
    bpy.context.collection.objects.link(obj)

    # Create a bmesh
    bm = bmesh.new()

    # Define corner vertices
    corners = [
        (-width / 2, -height / 2, 0),
        (-width / 2, height / 2, 0),
        (width / 2, height / 2, 0),
        (width / 2, -height / 2, 0),
    ]

    # Create vertices and edges for each corner
    for i in range(4):
        v1 = bm.verts.new(corners[i])
        v2 = bm.verts.new(corners[(i + 1) % 4])
        e = bm.edges.new((v1, v2))

    # Connect corners with edges
    for i in range(4):
        v1 = bm.verts[i]
        v2 = bm.verts[(i + 1) % 4]
        v3 = bm.verts[(i + 2) % 4]
        bm.edges.new((v1, v3))

    # Extrude the face to give it thickness
    bottom_face = bm.faces.new(bm.verts)
    bmesh.ops.translate(bm, vec=(0, 0, thickness))
    top_face = bm.faces.new(bm.verts)

    # Update the bmesh and mesh
    bm.to_mesh(mesh)
    bm.free()


# Example usage
# create_frame_part(width=2.0, height=2.0, thickness=0.1)


class Quad(Blueprint):
    """Use this to specify a quad that will be rendered."""

    def __init__(
        self, name="Quad", vertices=[(1, 1, 0), (-1, 1, 0), (-1, -1, 0), (1, -1, 0)]
    ):
        """Anti-clockwise order."""
        super().__init__(name)

        # Vertices coordinates
        self.vertices = vertices
        self.edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
        self.faces = [(0, 1, 2, 3)]

    def _create(self):
        """
        Private create method.
        Creates an empty node if not overriden.
        """
        # Create mesh and object
        mesh = bpy.data.meshes.new("QuadMesh")
        self.blender_object = bpy.data.objects.new(self.name, mesh)

        # Set mesh location and scene
        self.blender_object.location = bpy.context.scene.cursor.location
        bpy.context.collection.objects.link(self.blender_object)

        # Create mesh
        mesh.from_pydata(self.vertices, self.edges, self.faces)

        # Update mesh geometry
        mesh.update()


# Quad().create()

width = 2
height = 1
thickness = 0.1

upDirection = up
rightDirection = right

botLeft = Vector((0, 0, 0))
botRight = botLeft + right * width
topRight = botRight + upDirection * height
topLeft = botLeft + upDirection * height
botLeftInner = botLeft + thickness * (upDirection + rightDirection)
botRightInner = botRight + thickness * (upDirection - rightDirection)
topRightInner = topRight + thickness * (-upDirection - rightDirection)
topLeftInner = topLeft + thickness * (-upDirection + rightDirection)


Quad("BotQuad", [botLeft, botRight, botRightInner, botLeftInner]).create()
Quad("RightQuad", [botRight, topRight, topRightInner, botRightInner]).create()
Quad("TopQuad", [topRight, topLeft, topLeftInner, topRightInner]).create()
Quad("TopQuad", [topLeft, botLeft, botLeftInner, topLeftInner]).create()
