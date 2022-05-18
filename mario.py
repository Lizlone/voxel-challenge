from scene import Scene
import taichi as ti
from taichi.math import *
scene = Scene()
scene.set_floor(-1, vec3(170/255, 217/255, 112/255))
scene.set_background_color((148/255, 146/255, 1))
scene.set_directional_light(vec3(1), 1, (0.85, 0.9, 0.9))
@ti.func
def sdEllipsoid(p, r):
    k0 = (p/r).norm()
    k1 = (p/(r*r)).norm()
    p.x = 0
    return k0*(k0-1.0)/k1
@ti.func
def sdRoundedCylinder(p, ra, rb, h):
    d = vec2((p.xz).norm()-2.0*ra+rb, abs(p.y) - h)
    return min(max(d.x, d.y), 0.0) + (max(d, 0.0)).norm() - rb
@ti.func
def block(p, b, r):
    q = abs(p) - b
    return (max(q, 0.0)).norm() + min(max(q.x, max(q.y, q.z)), 0.0) - r
@ti.func
def sdCapsule(p, a, b, r):
    pa = p - a
    ba = b - a
    h = clamp(dot(pa, ba)/dot(ba, ba), 0.0, 1.0)
    return (pa - ba*h).norm() - r
@ti.func
def opSmoothSubtraction(d1, d2, k):
    h = clamp(0.5 - 0.5*(d2+d1)/k, 0.0, 1.0)
    return mix(d2, -d1, h) + k*h*(1.0-h)
@ti.func
def opSmoothUnion(d1, d2, k):
    h = clamp(0.5 + 0.5*(d2-d1)/k, 0.0, 1.0)
    return mix(d2, d1, h) - k*h*(1.0-h)
@ti.func
def question(i, j, k, a, offset):
    p = rotate3d(vec3(i, j-32, k+32), vec3(0, 1, 0), radians(a)) + offset
    if block(vec3(i, j-17, k), vec3(14, 3, 4), 0) < 0:  # t
        scene.set_voxel(p, 2, vec3(1))
    if block(vec3(i+14, j-11, k), vec3(4, 6, 4), 0) < 0:  # l
        scene.set_voxel(p, 2, vec3(1))
    if block(vec3(i-14, j-9, k), vec3(4, 8, 4), 0) < 0:  # R
        scene.set_voxel(p, 2, vec3(1))
    if block(vec3(i-7, j-2, k), vec3(7, 3, 4), 0) < 0:  # b
        scene.set_voxel(p, 2, vec3(1))
    if block(vec3(i, j+3, k), vec3(4, 6, 4), 0) < 0:  # top bar
        scene.set_voxel(p, 2, vec3(1))
    if block(vec3(i, j+16, k), vec3(4, 4, 4), 0) < 0:  # bottom bar
        scene.set_voxel(p, 2, vec3(1))
@ti.kernel
def initialize_voxels():
    for i, j, k in ti.ndrange((-64, 64), (-64, 64), (-64, 64)):
        offset_r = vec3(28, 0, 0)
        # mushroom
        if opSmoothSubtraction(j-20, sdEllipsoid(vec3(i, j-35, k), vec3(35, 28, 35)), 10) < 0:  # hat
            scene.set_voxel(vec3(i, j, k)+offset_r, 1, vec3(1, 0, 0))
            if sdCapsule(vec3(i, j-40, k), vec3(0, 0, k), vec3(0, 0, -k), 12) < 0:  # spot
                scene.set_voxel(vec3(i, j, k)+offset_r, 1, vec3(1))
            if sdCapsule(vec3(i, j-40, k), vec3(i, 0, 0), vec3(-i, 0, 0), 12) < 0:
                scene.set_voxel(vec3(i, j, k)+offset_r, 1, vec3(1))
            if sdCapsule(vec3(i, j-40, k), vec3(0, 0, 0), vec3(0, 64, 0), 12) < 0:
                scene.set_voxel(vec3(i, j, k)+offset_r, 1, vec3(1))
        if opSmoothSubtraction(j, sdRoundedCylinder(vec3(i, j-10, k), 10, 10, 15), 13) < 0:  # body
            scene.set_voxel(vec3(i, j, k)+offset_r, 1, vec3(244/255, 220/255, 180/255))
            if sdCapsule(vec3(abs(i), j-12, k), vec3(6, 0, k), vec3(6, 5, k), 2) < 0:  # eyes
                scene.set_voxel(vec3(i, j, k)+offset_r, 1, vec3(0))
        # block
        if block(vec3(i, j+32, k), vec3(22), 10) < 0:
            scene.set_voxel(vec3(i, j, k)+offset_r, 1, vec3(1, 1, 0))
        if sdCapsule(vec3(abs(i), abs(j), abs(k)), vec3(22, 22, 32), vec3(22, 22, -32), 2) < 0:  # hole
            scene.set_voxel(vec3(i, j-32, k)+offset_r, 0, vec3(0))
        if sdCapsule(vec3(abs(i), abs(j), abs(k)), vec3(32, 22, 22), vec3(-32, 22, 22), 2) < 0:
            scene.set_voxel(vec3(i, j-32, k)+offset_r, 0, vec3(0))
        question(i, j, k, 0, offset_r)
        question(i, j, k, 90, offset_r)
        question(i, j, k, 180, offset_r)
        question(i, j, k, 270, offset_r)
        # yoshi egg
        offset_l = vec3(-36, -36, 0)
        inside = {'t':0, 'b':0, 'egg':0}
        if sdEllipsoid(vec3(i, j, k), vec3(28, 48, 28)) < 0 and j > 0:  # t
            scene.set_voxel(vec3(i, j, k)+offset_l, 1, vec3(1))
            inside['t'] = 1
        if vec3(i, j, k).norm()-28 < 0 and j <= 0:  # b
            scene.set_voxel(vec3(i, j, k)+offset_l, 1, vec3(1))
            inside['b'] = 1
        if inside['t'] or inside['b']:
            inside['egg'] = 1
        if sdCapsule(vec3(i, j, k), vec3(-64, -64, 32), vec3(64, 64, -32), 10) < 0 and inside['egg']:  # spot
            scene.set_voxel(vec3(i, j, k)+offset_l, 1, vec3(0, 1, 0))
        if sdCapsule(vec3(i, j, k), vec3(64, -32, 64), vec3(-64, 32, -64), 13) < 0 and inside['egg']:
            scene.set_voxel(vec3(i, j, k)+offset_l, 1, vec3(0, 1, 0))
        if sdCapsule(vec3(i, j, k), vec3(-64, 108, 64), vec3(64, -108, -64), 18) < 0 and inside['egg']:
            scene.set_voxel(vec3(i, j, k)+offset_l, 1, vec3(0, 1, 0))
        if sdCapsule(vec3(i, j, k), vec3(64, 64, 64), vec3(-64, -64, -64), 8) < 0 and inside['egg']:
            scene.set_voxel(vec3(i, j, k)+offset_l, 1, vec3(0, 1, 0))
initialize_voxels()
scene.finish()
