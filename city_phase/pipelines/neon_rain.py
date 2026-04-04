import bpy
import math


def apply(context):
    scene = context.scene
    world = scene.world

    if not world:
        world = bpy.data.worlds.new("CityP_World")
        scene.world = world

    world.use_nodes = True
    tree = world.node_tree
    tree.nodes.clear()

    bg = tree.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.02, 0.02, 0.05, 1.0)
    bg.inputs["Strength"].default_value = 0.1
    bg.location = (-300, 0)

    output = tree.nodes.new("ShaderNodeOutputWorld")
    output.location = (200, 0)

    tree.links.new(bg.outputs["Background"], output.inputs["Surface"])

    scene.render.engine = "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 2, 0) else "BLENDER_EEVEE"

    eevee = scene.eevee
    eevee.use_bloom = True
    eevee.bloom_threshold = 0.6
    eevee.bloom_intensity = 1.2
    eevee.bloom_radius = 6.0
    eevee.use_gtao = True
    eevee.gtao_quality = 0.7

    for light in list(bpy.data.lights):
        if light.name.startswith("CityP_"):
            bpy.data.lights.remove(light)

    ambient_data = bpy.data.lights.new("CityP_Ambient", "POINT")
    ambient_data.energy = 5
    ambient_data.color = (0.1, 0.1, 0.2)
    ambient = bpy.data.objects.new("CityP_Ambient", ambient_data)
    ambient.location = (0, 0, 30)
    context.collection.objects.link(ambient)

    neon_colors = [
        (0.88, 0.12, 0.24),
        (0.12, 0.25, 0.88),
        (0.94, 0.75, 0.12),
    ]

    for i, color in enumerate(neon_colors):
        for j in range(3):
            neon_data = bpy.data.lights.new(f"CityP_Neon_{i}_{j}", "POINT")
            neon_data.energy = 15
            neon_data.color = color
            neon_data.use_shadow = False
            neon = bpy.data.objects.new(f"CityP_Neon_{i}_{j}", neon_data)
            angle = (i / 3) * 6.28 + j * 0.5
            radius = 30 + j * 15
            neon.location = (radius * math.cos(angle), radius * math.sin(angle), 5 + j * 10)
            context.collection.objects.link(neon)

    for mat in bpy.data.materials:
        if mat.name == "CityP_RoadMat":
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            bsdf = nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Base Color"].default_value = (0.05, 0.05, 0.08, 1.0)
                bsdf.inputs["Roughness"].default_value = 0.2
                bsdf.inputs["Metallic"].default_value = 0.1

    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = -0.5
