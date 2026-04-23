import bpy
from ._common import setup_world_nodes, cleanup_cityp_lights, add_light_to_scene, update_material


def apply(context):
    scene = context.scene
    world = scene.world

    if not world:
        world = bpy.data.worlds.new("CityP_World")
        scene.world = world

    tree = setup_world_nodes(world)

    bg = tree.nodes.new("ShaderNodeTexEnvironment")
    bg.location = (-300, 200)

    sky = tree.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "PREETHAM2"
    sky.sun_direction = (0.5, 0.3, 0.8)
    sky.turbidity = 2.0
    sky.ground_albedo = 0.3
    sky.location = (-300, 0)

    output = tree.nodes.new("ShaderNodeOutputWorld")
    output.location = (200, 0)

    mix = tree.nodes.new("ShaderNodeMixRGB")
    mix.inputs["Fac"].default_value = 0.0
    mix.location = (-50, 0)

    tree.links.new(sky.outputs["Color"], mix.inputs[1])
    tree.links.new(bg.outputs["Color"], mix.inputs[2])
    tree.links.new(mix.outputs["Shader"], output.inputs["Surface"])

    scene.render.engine = "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 2, 0) else "BLENDER_EEVEE"

    eevee = scene.eevee
    eevee.use_bloom = False
    eevee.use_ssr = False
    eevee.use_gtao = True
    eevee.gtao_quality = 0.5

    cleanup_cityp_lights()

    add_light_to_scene(
        context, "CityP_SoftLight", "SUN",
        energy=3.0, angle=0.1, color=(0.85, 0.88, 0.95),
    ).rotation_euler = (0.96, 0, 0.96)

    add_light_to_scene(
        context, "CityP_Fill", "AREA",
        energy=100, color=(0.5, 0.55, 0.7), size=20,
    ).location = (0, 0, 10)

    update_material("CityP_WhiteClay", {
        "Base Color": (0.94, 0.93, 0.92, 1.0),
        "Roughness": 0.85,
        "Specular IOR Level": 0.05,
    })
    update_material("CityP_RoadMat", {
        "Base Color": (0.75, 0.75, 0.78, 1.0),
        "Roughness": 0.9,
    })

    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
