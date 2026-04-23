"""
城市相 · Building Generator  v0.1
──────────────────────────────────
在 Blender Text Editor 粘贴后 Run Script 即可。
会在场景原点生成一栋参数化建筑，每次运行自动清除上一次结果。

支持形态（typology）:
  stepped_tower  —— 步退式高层（主要景观建筑类型）
  tapered        —— 锥削塔（单纯从底到顶线性收缩）
  podium_tower   —— 裙房 + 塔楼二段式
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

# ═══════════════════════════════════════════════
#  参数区 —— 在这里调整
# ═══════════════════════════════════════════════

P = {
    # 底层平面尺寸（米）
    "base_w":          24.0,
    "base_d":          18.0,

    # 总高度（米）
    "height":          120.0,

    # 形态类型: 'stepped_tower' | 'tapered' | 'podium_tower'
    "typology":        "stepped_tower",

    # ── stepped_tower 专用 ──
    "sections":        4,        # 步退段数（建议 3–6）
    "setback_ratio":   0.80,     # 每段 XY 收缩比（0.75–0.90 视觉效果好）
    "setback_variance":0.06,     # 收缩比随机浮动范围
    "twist_deg":       5.0,      # 每段扭转角度，0 = 不扭

    # ── tapered 专用 ──
    "taper_ratio":     0.30,     # 顶部相对底部的尺寸比

    # ── podium_tower 专用 ──
    "podium_height":   22.0,     # 裙房高度（米）
    "tower_ratio":     0.45,     # 塔楼宽度 / 裙房宽度

    # 随机种子
    "seed":            7,
}

# ═══════════════════════════════════════════════
#  底层几何工具函数
# ═══════════════════════════════════════════════

def make_rect_face(bm, w, d, z=0.0):
    """在 bmesh 里创建一个矩形底面，返回该 Face。"""
    hw, hd = w / 2, d / 2
    verts = [
        bm.verts.new(Vector((-hw, -hd, z))),
        bm.verts.new(Vector(( hw, -hd, z))),
        bm.verts.new(Vector(( hw,  hd, z))),
        bm.verts.new(Vector((-hw,  hd, z))),
    ]
    face = bm.faces.new(verts)
    return face


def extrude_face(bm, face, dz):
    """
    沿 Z 轴拉伸 face，高度 dz。
    返回拉伸后的顶面（top face）。

    bmesh.ops.extrude_face_region 会在原位克隆顶面，
    需要手动 translate 新生成的顶部顶点。
    """
    ret = bmesh.ops.extrude_face_region(bm, geom=[face])

    # 从返回的 geom 里拿顶部顶点和顶部面
    top_verts = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)]
    top_face  = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMFace)][0]

    bmesh.ops.translate(bm, verts=top_verts, vec=Vector((0, 0, dz)))
    return top_face


def scale_face_xy(bm, face, sx, sy):
    """
    以面中心为基准，在 XY 平面上缩放顶面顶点。
    用于实现步退（setback）效果。
    """
    center = face.calc_center_median()
    for v in face.verts:
        v.co.x = center.x + (v.co.x - center.x) * sx
        v.co.y = center.y + (v.co.y - center.y) * sy


def rotate_face_z(bm, face, angle_rad):
    """
    以面中心为基准，绕 Z 轴旋转顶面顶点。
    用于实现扭转（twist）效果。
    """
    center = face.calc_center_median()
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
    for v in face.verts:
        dx = v.co.x - center.x
        dy = v.co.y - center.y
        v.co.x = center.x + dx * cos_a - dy * sin_a
        v.co.y = center.y + dx * sin_a + dy * cos_a


def add_floor_loop(bm, face, inset=0.4):
    """
    在顶面边缘内缩一圈 edge loop，
    制造楼板/腰线的视觉分隔感。
    """
    bmesh.ops.inset_individual(bm, faces=[face], thickness=inset, depth=0.0)


# ═══════════════════════════════════════════════
#  形态生成器
# ═══════════════════════════════════════════════

def gen_stepped_tower(bm, p, rng):
    """
    步退式高层算法：
    将总高度分配给 N 段，每段向上拉伸后，
    顶面向内收缩（+ 可选扭转），再拉伸下一段。

    高度分配策略：底段最高，越往上越矮。
    权重：[N, N-1, ..., 1]，形成收腰感。
    """
    w, d  = p["base_w"], p["base_d"]
    H     = p["height"]
    N     = p["sections"]
    sr    = p["setback_ratio"]
    sv    = p["setback_variance"]
    twist = math.radians(p["twist_deg"])

    # 高度权重：底段 N 份，顶段 1 份
    weights = [N - i for i in range(N)]
    total_w = sum(weights)
    section_heights = [H * wt / total_w for wt in weights]

    # 创建底面
    face = make_rect_face(bm, w, d, z=0.0)

    for i in range(N):
        sh = section_heights[i]

        # ① 拉伸当前段
        face = extrude_face(bm, face, sh)

        # ② 不是最后一段才做步退
        if i < N - 1:
            # 每轴独立随机收缩，避免完全轴对称（太机械）
            rx = sr + rng.uniform(-sv, sv)
            ry = sr + rng.uniform(-sv, sv)
            scale_face_xy(bm, face, rx, ry)

            # ③ 可选：每段交替方向扭转
            if twist != 0:
                sign = 1 if i % 2 == 0 else -1
                rotate_face_z(bm, face, twist * sign)

            # ④ 加一条楼层分隔 loop（装饰性，可注释掉）
            add_floor_loop(bm, face, inset=0.3)


def gen_tapered(bm, p, rng):
    """
    线性锥削塔：
    每隔固定高度做一次均匀收缩，
    收缩率由 taper_ratio 控制（顶/底尺寸比）。

    per-step ratio = taper_ratio ^ (1 / steps)
    """
    w, d   = p["base_w"], p["base_d"]
    H      = p["height"]
    tr     = p["taper_ratio"]
    steps  = 12   # 内部分段数，越多越平滑

    step_h  = H / steps
    # 每步应缩放到的比例（等比数列）
    per_step = tr ** (1.0 / steps)

    face = make_rect_face(bm, w, d, z=0.0)

    for _ in range(steps):
        face = extrude_face(bm, face, step_h)
        scale_face_xy(bm, face, per_step, per_step)


def gen_podium_tower(bm, p, rng):
    """
    裙房 + 塔楼二段式：
    ① 宽底盘（裙房）拉伸到 podium_height
    ② 顶面收缩到 tower_ratio 尺寸
    ③ 对塔楼部分应用步退逻辑（复用 stepped_tower 子步骤）
    """
    w, d        = p["base_w"], p["base_d"]
    H           = p["height"]
    ph          = p["podium_height"]
    tr          = p["tower_ratio"]
    sr          = p["setback_ratio"]
    sv          = p["setback_variance"]
    twist       = math.radians(p["twist_deg"])

    # ── 裙房段 ──
    face = make_rect_face(bm, w, d, z=0.0)
    face = extrude_face(bm, face, ph)
    add_floor_loop(bm, face, inset=0.5)

    # 裙房顶面收缩到塔楼尺寸
    scale_face_xy(bm, face, tr, tr)

    # ── 塔楼段（3段步退）──
    tower_h = H - ph
    N = 3
    weights = [N - i for i in range(N)]
    total_w = sum(weights)
    section_heights = [tower_h * wt / total_w for wt in weights]

    for i in range(N):
        face = extrude_face(bm, face, section_heights[i])
        if i < N - 1:
            rx = sr + rng.uniform(-sv, sv)
            ry = sr + rng.uniform(-sv, sv)
            scale_face_xy(bm, face, rx, ry)
            if twist != 0:
                rotate_face_z(bm, face, twist * (1 if i % 2 == 0 else -1))


# ═══════════════════════════════════════════════
#  材质：白膜 Clay
# ═══════════════════════════════════════════════

def apply_white_clay(obj):
    """
    创建并应用一个简单的白色漫反射材质。
    Roughness 0.85 模拟石膏/混凝土质感。
    """
    mat_name = "CityP_WhiteClay"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.92, 0.91, 0.90, 1.0)
            bsdf.inputs["Roughness"].default_value  = 0.85
            bsdf.inputs["Specular IOR Level"].default_value = 0.05

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


# ═══════════════════════════════════════════════
#  主入口
# ═══════════════════════════════════════════════

def main():
    rng = random.Random(P["seed"])

    # 清除上一次生成的建筑（按名称前缀删除）
    for obj in list(bpy.data.objects):
        if obj.name.startswith("CityP_Building"):
            bpy.data.objects.remove(obj, do_unlink=True)

    # 创建 Mesh + BMesh
    mesh = bpy.data.meshes.new("CityP_BuildingMesh")
    bm   = bmesh.new()

    # 根据 typology 分发到对应生成器
    dispatch = {
        "stepped_tower": gen_stepped_tower,
        "tapered":       gen_tapered,
        "podium_tower":  gen_podium_tower,
    }
    typology = P["typology"]
    if typology not in dispatch:
        print(f"[CityP] 未知 typology: {typology}")
        bm.free()
        return

    dispatch[typology](bm, P, rng)

    # 法线计算 + 写入 Mesh
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()

    # 创建场景对象
    obj = bpy.data.objects.new("CityP_Building", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # 应用白膜材质
    apply_white_clay(obj)

    # 添加 Smooth Shade（侧面更柔和）+ 锐化棱角
    bpy.ops.object.shade_smooth()
    mesh.use_auto_smooth = True
    mesh.auto_smooth_angle = math.radians(45)

    print(f"[CityP] 生成完成 · typology={typology} · 高度={P['height']}m · seed={P['seed']}")


main()
