import array
import math

from panda3d.core import Vec3, Point3, Vec2, Quat

from .create_geometry import ProceduralGeometry


class Torus(ProceduralGeometry):

    """Create a geom node of torus, spiral, half ring and so on.
       Args:
            segs_rcnt (int): the number of segments
            segs_r (int): the number of segments of the ring
            segs_s (int): the number of segments of the cross-sections
            ring_radius (float): the radius of the ring; cannot be negative;
            section_radius (float): the radius of the cross-sections perpendicular to the ring; cannot be negative;
            slope (float): the increase of the cross-sections hight
    """

    def __init__(self, segs_rcnt=24, segs_r=24, segs_s=12, ring_radius=1.2, section_radius=0.5, slope=0):
        super().__init__()
        self.segs_rcnt = segs_rcnt
        self.segs_r = segs_r
        self.segs_s = segs_s
        self.ring_radius = ring_radius
        self.section_radius = section_radius
        self.slope = slope

        # ****************************
        self.ring_slice = 60   # deg
        self.section_slice = 180  # deg

        self.ring_slice_rad = math.pi * self.ring_slice / 180
        self.section_slice_rad = math.pi * self.section_slice / 180

        self.delta_angle_h = math.pi * ((360 - self.ring_slice) / 180) / self.segs_r
        self.delta_angle_v = math.pi * ((360 - self.section_slice) / 180) / self.segs_s
        self.inverted = False

        self.section_slice_start_cap = 2
        self.section_slice_end_cap = 2
        self.thickness = 0.2
        self.inner_radius = self.section_radius - self.thickness

        self.ring_slice_start_cap = 2
        self.ring_slice_end_cap = 2

    def create_mantle(self, vdata_values, prim_indices):
        n = 0 if self.inverted else self.ring_slice_rad
        direction = -1 if self.inverted else 1
        vertex_cnt = 0

        for i in range(self.segs_r + 1):
            angle_h = self.delta_angle_h * i + n
            c = math.cos(angle_h)
            s = math.sin(angle_h) * direction
            u = u_sc = i / self.segs_r

            for j in range(self.segs_s + 1):
                angle_v = self.delta_angle_v * j + self.section_slice_rad
                r = self.ring_radius - self.section_radius * math.cos(angle_v)
                x = r * c
                y = r * s
                z = self.section_radius * math.sin(angle_v)
                nx = x - self.ring_radius * c
                ny = y - self.ring_radius * s

                normal = Vec3(nx, ny, z).normalized() * direction
                v = 1.0 - j / self.segs_s

                vdata_values.extend((x, y, z))
                vdata_values.extend((1, 1, 1, 1))
                vdata_values.extend(normal)
                vdata_values.extend((u, v))
                vertex_cnt += 1

        n = self.segs_s + 1

        for i in range(1, self.segs_r + 1):
            for j in range(self.segs_s):
                vi1 = i * n + j
                vi2 = vi1 - n
                vi3 = vi2 + 1
                vi4 = vi1 + 1
                prim_indices.extend((vi1, vi2, vi4) if self.inverted else (vi1, vi2, vi3))
                prim_indices.extend((vi1, vi3, vi4) if self.inverted else (vi1, vi3, vi4))

        return vertex_cnt


    # def create_slice_cap(self, index_offset, vdata_values, prim_indices):
    #     vertex_cnt = 0


    def create_slice_cap_triangles(self, index_offset, vdata_values, prim_indices):
        direction = -1. if self.inverted else 1.
        vertex_cnt = 0
        current_cnt = index_offset

        for is_start in [True, False]:
            segs_sc = self.ring_slice_start_cap if is_start else self.ring_slice_end_cap
            index_offset = current_cnt + vertex_cnt

            if is_start:
                normal = Vec3(0, direction, 0)
            else:
                angle_h = self.delta_angle_h * self.segs_r
                c_h = math.cos(angle_h)
                s_h = -math.sin(angle_h)
                normal = Vec3(s_h, -c_h, 0) * direction

            if not self.inner_radius:
                # Define the ring slice cap triangle vertices
                if is_start:
                    pos = Point3(self.ring_radius, 0, 0)
                else:
                    pos = Point3(self.ring_radius * c_h, self.ring_radius * s_h, 0)

                u = v = 0.5

                vdata_values.extend(pos)
                vdata_values.extend((1, 1, 1, 1))
                vdata_values.extend(normal)
                vdata_values.extend((u, v))
                vertex_cnt += 1

                radius = self.section_radius / segs_sc

                for i in range(self.segs_s + 1):
                    # angle_v = self.delta_angle_v * i + self.ring_slice_rad
                    angle_v = self.delta_angle_v * i + self.section_slice_rad
                    c = math.cos(angle_v)
                    s = math.sin(angle_v)
                    _r = radius * c
                    r = self.ring_radius - _r
                    z = radius * s

                    pos = Point3(r, 0.0, z) if is_start else Point3(r * c_h, r * s_h, z)
                    if is_start:
                        u = 0.5 + 0.5 * _r / self.section_radius * direction
                    else:
                        u = 0.5 - 0.5 * _r / self.section_radius * direction
                    v = 0.5 + 0.5 * s / segs_sc

                    vdata_values.extend(pos)
                    vdata_values.extend((1, 1, 1, 1))
                    vdata_values.extend(normal)
                    vdata_values.extend((u, v))
                    vertex_cnt += 1
                
                # Define the vertex order of the ring slice cap triangles
                for i in range(index_offset + 1, index_offset + 1 + self.segs_s):
                    if is_start:
                        prim_indices.extend((index_offset, i + 1, i) if self.inverted else (index_offset, i, i + 1))
                    else:
                        prim_indices.extend((index_offset, i, i + 1) if self.inverted else (index_offset, i + 1, i))

                # index_offset += 1  # **************** 

            index_offset += (self.segs_s + 1 if self.inner_radius else 1)
            n = 0 if self.inner_radius else 1
            sub_cnt = 0

            for i in range(n, segs_sc + 1 - n):
                radius = self.inner_radius + self.thickness * (i + n) / segs_sc

                for j in range(self.segs_s + 1):
                    angle_v = self.delta_angle_v * j + self.section_slice_rad
                    c = math.cos(angle_v)
                    s = math.sin(angle_v)
                    _r = radius * c
                    r = self.ring_radius - _r
                    z = radius * s

                    pos = (r, 0., z) if is_start else (r * c_h, r * s_h, z)
                    coef = .5 if is_start else -.5
                    u = .5 + coef * _r / self.section_radius * direction
                    v = .5 + .5 * z / self.section_radius
                    # print(pos)
                    vdata_values.extend(pos)
                    vdata_values.extend((1, 1, 1, 1))
                    vdata_values.extend(normal)
                    vdata_values.extend((u, v))
                    vertex_cnt += 1

                    sub_cnt += 1   # **********************

            n = 0 if self.inner_radius else 1

            for i in range(n, segs_sc):
                for j in range(self.segs_s):
                    vi1 = index_offset + i * (self.segs_s + 1) + j
                    vi2 = vi1 - self.segs_s - 1
                    vi3 = vi2 + 1
                    vi4 = vi1 + 1
                    if self.inverted:
                        prim_indices.extend((vi1, vi2, vi3) if is_start else (vi1, vi3, vi2))
                        prim_indices.extend((vi1, vi3, vi4) if is_start else (vi1, vi4, vi3))
                    else:
                        prim_indices.extend((vi1, vi3, vi2) if is_start else (vi1, vi2, vi3))
                        prim_indices.extend((vi1, vi4, vi3) if is_start else (vi1, vi3, vi4))

            index_offset += sub_cnt

        return vertex_cnt

    def create_section_cap(self, index_offset, vdata_values, prim_indices):
        vertex_cnt = 0
        current_cnt = index_offset
        direction = -1 if self.inverted else 1

        cap_normal = Vec3.down() if self.inverted else Vec3.up()
        x = self.delta_angle_h * self.ring_radius * direction
        # y = self.section_radius
        y = 0
        angle = math.atan2(y, x)
        quat = Quat()
        quat.set_from_axis_angle_rad(angle, Vec3.right())
        cap_normal = quat.xform(cap_normal)

        for is_start in [True, False]:
            segs_sc = self.section_slice_start_cap if is_start else self.section_slice_end_cap
            index_offset = current_cnt + vertex_cnt

            for i in range(self.segs_r + 1):
                angle_h = self.delta_angle_h * i + (0. if self.inverted else self.ring_slice_rad)
                c = math.cos(angle_h)
                s = math.sin(angle_h) * direction
                u_sc = i / self.segs_r

                quat_h = Quat()
                axis = Vec3.down() if self.inverted else Vec3.up()
                quat_h.set_from_axis_angle_rad(angle_h, axis)

                # for j in range(segs_s + 1):
                # for j in (0, self.segs_s):
                j = 0 if is_start else self.segs_s

                angle_v = self.delta_angle_v * j + self.section_slice_rad
                r = self.ring_radius - self.section_radius * math.cos(angle_v)
                x = r * c
                y = r * s
                z = self.section_radius * math.sin(angle_v)

                quat_v = Quat()
                quat_v.set_from_axis_angle_rad(angle_v, Vec3.forward())
                n_vec = (quat_v * quat_h).xform(cap_normal)
                p1 = Point3(x, y, z)
                x = self.ring_radius * c
                y = self.ring_radius * s
                p2 = Point3(x, y, 0)
                r_vec = (p2 - p1).normalized() * self.thickness
                normal = n_vec * (-direction if j == 0 else direction)

                for k in range(segs_sc + 1):
                    pos = p1 + r_vec * k / segs_sc
                    v = .5 * r_vec.length() / self.section_radius * k / segs_sc
                    if not is_start:
                        v = 1.0 - v

                    vdata_values.extend(pos)
                    vdata_values.extend((1, 1, 1, 1))
                    vdata_values.extend(normal)
                    vdata_values.extend((u_sc, v))
                    vertex_cnt += 1

            for i in range(self.segs_r):
                for j in range(segs_sc):
                    vi1 = index_offset + j
                    vi2 = vi1 + segs_sc + 1
                    vi3 = vi2 + 1
                    vi4 = vi1 + 1
                    prim_indices.extend((vi1, vi2, vi3) if is_start else (vi1, vi3, vi2))
                    prim_indices.extend((vi1, vi3, vi4) if is_start else (vi1, vi4, vi3))
                index_offset += segs_sc + 1

        return vertex_cnt
                       


            # index_offset = current_cnt + vertex_cnt


            # self.__add_cap_data(segs_sssc, p1, r_vec, points, uvs, has_uvs,
            #                                 u_sc, False, tex_size_sssc, section_radius,
            #                                 ring_arc, section_arc, mat_sssc)




    def get_geom_node(self):
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        vertex_cnt += self.create_mantle(vdata_values, prim_indices)

        if self.ring_slice and self.thickness:
            vertex_cnt += self.create_slice_cap_triangles(vertex_cnt, vdata_values, prim_indices)

        if self.section_slice and self.thickness:
            vertex_cnt += self.create_section_cap(vertex_cnt, vdata_values, prim_indices)

        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'torus')

        # if self.inner_radius > 0:
        #     self.section_radius = self.inner_radius
        #     self.thickness = self.inner_radius

        #     vdata_values = array.array('f', [])
        #     prim_indices = array.array('H', [])
        #     vertex_cnt = self.create_mantle(vdata_values, prim_indices)

        #     self.add(geom_node, vdata_values, vertex_cnt, prim_indices, len(prim_indices))

        return geom_node






    def get_geom_node_2(self):
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])

        delta_angle_h = 2.0 * math.pi / self.segs_r
        delta_angle_v = 2.0 * math.pi / self.segs_s

        for i in range(self.segs_rcnt + 1):
            angle_h = delta_angle_h * i
            u = i / self.segs_rcnt

            for j in range(self.segs_s + 1):
                angle_v = delta_angle_v * j
                r = self.ring_radius - self.section_radius * math.cos(angle_v)
                c = math.cos(angle_h)
                s = math.sin(angle_h)

                x = r * c
                y = r * s
                z = self.section_radius * math.sin(angle_v) + self.slope * i

                nx = x - self.ring_radius * c
                ny = y - self.ring_radius * s
                normal_vec = Vec3(nx, ny, z).normalized()
                v = 1.0 - j / self.segs_s
                vdata_values.extend((x, y, z))
                vdata_values.extend((1, 1, 1, 1))
                vdata_values.extend(normal_vec)
                vdata_values.extend((u, v))

        for i in range(self.segs_rcnt):
            for j in range(0, self.segs_s):
                idx = j + i * (self.segs_s + 1)
                prim_indices.extend([idx, idx + 1, idx + self.segs_s + 1])
                prim_indices.extend([idx + self.segs_s + 1, idx + 1, idx + 1 + self.segs_s + 1])

        vertex_cnt = (self.segs_rcnt + 1) * (self.segs_s + 1)

        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'torus')

        return geom_node