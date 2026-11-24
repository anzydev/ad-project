import bpy
import math

# Clear existing objects
bpy.ops.wm.read_factory_settings(use_empty=True)

# 1. Central CPU Core (Icosphere with subdivisions)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0, location=(0, 0, 2.5))
core = bpy.context.active_object
core.name = "CpuCore"

# 2. Memory Ring (RAM Torus)
bpy.ops.mesh.primitive_torus_add(major_radius=2.2, minor_radius=0.08, location=(0, 0, 2.5), rotation=(0, 0, 0))
ram_ring = bpy.context.active_object
ram_ring.name = "RamRing"

# 3. Swap Ring (Inner Torus tilted at 45 degrees)
bpy.ops.mesh.primitive_torus_add(major_radius=1.6, minor_radius=0.06, location=(0, 0, 2.5), rotation=(math.radians(45), math.radians(25), 0))
swap_ring = bpy.context.active_object
swap_ring.name = "SwapRing"

# 4. Storage Base Platters (Disk Cylinders)
for i in range(3):
    bpy.ops.mesh.primitive_cylinder_add(radius=2.8 - (i * 0.25), depth=0.18, location=(0, 0, 0.25 + (i * 0.35)))
    platter = bpy.context.active_object
    platter.name = f"DiskPlatter_{i}"

# 5. Network Beacons (Upload and Download conduits)
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=3.0, location=(-3.2, 0, 1.5))
net_up = bpy.context.active_object
net_up.name = "NetUploadBeacon"

bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=3.0, location=(3.2, 0, 1.5))
net_down = bpy.context.active_object
net_down.name = "NetDownloadBeacon"

# 6. Battery Power Cell (Capsule / Cylinder with rounded bevel)
bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=1.6, location=(0, -2.8, 1.0))
battery = bpy.context.active_object
battery.name = "BatteryCell"

# Save .blend
bpy.ops.wm.save_as_mainfile(filepath="ISD/Blender/TelemetryCore.blend")

# Export FBX
bpy.ops.export_scene.fbx(
    filepath="ISD/Unity/Assets/Art/TelemetryCore.fbx",
    use_selection=False,
    global_scale=1.0,
    axis_forward='-Z',
    axis_up='Y'
)
print("SUCCESS: TelemetryCore model exported cleanly.")

