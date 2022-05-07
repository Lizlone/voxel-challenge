from matplotlib.colors import rgb2hex
from scene import Scene
import taichi as ti
from taichi.math import *

scene = Scene(voxel_edges=0)
scene.set_background_color((0, 0, 0))
scene.set_directional_light((.5, .5, 1), 0, (.5, .5, .5))


@ti.func
def rgb(r, g, b):
    return vec3(r/255, g/255, b/255)


@ti.kernel
def initialize_voxels():
    for i in range(64):
        for j in range(64):
            scene.set_voxel(vec3(i, 0, j), 1, rgb(70, 60, 69))
            scene.set_voxel(vec3(i, j, 0), 1, rgb(194, 183, 177))
            if j % 2:
                scene.set_voxel(vec3(0, j, i), 1, rgb(80, 80, 80))
            else:
                scene.set_voxel(vec3(0, j, i), 1, rgb(127, 138, 127))
    r = 11.4
    for i, j, k in ti.ndrange((-r, r), (-r, r), (-r, r)):
        if vec3(i, j, k).norm() < r:
            scene.set_voxel(vec3(r + i, r + j, r + k), 1, rgb(156, 110, 105))


initialize_voxels()
scene.finish()
