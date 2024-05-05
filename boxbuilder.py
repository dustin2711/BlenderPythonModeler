"""
To use this script, fun these VSCode commands from "Blender Development" extension:
1. Blender: Start (one time at start)
2. Blender: Run Script (each time to execute script)
"""

import sys

# from varname import nameof # Doesnt work with blender :(

sys.path.append("E:/Coding/BlueprintCreator")
import bpy
import bmesh
from mathutils import Vector
from enum import Enum

from Cuboid import *
from numpy import sin, cos, pi
import bmesh

tau = 2 * pi


def setObjectMode():
    try:
        bpy.ops.object.mode_set(mode="OBJECT")
    except RuntimeError as error:
        print(f"Cannot set object mode: {error}")


def setEditMode():
    try:
        bpy.ops.object.mode_set(mode="EDIT")
    except RuntimeError as error:
        print(f"Cannot set edit mode: {error}")


def getMode():
    return bpy.context.mode


def deselectAll():
    bpy.ops.object.select_all(action="DESELECT")


def selectAll():
    bpy.ops.object.select_all(action="SELECT")


def clear_objects(filter=""):
    objects = bpy.context.scene.objects

    # Find and delete all objects where filter is in name
    if filter:
        objects = [it for it in bpy.context.scene.objects if filter in it.name]

    setObjectMode()

    deselectAll()

    for object in objects:
        object.hide_set(False)
        object.select_set(True)

    bpy.ops.object.delete()


def removeObject(object):
    # Deselect all
    bpy.ops.object.select_all(action="DESELECT")
    # Select object and delete
    object.select_set(True)
    bpy.ops.object.delete()


# Clear existing blender objects
clear_objects()

left = Vector((0, -1, 0))
right = Vector((0, 1, 0))
up = Vector((0, 0, 1))
down = Vector((0, 0, -1))
forward = Vector((1, 0, 0))
backward = Vector((-1, 0, 0))


class BooleanOperation(Enum):
    Difference = 0
    Intersect = 1
    Union = 2


def union(objects: list):
    """Unites all objects on the first object. THIS WILL FAIL FOR MORE THAN 2 OBJECTS."""
    booleanOperationMultiple(objects, BooleanOperation.Union)


def booleanOperationMultiple(objects: list, operation: BooleanOperation):
    """Executes all operations between the first and the other objects."""
    firstObject = objects[0]
    otherObjects = objects[1:]
    for otherObject in otherObjects:
        booleanOperation(firstObject, otherObject, operation)


def subtract(object: bpy.types.Object, subtractedObject: bpy.types.Object):
    """Substracts the second from the first object."""
    booleanOperation(object, subtractedObject, BooleanOperation.Difference)


def unite(object: bpy.types.Object, addedObject: bpy.types.Object):
    """Adds the second to the first object."""
    booleanOperation(object, addedObject, BooleanOperation.Union)


def intersect(object: bpy.types.Object, intersectingObject: bpy.types.Object):
    """Reduces the object by intersecting with another object."""
    booleanOperation(object, intersectingObject, BooleanOperation.Intersect)


def booleanOperation(
    firstObject: bpy.types.Object,
    secondObject: bpy.types.Object,
    operation: BooleanOperation,
):
    operationName = operation.name.upper()
    modifierName = f"{firstObject.name} {operationName} {secondObject.name}"

    # Apply boolean modifier to subtract cylinder from cuboid
    modifier = firstObject.modifiers.new(name=modifierName, type="BOOLEAN")
    modifier.operation = operationName
    modifier.object = secondObject

    if not (firstObject.visible_get() and not firstObject.hide_render):
        raise Error("Object must be visible")

    # Select the object and apply the modifier
    bpy.context.view_layer.objects.active = firstObject
    # bpy.ops.object.modifier_apply(modifier=modifier.name)

    # firstObject.modifiers.clear()

    # Recalculate normals (not sure if neccessary)
    setEditMode()
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    setObjectMode()


class Side(Enum):
    BotTop = 0
    """Bot and top. """
    LeftRight = 1
    """Left and right. """
    BackFront = 2
    """Back and front. """


class Blueprint:
    """An instruction how a geometric is rendered."""

    def __init__(
        self, name="Blueprint", parent: "Blueprint" = None, offset=Vector((0, 0, 0))
    ):
        # self.name = f"{((parent.name + '.') if parent else '')}{name}"
        self.name = name

        self.parent: Blueprint = parent
        """The parent blueprint (if available). """

        self.offset = offset
        """ Position offset when creating the object. """

        self.object: bpy.types.Object = None
        """The created Blender object. This is None if create() was not called yet. """

        self.isBlenderObjectAddedDuringCreation = False
        """ If true, the _createBlenderObject already adds the blender object to the collection. Neccessary as some creation methods automatically do this. """

    def hide(self):
        self.object.hide_set(True)

    def show(self):
        self.object.hide_set(False)

    def remove(self):
        # Deselect all
        bpy.ops.object.select_all(action="DESELECT")
        # Select object and delete
        self.object.select_set(True)
        bpy.ops.object.delete()

    def __repr__(self) -> str:
        return f"{type(self)} {self.name}"

    def write(self, message: str) -> None:
        print(self.name + ": " + str(message))

    def __sub__(self, other):
        return subtract(self, other)

    # @staticmethod
    # def roundfloat(value, roundTo=0.001):
    #     """Round to millimeter or any other value just for better representation."""
    #     return round(value / roundTo) * roundTo

    def create(self):
        """Creates a Blender object from this blueprint.
        Also sets the parent if it is available."""

        self.object = self._createBlenderObject()
        self.object.location += Vector(self.offset)

        if not self.isBlenderObjectAddedDuringCreation:
            self.addToBlenderCollection()

        # Set name
        self.object.name = self.name

        # Set parent of the blender object if a parent is associated with this blueprint
        if self.parent:
            if not self.parent.object:
                self.write("PARENT IS MISSING!")
            self.object.parent = self.parent.object
            self.write(f"Set parent to {self.parent.object.name}\n\n")

    def _createBlenderObject(self) -> bpy.types.Object:
        """
        Private method to create the blender object/node AND add it to the scene, since some geometries like cube are automatically added.
        By default, creates an empty object.
        """
        blenderObject = bpy.data.objects.new(self.name, None)
        blenderObject.name = self.name
        return blenderObject

    def addToBlenderCollection(self):
        """Adds the blender object to the blender "SceneCollection/Collection" node."""
        # To retrieve the collection...
        # - Does work:      bpy.context.collection.objects
        # - Does work:      bpy.data.collections.get("Collection")
        # - Does not work:  bpy.context.scene.collection
        collectionObjects = bpy.context.collection.objects
        if False:  # self.name in collectionObjects:
            self.write(f"Cannot add. Already in collection.")
        else:
            try:
                collectionObjects.link(self.object)
                self.write("Added to collection.")
            except RuntimeError as error:
                self.write(f"Could not add. {error}")

    def copy(self, newName, newParent):
        return Blueprint(newName, newParent)


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


class LastAddedBlenderObject:
    """
    Helping class for working with the last added Blender object defined by bpy.context.object.
    Removes the object after the "with" block.
    """

    def __init__(self):
        self.object = None

    def __enter__(self):
        self.object = bpy.context.object
        return self.object

    def __exit__(self, exc_type, exc_value, traceback):
        bpy.data.objects.remove(self.object)


class PrimitiveBlueprint(Blueprint):
    """A blueprint with isBlenderObjectAddedDuringCreation set to true."""

    def __init__(
        self, name="Blueprint", parent: Blueprint = None, offset=Vector((0, 0, 0))
    ):
        super().__init__(name, parent, offset)

        self.isBlenderObjectAddedDuringCreation = True


class ConeBlueprint(PrimitiveBlueprint):

    def __init__(
        self,
        parent: Blueprint = None,
        name="Cone",
        height=1.0,
        radius1=1.0,
        radius2=0.0,
        offset=(0, 0, 0),
        resolution=256,
    ):
        super().__init__(name, parent, offset)
        self.height = height
        self.radius1 = radius1
        self.radius2 = radius2
        self.resolution = resolution

    def _createBlenderObject(self) -> bpy.types.Object:
        bpy.ops.mesh.primitive_cone_add(
            radius1=self.radius1,
            radius2=self.radius2,
            depth=self.height,  # Depth is height...
            vertices=self.resolution,
        )
        return bpy.context.object


class CylinderBlueprint(PrimitiveBlueprint):

    def __init__(
        self,
        parent: Blueprint = None,
        name="Cylinder",
        height=1,
        radius=0.5,
        offset=(0, 0, 0),
        resolution=256,
    ):
        super().__init__(name, parent, offset)
        self.height = height
        self.radius = radius
        self.resolution = resolution

    def _createBlenderObject(self) -> bpy.types.Object:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=self.radius,
            depth=self.height,  # Depth is height...
            vertices=self.resolution,
            # scale=(self.radius, self.radius, self.height),
        )
        return bpy.context.object


class CuboidBlueprint(PrimitiveBlueprint):
    """Use this to specify a cuboid that will be rendered."""

    def __init__(
        self,
        parent: Blueprint = None,
        name="Cuboid",
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

    def _createBlenderObject(self) -> bpy.types.Object:
        """Adds a cube node."""
        dimensions = self.frontrighttop - self.backleftbot
        location = self.backleftbot + dimensions / 2

        bpy.ops.mesh.primitive_cube_add(
            size=1,
            enter_editmode=False,
            align="WORLD",
            location=location,
            scale=dimensions,
        )

        return bpy.context.object

    def __str__(self):
        return f"Cube: {self.left} to {self.right}, {self.bot} to {self.top}, {self.back} to {self.front}"

    def __repr__(self):
        return self.__str__()

    def copy(self, name):
        cuboid = deepcopy(self)
        cuboid.name = name
        return cuboid


class BoxBlueprint(BlueprintContainer):

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
        botpart = CuboidBlueprint(self, "botpart")
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
        leftpart = CuboidBlueprint(self, "leftpart")
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
        backpart = CuboidBlueprint(self, "backpart")
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


# class PolygonBlueprint(Blueprint):
#     """Use this to specify a quad that will be rendered."""

#     def __init__(
#         self,
#         parent: Blueprint,
#         name="Quad",
#         vertices=[(1, 1, 0), (-1, 1, 0), (-1, -1, 0), (1, -1, 0)],
#     ):
#         """Anti-clockwise order."""
#         super().__init__(name, parent)

#         # Vertices coordinates
#         self.vertices = vertices
#         self.edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
#         self.faces = [(0, 1, 2, 3)]

#     def _createBlenderObject(self) -> bpy.types.Object:
#         """Creates a QuadMesh."""

#         # Create mesh
#         mesh = bpy.data.meshes.new("QuadMesh")
#         mesh.from_pydata(self.vertices, self.edges, self.faces)

#         # Create object with mesh
#         blenderObject = bpy.data.objects.new(self.name, mesh)

#         # Set location
#         blenderObject.location = bpy.context.scene.cursor.location

#         # Link to collection. This is neccessary for all objects?
#         # addToScene(self)

#         # Update mesh geometry
#         mesh.update()

#         return blenderObject


class PolygonBlueprint(Blueprint):
    """Use this to specify a quad that will be rendered."""

    def __init__(
        self,
        parent: Blueprint,
        name="Quad",
        vertices=[(1, 1, 0), (-1, 1, 0), (-1, -1, 0), (1, -1, 0)],
        offset=Vector((0, 0, 0)),
    ):
        """Anti-clockwise order."""
        super().__init__(name, parent, offset)

        # Vertices coordinates
        self.vertices = vertices
        vertexCount = len(vertices)
        # if len(vertices) == 4:
        self.edges = [(i, (i + 1) % (vertexCount)) for i in range(vertexCount)]
        self.faces = [tuple(range(vertexCount))]

    def _createBlenderObject(self) -> bpy.types.Object:
        """Creates a QuadMesh."""

        # Create mesh
        mesh = bpy.data.meshes.new("QuadMesh")
        mesh.from_pydata(self.vertices, self.edges, self.faces)

        # Create object with mesh
        blenderObject = bpy.data.objects.new(self.name, mesh)

        # Set location
        blenderObject.location = bpy.context.scene.cursor.location

        # Link to collection. This is neccessary for all objects?
        # addToScene(self)

        # Update mesh geometry
        mesh.update()

        return blenderObject


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
        """ The points that determine the bottom of the palisade polygon. """

        self.closeLoop = closeLoop
        """ If true, the starting point will be appended to the end. This creates a closed list of points. """

        self.halfOffsettedPoints = [point + 0.5 * offset for point in basePoints]

        offsettedPoints = [point + offset for point in basePoints]
        self.offsettedPoints = offsettedPoints

        # May add start point to end
        if closeLoop:
            basePoints.append(basePoints[0])
            offsettedPoints.append(offsettedPoints[0])

        for (point, nextPoint), (offsetted, nextOffsetted) in zip(
            enumerate_two_elements(basePoints), enumerate_two_elements(offsettedPoints)
        ):
            quad = PolygonBlueprint(
                self, "Quad", [point, nextPoint, nextOffsetted, offsetted]
            )
            self.add_child(quad)


class ChangingPalisadeBlueprint(BlueprintContainer):
    """Specifies walls with different bottom than top points."""

    def __init__(
        self,
        name="Palisade",
        parent=None,
        botPoints: list[Vector] = [
            Vector((0, 0, 0)),
            Vector((1, 0, 0)),
            Vector((1, 1, 0)),
            Vector((0, 1, 0)),
        ],
        topPoints: list[Vector] = [
            Vector((0, 0, 1)),
            Vector((1, 0, 1)),
            Vector((1, 1, 1)),
            Vector((0, 1, 1)),
        ],
        closeLoop=True,
    ):
        super().__init__(name, parent)

        self.botPoints = botPoints
        """ The points that determine the bottom of the palisade polygon. """
        self.topPoints = topPoints
        """ The points that determine the bottom of the palisade polygon. """

        self.closeLoop = closeLoop
        """ If true, the starting point will be appended to the end. This creates a closed list of points. """

        # May add start point to end
        if closeLoop:
            botPoints.append(botPoints[0])
            topPoints.append(topPoints[0])

        for (point, nextPoint), (offsetted, nextOffsetted) in zip(
            enumerate_two_elements(botPoints), enumerate_two_elements(topPoints)
        ):
            quad = PolygonBlueprint(
                self, "Quad", [point, nextPoint, nextOffsetted, offsetted]
            )
            self.add_child(quad)


# To do: Dont group back, front and sides together but rather each board (top, left, right, bottom)
class Frame3dBlueprint(BlueprintContainer):
    """A 3d frame consisting of two 2d frames and their connection. Like an actual window frame."""

    def __init__(
        self,
        parent: Blueprint,
        name="Frame3d",
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
    """A flat 2d frame consisting of 4 quads like a window front.

    |\''''''''''''''/|
    | |''''''''''''| |
    | |            | |
    | |            | |
    | |            | |
    | |____________| |
    |/______________\|

    """

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

        self.botQuad = PolygonBlueprint(
            self,
            "BotQuad",
            [botLeft, self.botRight, self.botRightInner, self.botLeftInner],
        )
        self.rightQuad = PolygonBlueprint(
            self,
            "RightQuad",
            [self.botRight, self.topRight, self.topRightInner, self.botRightInner],
        )
        self.topQuad = PolygonBlueprint(
            self,
            "TopQuad",
            [self.topRight, self.topLeft, self.topLeftInner, self.topRightInner],
        )
        self.leftQuad = PolygonBlueprint(
            self,
            "LeftQuad",
            [self.topLeft, botLeft, self.botLeftInner, self.topLeftInner],
        )
        self.quads = [
            self.botQuad,
            self.rightQuad,
            self.topQuad,
            self.leftQuad,
        ]
        self.add_children(self.quads)


def extrudeOld(object, length=2):
    """Thanks to: https://blender.stackexchange.com/questions/115397/extrude-in-python"""
    # Select object
    bpy.context.view_layer.objects.active = object

    # Enter edit and face mode, then select all faces
    setEditMode()
    bpy.ops.mesh.select_mode(type="FACE")  # Change to face selection
    bpy.ops.mesh.select_all(action="SELECT")  # Select all faces

    # Create Bmesh
    mesh = bmesh.from_edit_mesh(bpy.context.object.data)

    # Select last? normal
    for face in mesh.faces:
        normal = face.normal

    # Extrude mesh
    geometry = bmesh.ops.extrude_face_region(mesh, geom=mesh.faces[:])
    # Collect BMVERT vertices from extrusion
    vertices = [it for it in geometry["geom"] if isinstance(it, bmesh.types.BMVert)]
    direction = normal * length  # Extrude Strength/Length
    bmesh.ops.translate(mesh, vec=direction, verts=vertices)

    # Update & destroy Bmesh
    bmesh.update_edit_mesh(bpy.context.object.data)  # Write the bmesh back to the mesh
    mesh.free()  # free and prevent further access

    # Flip normals
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.flip_normals()

    # Recalculate UV
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project()

    # Switch back to object mode
    setObjectMode()

    # Origin to center
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")


def extrude(object, length=1):
    """Extrude the selected faces of the object."""
    # Select object
    bpy.context.view_layer.objects.active = object

    # Enter edit mode, face selection mode, and select all faces
    setEditMode()
    bpy.ops.mesh.select_mode(type="FACE")  # Change to face selection
    bpy.ops.mesh.select_all(action="SELECT")  # Select all faces

    # Extrude the selected faces
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, length)})

    # Switch back to object mode
    setObjectMode()


# frame = Frame3dBlueprint(
#     None, "WindowFrame", width=1.235, height=1.27, frameWidth=0.069, depth=0.014
# )
# windowQuad = QuadBlueprint(None, "WindowQuad", frame.innerPalisade.halfOffsettedPoints)

# frame.create()
# windowQuad.create()

# cylinder = CylinderBlueprint(None)
# cylinder.create()


# # Cut hole into cylinder
# bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=5, location=(0, 0, 0))
# with LastAddedBlenderObject() as object:
#     booleanOperation(cylinder.blenderObject, object)

# extrude(cylinder.blenderObject)
# extrude2(cylinder.blenderObject, 2)


def calculateRegularPolygonPoints(
    sideCount, radius, offset: Vector = Vector((0, 0, 0))
) -> list[tuple]:
    """Calculate points for a rectangular flat polygon."""
    points = []
    angleDelta = tau / sideCount
    for index in range(sideCount):
        angle = index * angleDelta
        x = radius * cos(angle)
        y = radius * sin(angle)
        points.append((x + offset.x, y + offset.y, offset.z))
    return points


def join(first: bpy.types.Object, second: bpy.types.Object):
    """Joins two blender objects."""
    first.select_set(True)
    second.select_set(True)
    bpy.context.view_layer.objects.active = first
    bpy.ops.object.join()


class PrismBlueprint(Blueprint):

    def __init__(
        self,
        parent: Blueprint = None,
        name="Prism",
        offset=Vector((0, 0, 0)),
        sideCount=6,
        height=1,
        botRadius=1,
        topRadius=0.8,
    ):
        super().__init__(name, parent)

        botVertices = calculateRegularPolygonPoints(sideCount, botRadius, offset)
        topVertices = calculateRegularPolygonPoints(
            sideCount, topRadius, Vector((0, 0, height)) + offset
        )

        # The top will be the object the bot and walls are merged to
        self.top = PolygonBlueprint(None, name, topVertices)
        self.bot = PolygonBlueprint(None, name + ".Bot", botVertices)
        self.walls = ChangingPalisadeBlueprint(
            name + ".Walls", None, topVertices, botVertices
        )

    def create(self):
        self.top.create()
        self.bot.create()
        self.walls.create()

        # Join all objects
        join(self.top.object, self.bot.object)
        for wall in self.walls.children:
            join(self.top.object, wall.object)

        removeObject(self.walls.object)

        self.object = self.top.object
        # self.object.location += Vector(self.offset)


hexPrism = PrismBlueprint(
    None,
    "HexPrism",
    sideCount=6,
    height=1.0001,
    offset=Vector((0, 0, 0.0)),
    topRadius=0.9,
    botRadius=0.8,
)
hexPrism.create()

cylinder = CylinderBlueprint(
    None, "Cylinder", height=2, radius=1, offset=Vector((0, 0, 0))
)
cylinder.create()

cone = ConeBlueprint(
    None, "Cone", radius1=0, radius2=1, height=1.0, offset=Vector((0, 0, 0.5))
)
cone.create()

subtract(cylinder.object, cone.object)
cone.hide()

# Remove hexPrism from cylinder
subtract(cylinder.object, hexPrism.object)
hexPrism.hide()

implant = PrismBlueprint(
    None,
    "HexPrism",
    sideCount=6,
    height=1.0001,
    offset=Vector((0, 0, 2.0)),
    topRadius=0.9,
    botRadius=0.8,
)
implant.create()
