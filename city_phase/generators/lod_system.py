import bpy
import bmesh


def apply_lod(building_obj, lod_level):
    if lod_level == 0:
        _simplify_to_bbox(building_obj)
    elif lod_level == 1:
        _reduce_geometry(building_obj, ratio=0.25)
    elif lod_level == 2:
        _reduce_geometry(building_obj, ratio=0.5)

    return building_obj


def _simplify_to_bbox(obj):
    mesh = obj.data
    if not mesh.vertices:
        return

    min_x = min(v.co.x for v in mesh.vertices)
    max_x = max(v.co.x for v in mesh.vertices)
    min_y = min(v.co.y for v in mesh.vertices)
    max_y = max(v.co.y for v in mesh.vertices)
    min_z = min(v.co.z for v in mesh.vertices)
    max_z = max(v.co.z for v in mesh.vertices)

    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2
    cz = (min_z + max_z) / 2
    hw = (max_x - min_x) / 2
    hd = (max_y - min_y) / 2
    hh = (max_z - min_z) / 2

    from mathutils import Vector

    bm = bmesh.new()
    verts = [
        bm.verts.new(Vector((cx - hw, cy - hd, cz - hh))),
        bm.verts.new(Vector((cx + hw, cy - hd, cz - hh))),
        bm.verts.new(Vector((cx + hw, cy + hd, cz - hh))),
        bm.verts.new(Vector((cx - hw, cy + hd, cz - hh))),
        bm.verts.new(Vector((cx - hw, cy - hd, cz + hh))),
        bm.verts.new(Vector((cx + hw, cy - hd, cz + hh))),
        bm.verts.new(Vector((cx + hw, cy + hd, cz + hh))),
        bm.verts.new(Vector((cx - hw, cy + hd, cz + hh))),
    ]
    bm.faces.new([verts[0], verts[1], verts[2], verts[3]])
    bm.faces.new([verts[4], verts[5], verts[6], verts[7]])
    for i in range(4):
        bm.faces.new([verts[i], verts[(i + 1) % 4], verts[((i + 1) % 4) + 4], verts[i + 4]])

    bm.to_mesh(mesh)
    bm.free()


def _reduce_geometry(obj, ratio):
    mesh = obj.data
    target_faces = max(4, int(len(mesh.polygons) * ratio))

    if len(mesh.polygons) <= target_faces:
        return

    bm = bmesh.new()
    bm.from_mesh(mesh)

    iterations = 0
    while len(bm.faces) > target_faces and iterations < 20:
        bmesh.ops.dissolve_limit(
            bm,
            angle_limit=0.1,
            verts=bm.verts,
            edges=bm.edges,
        )
        iterations += 1

    bm.to_mesh(mesh)
    bm.free()
