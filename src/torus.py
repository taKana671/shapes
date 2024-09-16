import array
import math

from panda3d.core import Vec3, Point3, Vec2, Quat

from .create_geometry import ProceduralGeometry


class Torus(ProceduralGeometry):

    """Create a Torus model.
       Args:
            segs_r (int): the number of segments of the ring
            segs_s (int): the number of segments of the cross-sections
            ring_radius (float): the radius of the ring; cannot be negative;
            section_radius (float): the radius of the cross-sections perpendicular to the ring; cannot be negative;
            section_inner_radius (float): the radius of the inner torus cross-sections
            ring_slice_deg (float): the angle of the ring pie slice removed from the torus, in degrees
            section_slice_deg (float): the angle of the section pie slice removed from the torus, in degrees
            section_slice_start_cap (int): radial subdivisions of the cap at the start of the section slice; 0 (no cap)
            section_slice_end_cap (int): radial subdivisions of the cap at the end of the section slice; 0 (no cap)
            ring_slice_start_cap (int): radial subdivisions of the cap at the start of the ring slice; 0 (no cap)
            ring_slice_end_cap (int): radial subdivisions of the cap at the end of the ring slice; 0 (no cap)
            invert (bool): whether or not the geometry should be rendered inside-out; default is False
    """

    def __init__(self, segs_r=40, segs_s=20, ring_radius=1., section_radius=.5, section_inner_radius=0.,
                 ring_slice_deg=0, section_slice_deg=0, section_slice_start_cap=2,
                 section_slice_end_cap=2, ring_slice_start_cap=2, ring_slice_end_cap=2, invert=False):
        super().__init__()
        self.segs_r = segs_r
        self.segs_s = segs_s
        self.ring_radius = ring_radius
        self.section_radius = section_radius
        self.section_inner_radius = section_inner_radius

        self.ring_slice_deg = ring_slice_deg
        self.section_slice_deg = section_slice_deg

        self.invert = invert
        self.color = (1, 1, 1, 1)

        self.sssc = section_slice_start_cap
        self.ssec = section_slice_end_cap

        self.rssp = ring_slice_start_cap
        self.rsec = ring_slice_end_cap

    def create_mantle(self, vdata_values, prim_indices, outer=True):
        invert = self.invert
        section_radius = self.section_radius

        if not outer:
            invert = not self.invert
            section_radius = self.section_inner_radius

        n = 0 if invert else self.ring_slice_rad
        direction = -1 if invert else 1
        vertex_cnt = 0

        # mantle quad vertices
        for i in range(self.segs_r + 1):
            angle_h = self.delta_angle_h * i + n
            c = math.cos(angle_h)
            s = math.sin(angle_h) * direction
            u = i / self.segs_r

            for j in range(self.segs_s + 1):
                angle_v = self.delta_angle_v * j + self.section_slice_rad
                r = self.ring_radius - section_radius * math.cos(angle_v)
                x = r * c
                y = r * s
                z = section_radius * math.sin(angle_v)
                nx = x - self.ring_radius * c
                ny = y - self.ring_radius * s

                vertex = Point3(x, y, z)
                normal = Vec3(nx, ny, z).normalized() * direction
                v = 1.0 - j / self.segs_s

                vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])
                vertex_cnt += 1

        # the vertex order of the mantle quads
        n = self.segs_s + 1

        for i in range(1, self.segs_r + 1):
            for j in range(self.segs_s):
                vi1 = i * n + j
                vi2 = vi1 - n
                vi3 = vi2 + 1
                vi4 = vi1 + 1
                prim_indices.extend((vi1, vi2, vi4) if invert else (vi1, vi2, vi3))
                prim_indices.extend((vi2, vi3, vi4) if invert else (vi1, vi3, vi4))

        return vertex_cnt

    def create_ring_cap(self, index_offset, vdata_values, prim_indices):
        direction = -1. if self.invert else 1.
        vertex_cnt = 0

        for is_start in [True, False]:
            if not (segs_sc := self.rssp if is_start else self.rsec):
                continue

            offset = index_offset + vertex_cnt

            if is_start:
                normal = Vec3(0, direction, 0)
            else:
                angle_h = self.delta_angle_h * self.segs_r
                c_h = math.cos(angle_h)
                s_h = -math.sin(angle_h)
                normal = Vec3(s_h, -c_h, 0) * direction

            if not self.thickness:
                # the ring cap triangle vertices
                if is_start:
                    vertex = Point3(self.ring_radius, 0, 0)
                else:
                    vertex = Point3(self.ring_radius * c_h, self.ring_radius * s_h, 0)

                uv = Vec2(0.5, 0.5)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

                radius = self.section_radius / segs_sc

                for i in range(self.segs_s + 1):
                    angle_v = self.delta_angle_v * i + self.section_slice_rad
                    c = math.cos(angle_v)
                    s = math.sin(angle_v)
                    _r = radius * c
                    r = self.ring_radius - _r
                    z = radius * s

                    vertex = Point3(r, 0.0, z) if is_start else Point3(r * c_h, r * s_h, z)
                    coef = .5 if is_start else -.5
                    u = 0.5 + coef * _r / self.section_radius * direction
                    v = 0.5 + 0.5 * s / segs_sc
                    uv = Vec2(u, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # the vertex order of the ring cap triangles
                for i in range(offset + 1, offset + 1 + self.segs_s):
                    if is_start:
                        prim_indices.extend((offset, i + 1, i) if self.invert else (offset, i, i + 1))
                    else:
                        prim_indices.extend((offset, i, i + 1) if self.invert else (offset, i + 1, i))

            # the ring cap quad vertices
            offset += (self.segs_s + 1 if self.thickness else 1)
            n = 0 if self.thickness else 1

            for i in range(n, segs_sc + 1 - n):
                radius = self.section_inner_radius + self.thickness * (i + n) / segs_sc

                for j in range(self.segs_s + 1):
                    angle_v = self.delta_angle_v * j + self.section_slice_rad
                    _r = radius * math.cos(angle_v)
                    r = self.ring_radius - _r
                    z = radius * math.sin(angle_v)

                    vertex = Point3(r, 0., z) if is_start else Point3(r * c_h, r * s_h, z)
                    coef = .5 if is_start else -.5
                    u = .5 + coef * _r / self.section_radius * direction
                    v = .5 + .5 * z / self.section_radius
                    uv = Vec2(u, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

            # the vertex order of the ring cap quads
            n = 0 if self.thickness else 1

            for i in range(n, segs_sc):
                for j in range(self.segs_s):
                    vi1 = offset + i * (self.segs_s + 1) + j
                    vi2 = vi1 - self.segs_s - 1
                    vi3 = vi2 + 1
                    vi4 = vi1 + 1
                    if self.invert:
                        prim_indices.extend((vi1, vi2, vi3) if is_start else (vi1, vi3, vi2))
                        prim_indices.extend((vi1, vi3, vi4) if is_start else (vi1, vi4, vi3))
                    else:
                        prim_indices.extend((vi1, vi3, vi2) if is_start else (vi1, vi2, vi3))
                        prim_indices.extend((vi1, vi4, vi3) if is_start else (vi1, vi3, vi4))

        return vertex_cnt

    def create_section_cap(self, index_offset, vdata_values, prim_indices):
        vertex_cnt = 0
        direction = -1 if self.invert else 1

        cap_normal = Vec3.down() if self.invert else Vec3.up()
        x = self.delta_angle_h * self.ring_radius * direction
        angle = math.atan2(0, x)
        quat = Quat()
        quat.set_from_axis_angle_rad(angle, Vec3.right())
        cap_normal = quat.xform(cap_normal)

        for is_start in [True, False]:
            if not (segs_sc := self.sssc if is_start else self.ssec):
                continue

            offset = index_offset + vertex_cnt
            seg = 0 if is_start else self.segs_s

            for i in range(self.segs_r + 1):
                angle_h = self.delta_angle_h * i + (0. if self.invert else self.ring_slice_rad)
                c = math.cos(angle_h)
                s = math.sin(angle_h) * direction

                quat_h = Quat()
                axis = Vec3.down() if self.invert else Vec3.up()
                quat_h.set_from_axis_angle_rad(angle_h, axis)

                angle_v = self.delta_angle_v * seg + self.section_slice_rad
                r = self.ring_radius - self.section_radius * math.cos(angle_v)
                x = r * c
                y = r * s
                z = self.section_radius * math.sin(angle_v)
                p1 = Point3(x, y, z)

                quat_v = Quat()
                quat_v.set_from_axis_angle_rad(angle_v, Vec3.forward())
                n_vec = (quat_v * quat_h).xform(cap_normal)

                x = self.ring_radius * c
                y = self.ring_radius * s
                p2 = Point3(x, y, 0)

                v = self.thickness if self.thickness else self.section_inner_radius
                r_vec = (p2 - p1).normalized() * v
                normal = n_vec * (-direction if seg == 0 else direction)
                u = i / self.segs_r

                for j in range(segs_sc + 1):
                    vertex = p1 + r_vec * j / segs_sc
                    v = .5 * r_vec.length() / self.section_radius * j / segs_sc
                    if not is_start:
                        v = 1.0 - v

                    vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])
                    vertex_cnt += 1

            for i in range(self.segs_r):
                for j in range(segs_sc):
                    vi1 = offset + j
                    vi2 = vi1 + segs_sc + 1
                    vi3 = vi2 + 1
                    vi4 = vi1 + 1
                    prim_indices.extend((vi1, vi2, vi3) if is_start else (vi1, vi3, vi2))
                    prim_indices.extend((vi1, vi3, vi4) if is_start else (vi1, vi4, vi3))
                offset += segs_sc + 1

        return vertex_cnt

    def get_geom_node(self):
        self.ring_slice_rad = math.pi * self.ring_slice_deg / 180
        self.section_slice_rad = math.pi * self.section_slice_deg / 180
        self.delta_angle_h = math.pi * ((360 - self.ring_slice_deg) / 180) / self.segs_r
        self.delta_angle_v = math.pi * ((360 - self.section_slice_deg) / 180) / self.segs_s
        self.thickness = self.section_radius - self.section_inner_radius

        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        # Create an outer torus.
        vertex_cnt += self.create_mantle(vdata_values, prim_indices, self.invert)

        if self.ring_slice_deg:
            vertex_cnt += self.create_ring_cap(vertex_cnt, vdata_values, prim_indices)

        if self.section_slice_deg:
            vertex_cnt += self.create_section_cap(vertex_cnt, vdata_values, prim_indices)

        # Create the outer torus geom.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'torus')

        # Create an inner torus mantle.
        if self.thickness > 0:
            vdata_values = array.array('f', [])
            prim_indices = array.array('H', [])
            vertex_cnt = self.create_mantle(vdata_values, prim_indices, not self.invert)

            # Connect the inner torus mantle to the outer torus.
            self.add(geom_node, vdata_values, vertex_cnt, prim_indices)

        return geom_node