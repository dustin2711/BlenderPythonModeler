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


class Blueprint:
    """An instruction how a geometric is rendered."""

    def __init__(self, name="Blueprint", parent: "Blueprint" = None):
        self.name = f"{((parent.name + '.') if parent else '')}{name}"
        self.parent: Blueprint = parent
        """The parent blueprint (if available). """
        self.blender_object: bpy.types.Object = None
        """The created Blender object. This is None if create() was not called yet. """

    def __repr__(self) -> str:
        return f"{type(self)} {self.name}"

    # @staticmethod
    # def roundfloat(value, roundTo=0.001):
    #     """Round to millimeter or any other value just for better representation."""
    #     return round(value / roundTo) * roundTo

    def create(self):
        """Creates a Blender object from this blueprint.
        Also sets the parent if it is available."""

        self.createEmptyNode()

        # Set name
        self.blender_object.name = self.name
        # if self.parent:
        #     self.blender_object.name = self.parent.name + "." + self.name

        # Set parent if available
        if self.parent and self.parent.blender_object:
            self.blender_object.parent = self.parent.blender_object
            print(
                f"New parent of '{self.blender_object.name}' is '{self.parent.blender_object.name}'"
            )
        else:
            print(f"Missing parent for {self.name}")
            collection = bpy.data.collections.get("Collection")
            try:
                collection.objects.link(self.blender_object)
            except RuntimeError:
                print(f"{self.name} already exists in Collection.")
            # self.blender_object.parent = collection

    def createEmptyNode(self):
        """
        Private create method.
        Creates an empty node if not overriden.
        """
        self.blender_object = bpy.data.objects.new(self.name, None)
        self.blender_object.name = self.name
        bpy.context.scene.collection.objects.link(self.blender_object)


class BlueprintContainer(Blueprint):
    """Parent of multiple blueprint children."""

    def __init__(self, name="BlueprintContainer", parent=None):
        super().__init__(name, parent)

        self.children: list[Blueprint] = []

    def add_child(self, child: Blueprint):
        """Adds the child to the list so it can be created together."""
        self.children.append(child)

    def add_children(self, children: list[Blueprint]):
        """Adds the children to the list so they can be created together."""
        self.children.extend(children)

    def create(self):
        super().create()

        for child in self.children:
            child.create()
            # try:
            #     child.create(self)
            # except:
            #     print("bla")


class Cuboid(Blueprint):
    """Use this to specify a cuboid that will be rendered."""

    def __init__(
        self,
        name="Cuboid",
        parent: Blueprint = None,
        left=0,
        right=1,
        bot=0,
        top=1,
        back=0,
        front=1,
    ):
        super().__init__(name, parent)
        self.left = left
        self.right = right
        self.bot = bot
        self.top = top
        self.back = back
        self.front = front

    def move(self, x=0, y=0, z=0):
        self.left += y
        self.right += y
        self.back += x
        self.front += x
        self.bot += z
        self.top += z

    @property
    def height(self):
        return self.top - self.bot

    @height.setter
    def height(self, value: float):
        """Changes  so that height is as given."""
        """Changes top (if positive) or bot (if negative) so that width is as given."""
        if value < 0:
            self.bot = self.top + value
        else:
            self.top = self.bot + value

    @property
    def width(self):
        return self.right - self.left

    @width.setter
    def width(self, value: float):
        """Changes right (if positive) or left (if negative) so that width is as given."""
        if value < 0:
            self.left = self.right + value
        else:
            self.right = self.left + value

    @property
    def depth(self):
        return self.front - self.back

    @depth.setter
    def depth(self, value: float):
        """Changes front (if positive) or back (if negative) so that width is as given."""
        if value < 0:
            self.back = self.front + value
        else:
            self.front = self.back + value

    # Corners

    @property
    def frontrighttop(self):
        return Vector((self.front, self.right, self.top))

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

    def createEmptyNode(self):
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
        return f"Cube: {self.left} to {self.right}, {self.bot} to {self.top}, {self.back} to {self.front}"

    def __repr__(self):
        return self.__str__()

    def copy(self, name):
        cuboid = deepcopy(self)
        cuboid.name = name
        return cuboid


class Box(BlueprintContainer):

    def __init__(
        self,
        parent: Blueprint = None,
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
        super().__init__(name, parent)

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
        botpart = Cuboid("botpart", self)
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
        leftpart = Cuboid("leftpart", self)
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
        backpart = Cuboid("backpart", self)
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
        rightpart = leftpart.copy("rightpart", self)
        rightpart.move(y=width - thickness)

        # Top part
        toppart = botpart.copy("toppart", self)
        toppart.move(z=height - thickness)

        # Bot part
        frontpart = backpart.copy("frontpart", self)
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


class Quad(Blueprint):
    """Use this to specify a quad that will be rendered."""

    def __init__(
        self,
        name="Quad",
        parent: Blueprint = None,
        vertices=[(1, 1, 0), (-1, 1, 0), (-1, -1, 0), (1, -1, 0)],
    ):
        """Anti-clockwise order."""
        super().__init__(name, parent)

        # Vertices coordinates
        self.vertices = vertices
        self.edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
        self.faces = [(0, 1, 2, 3)]

    def createEmptyNode(self):
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


def enumerate_two_elements(list):
    """Enumerates an iterable, yielding pairs of consecutive elements."""
    item = iter(list)
    previous = next(item)
    for item in item:
        yield previous, item
        previous = item


# Example usage
my_list = [1, 2, 3, 4, 5]
for item1, item2 in enumerate_two_elements(my_list):
    print(f"Item1: {item1}, Item2: {item2}")


class Palisade(BlueprintContainer):
    """Specifies quads by base points and an offset by whom they are extruded."""

    def __init__(
        self,
        name="Palisade",
        parent=None,
        basePoints: list[Vector] = [
            Vector((0, 0, 0)),
            Vector((1, 0, 0)),
            Vector((1, 1, 0)),
            Vector((0, 1, 0)),
        ],
        offset=Vector((0, 0, 1)),
        closeLoop=True,
    ):
        super().__init__(name, parent)

        self.basePoints = basePoints
        self.closeLoop = closeLoop

        self.halfOffsettedPoints = [point + 0.5 * offset for point in basePoints]

        offsettedPoints = [point + offset for point in basePoints]
        self.offsettedPoints = offsettedPoints

        # Add start to end?
        if closeLoop:
            basePoints.append(basePoints[0])
            offsettedPoints.append(offsettedPoints[0])

        for (point, nextPoint), (offsetted, nextOffsetted) in zip(
            enumerate_two_elements(basePoints), enumerate_two_elements(offsettedPoints)
        ):
            quad = Quad("Quad", self, [point, nextPoint, nextOffsetted, offsetted])
            self.add_child(quad)


class Frame3d(BlueprintContainer):
    """A 3d frame consisting of two 2d frames and their connection. Like an actual window frame."""

    def __init__(
        self,
        name="Frame3d",
        parent: Blueprint = None,
        botLeft=Vector((0, 0, 0)),
        width=2,
        height=1,
        frameWidth=0.1,
        upDirection=up,
        rightDirection=right,
        frontDirection=forward,
        depth=0.2,
    ):
        super().__init__(name, parent)

        def createFrame(frameName, botLeftPosition):
            """Creates the frame for the back or the front."""
            return Frame(
                frameName,
                self,
                botLeftPosition,
                width,
                height,
                frameWidth,
                upDirection,
                rightDirection,
            )

        self.width = width
        self.height = height
        self.depth = depth
        self.frameThickness = frameWidth

        self.backFrame = createFrame("BackFrame", botLeft)
        self.frontFrame = createFrame("FrontFrame", botLeft + frontDirection * depth)

        self.outerPalisade = Palisade(
            "OuterPalisade", self, self.backFrame.outerPoints, Vector((depth, 0, 0))
        )
        self.innerPalisade = Palisade(
            "InnerPalisade", self, self.backFrame.innerPoints, Vector((depth, 0, 0))
        )
        self.add_children(
            [self.frontFrame, self.backFrame, self.outerPalisade, self.innerPalisade]
        )


class Frame(BlueprintContainer):
    """A flat frame consisting of 4 quads like a window front."""

    def __init__(
        self,
        name="Frame",
        parent: Blueprint = None,
        botLeft=Vector((0, 0, 0)),
        width=2,
        height=1,
        frameThickness=0.1,
        upDirection=up,
        rightDirection=right,
    ):
        super().__init__(name, parent)

        self.botLeft = Vector(botLeft)
        self.botRight = botLeft + right * width
        self.topRight = self.botRight + upDirection * height
        self.topLeft = botLeft + upDirection * height
        self.botLeftInner = botLeft + frameThickness * (upDirection + rightDirection)
        self.botRightInner = self.botRight + frameThickness * (
            upDirection - rightDirection
        )
        self.topRightInner = self.topRight + frameThickness * (
            -upDirection - rightDirection
        )
        self.topLeftInner = self.topLeft + frameThickness * (
            -upDirection + rightDirection
        )

        self.outerPoints = [self.botLeft, self.botRight, self.topRight, self.topLeft]
        self.innerPoints = [
            self.botLeftInner,
            self.botRightInner,
            self.topRightInner,
            self.topLeftInner,
        ]

        self.botQuad = Quad(
            "BotQuad",
            self,
            [botLeft, self.botRight, self.botRightInner, self.botLeftInner],
        )
        self.rightQuad = Quad(
            "RightQuad",
            self,
            [self.botRight, self.topRight, self.topRightInner, self.botRightInner],
        )
        self.topQuad = Quad(
            "TopQuad",
            self,
            [self.topRight, self.topLeft, self.topLeftInner, self.topRightInner],
        )
        self.leftQuad = Quad(
            "LeftQuad",
            self,
            [self.topLeft, botLeft, self.botLeftInner, self.topLeftInner],
        )
        self.quads = [
            self.botQuad,
            self.rightQuad,
            self.topQuad,
            self.leftQuad,
        ]
        self.add_children(self.quads)


frame = Frame3d(
    "WindowFrame", None, width=1.235, height=1.27, frameWidth=0.069, depth=0.014
)
window = Quad("Windowpane", None, frame.innerPalisade.halfOffsettedPoints)

frame.create()
window.create()
