import bpy
import bmesh
import math
import random
from mathutils import Vector


def make_rect_face(bm, w, d, z=0.0):
    hw, hd = w / 2, d / 2
    verts = [
        bm.verts.new(Vector((-hw, -hd, z))),
        bm.verts.new(Vector((hw, -hd, z))),
        bm.verts.new(Vector((hw, hd, z))),
        bm.verts.new(Vector((-hw, hd, z))),
    ]
    face = bm.faces.new(verts)
    return face


def extrude_face(bm, face, dz):
    ret = bmesh.ops.extrude_face_region(bm, geom=[face])
    top_verts = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)]
    top_face = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMFace)][0]
    bmesh.ops.translate(bm, verts=top_verts, vec=Vector((0, 0, dz)))
    return top_face


def scale_face_xy(bm, face, sx, sy):
    center = face.calc_center_median()
    for v in face.verts:
        v.co.x = center.x + (v.co.x - center.x) * sx
        v.co.y = center.y + (v.co.y - center.y) * sy


def rotate_face_z(bm, face, angle_rad):
    center = face.calc_center_median()
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
    for v in face.verts:
        dx = v.co.x - center.x
        dy = v.co.y - center.y
        v.co.x = center.x + dx * cos_a - dy * sin_a
        v.co.y = center.y + dx * sin_a + dy * cos_a


def add_floor_loop(bm, face, inset=0.4):
    bmesh.ops.inset_individual(bm, faces=[face], thickness=inset, depth=0.0)


# ============================================================
# Roof System
# ============================================================
def _get_top_faces(bm):
    max_z = max(v.co.z for v in bm.verts) if bm.verts else 0.0
    top_faces = [f for f in bm.faces if all(v.co.z >= max_z - 0.01 for v in f.verts)]
    return top_faces


def _apply_roof(bm, params, rng):
    roof_type = params.get("roof_type", "flat")
    if roof_type == "flat":
        return

    top_faces = _get_top_faces(bm)
    if not top_faces:
        return

    if roof_type == "hip":
        _roof_hip(bm, top_faces)
    elif roof_type == "gable":
        _roof_gable(bm, top_faces)
    elif roof_type == "dome":
        _roof_dome(bm, top_faces)
    elif roof_type == "terrace":
        _roof_terrace(bm, top_faces)
    elif roof_type == "parapet":
        _roof_parapet(bm, top_faces)


def _roof_hip(bm, top_faces):
    for face in top_faces:
        if len(face.verts) < 3:
            continue
        top = extrude_face(bm, face, face.calc_center_median().z * 0.05 + 0.5)
        scale_face_xy(bm, top, 0.01, 0.01)


def _roof_gable(bm, top_faces):
    for face in top_faces:
        if len(face.verts) < 4:
            _roof_hip(bm, [face])
            continue
        # Extrude then squash along short axis
        top = extrude_face(bm, face, face.calc_center_median().z * 0.05 + 1.0)
        # Identify long axis by bounding box
        xs = [v.co.x for v in top.verts]
        ys = [v.co.y for v in top.verts]
        dx = max(xs) - min(xs)
        dy = max(ys) - min(ys)
        if dx >= dy:
            scale_face_xy(bm, top, 1.0, 0.01)
        else:
            scale_face_xy(bm, top, 0.01, 1.0)


def _roof_dome(bm, top_faces):
    for face in top_faces:
        if len(face.verts) < 3:
            continue
        steps = [(0.6, 0.5), (0.35, 0.4), (0.15, 0.3), (0.05, 0.2)]
        current = face
        for sx, dz in steps:
            current = extrude_face(bm, current, dz)
            scale_face_xy(bm, current, sx, sx)


def _roof_terrace(bm, top_faces):
    for face in top_faces:
        if len(face.verts) < 3:
            continue
        steps = 3
        for _ in range(steps):
            bmesh.ops.inset_individual(bm, faces=[face], thickness=0.8, depth=0.0)
            # After inset, extrude the newly created inner face
            # Inset creates new faces; find the innermost one by area
            inner = min(face.verts[0].link_faces, key=lambda f: f.calc_area())
            face = extrude_face(bm, inner, 1.2)


def _roof_parapet(bm, top_faces):
    for face in top_faces:
        if len(face.verts) < 3:
            continue
        # Extrude boundary edges upward
        edges = [e for e in face.edges]
        ret = bmesh.ops.extrude_edge_region(bm, edges=edges)
        new_verts = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=new_verts, vec=Vector((0, 0, 1.0)))


# ============================================================
# Facade Grammar
# ============================================================
def _get_vertical_faces(bm):
    return [f for f in bm.faces if abs(f.normal.z) < 0.1 and len(f.verts) >= 3]


def _apply_facade(bm, params, rng):
    detail = params.get("facade_detail", "none")
    if detail == "none":
        return

    vertical_faces = _get_vertical_faces(bm)
    if not vertical_faces:
        return

    if detail in ("windows", "full"):
        _facade_windows(bm, vertical_faces)
    if detail in ("balcony", "full"):
        _facade_balconies(bm, vertical_faces)


def _facade_windows(bm, faces):
    for face in faces:
        area = face.calc_area()
        if area < 4.0:
            continue
        # Recessed panel
        inset = max(0.1, min(0.4, area ** 0.5 * 0.08))
        try:
            bmesh.ops.inset_individual(bm, faces=[face], thickness=inset, depth=-0.15)
        except Exception:
            pass


def _facade_balconies(bm, faces):
    for face in faces:
        area = face.calc_area()
        if area < 6.0:
            continue
        try:
            ret = bmesh.ops.extrude_face_region(bm, geom=[face])
            new_faces = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMFace)]
            new_verts = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)]
            # Move outward along normal
            n = face.normal
            bmesh.ops.translate(bm, verts=new_verts, vec=n * 0.4)
            # Scale down slightly to look like a balcony slab
            for f in new_faces:
                center = f.calc_center_median()
                for v in f.verts:
                    v.co.x = center.x + (v.co.x - center.x) * 0.85
                    v.co.y = center.y + (v.co.y - center.y) * 0.85
        except Exception:
            pass


# ============================================================
# Typology Generators
# ============================================================
def gen_stepped_tower(bm, params, rng):
    w, d = params["base_w"], params["base_d"]
    H = params["height"]
    N = params["sections"]
    sr = params["setback_ratio"]
    sv = params["setback_variance"]
    twist = math.radians(params["twist_deg"])

    weights = [N - i for i in range(N)]
    total_w = sum(weights)
    section_heights = [H * wt / total_w for wt in weights]

    face = make_rect_face(bm, w, d, z=0.0)

    for i in range(N):
        sh = section_heights[i]
        face = extrude_face(bm, face, sh)
        if i < N - 1:
            rx = max(0.3, min(1.5, sr + rng.uniform(-sv, sv)))
            ry = max(0.3, min(1.5, sr + rng.uniform(-sv, sv)))
            scale_face_xy(bm, face, rx, ry)
            if twist != 0:
                sign = 1 if i % 2 == 0 else -1
                rotate_face_z(bm, face, twist * sign)
            add_floor_loop(bm, face, inset=0.3)


def gen_tapered(bm, params, rng):
    w, d = params["base_w"], params["base_d"]
    H = params["height"]
    tr = params["taper_ratio"]
    steps = 12
    step_h = H / steps
    per_step = tr ** (1.0 / steps)

    face = make_rect_face(bm, w, d, z=0.0)
    for _ in range(steps):
        face = extrude_face(bm, face, step_h)
        scale_face_xy(bm, face, per_step, per_step)


def gen_podium_tower(bm, params, rng):
    w, d = params["base_w"], params["base_d"]
    H = params["height"]
    ph = params["podium_height"]
    tr = params["tower_ratio"]
    sr = params["setback_ratio"]
    sv = params["setback_variance"]
    twist = math.radians(params["twist_deg"])

    face = make_rect_face(bm, w, d, z=0.0)
    face = extrude_face(bm, face, ph)
    add_floor_loop(bm, face, inset=0.5)
    scale_face_xy(bm, face, tr, tr)

    tower_h = H - ph
    N = 3
    weights = [N - i for i in range(N)]
    total_w = sum(weights)
    section_heights = [tower_h * wt / total_w for wt in weights]

    for i in range(N):
        face = extrude_face(bm, face, section_heights[i])
        if i < N - 1:
            rx = max(0.3, min(1.5, sr + rng.uniform(-sv, sv)))
            ry = max(0.3, min(1.5, sr + rng.uniform(-sv, sv)))
            scale_face_xy(bm, face, rx, ry)
            if twist != 0:
                rotate_face_z(bm, face, twist * (1 if i % 2 == 0 else -1))


def gen_slab(bm, params, rng):
    w, d = params["base_w"], params["base_d"]
    H = params["height"]
    floor_h = 3.0
    floors = max(1, int(H / floor_h))
    step_h = H / floors

    face = make_rect_face(bm, w, d, z=0.0)

    for i in range(floors):
        face = extrude_face(bm, face, step_h)
        if i % 2 == 0:
            add_floor_loop(bm, face, inset=0.15)


def gen_old_residential(bm, params, rng):
    w = params["base_w"] * rng.uniform(0.7, 1.0)
    d = params["base_d"] * rng.uniform(0.7, 1.0)
    H = params["height"]
    floors = max(1, int(H / 3.0))
    step_h = H / floors

    face = make_rect_face(bm, w, d, z=0.0)

    for i in range(floors):
        face = extrude_face(bm, face, step_h)
        if i == floors - 1:
            bmesh.ops.inset_individual(bm, faces=[face], thickness=0.3, depth=-0.3)


def gen_complex(bm, params, rng):
    w, d = params["base_w"], params["base_d"]
    H = params["height"]
    base_h = params.get("complex_base_height", 18.0)

    face = make_rect_face(bm, w, d, z=0.0)
    face = extrude_face(bm, face, base_h)
    add_floor_loop(bm, face, inset=0.5)

    n_towers = rng.randint(2, 4)
    tower_positions = _generate_tower_positions(w, d, n_towers, rng)

    for tx, ty, tw, td, th in tower_positions:
        tower_face = _create_offset_rect(bm, tx, ty, tw, td, base_h)
        tower_floors = max(2, int(th / 3.0))
        tower_step = (H - base_h) / tower_floors if tower_floors > 0 else 0

        for j in range(tower_floors):
            tower_face = extrude_face(bm, tower_face, tower_step)
            if j < tower_floors - 1:
                scale_face_xy(bm, tower_face, 0.95, 0.95)


def gen_industrial(bm, params, rng):
    w, d = params["base_w"], params["base_d"]
    H = params["height"]

    face = make_rect_face(bm, w, d, z=0.0)
    face = extrude_face(bm, face, H * 0.7)

    n_teeth = max(2, int(w / 8.0))
    tooth_w = w / n_teeth
    tooth_h = H * 0.3

    for i in range(n_teeth):
        x_start = -w / 2 + i * tooth_w
        tooth_center_x = x_start + tooth_w / 2
        tooth_face = _create_offset_rect(bm, x_start + tooth_w * 0.1, -d / 2 + 1.0, tooth_w * 0.8, d - 2.0, H * 0.7)
        tooth_face = extrude_face(bm, tooth_face, tooth_h)

        top_verts = [v for v in tooth_face.verts]
        if len(top_verts) >= 4:
            for v in top_verts:
                if v.co.x > tooth_center_x:
                    v.co.z += tooth_h * 0.5


def _generate_tower_positions(base_w, base_d, count, rng):
    positions = []
    margin = 3.0
    for _ in range(count):
        tw = rng.uniform(6.0, base_w * 0.3)
        td = rng.uniform(6.0, base_d * 0.3)
        tx = rng.uniform(-base_w / 2 + margin + tw / 2, base_w / 2 - margin - tw / 2)
        ty = rng.uniform(-base_d / 2 + margin + td / 2, base_d / 2 - margin - td / 2)
        th = rng.uniform(30.0, 80.0)
        positions.append((tx, ty, tw, td, th))
    return positions


def _create_offset_rect(bm, cx, cy, w, d, z):
    hw, hd = w / 2, d / 2
    verts = [
        bm.verts.new(Vector((cx - hw, cy - hd, z))),
        bm.verts.new(Vector((cx + hw, cy - hd, z))),
        bm.verts.new(Vector((cx + hw, cy + hd, z))),
        bm.verts.new(Vector((cx - hw, cy + hd, z))),
    ]
    face = bm.faces.new(verts)
    return face


def _cleanup_objects_by_name(prefix):
    to_remove = [obj for obj in bpy.data.objects if obj.name.startswith(prefix)]
    for obj in to_remove:
        bpy.data.objects.remove(obj, do_unlink=True)


def apply_white_clay(obj):
    mat_name = "CityP_WhiteClay"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.92, 0.91, 0.90, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.85
            bsdf.inputs["Specular IOR Level"].default_value = 0.05

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def generate_building(params, name="CityP_Building", context=None):
    if context is None:
        context = bpy.context

    rng = random.Random(params.get("seed", 7))

    _cleanup_objects_by_name(name)

    typology = params.get("typology", "stepped_tower")

    # --- v2.0 Style Generators (use CompositionBuilder) ---
    if typology == "bauhaus":
        from .styles import bauhaus_gen
        obj = bauhaus_gen.generate(params, context=context)
        if obj:
            apply_white_clay(obj)
        return obj
    elif typology == "constructivist":
        from .styles import constructivist_gen
        obj = constructivist_gen.generate(params, context=context)
        if obj:
            apply_white_clay(obj)
        return obj
    elif typology == "minimalist":
        from .styles import minimalist_gen
        obj = minimalist_gen.generate(params, context=context)
        if obj:
            apply_white_clay(obj)
        return obj
    elif typology == "postmodern":
        from .styles import postmodern_gen
        obj = postmodern_gen.generate(params, context=context)
        if obj:
            apply_white_clay(obj)
        return obj
    elif typology == "brutalist":
        from .styles import brutalist_gen
        obj = brutalist_gen.generate(params, context=context)
        if obj:
            apply_white_clay(obj)
        return obj

    # --- Legacy Generators (direct BMesh) ---
    mesh = bpy.data.meshes.new(name + "Mesh")
    bm = bmesh.new()

    dispatch = {
        "stepped_tower": gen_stepped_tower,
        "tapered": gen_tapered,
        "podium_tower": gen_podium_tower,
        "slab": gen_slab,
        "old_res": gen_old_residential,
        "complex": gen_complex,
        "industrial": gen_industrial,
    }

    if typology not in dispatch:
        print(f"[CityP] Unknown typology: {typology}")
        bm.free()
        return None

    dispatch[typology](bm, params, rng)

    # Apply roof & facade before finalizing
    _apply_roof(bm, params, rng)
    _apply_facade(bm, params, rng)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)
    context.view_layer.objects.active = obj
    obj.select_set(True)

    apply_white_clay(obj)

    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))

    if bpy.app.version < (4, 1, 0):
        mesh.use_auto_smooth = True
        mesh.auto_smooth_angle = math.radians(45)

    print(f"[CityP] Generated · typology={typology} · height={params['height']}m · seed={params.get('seed', 7)}")
    return obj
