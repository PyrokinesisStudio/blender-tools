# Copyright (c) 2014 Shane Ambler
#
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1.  Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
# 2.  Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

def calculate_object_center(obj):
    """Returns the center point of an object."""

    from mathutils import Vector

    return obj.matrix_world * ((1.0 / 8.0) * sum((Vector(b) for b in obj.bound_box), Vector()))

def add_bounding_box(objs, name = ""):
    """"""

    import bpy
    import bmesh

    from bpy_extras import object_utils

    import mathutils

    def _bounding_box(width, height, depth):
        """This function takes inputs and returns vertex and face arrays. No actual mesh
        data creation is done here."""

        verts = [(+1.0, +1.0, -1.0),
                 (+1.0, -1.0, -1.0),
                 (-1.0, -1.0, -1.0),
                 (-1.0, +1.0, -1.0),
                 (+1.0, +1.0, +1.0),
                 (+1.0, -1.0, +1.0),
                 (-1.0, -1.0, +1.0),
                 (-1.0, +1.0, +1.0)]
        faces = [(0, 1, 2, 3),
                 (4, 7, 6, 5),
                 (0, 4, 5, 1),
                 (1, 5, 6, 2),
                 (2, 6, 7, 3),
                 (4, 0, 3, 7)]
        # Apply size
        for (i, v) in enumerate(verts):
            verts[i] = v[0] * width, v[1] * depth, v[2] * height
        return (verts, faces)

    minx, miny, minz = (999999.0,) * 3
    maxx, maxy, maxz = (-999999.0,) * 3
    selected_objs = objs
    for obj in selected_objs:
        for v in obj.bound_box:
            v_world = obj.matrix_world * mathutils.Vector((v[0], v[1], v[2]))
            if v_world[0] < minx:
                minx = v_world[0]
            if v_world[0] > maxx:
                maxx = v_world[0]
            if v_world[1] < miny:
                miny = v_world[1]
            if v_world[1] > maxy:
                maxy = v_world[1]
            if v_world[2] < minz:
                minz = v_world[2]
            if v_world[2] > maxz:
                maxz = v_world[2]
    verts_loc, faces = _bounding_box((maxx - minx) / 2.0, (maxz - minz) / 2.0, (maxy - miny) / 2.0)
    mesh = bpy.data.meshes.new(("%s.BB" % (name)) if name else "BoundingBox")
    new_bmesh = bmesh.new()
    for v_co in verts_loc:
        new_bmesh.verts.new(v_co)
    new_bmesh.verts.ensure_lookup_table()
    for f_idx in faces:
        new_bmesh.faces.new([new_bmesh.verts[i] for i in f_idx])
    new_bmesh.to_mesh(mesh)
    mesh.update()
    new_bmesh.free()
    bounding_box_obj = object_utils.object_data_add(bpy.context, mesh)
    bounding_box_obj.object.location[0] = minx + ((maxx - minx) / 2.0)
    bounding_box_obj.object.location[1] = miny + ((maxy - miny) / 2.0)
    bounding_box_obj.object.location[2] = minz + ((maxz - minz) / 2.0)
    # Does a bounding box need to display more than the bounds?
    bounding_box_obj.object.draw_type = 'BOUNDS'
    bounding_box_obj.object.hide_render = True
    return bounding_box_obj.object
