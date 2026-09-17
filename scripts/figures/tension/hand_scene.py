"""A right hand in a claw grip on a modern symmetrical mouse, rendered for Tension Management.

    blender -b -P hand_scene.py -- --out file.png [--view front|threequarter|side|top|mouse]
        [--forces] [--final] [--no-hand] [--mouse-color r,g,b]
    blender -b -P hand_scene.py -- --shots shots.json [--final] ...

build.py runs this for the page; call it directly only to try a new view. --shots takes a JSON list
of {"out", "view", "forces"} and renders every one of them from a scene built once, which is what
build.py uses: the hand costs about twice what a render does, so paying for it per figure was the
slowest thing here.

The mouse is "Razer Viper Mini" by kimberly.h, CC BY 4.0, from Sketchfab; see the note above MODEL.
The hand is metaballs, so joints blend into one smooth surface, converted to a mesh. The forearm is
"FPS Arm Rig" by Miles0707, CC BY 4.0, from Sketchfab; see the note above FOREARM_MODEL. The hand is
one flat grey, and the forearm wears a compression sleeve. Every finger is posed by flexion angles
only, so no joint can bend backwards. A sidecar JSON gives label anchor points in image space.
"""
import json
import math
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeAlias, overload

import bpy
from mathutils import Vector

if TYPE_CHECKING:
    from mathutils import Quaternion
    from mathutils.bvhtree import BVHTree

# A point, written as a Vector or as the plain tuple the callers find easier to read.
Point: TypeAlias = "Vector | tuple[float, float, float]"
# One metaball: its kind, and the arguments build_hand needs to place it.
Element = tuple[str, Any]

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


@overload
def arg(name: str, default: str) -> str: ...


@overload
def arg(name: str, default: None = None) -> str | None: ...


def arg(name: str, default: str | None = None) -> str | None:
    return argv[argv.index(name) + 1] if name in argv else default


OUT = arg("--out", "render.png")
VIEW = arg("--view", "front")
FORCES, FINAL = "--forces" in argv, "--final" in argv
SHOTS = arg("--shots")
# One render: where it goes, which viewpoint, and whether the force arrows are in it.
Shot = tuple[str, str, bool]
# The anchors that belong to those arrows, left out of a shot that does not show them.
FORCE_ANCHORS = ("squeeze_left", "squeeze_right", "press")


def shots() -> list[Shot]:
    """Every render this run produces: the list in the --shots file, or the single one on argv."""
    if SHOTS is None:
        return [(OUT, VIEW, FORCES)]
    jobs = json.loads(Path(SHOTS).read_text(encoding="utf-8"))
    return [(job["out"], job["view"], bool(job.get("forces"))) for job in jobs]

K = 0.574  # a metaball's surface sits at K * radius at the default threshold

# Mouse: 1 unit is 10 mm. The mouse is "Razer Viper Mini" by kimberly.h
# (https://skfb.ly/oqIQA), licensed under
# CC BY 4.0. It is scaled to the real mouse's 118 mm length, turned so its front faces +y, recoloured
# in MOUSE_COLOR, and its logo and underside light strip are removed.
# models/razer-viper-mini/license.txt holds the credit.
MODEL = Path(__file__).resolve().parent / "models" / "razer-viper-mini" / "scene.gltf"
MOUSE_LENGTH = 11.8
# Shell colour as linear RGB, with metallic and roughness for the textured body and the smoother
# buttons. Glossy dark grey by default; --mouse-color r,g,b overrides the colour for a trial render.
MOUSE_COLOR = tuple(float(c) for c in arg("--mouse-color", "0.07,0.07,0.075").split(","))
MOUSE_METALLIC = 0.0
MOUSE_ROUGHNESS = {"Grain": 0.22, "Gloss": 0.12}
BVH: Any = None


def load_mouse() -> "BVHTree":
    """Import the mouse, place it on the pad centred at the origin, and keep a BVH of its surface for
    placing the hand."""
    from mathutils import Matrix
    from mathutils.bvhtree import BVHTree
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(MODEL))
    bpy.context.view_layer.update()
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    points = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    lo = Vector((min(q.x for q in points), min(q.y for q in points), min(q.z for q in points)))
    hi = Vector((max(q.x for q in points), max(q.y for q in points), max(q.z for q in points)))
    centre = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    place = (Matrix.Rotation(math.pi / 2, 4, "Z") @ Matrix.Scale(MOUSE_LENGTH / (hi.x - lo.x), 4) @
             Matrix.Translation(-centre))
    verts: list[Any] = []
    polys: list[list[int]] = []
    for o in meshes:
        o.data.transform(place @ o.matrix_world)
        o.parent = None
        o.matrix_world = Matrix.Identity(4)
        name = o.data.materials[0].name
        if name == "Green":
            o.hide_render = True
            continue
        if name in ("Grain", "Gloss"):
            bsdf = next(n for n in o.data.materials[0].node_tree.nodes if n.type == "BSDF_PRINCIPLED")
            # The body's normal map carries the embossed logo, so the body goes without it.
            sockets = ("Base Color", "Metallic", "Roughness") + (("Normal",) if name == "Grain" else ())
            for socket in sockets:
                for link in list(bsdf.inputs[socket].links):
                    o.data.materials[0].node_tree.links.remove(link)
            bsdf.inputs["Base Color"].default_value = (*MOUSE_COLOR, 1)
            bsdf.inputs["Metallic"].default_value = MOUSE_METALLIC
            bsdf.inputs["Roughness"].default_value = MOUSE_ROUGHNESS[name]
        if name != "Skates":
            offset = len(verts)
            verts += [v.co.copy() for v in o.data.vertices]
            polys += [[offset + i for i in poly.vertices] for poly in o.data.polygons]
    for o in list(bpy.context.scene.objects):
        if o.type == "EMPTY":
            bpy.data.objects.remove(o)
    return BVHTree.FromPolygons(verts, polys)


def surface_hit(origin: Point, direction: Point, lift: float) -> Vector:
    loc, normal, _index, _dist = BVH.ray_cast(Vector(origin), Vector(direction).normalized())
    if loc is None:
        raise ValueError(f"no mouse surface from {origin} toward {direction}")
    if normal.dot(Vector(direction)) > 0:
        normal = -normal
    return loc + normal * lift


def on_top(x: float, y: float, lift: float) -> Vector:
    """The mouse surface straight below (x, y), lifted along its normal."""
    return surface_hit((x, y, 20.0), (0, 0, -1), lift)


def clear_of_mouse(p: Point, radius: float) -> Vector:
    """Move p out to the mouse's surface when it sits inside the shell or too close to it, so a finger
    drawn around it never passes through the mouse."""
    loc, normal, _index, _dist = BVH.find_nearest(Vector(p))
    if loc is None:
        return Vector(p)
    out = Vector(p) - loc
    if normal.dot(out) < 0:
        normal = -normal
    gap = radius * 1.15 + THUMB_GAP
    return loc + normal * gap if out.length < gap else Vector(p)


def on_side(side: int, y: float, z: float, lift: float) -> Vector:
    """The mouse's right (side 1) or left (side -1) flank at height z."""
    return surface_hit((side * 20.0, y, z), (-side, 0, 0), lift)


BVH = load_mouse()
THUMB_GAP = float(arg("--thumb-gap", "0"))   # skin kept this far off the shell along the thumb
THUMB_OUT = float(arg("--thumb-out", "0"))    # the whole thumb moved this far out from the mouse


# Skeleton.
PITCH = math.radians(19)
F = Vector((0, math.cos(PITCH), math.sin(PITCH)))   # along the palm toward the knuckles
U = Vector((0, -math.sin(PITCH), math.cos(PITCH)))  # out of the back of the hand
X = Vector((1, 0, 0))
CONTACT = on_top(0.25, -4.1, 0.0)                    # palm heel on the rear of the hump
PALM_T = 2.0
HAND_DROP = float(arg("--hand-drop", "0.65"))        # how far the whole hand sits down the mouse
PALM_BACK = CONTACT - F * 1.4 + U * (PALM_T / 2 - HAND_DROP)
PALM_FRONT = CONTACT + F * 5.8 + U * (PALM_T / 2 + 0.15 - HAND_DROP)
WRIST = PALM_BACK - F * 1.9 + U * 0.1
ELBOW = Vector((-2.2, WRIST.y - 21.0, 2.2))


def finger_chain(base: Point, target: Point, lengths: Sequence[float], bend: Point) -> list[Vector]:
    """Joints from base to target for a finger that only flexes toward `bend`.

    Segment directions are cos(a)*forward + sin(a)*bend, with cumulative angles knuckle,
    knuckle + middle and knuckle + middle again: the joint nearest the tip stays straight, so the
    finger bends at two joints and rests on its pad.
    """
    base, target = Vector(base), Vector(target)
    b = Vector(bend).normalized()
    rel = target - base
    fwd = (rel - b * rel.dot(b)).normalized()
    goal = (rel.dot(fwd), rel.dot(b))
    best: tuple[float, tuple[int, int, int]] | None = None
    for knuckle in range(-35, 71):
        for middle in range(0, 101):
            angles = (knuckle, knuckle + middle, knuckle + middle)
            px = sum(l * math.cos(math.radians(a)) for l, a in zip(lengths, angles))
            py = sum(l * math.sin(math.radians(a)) for l, a in zip(lengths, angles))
            err = (px - goal[0]) ** 2 + (py - goal[1]) ** 2 + 0.003 * middle
            if best is None or err < best[0]:
                best = (err, angles)
    pts = [base]
    assert best is not None
    for length, a in zip(lengths, best[1]):
        r = math.radians(a)
        pts.append(pts[-1] + (fwd * math.cos(r) + b * math.sin(r)) * length)
    return pts


# Phalanx lengths below are an adult hand's; the render uses them at FINGER_LENGTH, and the thumb at
# THUMB_LENGTH, so the fingers do not dwarf the mouse.
FINGER_LENGTH, THUMB_LENGTH = 0.8, 0.956
# name: knuckle offset across the palm, knuckle offset back along F, phalanx lengths,
# radii at knuckle / middle / tip, fingertip contact as a function of fingertip radius.
# A fingertip's skin sits at TIP_TOUCH of the radius its bone is given, so the contact is lifted by
# that much: the pad rests on the mouse instead of floating above it.
TIP_TOUCH = float(arg("--tip-touch", "0.6"))
FINGERS = {
    "index": (-2.05, 0.1, (3.1, 2.1, 1.7), (0.66, 0.58, 0.5), lambda r: on_top(-1.35, 4.3, r * TIP_TOUCH)),
    "middle": (-0.35, 0.0, (3.4, 2.3, 1.8), (0.68, 0.6, 0.52), lambda r: on_top(1.2, 4.6, r * TIP_TOUCH)),
    "ring": (1.3, 0.35, (3.35, 2.25, 1.75), (0.63, 0.55, 0.48), lambda r: on_side(1, 0.9, 1.2, r * TIP_TOUCH)),
    "pinky": (2.75, 1.1, (2.65, 1.8, 1.55), (0.55, 0.49, 0.43), lambda r: on_side(1, -1.6, 0.9, r * TIP_TOUCH)),
}
# The thumb has two segments past the palm, so it shows one joint, as a real thumb does.
# The thumb rests low on the flank, below the side buttons, so both stay visible above it. Its contact
# is lifted by more than the tip's radius, so the skin sits on the shell instead of sinking into it.
THUMB = ((3.45, 2.05), (0.8, 0.62, 0.46), lambda r: on_side(-1, 4.5, 0.5, r * 10 + 0.1))
THUMB_BASE = PALM_BACK + F * 2.2 - X * 2.8 - U * 0.6


# Fingers and thumb are drawn FINGER_THICKNESS times the radii in their tables; the palm and wrist are
# puffed out by BODY_PUFF, so the hand reads soft rather than bony.
FINGER_THICKNESS, BODY_PUFF = 1.4, 1.08


def finger_tube(elements: list[Element], pts: Sequence[Vector], r: Sequence[float],
                clear: bool = False) -> None:
    """A finger as closely spaced balls with radii eased along its bones. Capsules would overlap at
    each joint and swell it; an even run of balls keeps the finger smooth from knuckle to tip. With
    clear set, every ball is held outside the mouse, so no part of the finger sinks into the shell."""
    def ball(centre: Vector, radius: float) -> None:
        elements.append(("ball", (clear_of_mouse(centre, radius) if clear else centre, radius * 0.78)))

    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        n = max(2, int((b - a).length / 0.22))
        for j in range(n):
            t = j / n
            ball(a.lerp(b, t), r[i] + (r[i + 1] - r[i]) * t)
    ball(pts[-1], r[len(pts) - 1])


def build_skeleton() -> tuple[list[Element], dict[str, tuple[list[Vector], list[float]]]]:
    """Metaball elements as (kind, data), and each finger's joints and radii."""
    elements: list[Element] = []
    joints: dict[str, tuple[list[Vector], list[float]]] = {}
    palm_mid = (PALM_BACK + PALM_FRONT) / 2
    k = BODY_PUFF
    elements.append(("ellipsoid", (palm_mid, (3.35 * k, ((PALM_FRONT - PALM_BACK).length / 2 + 0.2) * k, 1.0 * k), F)))
    elements.append(("capsule", (PALM_FRONT - X * 2.1 - F * 0.35 - U * 0.25, PALM_FRONT + X * 2.5 - F * 0.95 - U * 0.25, 0.85 * k)))
    elements.append(("ball", (PALM_BACK + F * 1.3 - X * 1.9 - U * 0.35, 1.3 * k)))
    elements.append(("ball", (PALM_BACK + F * 1.0 + X * 1.8 - U * 0.3, 1.15 * k)))
    # A flat pad over the back of the hand hides the ridges the knuckle row and palm would show.
    elements.append(("ellipsoid", (PALM_BACK.lerp(PALM_FRONT, 0.62) + U * 0.35, (3.0 * k, 2.6 * k, 0.55 * k), F)))
    # The pad runs on toward the wrist and tapers, so the back of the hand falls to the wrist in one slope.
    for i in range(1, 5):
        t = i / 4
        centre = PALM_BACK.lerp(PALM_FRONT, 0.62 - 0.62 * t).lerp(WRIST, 0.6 * t) + U * (0.35 - 0.3 * t)
        elements.append(("ellipsoid", (centre, ((3.0 - 0.7 * t) * k, 1.6 * k, (0.55 - 0.1 * t) * k), F)))
    # A second, wider pad on the thumb side fills the crease between the back of the hand and the web.
    elements.append(("ellipsoid", (PALM_BACK.lerp(PALM_FRONT, 0.5) - X * 1.6 - U * 0.05, (1.6 * k, 2.8 * k, 0.42 * k), F)))
    # Wrist and forearm: closely spaced ovals, so the surface stays smooth instead of ribbed.
    arm_axis = (ELBOW - WRIST).normalized()
    # The hollow between the back of the hand and the wrist is filled, so the two meet in a soft rise
    # rather than a dip.
    for i, (side, size) in enumerate(((-0.7, 2.0), (0.5, 1.8))):
        centre = PALM_BACK.lerp(WRIST, 0.2 + 0.12 * i) + X * side + U * 0.3
        elements.append(("ellipsoid", (centre, (size * k, 1.9 * k, 0.8 * k), F)))
    # Many closely spaced ovals taper evenly from the back of the palm to the wrist, starting inside the
    # palm, so the hand narrows into the wrist without a groove where the two meet.
    start = PALM_BACK + F * 1.2
    for i in range(10):
        t = smoothstep(0.0, 1.0, i / 9)
        width = 3.1 - 0.85 * t
        elements.append(("ellipsoid", (start.lerp(WRIST, i / 9) - U * 0.05 * t, (width * k, 0.9, (1.0 - 0.02 * t) * k), F)))
    for i in range(1, 5):
        t = i / 28
        elements.append(("ellipsoid", (WRIST.lerp(ELBOW, t), ((2.25 + 0.6 * t) * k, 1.0, (1.25 + 0.55 * t) * k), arm_axis)))
    for name, (dx, back, bones, widths, contact) in FINGERS.items():
        radii = [v * FINGER_THICKNESS for v in widths]
        knuckle = PALM_FRONT - F * back + X * dx - U * 0.05
        lengths = [v * FINGER_LENGTH for v in bones]
        pts = finger_chain(knuckle, contact(radii[2]), lengths, (0, 0, -1))
        joints[name] = (pts, radii)
        finger_tube(elements, pts, (radii[0], radii[1], radii[2], radii[2] * 0.92))
    thumb_bones, thumb_widths, thumb_contact = THUMB
    radii = [v * FINGER_THICKNESS * 0.975 for v in thumb_widths]
    lengths = [v * THUMB_LENGTH for v in thumb_bones]
    pts = finger_chain(THUMB_BASE, thumb_contact(radii[2]), lengths, (1, 0.1, -0.55))
    # Every joint is held outside the shell, then the last segment turns in toward the mouse and
    # forward, so the thumb arcs around it rather than passing through it.
    pts = [clear_of_mouse(q - X * THUMB_OUT, rad) for q, rad in zip(pts, radii)]
    tip_dir = (pts[2] - pts[1]).normalized() + X * 0.5 + F * 0.45
    pts[2] = pts[1] + tip_dir.normalized() * (pts[2] - pts[1]).length
    joints["thumb"] = (pts, radii)
    # The thumb's first segment is mostly inside the hand: it is drawn as a thenar mass that blends into
    # the palm, and the thumb proper starts partway along it, so no ridge runs across the palm.
    root = pts[0].lerp(pts[1], 0.45)
    thenar = pts[0].lerp(root, 0.5) - U * 0.1
    elements.append(("ellipsoid", ((thenar + PALM_BACK.lerp(PALM_FRONT, 0.45) + X * 0.6) / 2,
                                   (1.1 * k, (root - pts[0]).length * 0.75, 0.88 * k), root - pts[0])))
    finger_tube(elements, [root, pts[1], pts[2]], (radii[0] * 1.05, radii[1], radii[2]), clear=True)
    # Fill the valley where the thumb's root meets the palm, so the two run together instead of meeting
    # in a fold that catches a shadow.
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        low = pts[0].lerp(root, 0.15 + 0.75 * t)
        high = PALM_BACK.lerp(PALM_FRONT, 0.25 + 0.45 * t) - X * 1.3 + U * 0.12
        elements.append(("ellipsoid", (low.lerp(high, 0.55), (1.45 * k, (high - low).length * 0.85, 1.15 * k), high - low)))
    # The web between thumb and index finger: a thin fold of skin from the thumb's first segment to the
    # index knuckle, lying in the plane of the back of the hand so it blends into that skin.
    index_pts = joints["index"][0]
    for t in (0.0, 0.5, 1.0):
        thumb_side = THUMB_BASE.lerp(pts[1], 0.3 + 0.2 * t)
        index_side = index_pts[0].lerp(index_pts[1], 0.05 + 0.12 * t)
        mid = thumb_side.lerp(index_side, 0.5)
        along = index_side - thumb_side
        along -= U * along.dot(U)
        elements.append(("ellipsoid", (mid, (0.44, along.length * 0.4, 0.27), along)))
    return elements, joints


def material(name: str, color: tuple[float, float, float], rough: float = 0.55,
             emit: float = 0.0, sss: float = 0.0) -> bpy.types.Material:
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    if sss:
        bsdf.inputs["Subsurface Weight"].default_value = sss
        bsdf.inputs["Subsurface Radius"].default_value = (0.6, 0.3, 0.2)
        bsdf.inputs["Subsurface Scale"].default_value = 0.08
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Strength"].default_value = emit
    return m


def shade_smooth(obj: bpy.types.Object) -> None:
    for poly in obj.data.polygons:
        poly.use_smooth = True


def look(obj: bpy.types.Object, target: Point) -> None:
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = (Vector(target) - obj.location).to_track_quat("-Z", "Y")


def smoothstep(e0: float, e1: float, x: float) -> float:
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def build_hand(elements: list[Element]) -> None:
    mb = bpy.data.metaballs.new("hand")
    mb.resolution = 0.12
    mb.render_resolution = 0.06 if FINAL else 0.1
    obj = bpy.data.objects.new("hand", mb)
    bpy.context.collection.objects.link(obj)
    for kind, data in elements:
        e = mb.elements.new()
        if kind == "ball":
            c, r = data
            e.type, e.co, e.radius = "BALL", c, r / K
        elif kind == "capsule":
            a, b, r = Vector(data[0]), Vector(data[1]), data[2]
            e.type, e.co, e.radius = "CAPSULE", (a + b) / 2, r / K
            e.size_x = (b - a).length / 2
            e.rotation = (b - a).to_track_quat("X", "Z")
        else:
            c, (sx, sy, sz), axis = data
            e.type, e.co, e.radius = "ELLIPSOID", c, 1 / K
            e.size_x, e.size_y, e.size_z = sx, sy, sz
            e.rotation = Vector(axis).to_track_quat("Y", "Z")
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    bpy.data.objects.remove(obj)
    hand = bpy.data.objects.new("hand_mesh", mesh)
    bpy.context.collection.objects.link(hand)
    shade_smooth(hand)
    # Metaball parts fuse with a fold where they meet, clearest around the thumb's root; relaxing the
    # whole surface evens those out without losing the shape.
    relax = hand.modifiers.new("relax", "SMOOTH")
    relax.factor, relax.iterations = 1.0, 60

    # The sleeve starts in a clean ring past the wrist, cut in the shader rather than along mesh faces.
    # It stands slightly proud of the skin, so the cuff reads as an edge. UVs unwrap the arm, u around
    # and v along from the cuff, for the knit pattern.
    cuff = CUFF
    axis = (ELBOW - cuff).normalized()
    e1 = (Vector((0, 0, 1)) - axis * axis.z).normalized()
    e2 = axis.cross(e1)
    for v in mesh.vertices:
        v.co = v.co + v.normal * 0.07 * smoothstep(-0.03, 0.03, (v.co - cuff).dot(axis))
    uv = mesh.uv_layers.new(name="sleeve")
    for loop in mesh.loops:
        p = mesh.vertices[loop.vertex_index].co - cuff
        along = p.dot(axis)
        d = p - axis * along
        uv.data[loop.index].uv = (math.atan2(d.dot(e2), d.dot(e1)) * 2.6, along)
    mesh.update()
    mesh.materials.append(hand_material())


# Forearm: "FPS Arm Rig" by Miles0707 (https://skfb.ly/o9Vty), licensed under CC BY 4.0. Only its right
# forearm is kept, rolled palm-down, scaled to the hand's wrist and cut at the cuff.
# models/fps-arm-rig/license.txt holds the credit.
FOREARM_MODEL = Path(__file__).resolve().parent / "models" / "fps-arm-rig" / "scene.gltf"
CUFF = WRIST - F * 1.6
WRIST_WIDTH = 5.2


def build_forearm() -> None:
    """Import the rigged arm, keep its right forearm, lay it from the elbow to the wrist, and cut it
    at the cuff so the sleeve starts where the hand's skin ends."""
    import bmesh
    from mathutils import Matrix
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(FOREARM_MODEL))
    new = [o for o in bpy.data.objects if o not in before]
    rig = next(o for o in new if o.type == "ARMATURE")
    body = next(o for o in new if o.type == "MESH" and any(m.type == "ARMATURE" for m in o.modifiers))
    bpy.context.view_layer.update()
    world_matrix = rig.matrix_world.copy()
    rig.parent = None
    rig.matrix_world = world_matrix
    for o in new:
        if o not in (rig, body):
            bpy.data.objects.remove(o)
    bpy.context.view_layer.update()

    def bone(prefix: str) -> bpy.types.PoseBone:
        return next(pb for pb in rig.pose.bones if pb.name.startswith(prefix))

    def head(pb: bpy.types.PoseBone) -> Vector:
        return rig.matrix_world @ pb.head

    # Keep the vertices that follow the right forearm bone.
    group = next(g.index for g in body.vertex_groups if g.name.startswith("Forearm.R"))
    bm = bmesh.new()
    bm.from_mesh(body.data)
    deform = bm.verts.layers.deform.active
    doomed = [v for v in bm.verts if not v[deform] or max(v[deform].items(), key=lambda kv: kv[1])[0] != group]
    bmesh.ops.delete(bm, geom=doomed, context="VERTS")
    bm.to_mesh(body.data)
    bm.free()

    # Scale so the forearm near the wrist is as wide as the hand's wrist.
    wrist0, elbow0 = head(bone("Hand.R")), head(bone("Forearm.R"))
    along = (wrist0 - elbow0).normalized()
    near = [body.matrix_world @ v.co for v in body.data.vertices
            if 0 < (wrist0 - body.matrix_world @ v.co).dot(along) < (wrist0 - elbow0).length * 0.15]
    width = max(q.x for q in near) - min(q.x for q in near)
    rig.matrix_world = Matrix.Scale(WRIST_WIDTH / width, 4) @ rig.matrix_world
    bpy.context.view_layer.update()

    def turn(pb: bpy.types.PoseBone, rotation: "Quaternion") -> None:
        bpy.context.view_layer.update()
        m = rig.matrix_world @ pb.matrix
        pivot = m.translation.copy()
        turned = Matrix.Translation(pivot) @ rotation.to_matrix().to_4x4() @ Matrix.Translation(-pivot) @ m
        pb.matrix = rig.matrix_world.inverted() @ turned
        bpy.context.view_layer.update()

    forearm = bone("Forearm.R")
    y = ((rig.matrix_world @ forearm.matrix).to_3x3() @ Vector((0, 1, 0))).normalized()
    turn(forearm, y.rotation_difference((WRIST - ELBOW).normalized()))
    y = ((rig.matrix_world @ forearm.matrix).to_3x3() @ Vector((0, 1, 0))).normalized()
    have = head(bone("Index 3.R")) - head(bone("Little 3.R"))
    have, want = have - y * have.dot(y), -X - y * (-X).dot(y)
    turn(forearm, have.normalized().rotation_difference(want.normalized()))
    rig.matrix_world = Matrix.Translation(WRIST - head(bone("Hand.R"))) @ rig.matrix_world
    bpy.context.view_layer.update()

    mesh = bpy.data.meshes.new_from_object(body.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    mesh.transform(body.matrix_world)
    bpy.data.objects.remove(body)
    bpy.data.objects.remove(rig)

    # Cut at the cuff, keeping the elbow side, and close both open ends.
    arm_axis = (ELBOW - WRIST).normalized()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=CUFF, plane_no=arm_axis,
                           clear_inner=True)
    bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)
    bm.to_mesh(mesh)
    bm.free()

    e1 = (Vector((0, 0, 1)) - arm_axis * arm_axis.z).normalized()
    e2 = arm_axis.cross(e1)
    while mesh.uv_layers:
        mesh.uv_layers.remove(mesh.uv_layers[0])
    mesh.materials.clear()
    uv = mesh.uv_layers.new(name="sleeve")
    for loop in mesh.loops:
        q = mesh.vertices[loop.vertex_index].co - CUFF
        along = q.dot(arm_axis)
        d = q - arm_axis * along
        uv.data[loop.index].uv = (math.atan2(d.dot(e2), d.dot(e1)) * 2.6, max(along, 0.001))
    mesh.update()
    obj = bpy.data.objects.new("forearm", mesh)
    bpy.context.collection.objects.link(obj)
    shade_smooth(obj)
    smooth = obj.modifiers.new("smooth", "SUBSURF")
    smooth.levels = smooth.render_levels = 1
    mesh.materials.append(hand_material())


def hand_material() -> bpy.types.Material:
    """Flat grey skin, and past the cuff a compression sleeve: matte black knit with a ribbed cuff and
    two accent bands near it."""
    skin, base = (0.2, 0.2, 0.205), (0.012, 0.013, 0.015)
    m = bpy.data.materials.new("hand")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Sheen Roughness"].default_value = 0.4
    uvn = nt.nodes.new("ShaderNodeUVMap")
    uvn.uv_map = "sleeve"
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uvn.outputs["UV"], sep.inputs["Vector"])

    def math_node(op: str, a: Any, b: Any = None) -> bpy.types.Node:
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                nt.links.new(x, n.inputs[i])
        return n.outputs["Value"]

    u, v = sep.outputs["X"], sep.outputs["Y"]
    color = (0.78, 0.2, 0.12)
    band1 = math_node("MULTIPLY", math_node("GREATER_THAN", v, 1.4), math_node("LESS_THAN", v, 1.85))
    band2 = math_node("MULTIPLY", math_node("GREATER_THAN", v, 2.15), math_node("LESS_THAN", v, 2.35))
    mark = math_node("MAXIMUM", band1, band2)
    sleeve = math_node("GREATER_THAN", v, 0.0)
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*base, 1)
    mix.inputs["B"].default_value = (*color, 1)
    nt.links.new(mark, mix.inputs["Factor"])
    cloth = nt.nodes.new("ShaderNodeMix")
    cloth.data_type = "RGBA"
    cloth.inputs["A"].default_value = (*skin, 1)
    nt.links.new(sleeve, cloth.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], cloth.inputs["B"])
    nt.links.new(cloth.outputs["Result"], bsdf.inputs["Base Color"])
    nt.links.new(math_node("ADD", 0.55, math_node("MULTIPLY", sleeve, 0.1)), bsdf.inputs["Roughness"])
    nt.links.new(math_node("MULTIPLY", sleeve, 0.1), bsdf.inputs["Sheen Weight"])
    # Ribbed cuff: fine rings over the first stretch of sleeve, and a fine knit along the rest.
    ribs = math_node("MULTIPLY", math_node("SINE", math_node("MULTIPLY", v, 60)),
                     math_node("LESS_THAN", v, 0.8))
    knit = math_node("MULTIPLY", math_node("SINE", math_node("MULTIPLY", u, 90)), sleeve)
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.2
    bump.inputs["Distance"].default_value = 0.01
    height = math_node("MULTIPLY", math_node("ADD", ribs, math_node("MULTIPLY", knit, 0.08)), sleeve)
    nt.links.new(height, bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


ARROWS: list[bpy.types.Object] = []


def arrow(tip: Point, direction: Point, length: float, mat: bpy.types.Material,
          radius: float = 0.12) -> Vector:
    """A slim arrow ending at tip; returns the tail point. Every arrow is kept in ARROWS, so a shot
    without forces can hide them all rather than rebuilding the scene without them."""
    d = Vector(direction).normalized()
    tip = Vector(tip)
    head_len, head_r = 0.7, radius * 3.0
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=length - head_len,
                                        location=tip - d * (head_len + (length - head_len) / 2))
    shaft = bpy.context.object
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=head_r, radius2=0, depth=head_len,
                                    location=tip - d * head_len / 2)
    cone = bpy.context.object
    for part in (shaft, cone):
        part.rotation_mode = "QUATERNION"
        part.rotation_quaternion = d.to_track_quat("Z", "Y")
        part.data.materials.append(mat)
        ARROWS.append(part)
    return tip - d * length


def build() -> dict[str, Vector]:
    bpy.ops.mesh.primitive_plane_add(size=120, location=(0, -6, -0.01))
    bpy.context.object.data.materials.append(material("pad", (0.085, 0.09, 0.1), 0.95))
    elements, joints = build_skeleton()
    if "--no-hand" not in argv:
        build_hand(elements)
        build_forearm()
    mp, mr = joints["middle"]
    anchors = {
        "fingers": (mp[1] + mp[2]) / 2 + Vector((0, 0, mr[1])),
        "wrist": WRIST + U * 1.3,
        "arm": WRIST.lerp(ELBOW, 0.35) + Vector((0, 0, 1.7)),
    }
    squeeze = material("squeeze", (0.1, 0.55, 0.88), 0.4, 0.8)
    press = material("press", (0.93, 0.42, 0.16), 0.4, 0.8)
    gap = 0.12
    tp, tr = joints["thumb"]
    rp, rr = joints["ring"]
    ip, ir = joints["index"]
    left_tip = tp[-1] - X * (tr[2] + gap)
    anchors["squeeze_left"] = arrow(left_tip, X, 3.0, squeeze)
    # The pair reads as one squeeze, so the right arrow meets the mouse's other flank on the same
    # line as the left one rather than chasing the ring finger's hidden tip.
    # Pulled back a little further than the left one: the fingers on that flank would otherwise
    # cover its head.
    anchors["squeeze_right"] = arrow(on_side(1, left_tip.y, left_tip.z, rr[2] + gap + 0.5), -X, 3.0, squeeze)
    # Nearly straight down and short, so the arrow does not lie across the other fingers.
    press_dir = Vector((0.2, 0.0, -0.98)).normalized()
    # Held back off the fingertip as well, so the head reads clear of the finger it points at.
    anchors["press"] = arrow(ip[-1] - press_dir * (ir[2] + gap + 1.5), press_dir, 2.2, press)
    return anchors


CAMS: dict[str, tuple[Point, Point, int]] = {
    "front": ((-13.5, 16.0, 16.0), (0.3, -2.6, 3.2), 42),
    "mouse": ((-7.5, 11.5, 9.0), (0.2, 0.6, 1.6), 50),
    "threequarter": ((-6.5, 20.5, 17.5), (0.2, -1.6, 2.9), 42),
    "side": ((-60, 0.0, 2.2), (0, 0.0, 2.0), 110),
    "top": ((0, 0, 60), (0, 0.01, 0), 110),
}


def camera(view: str) -> None:
    """Put the one camera at a named viewpoint. Shots differ by where it stands, so it is moved
    rather than rebuilt."""
    cam_loc, cam_target, lens = CAMS[view]
    cam = bpy.context.scene.camera
    if cam is None:
        bpy.ops.object.camera_add()
        cam = bpy.context.object
        bpy.context.scene.camera = cam
    cam.location = Vector(cam_loc)
    look(cam, cam_target)
    cam.data.lens = lens


def lights() -> None:
    world = bpy.data.worlds.new("world")
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.9, 0.9, 0.93, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35
    for loc, energy, size in (((-12, 10, 22), 9000, 12), ((16, -6, 14), 2600, 10), ((0, 18, 6), 1500, 8)):
        bpy.ops.object.light_add(type="AREA", location=loc)
        light = bpy.context.object
        light.data.energy, light.data.size = energy, size
        look(light, (0, -2, 3))


def setup_render() -> None:
    """Engine, device and image settings, which every shot in a run shares."""
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = (1600, 1000) if FINAL else (800, 500)
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type == "OPTIX"
    scene.cycles.device = "GPU"
    scene.cycles.samples = 256 if FINAL else 32
    scene.cycles.use_denoising = True
    scene.view_settings.view_transform = "AgX"


def shoot(shot: Shot, anchors: dict[str, Vector]) -> None:
    """One render, and the sidecar JSON giving its label anchors in image space."""
    from bpy_extras.object_utils import world_to_camera_view
    out_path, view, forces = shot
    for part in ARROWS:
        part.hide_render = not forces
    camera(view)
    scene = bpy.context.scene
    scene.render.filepath = str(Path(out_path).resolve())
    bpy.context.view_layer.update()
    seen = {name: p for name, p in anchors.items() if forces or name not in FORCE_ANCHORS}
    out: dict[str, list[float]] = {}
    for name, p in seen.items():
        c = world_to_camera_view(scene, scene.camera, Vector(p))
        out[name] = [round(c.x, 4), round(1 - c.y, 4)]
    Path(out_path).with_suffix(".json").write_text(json.dumps(out))
    bpy.ops.render.render(write_still=True)


scene_anchors = build()
lights()
setup_render()
for one in shots():
    shoot(one, scene_anchors)
