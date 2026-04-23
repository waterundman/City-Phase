import bpy
import bmesh
import math
from mathutils import Vector


def apply_grime(obj, intensity=0.3):
    """Add procedural grime/grunge texture to the white clay material."""
    if not obj.data.materials:
        return

    mat = obj.data.materials[0]
    if not mat.use_nodes:
        mat.use_nodes = True

    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links

    # Remove existing grime nodes to avoid duplicates
    for name in ["CityP_GrimeTex", "CityP_GrimeRamp", "CityP_GrimeMix", "CityP_GrimeColor"]:
        n = nodes.get(name)
        if n:
            nodes.remove(n)

    bsdf = nodes.get("Principled BSDF")
    if bsdf is None:
        return

    # Musgrave texture for organic grime
    tex = nodes.new(type="ShaderNodeTexMusgrave")
    tex.name = "CityP_GrimeTex"
    tex.inputs["Scale"].default_value = 12.0
    tex.inputs["Detail"].default_value = 6.0
    tex.inputs["Dimension"].default_value = 0.0
    tex.inputs["Lacunarity"].default_value = 2.5
    tex.location = (-600, 200)

    # Color ramp: black (grime) -> white (clean)
    ramp = nodes.new(type="ShaderNodeValToRGB")
    ramp.name = "CityP_GrimeRamp"
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    ramp.location = (-400, 200)

    # Grime color (dark grey-brown)
    grime_color = nodes.new(type="ShaderNodeRGB")
    grime_color.name = "CityP_GrimeColor"
    grime_color.outputs["Color"].default_value = (0.18, 0.16, 0.14, 1.0)
    grime_color.location = (-400, -100)

    # Mix original base color with grime
    mix = nodes.new(type="ShaderNodeMixRGB")
    mix.name = "CityP_GrimeMix"
    mix.blend_type = "MIX"
    mix.inputs["Fac"].default_value = intensity
    mix.location = (-200, 0)

    links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], mix.inputs["Fac"])

    # Find the original base color input connection
    base_color_input = bsdf.inputs["Base Color"]
    if base_color_input.links:
        orig_color = base_color_input.links[0].from_socket
        links.new(orig_color, mix.inputs["Color1"])
    else:
        # Create a value node to hold the original color
        orig = nodes.new(type="ShaderNodeRGB")
        orig.outputs["Color"].default_value = base_color_input.default_value
        orig.location = (-400, -300)
        links.new(orig.outputs["Color"], mix.inputs["Color1"])

    links.new(grime_color.outputs["Color"], mix.inputs["Color2"])
    links.new(mix.outputs["Color"], base_color_input)


def apply_bevel(obj, segments=2, width=0.08):
    """Apply edge bevel via bmesh for LOD 2-3 quality."""
    if obj is None or obj.type != "MESH":
        return

    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # Only bevel edges where angle > 30 degrees (corners)
    edges = [e for e in bm.edges if not e.smooth and e.calc_face_angle() and e.calc_face_angle() > math.radians(30)]
    if not edges:
        bm.free()
        return

    try:
        bmesh.ops.bevel(bm, geom=edges, offset=width, offset_type="OFFSET", segments=segments, profile=0.5)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(mesh)
    except Exception:
        pass
    finally:
        bm.free()


def apply_window_emission(obj, intensity=2.0, density=(8.0, 12.0)):
    """Add procedural window grid emission to the material.

    Uses a Brick Texture in object-space to fake lit windows.
    Safe for large-scale scenes (no extra geometry).
    """
    if not obj.data.materials:
        return

    mat = obj.data.materials[0]
    if not mat.use_nodes:
        mat.use_nodes = True

    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links

    # Remove existing window nodes
    for name in ["CityP_WinBrick", "CityP_WinColor", "CityP_WinEmit", "CityP_WinMix", "CityP_WinMapping"]:
        n = nodes.get(name)
        if n:
            nodes.remove(n)

    bsdf = nodes.get("Principled BSDF")
    if bsdf is None:
        return

    # Mapping node for object-space scale
    mapping = nodes.new(type="ShaderNodeMapping")
    mapping.name = "CityP_WinMapping"
    mapping.vector_type = "TEXTURE"
    mapping.inputs["Scale"].default_value = Vector((density[0], density[1], 1.0))
    mapping.location = (-900, -400)

    tex_coord = nodes.get("Texture Coordinate")
    if tex_coord is None:
        tex_coord = nodes.new(type="ShaderNodeTexCoord")
        tex_coord.location = (-1100, -400)

    links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

    # Brick texture as window mask
    brick = nodes.new(type="ShaderNodeTexBrick")
    brick.name = "CityP_WinBrick"
    brick.inputs["Color1"].default_value = (1.0, 0.95, 0.8, 1.0)  # lit
    brick.inputs["Color2"].default_value = (0.0, 0.0, 0.0, 1.0)   # unlit
    brick.inputs["Mortar"].default_value = (0.0, 0.0, 0.0, 1.0)   # frame
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = 0.15
    brick.inputs["Mortar Smooth"].default_value = 0.1
    brick.inputs["Bias"].default_value = -0.5
    brick.inputs["Brick Width"].default_value = 1.0
    brick.inputs["Row Height"].default_value = 1.0
    brick.location = (-600, -400)

    links.new(mapping.outputs["Vector"], brick.inputs["Vector"])

    # Emission shader
    emit = nodes.new(type="ShaderNodeEmission")
    emit.name = "CityP_WinEmit"
    emit.inputs["Strength"].default_value = intensity
    emit.location = (-300, -300)

    win_color = nodes.new(type="ShaderNodeRGB")
    win_color.name = "CityP_WinColor"
    win_color.outputs["Color"].default_value = (1.0, 0.92, 0.78, 1.0)
    win_color.location = (-500, -500)

    links.new(win_color.outputs["Color"], emit.inputs["Color"])
    links.new(brick.outputs["Color"], emit.inputs["Color"])

    # Mix with principled BSDF
    mix = nodes.new(type="ShaderNodeMixShader")
    mix.name = "CityP_WinMix"
    mix.location = (100, 0)

    # Connect original BSDF output into mix
    output_node = nodes.get("Material Output")
    if output_node and bsdf.outputs["BSDF"].links:
        # Find existing link from BSDF to output
        old_link = bsdf.outputs["BSDF"].links[0]
        old_socket = old_link.to_socket
        links.remove(old_link)
        links.new(bsdf.outputs["BSDF"], mix.inputs[1])
        links.new(emit.outputs["Emission"], mix.inputs[2])
        links.new(brick.outputs["Fac"], mix.inputs["Fac"])
        links.new(mix.outputs["Shader"], old_socket)
    else:
        # Fallback
        links.new(bsdf.outputs["BSDF"], mix.inputs[1])
        links.new(emit.outputs["Emission"], mix.inputs[2])
        links.new(brick.outputs["Fac"], mix.inputs["Fac"])
        if output_node:
            links.new(mix.outputs["Shader"], output_node.inputs["Surface"])


def apply_atmospheric_fog(intensity=0.03, start=50.0, depth=800.0):
    """Add scene-level atmospheric fog via World Volume Scatter."""
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new(name="CityP_World")
        bpy.context.scene.world = world

    if not world.use_nodes:
        world.use_nodes = True

    nt = world.node_tree
    nodes = nt.nodes
    links = nt.links

    # Remove existing fog nodes
    for name in ["CityP_FogScatter", "CityP_FogDensity", "CityP_FogColor", "CityP_FogAdd"]:
        n = nodes.get(name)
        if n:
            nodes.remove(n)

    output = nodes.get("World Output")
    if output is None:
        return

    # Volume scatter
    scatter = nodes.new(type="ShaderNodeVolumeScatter")
    scatter.name = "CityP_FogScatter"
    scatter.location = (0, -300)

    # Color
    fog_color = nodes.new(type="ShaderNodeRGB")
    fog_color.name = "CityP_FogColor"
    fog_color.outputs["Color"].default_value = (0.85, 0.88, 0.92, 1.0)
    fog_color.location = (-300, -400)
    links.new(fog_color.outputs["Color"], scatter.inputs["Color"])

    # Density via depth-based falloff (simplified: use constant + noise if needed)
    # For now, use a simple density value adjusted by intensity
    scatter.inputs["Density"].default_value = intensity

    # Connect volume output
    if "Volume" in output.inputs:
        links.new(scatter.outputs["Volume"], output.inputs["Volume"])

    # Also add a subtle background gradient
    bg = nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.65, 0.70, 0.78, 1.0)
        bg.inputs["Strength"].default_value = 1.0
