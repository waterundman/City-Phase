import bpy
import math
from ._common import setup_world_nodes, cleanup_cityp_lights, add_light_to_scene, update_material


def apply(context):
    scene = context.scene
    world = scene.world

    if not world:
        world = bpy.data.worlds.new("CityP_World")
        scene.world = world

    tree = setup_world_nodes(world)

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

    cleanup_cityp_lights()

    add_light_to_scene(
        context, "CityP_Ambient", "POINT",
        energy=5, color=(0.1, 0.1, 0.2),
    ).location = (0, 0, 30)

    neon_colors = [
        (0.88, 0.12, 0.24),
        (0.12, 0.25, 0.88),
        (0.94, 0.75, 0.12),
    ]

    for i, color in enumerate(neon_colors):
        for j in range(3):
            angle = (i / 3) * 6.28 + j * 0.5
            radius = 30 + j * 15
            obj = add_light_to_scene(
                context, f"CityP_Neon_{i}_{j}", "POINT",
                energy=15, color=color, use_shadow=False,
            )
            obj.location = (radius * math.cos(angle), radius * math.sin(angle), 5 + j * 10)

    update_material("CityP_RoadMat", {
        "Base Color": (0.05, 0.05, 0.08, 1.0),
        "Roughness": 0.2,
        "Metallic": 0.1,
    })

    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = -0.5
