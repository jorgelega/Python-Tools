# Convert FBX to images using blender
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def find_fbx_files(directory):
    fbx_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".fbx"):
                fbx_files.append(os.path.join(root, file))
    return fbx_files


def render_fbx_to_png(fbx_file, output_dir, blender_path):
    blender_script = f"""
import bpy
from mathutils import Vector

# Delete default objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Load the FBX file
bpy.ops.import_scene.fbx(filepath=r'{fbx_file}')

# Add 3-point lighting
def add_light(name, location, energy):
    bpy.ops.object.light_add(type='POINT', location=location)
    light = bpy.context.object
    light.data.energy = energy
    light.name = name

add_light('Key Light', (3, -3, 3), 1000)
add_light('Fill Light', (-3, -3, 3), 500)
add_light('Back Light', (0, 3, 3), 750)

# Find the bounding box of the imported object
imported_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
if imported_objects:
    # Assume first object is the target
    target_obj = imported_objects[0]
    bpy.context.view_layer.objects.active = target_obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # Calculate the dimensions and position the camera
    dims = target_obj.dimensions
    max_dim = max(dims)
    target_obj.location = (0, 0, 0)

    # Create and position camera
    camera_distance = max_dim * 1.5
    bpy.ops.object.camera_add(location=(camera_distance, camera_distance, camera_distance))
    camera = bpy.context.object
    camera.data.type = 'PERSP'
    camera.data.lens = 50  # Standard lens focal length

    # Point the camera to the object
    direction = (Vector(target_obj.location) - camera.location).normalized()
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()

    # Set the camera as the active camera
    bpy.context.scene.camera = camera

# Render settings
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.resolution_x = 600
bpy.context.scene.render.resolution_y = 600

# Output path
output_file = r'{os.path.join(output_dir, os.path.basename(fbx_file).replace('.fbx', '.png'))}'

# Render the scene
bpy.ops.render.render(write_still=True)
bpy.data.images['Render Result'].save_render(filepath=output_file)
"""

    subprocess.run([blender_path, '--background', '--python-expr', blender_script])


def start_rendering():
    fbx_files = find_fbx_files(fbx_dir.get())
    for fbx_file in fbx_files:
        render_fbx_to_png(fbx_file, output_dir.get(), blender_path.get())
    messagebox.showinfo("Rendering Complete", "All files have been rendered.")

def select_directory(entry):
    directory = filedialog.askdirectory()
    entry.set(directory)

def select_file(entry):
    file_path = filedialog.askopenfilename()
    entry.set(file_path)

root = tk.Tk()
root.title("FBX to PNG")
root.geometry("600x370")

# Dark theme colors
dark_color = "#333333"
light_color = "#eeeeee"

# Set the color scheme
root.configure(bg=dark_color)
style = {"bg": dark_color, "fg": light_color}

# Define the StringVar objects
fbx_dir = tk.StringVar()
output_dir = tk.StringVar()
blender_path = tk.StringVar()

tk.Label(root, text="FBX Directory:", **style, padx=30,pady=10).pack()
tk.Entry(root, textvariable=fbx_dir, bg=light_color, fg=dark_color, width=95).pack()
tk.Button(root, text="Browse", command=lambda: select_directory(fbx_dir), **style, padx=30,pady=10).pack()

tk.Label(root, text="Output Directory:", **style, padx=30,pady=10).pack()
tk.Entry(root, textvariable=output_dir, bg=light_color, fg=dark_color, width=95).pack()
tk.Button(root, text="Browse", command=lambda: select_directory(output_dir), **style, padx=30,pady=10).pack()

tk.Label(root, text="Blender Executable:", **style, padx=30,pady=10).pack()
tk.Entry(root, textvariable=blender_path, bg=light_color, fg=dark_color, width=95).pack()
tk.Button(root, text="Browse", command=lambda: select_file(blender_path), **style, padx=30,pady=10).pack()

tk.Button(root, text="Start Rendering", command=start_rendering, **style, padx=30,pady=10).pack()

root.mainloop()
