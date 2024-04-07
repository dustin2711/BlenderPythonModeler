bl_info = {
    "name": "My Test Add-on",
    "blender": (2, 80, 0),
    "category": "Render",
}


def register():
    print("Hello World")


def unregister():
    print("Goodbye World")
