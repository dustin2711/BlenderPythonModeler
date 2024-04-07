"""
To use this script, fun these VSCode commands from "Blender Development" extension:
1. Blender: Start (one time at start)
2. Blender: Run Script (each time to execute script)
"""

import sys

sys.path.append("E:/Coding/BlueprintCreator")
import bpy
from mathutils import Vector

from Cuboid import *


def clear_objects():
    # Find and delete all objects with names starting with "Cube"
    cube_objs = [
        obj for obj in bpy.context.scene.objects if obj.name.startswith("Cube")
    ]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in cube_objs:
        obj.select_set(True)
    bpy.ops.object.delete()


# Clear existing blender objects
clear_objects()

# Parameters
thickness = 0.02
width = 0.70
depth = 0.50
height = 0.30

# Define cuboids


def left(value):
    return Vector((0, -value, 0))


def right(value):
    return Vector((0, value, 0))


def up(value):
    return Vector((0, 0, value))


def down(value):
    return Vector((0, 0, -value))


def forward(value):
    return Vector((value, 0, 0))


def backward(value):
    return Vector((-value, 0, 0))


box = BlueprintContainer()

botpart = Cuboid()
botpart.backleftbot = Vector((0, 0, 0))
botpart.frontrighttop = Vector((depth, width, thickness))

leftpart = Cuboid()
leftpart.left = botpart.left
leftpart.width = thickness
leftpart.bot = botpart.top
leftpart.top = botpart.top + height
leftpart.back = botpart.back
leftpart.front = botpart.front

rightpart = leftpart.copy()
rightpart.left = botpart.right - thickness
rightpart.right = botpart.right

toppart = botpart.copy()
toppart.bot = leftpart.top
toppart.height = thickness

backpart = Cuboid()
backpart.back = botpart.back
backpart.depth = thickness
backpart.left = leftpart.right
backpart.right = rightpart.left
backpart.bot = botpart.top
backpart.top = toppart.bot

frontpart = backpart.copy()
frontpart.front = botpart.front
frontpart.back = frontpart.front - thickness

box.add_children([botpart, leftpart, rightpart, toppart, backpart, frontpart])


box.render()
