import bpy
import bmesh
import math
import random
from mathutils import Vector


def add_roof_details(building_obj, seed):
    rng = random.Random(seed)

    mesh = building_obj.data
    if not mesh.polygons:
        return

    top_z = max(v.co.z for v in mesh.vertices)

    roof_items = _generate_roof_items(rng)

    for item in roof_items:
        bm = bmesh.new()
        _create_roof_item(bm, item, rng)

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        item_mesh = bpy.data.meshes.new(f"CityP_RoofItem_{seed}_{item['type']}")
        bm.to_mesh(item_mesh)
        bm.free()

        item_obj = bpy.data.objects.new(f"CityP_RoofItem_{seed}_{item['type']}", item_mesh)
        item_obj.location = Vector((
            item["offset_x"],
            item["offset_y"],
            top_z,
        ))

        building_obj.users_collection[0].objects.link(item_obj)


def _generate_roof_items(rng):
    items = []

    if rng.random() < 0.6:
        items.append({
            "type": "cooling_tower",
            "offset_x": rng.uniform(-5, 5),
            "offset_y": rng.uniform(-5, 5),
            "size": rng.uniform(1.5, 3.0),
        })

    if rng.random() < 0.5:
        items.append({
            "type": "water_tank",
            "offset_x": rng.uniform(-4, 4),
            "offset_y": rng.uniform(-4, 4),
            "size": rng.uniform(1.0, 2.0),
        })

    if rng.random() < 0.4:
        items.append({
            "type": "elevator_shaft",
            "offset_x": rng.uniform(-3, 3),
            "offset_y": rng.uniform(-3, 3),
            "size": rng.uniform(1.5, 2.5),
            "height": rng.uniform(2.0, 4.0),
        })

    return items


def _create_roof_item(bm, item, rng):
    if item["type"] == "cooling_tower":
        s = item["size"]
        verts = [
            bm.verts.new(Vector((-s, -s, 0))),
            bm.verts.new(Vector((s, -s, 0))),
            bm.verts.new(Vector((s, s, 0))),
            bm.verts.new(Vector((-s, s, 0))),
            bm.verts.new(Vector((-s * 0.8, -s * 0.8, s * 0.6))),
            bm.verts.new(Vector((s * 0.8, -s * 0.8, s * 0.6))),
            bm.verts.new(Vector((s * 0.8, s * 0.8, s * 0.6))),
            bm.verts.new(Vector((-s * 0.8, s * 0.8, s * 0.6))),
        ]
        bm.faces.new([verts[0], verts[1], verts[2], verts[3]])
        bm.faces.new([verts[4], verts[5], verts[6], verts[7]])
        for i in range(4):
            bm.faces.new([verts[i], verts[(i + 1) % 4], verts[((i + 1) % 4) + 4], verts[i + 4]])

    elif item["type"] == "water_tank":
        r = item["size"] * 0.5
        h = item["size"] * 0.8
        segments = 8
        verts_bottom = [bm.verts.new(Vector((r * math.cos(a), r * math.sin(a), 0))) for a in [i * 6.28 / segments for i in range(segments)]]
        verts_top = [bm.verts.new(Vector((r * math.cos(a), r * math.sin(a), h))) for a in [i * 6.28 / segments for i in range(segments)]]
        bm.faces.new(verts_bottom)
        bm.faces.new(verts_top)
        for i in range(segments):
            bm.faces.new([verts_bottom[i], verts_bottom[(i + 1) % segments], verts_top[(i + 1) % segments], verts_top[i]])

    elif item["type"] == "elevator_shaft":
        s = item["size"] * 0.5
        h = item.get("height", 3.0)
        verts = [
            bm.verts.new(Vector((-s, -s, 0))),
            bm.verts.new(Vector((s, -s, 0))),
            bm.verts.new(Vector((s, s, 0))),
            bm.verts.new(Vector((-s, s, 0))),
            bm.verts.new(Vector((-s, -s, h))),
            bm.verts.new(Vector((s, -s, h))),
            bm.verts.new(Vector((s, s, h))),
            bm.verts.new(Vector((-s, s, h))),
        ]
        bm.faces.new([verts[0], verts[1], verts[2], verts[3]])
        bm.faces.new([verts[4], verts[5], verts[6], verts[7]])
        for i in range(4):
            bm.faces.new([verts[i], verts[(i + 1) % 4], verts[((i + 1) % 4) + 4], verts[i + 4]])
