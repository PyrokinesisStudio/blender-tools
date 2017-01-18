# MIT License
# 
# Copyright (c) 2017 Israel Jacquez
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

bl_info = {
    "name": "Export to Unity3D",
    "author": "Israel Jacquez",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "File > Import-Export",
    "description": "Write FBX files for Unity3D",
    "warning": "",
    "wiki_url": "https://github.com/ijacquez/blender_tools",
    "tracker_url": "https://github.com/ijacquez/blender_tools",
    "category": "Import-Export"
}

import os
import math

import bpy
import bmesh

from mathutils import Vector, Matrix
from bpy_extras import io_utils

import helper_utils

class ExportUnity3D(bpy.types.Operator, io_utils.ExportHelper):
    bl_idname = "export_scene.export_unity3d"
    bl_label = "Export Unity3D (.fbx)"
    bl_description = "Write FBX files for Unity3D"
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = ".fbx"

    def _export(self, filepath, objs):
        _rotate_axis = lambda angle, axis: Matrix.Rotation(math.radians(angle), 4, axis)

        _debug_print_quaternion = lambda q: [(math.degrees(x) if (x <= -1.0e-05) or (x >= 1.0e-05) else 0.0) for x in q.to_euler()]
        _debug_print_rot_matrix = lambda m: _debug_print_quaternion(m.decompose()[1])

        def _axis_conversion(obj, is_root, rot_mat = Matrix()):
            r1 = _rotate_axis(-90.0, 'X')
            r2 = _rotate_axis(180.0, 'Y')
            return (r1.inverted() if is_root else Matrix()) * ((r2 * (r1 * ((obj.matrix_local * rot_mat) * r2))))

        def _rotate_camera(obj, is_root):
            _translate_object(obj, is_root)
            matrix = _axis_conversion(obj, is_root) * _rotate_axis(90.0, 'Y').inverted()
            _, R, _ = matrix.decompose()
            euler = R.to_euler()
            obj.rotation_euler = euler

        def _rotate_mesh(obj, is_root):
            _translate_object(obj, is_root)
            mesh = obj.data
            new_bmesh = bmesh.new()
            new_bmesh.from_mesh(mesh)
            unique_verts = sorted(list(set([vert for face in new_bmesh.faces for vert in face.verts])),
                                  key = lambda vert: vert.index)
            bmesh.ops.rotate(new_bmesh, cent = (0.0, 0.0, 0.0), matrix = _rotate_axis(180.0, 'Z') * _rotate_axis(90.0, 'X'), verts = unique_verts)
            new_bmesh.to_mesh(mesh)
            mesh.update()
            if is_root:
                matrix = _rotate_axis(-90.0, 'X').inverted() * obj.matrix_local
                _, R, _ = matrix.decompose()
                euler = R.to_euler()
                obj.rotation_euler = euler

        def _rotate_object(obj, is_root):
            _translate_object(obj, is_root)
            matrix = _axis_conversion(obj, is_root, _rotate_axis( 90.0, 'X'))
            _, R, _ = matrix.decompose()
            euler = R.to_euler()
            obj.rotation_euler = euler

        def _translate_object(obj, is_root):
            local_loc = obj.matrix_local.to_translation()
            world_loc = obj.matrix_world.to_translation()
            diff_loc = world_loc - local_loc
            if is_root:
                obj.location = -diff_loc + (_rotate_axis(180.0, 'Z') * (diff_loc + local_loc))
            else:
                obj.location = (_rotate_axis(180.0, 'Z') * _rotate_axis(90.0, 'X')) * local_loc

        def _parent_in_list(obj, objs):
            """Return True if obj has a parent in objs. False otherwise."""
            def _parent_in_list(obj, first_obj, objs):
                if obj is None:
                    return []
                return [obj if (obj in objs) and (obj != first_obj) else None] + _parent_in_list(obj.parent, first_obj, objs)
            return any(_parent_in_list(obj, obj, objs))

        with helper_utils.DuplicateScene() as override_context:
            objs = [obj for obj in bpy.context.selected_objects]
            for obj in objs:
                is_root = not _parent_in_list(obj, objs)
                if obj.type == 'MESH':
                    _rotate_mesh(obj, is_root)
                elif obj.type == 'CAMERA':
                    _rotate_camera(obj, is_root)
                elif obj.type == 'EMPTY':
                    _rotate_object(obj, is_root)
            # Update override context
            override_context['selected_objects'] = objs
            # Finally, export
            bpy.ops.export_scene.fbx(override_context, filepath = self.filepath,
                                     check_existing = False,
                                     axis_forward = 'Y',
                                     axis_up = 'Z',
                                     use_selection = True,
                                     global_scale = 1.0,
                                     apply_unit_scale = False,
                                     bake_anim = False,
                                     object_types = {
                                         'EMPTY',
                                         'CAMERA',
                                         'LAMP',
                                         'MESH'},
                                     use_custom_props = True)

    def execute(self, context):
        try:
            self._export(self.filepath, context.selected_objects)
            return {'FINISHED'}
        except (ValueError, RuntimeError) as e:
            self.report({'ERROR'}, "%s" % (e))
            return {'CANCELLED'}
        return {'FINISHED'}

def menu_export_unity3d(self, context):
    self.layout.operator(ExportUnity3D.bl_idname, text = ExportUnity3D.bl_label)

def register():
    bpy.utils.register_class(ExportUnity3D)
    bpy.types.INFO_MT_file_export.append(menu_export_unity3d)

def unregister():
    bpy.utils.unregister_class(ExportUnity3D)
    bpy.types.INFO_MT_file_export.remove(menu_export_unity3d)

if __name__ == '__main__':
    register()
