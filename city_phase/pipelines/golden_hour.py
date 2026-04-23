import bpy
import math
from ._common import setup_world_nodes, cleanup_cityp_lights, add_light_to_scene


def apply(context):
    scene = context.scene
    world = scene.world

    if not world:
        world = bpy.data.worlds.new("CityP_World")
        scene.world = world

    tree = setup_world_nodes(world)

    sky = tree.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "PREETHAM2"
    sky.sun_direction = (0.966, 0.0, 0.259)
    sky.turbidity = 4.5
    sky.ground_albedo = 0.2
    sky.location = (-300, 0)

    output = tree.nodes.new("ShaderNodeOutputWorld")
    output.location = (200, 0)

    tree.links.new(sky.outputs["Color"], output.inputs["Surface"])

    scene.render.engine = "CYCLES"
    scene.cycles.samples = 256
    scene.cycles.use_denoising = True

    cleanup_cityp_lights()

    add_light_to_scene(
        context, "CityP_GoldenSun", "SUN",
        energy=8.0, angle=0.02, color=(0.96, 0.65, 0.35),
    ).rotation_euler = (math.radians(15), 0, math.radians(45))

    add_light_to_scene(
        context, "CityP_CoolFill", "AREA",
        energy=50, color=(0.35, 0.4, 0.65), size=30,
    )

    add_light_to_scene(
        context, "CityP_Rim", "AREA",
        energy=30, color=(0.8, 0.5, 0.3), size=15,
    )

    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.sequencer_colorspace_settings.name = "sRGB"
