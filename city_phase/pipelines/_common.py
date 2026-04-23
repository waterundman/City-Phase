import bpy


def setup_world_nodes(world):
    if not world:
        return None
    world.use_nodes = True
    tree = world.node_tree
    tree.nodes.clear()
    return tree


def cleanup_cityp_lights():
    for light in list(bpy.data.lights):
        if light.name.startswith("CityP_"):
            bpy.data.lights.remove(light)


def add_light_to_scene(context, name, light_type, **kwargs):
    light_data = bpy.data.lights.new(name, light_type)
    for key, value in kwargs.items():
        if hasattr(light_data, key):
            setattr(light_data, key, value)
    obj = bpy.data.objects.new(name, light_data)
    context.collection.objects.link(obj)
    return obj


def update_material(name, updates):
    mat = bpy.data.materials.get(name)
    if not mat:
        return
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        return
    for key, value in updates.items():
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = value
