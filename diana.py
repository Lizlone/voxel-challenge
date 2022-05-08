from scene import Scene
import taichi as ti
from taichi.math import *
# inspired by https://t.bilibili.com/520981951078003843?tab=2
scene = Scene()
scene.set_floor(-1, vec3(1, 1, 1))
scene.set_background_color((0.2, 0.2, 0.2))
scene.set_background_color((1, 1, 1))
scene.set_directional_light((1, 0.5, 1), 0.3, (0.85, 0.9, 0.9))


# 2d
@ti.func
def sdUnevenCapsule(p, r1, r2, h):
    p.x = abs(p.x)
    b = (r1-r2)/h
    a = ti.sqrt(1.0-b*b)
    k = dot(p, vec2(-b, a))
    result = dot(p, vec2(a, b)) - r1
    if(k < 0.0):
        result = p.norm() - r1
    if(k > a*h):
        result = (p-vec2(0.0, h)).norm() - r2
    return result


@ti.func
def sdMoon(p, d, ra, rb):
    p.y = abs(p.y)
    a = (ra*ra - rb*rb + d*d)/(2.0*d)
    b = ti.sqrt(max(ra*ra-a*a, 0.0))
    result = max((p.norm()-ra), -((p-vec2(d, 0)).norm()-rb))
    if(d*(p.x*b-p.y*a) > d*d*max(b-p.y, 0.0)):
        result = (p-vec2(a, b)).norm()
    return result

# 3d


@ti.func
def sdEllipsoid(p, r):
    k0 = (p/r).norm()
    k1 = (p/(r*r)).norm()
    p.x = 0
    return k0*(k0-1.0)/k1


@ti.func
def sdCapsule(p, a, b, r):
    pa = p - a
    ba = b - a
    h = clamp(dot(pa, ba)/dot(ba, ba), 0.0, 1.0)
    return (pa - ba*h).norm() - r


@ti.kernel
def initialize_voxels():
    for i, j, k in ti.ndrange((-64, 64), (-64, 64), (-64, 64)):
        if sdMoon(vec2(i, j), 2, 10, 9) < 0 and -5 < k < 5:  # draw dumb hair
            scene.set_voxel(vec3(i, j, k)+vec3(4, 42, 0), 1, vec3(0))
        # if sdUnevenCapsule(vec2(i, j), 5, 20, 30) < 0 and -10 < k < 10:  # left bow tie
        #     scene.set_voxel(rotate3d(vec3(i, j, k)+vec3(20, 20, -20), vec3(0, 0, 1), radians(70)) + vec3(0), 1, vec3(1))
        # if sdUnevenCapsule(vec2(i, j), 5, 20, 30) < 0 and -10 < k < 10:  # right bow tie
        #     scene.set_voxel(rotate3d(vec3(i, j, k)+vec3(-20, 20, -20), vec3(0, 0, 1), radians(-70)) + vec3(0), 1, vec3(1))
        # badminton
        if sdEllipsoid(vec3(i, j+110, k), vec3(50, 100, 50)) < 0:  # draw body
            scene.set_voxel(vec3(i, j, k), 1, vec3(1))
        if sdEllipsoid(vec3(i, j-11, k), vec3(30, 25, 30)) < 0:  # draw head
            scene.set_voxel(vec3(i, j, k), 1, vec3(1))
            for z in range(64):
                if sdEllipsoid(vec3(i, j-11, z), vec3(30, 25, 30)) < 0:
                    # eyes
                    if k > 0 and sdEllipsoid(vec3(ti.abs(i)-9, j-17, k), vec3(2, 4, 3)) < 0:
                        scene.set_voxel(vec3(i, j, z), 1, vec3(0))
                    # blush
                    if k > 0 and sdEllipsoid(vec3(ti.abs(i)-20, j-9, k), vec3(6, 3, 3)) < 0:
                        scene.set_voxel(vec3(i, j, z), 1, vec3(
                            231/255, 153/255, 176/255))  # E799B0
            # top lip
            if k > 0 and sdCapsule(vec3(i, j-11, k), vec3(-8, -6, k), vec3(8, -6, k), 1) < 0:
                scene.set_voxel(vec3(i, j, k), 1, vec3(0))
            # botton lip
            if k > 0 and sdCapsule(vec3(ti.abs(i), j-11, k), vec3(0, -15, k), vec3(4, -6, k), 1) < 0:
                scene.set_voxel(vec3(i, j, k), 1, vec3(0))
        # tomato fry egg punch
        if sdCapsule(vec3(i, j+64, k), vec3(-50, 50, 0), vec3(0), 5) < 0:  # draw awrms
            scene.set_voxel(vec3(i, j, k), 1, vec3(0))
        if vec3(i+50, j+14, k).norm() - 8 < 0:  # fist
            scene.set_voxel(vec3(i, j, k), 1, vec3(0))
        if sdCapsule(vec3(i+50, j+14, k), vec3(-12, 12, 0), vec3(0), 2) < 0:  # tiny
            scene.set_voxel(vec3(i, j, k), 1, vec3(0))
        if sdCapsule(vec3(i+50, j+14, k), vec3(0, 18, 0), vec3(0), 2) < 0:  # perfumed
            scene.set_voxel(vec3(i, j, k), 1, vec3(0))


initialize_voxels()
scene.finish()
