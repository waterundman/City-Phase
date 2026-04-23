"""
Composition Engine for CityPhase v2.0
Provides a predicate-based grammar for architectural composition.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
from dataclasses import dataclass, field
from typing import List, Set, Optional, Tuple, Union
from enum import Enum, auto


class ConnType(Enum):
    BRIDGE = auto()
    RAMP = auto()
    STAIR = auto()


class AlignAxis(Enum):
    X = auto()
    Y = auto()
    Z = auto()


@dataclass
class Volume:
    """A logical volume in the composition, tracking its constituent geometry."""
    faces: List[bmesh.types.BMFace] = field(default_factory=list)
    verts: Set[bmesh.types.BMVert] = field(default_factory=set)
    edges: Set[bmesh.types.BMEdge] = field(default_factory=set)
    metadata: dict = field(default_factory=dict)

    def calc_center(self) -> Vector:
        if not self.verts:
            return Vector((0, 0, 0))
        total = Vector((0, 0, 0))
        for v in self.verts:
            total += v.co
        return total / len(self.verts)

    def calc_bounds(self) -> Tuple[Vector, Vector]:
        """Return (min, max) bounds."""
        if not self.verts:
            return Vector((0, 0, 0)), Vector((0, 0, 0))
        xs = [v.co.x for v in self.verts]
        ys = [v.co.y for v in self.verts]
        zs = [v.co.z for v in self.verts]
        return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))


class CompositionBuilder:
    """High-level API for architectural composition using BMesh."""

    def __init__(self):
        self.bm = bmesh.new()
        self.op_log = []
        self.volumes = []

    # ------------------------------------------------------------------
    # Core Primitives
    # ------------------------------------------------------------------

    def place_box(self, w, d, h, pos=(0, 0, 0), rot=(0, 0, 0)) -> Volume:
        """Place a rectangular box volume."""
        hw, hd = w / 2.0, d / 2.0

        v0 = self.bm.verts.new(Vector((-hw, -hd, 0)))
        v1 = self.bm.verts.new(Vector((hw, -hd, 0)))
        v2 = self.bm.verts.new(Vector((hw, hd, 0)))
        v3 = self.bm.verts.new(Vector((-hw, hd, 0)))
        bottom = self.bm.faces.new((v0, v1, v2, v3))

        # Extrude upward
        ret = bmesh.ops.extrude_face_region(self.bm, geom=[bottom])
        new_verts = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)]
        new_faces = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMFace)]
        bmesh.ops.translate(self.bm, verts=new_verts, vec=Vector((0, 0, h)))

        all_faces = [bottom] + new_faces
        all_verts = set([v0, v1, v2, v3] + new_verts)
        all_edges = set(e for f in all_faces for e in f.edges)

        # Apply transform
        center = self._calc_verts_center(all_verts)
        matrix = self._build_transform_matrix(center, pos, rot)
        for v in all_verts:
            v.co = matrix @ v.co

        vol = Volume(faces=all_faces, verts=all_verts, edges=all_edges)
        self.volumes.append(vol)
        self.op_log.append(("PLACE_BOX", {"w": w, "d": d, "h": h, "pos": pos, "rot": rot}))
        return vol

    def place_cylinder(self, radius, h, segments=16, pos=(0, 0, 0), rot=(0, 0, 0)) -> Volume:
        """Place a cylinder volume."""
        verts_bottom = []
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            verts_bottom.append(self.bm.verts.new(Vector((x, y, 0))))

        bottom = self.bm.faces.new(verts_bottom)
        ret = bmesh.ops.extrude_face_region(self.bm, geom=[bottom])
        new_verts = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)]
        new_faces = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMFace)]
        bmesh.ops.translate(self.bm, verts=new_verts, vec=Vector((0, 0, h)))

        all_faces = [bottom] + new_faces
        all_verts = set(verts_bottom + new_verts)
        all_edges = set(e for f in all_faces for e in f.edges)

        center = self._calc_verts_center(all_verts)
        matrix = self._build_transform_matrix(center, pos, rot)
        for v in all_verts:
            v.co = matrix @ v.co

        vol = Volume(faces=all_faces, verts=all_verts, edges=all_edges)
        self.volumes.append(vol)
        self.op_log.append(("PLACE_CYLINDER", {"r": radius, "h": h, "pos": pos, "rot": rot}))
        return vol

    # ------------------------------------------------------------------
    # Surface Operations
    # ------------------------------------------------------------------

    def extrude_faces(self, faces, distance, taper=0.0) -> List[bmesh.types.BMFace]:
        """Extrude faces along their averaged normal."""
        if not faces:
            return []

        # Filter out deleted faces
        faces = [f for f in faces if f.is_valid]
        if not faces:
            return []

        ret = bmesh.ops.extrude_face_region(self.bm, geom=faces)
        new_verts = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)]
        new_faces = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMFace)]

        avg_normal = self._calc_faces_normal(faces)
        bmesh.ops.translate(self.bm, verts=new_verts, vec=avg_normal * distance)

        if taper != 0.0 and new_verts:
            center = self._calc_verts_center(new_verts)
            for v in new_verts:
                v.co = center + (v.co - center) * (1.0 - taper)

        self.op_log.append(("EXTRUDE", {"distance": distance, "taper": taper, "n_faces": len(faces)}))
        return new_faces

    def inset_faces(self, faces, thickness, depth) -> List[bmesh.types.BMFace]:
        """Inset faces. Returns the newly created inner faces."""
        faces = [f for f in faces if f.is_valid]
        if not faces:
            return []

        try:
            ret = bmesh.ops.inset_individual(
                self.bm, faces=faces, thickness=thickness, depth=depth
            )
            inner_faces = [g for g in ret.get("faces", []) if isinstance(g, bmesh.types.BMFace)]
            self.op_log.append(("INSET", {"thickness": thickness, "depth": depth}))
            return inner_faces
        except Exception as e:
            print(f"[CityP] Inset failed: {e}")
            return []

    def subdivide_face(self, face, cuts_u=1, cuts_v=1) -> List[bmesh.types.BMFace]:
        """Subdivide a quadrilateral face into a grid."""
        if not isinstance(face, bmesh.types.BMFace) or not face.is_valid:
            return []

        edges = list(face.edges)
        if len(edges) != 4:
            # For non-quad, just subdivide edges uniformly
            cuts = max(cuts_u, cuts_v)
            try:
                bmesh.ops.subdivide_edges(self.bm, edges=edges, cuts=cuts, use_grid_fill=True)
            except Exception:
                pass
            self.op_log.append(("SUBDIVIDE", {"cuts_u": cuts_u, "cuts_v": cuts_v}))
            return list(self.bm.faces)

        # Subdivide all 4 edges
        cuts = max(cuts_u, cuts_v)
        try:
            bmesh.ops.subdivide_edges(self.bm, edges=edges, cuts=cuts, use_grid_fill=True)
        except Exception:
            pass

        # Find new faces near the original face center
        orig_center = face.calc_center_median()
        new_faces = []
        for f in self.bm.faces:
            if not f.is_valid:
                continue
            # Heuristic: face center close to original center and face was created after subdivision
            if (f.calc_center_median() - orig_center).length < 0.1:
                new_faces.append(f)

        self.op_log.append(("SUBDIVIDE", {"cuts_u": cuts_u, "cuts_v": cuts_v}))
        return new_faces if new_faces else list(self.bm.faces)

    # ------------------------------------------------------------------
    # Boolean Operations
    # ------------------------------------------------------------------

    def boolean_union(self, vol_a: Volume, vol_b: Volume) -> Volume:
        """Logically merge two volumes.

        For visual consistency with same-material volumes, geometric boolean
        is skipped and faces are merged logically. This avoids the well-known
        robustness issues of mesh booleans in architectural composition.
        """
        merged_faces = list(set(vol_a.faces + vol_b.faces))
        merged_verts = vol_a.verts | vol_b.verts
        merged_edges = vol_a.edges | vol_b.edges
        vol = Volume(faces=merged_faces, verts=merged_verts, edges=merged_edges)
        self.volumes.append(vol)
        self.op_log.append(("BOOLEAN_UNION", {}))
        return vol

    def boolean_difference(self, vol_a: Volume, vol_b: Volume) -> Optional[Volume]:
        """Subtract vol_b from vol_a. (TODO: robust geometric boolean)."""
        # Placeholder: return vol_a unchanged. Actual implementation requires
        # a robust convex-decomposition boolean or Blender modifier fallback.
        self.op_log.append(("BOOLEAN_DIFF", {"status": "TODO"}))
        return vol_a

    # ------------------------------------------------------------------
    # Connections
    # ------------------------------------------------------------------

    def connect_volumes(self, vol_a: Volume, vol_b: Volume, conn_type=ConnType.BRIDGE) -> Optional[Volume]:
        """Create a geometric connection between two volumes."""
        if conn_type == ConnType.BRIDGE:
            return self._bridge_volumes(vol_a, vol_b)
        elif conn_type == ConnType.RAMP:
            return self._ramp_volumes(vol_a, vol_b)
        elif conn_type == ConnType.STAIR:
            return self._stair_volumes(vol_a, vol_b)
        return self._bridge_volumes(vol_a, vol_b)

    def _bridge_volumes(self, vol_a, vol_b):
        c1 = vol_a.calc_center()
        c2 = vol_b.calc_center()
        direction = c2 - c1
        length = direction.length
        if length < 0.01:
            return None

        mid = c1 + direction * 0.5
        # Bridge dimensions proportional to connection length
        bw = min(3.0, length * 0.25)
        bd = min(3.0, length * 0.25)
        bh = min(3.0, length * 0.25)

        bridge = self.place_box(bw, bd, bh, pos=mid)

        # Align bridge to face from vol_a to vol_b
        direction.normalize()
        rot_z = math.atan2(direction.y, direction.x)
        # Rotate bridge around its center
        center = bridge.calc_center()
        mat_ct = Matrix.Translation(center)
        mat_ct_inv = Matrix.Translation(-center)
        mat_r = Euler((0, 0, rot_z), 'XYZ').to_matrix().to_4x4()
        matrix = mat_ct @ mat_r @ mat_ct_inv
        for v in bridge.verts:
            v.co = matrix @ v.co

        self.op_log.append(("CONNECT_BRIDGE", {}))
        return bridge

    def _ramp_volumes(self, vol_a, vol_b):
        # Simplified: create a slanted bridge
        return self._bridge_volumes(vol_a, vol_b)

    def _stair_volumes(self, vol_a, vol_b):
        # Simplified: create a bridge (stairs would need more steps)
        return self._bridge_volumes(vol_a, vol_b)

    # ------------------------------------------------------------------
    # Alignment & Offset
    # ------------------------------------------------------------------

    def align_volumes(self, vol_a: Volume, vol_b: Volume, axis: AlignAxis):
        """Align vol_b to vol_a along specified axis."""
        c1 = vol_a.calc_center()
        c2 = vol_b.calc_center()
        delta = Vector((0, 0, 0))
        if axis == AlignAxis.X:
            delta.x = c1.x - c2.x
        elif axis == AlignAxis.Y:
            delta.y = c1.y - c2.y
        elif axis == AlignAxis.Z:
            delta.z = c1.z - c2.z
        bmesh.ops.translate(self.bm, verts=list(vol_b.verts), vec=delta)
        self.op_log.append(("ALIGN", {"axis": axis.name}))

    def center_volume_on(self, target: Volume, vol: Volume):
        """Center vol on target in X and Y axes (keeping Z unchanged)."""
        c1 = target.calc_center()
        c2 = vol.calc_center()
        delta = Vector((c1.x - c2.x, c1.y - c2.y, 0))
        bmesh.ops.translate(self.bm, verts=list(vol.verts), vec=delta)
        self.op_log.append(("CENTER_ON", {}))

    def offset_volume(self, vol: Volume, direction: Vector, distance: float):
        """Offset volume in a direction."""
        vec = direction.normalized() * distance
        bmesh.ops.translate(self.bm, verts=list(vol.verts), vec=vec)
        self.op_log.append(("OFFSET", {"distance": distance}))

    # ------------------------------------------------------------------
    # Material
    # ------------------------------------------------------------------

    def set_face_material(self, faces, material_index: int):
        """Set material index for faces."""
        valid_faces = [f for f in faces if f.is_valid]
        for f in valid_faces:
            f.material_index = material_index
        self.op_log.append(("MATERIAL", {"mat_index": material_index, "n_faces": len(valid_faces)}))

    # ------------------------------------------------------------------
    # Finalization
    # ------------------------------------------------------------------

    def build(self, name="Building", context=None) -> Optional[bpy.types.Object]:
        """Finalize BMesh into a Blender object."""
        if context is None:
            context = bpy.context

        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:])

        mesh = bpy.data.meshes.new(name + "_Mesh")
        self.bm.to_mesh(mesh)
        self.bm.free()

        obj = bpy.data.objects.new(name, mesh)
        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        # Smooth shading
        mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))

        return obj

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _calc_verts_center(verts) -> Vector:
        total = Vector((0, 0, 0))
        n = 0
        for v in verts:
            total += v.co
            n += 1
        return total / n if n > 0 else Vector((0, 0, 0))

    @staticmethod
    def _calc_faces_normal(faces) -> Vector:
        avg = Vector((0, 0, 0))
        for f in faces:
            avg += f.normal
        return avg.normalized() if avg.length > 0 else Vector((0, 0, 1))

    @staticmethod
    def _build_transform_matrix(center, pos, rot):
        mat_t = Matrix.Translation(Vector(pos))
        mat_r = Euler(rot, 'XYZ').to_matrix().to_4x4()
        mat_ct = Matrix.Translation(center)
        mat_ct_inv = Matrix.Translation(-center)
        return mat_t @ mat_ct @ mat_r @ mat_ct_inv
