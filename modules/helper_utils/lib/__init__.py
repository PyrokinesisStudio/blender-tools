__all__ = ("mesh")

def bu_to_inches(d):
    """Return Blender unit d in inches."""
    import bpy
    import mathutils

    # 1bu = 1 / 0.3048 ft
    convert = lambda v: (12.0 * bpy.context.scene.unit_settings.scale_length * v) / 0.3048
    if isinstance(d, mathutils.Vector):
        return mathutils.Vector((convert(d.x), convert(d.y), convert(d.z)))
    if isinstance(d, (int, float)):
        return convert(d)

def inches_to_bu(d):
    """Return d (inches) in Blender units."""
    return d / bu_to_inches(1)

def feet_to_bu(d):
    """Return d (feet) in Blender units."""
    return 12.0 * inches_to_bu(d)

def approximately(left, right, value):
    EPSILON = 1.0e-05
    return ((left - EPSILON) <= value <= (right + EPSILON))

def cleanup_data():
    import bpy

    # Clean up camera list of any stale cameras
    for camera in bpy.data.cameras[:]:
        if not any((obj for obj in bpy.context.scene.objects if (obj.type == 'CAMERA') and (obj.data == camera))):
            bpy.data.cameras.remove(camera)
            # Clean up mesh list of any stale meshes
    for mesh in bpy.data.meshes[:]:
        if not any((obj for obj in bpy.context.scene.objects if (obj.type == 'MESH') and (obj.data == mesh))):
            bpy.data.meshes.remove(mesh)

class DuplicateScene():
    _file_stack = []
    _unique_id = 0

    def __init__(self):
        import os

        import bpy

        if not bpy.data.is_saved:
            raise ValueError("Save .blend file before exporting")
        # Push filepath onto stack
        if len(DuplicateScene._file_stack) == 0:
            DuplicateScene._file_stack.append(bpy.data.filepath)
            bpy.ops.wm.save_mainfile(filepath = bpy.data.filepath,
                                     check_existing = False)
        else:
            filepath, fileext = os.path.splitext(bpy.data.filepath)
            DuplicateScene._file_stack.append("%s.copy.%02i.blend" % (filepath, DuplicateScene._unique_id))
            DuplicateScene._unique_id += 1
            # Save file
            filepath = DuplicateScene._file_stack[-1]
            bpy.ops.wm.save_as_mainfile(filepath = filepath,
                                        check_existing = False,
                                        copy = True)
        filepath = DuplicateScene._file_stack[-1]

    def __enter__(self):
        import bpy

        # Return new context override
        context = bpy.context
        blend_data = bpy.data
        window = context.window_manager.windows[0]
        screen = window.screen
        scene = context.scene
        area_view3d = [area for area in screen.areas if area.type == 'VIEW_3D'][0]
        space_view3d = [space for space in area_view3d.spaces if space.type == 'VIEW_3D'][0]
        region_window_view3d = [region for region in area_view3d.regions if region.type == 'WINDOW'][0]
        return {'window': window,
                'screen': screen,
                'context': context,
                'blend_data': blend_data,
                'scene': scene,
                'area': area_view3d,
                'space': space_view3d,
                'region': region_window_view3d}

    def __exit__(self, type, value, traceback):
        import os

        import bpy

        filepath = DuplicateScene._file_stack.pop()
        bpy.ops.wm.open_mainfile(filepath = filepath,
                                 load_ui = True,
                                 use_scripts = False)
        if len(DuplicateScene._file_stack) > 0:
            os.remove(filepath)
