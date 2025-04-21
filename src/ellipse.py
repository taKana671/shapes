import array
import math

from panda3d.core import Vec3, Point3, Vec2

from .create_geometry import ProceduralGeometry


class Ellipse(ProceduralGeometry):
    """Creates a cylinder model.
       Args:
            major_axis (float): the longest diameter; must be more than zero
            minor_axis (float): the shortest diameter; must be more than zero
            thickness (floar): the radial offset of major and minor axes; must be 0 < thickness < minor_axis
            height (float): length of the cylinder
            segs_c (int): subdivisions of the mantle along a circular cross-section; mininum is 3
            segs_a (int): subdivisions of the mantle along the axis of rotation; minimum is 1
            segs_top_cap (int): radial subdivisions of the top cap; minimum = 0
            segs_bottom_cap (int): radial subdivisions of the bottom cap; minimum = 0
            ring_slice_deg (int): the angle of the pie slice removed from the ellipse, in degrees; must be from 0 to 360
            slice_caps_radial (int): subdivisions of both slice caps, along the radius; minimum = 0
            slice_caps_axial (int): subdivisions of both slice caps, along the axis of rotation; minimum=0
            invert (bool): whether or not the geometry should be rendered inside-out; default is False
    """

    def __init__(self, major_axis=2., minor_axis=1., thickness=0., height=1., segs_c=40, segs_a=2, segs_top_cap=3,
                 segs_bottom_cap=3, ring_slice_deg=0., slice_caps_radial=2, slice_caps_axial=2, invert=False):
        super().__init__()
        self.major_axis = major_axis
        self.minor_axis = minor_axis
        self.thickness = thickness
        self.height = height
        self.segs_c = segs_c
        self.segs_a = segs_a

        self.segs_tc = segs_top_cap
        self.segs_bc = segs_bottom_cap

        self.ring_slice_deg = ring_slice_deg
        self.segs_sc_r = slice_caps_radial
        self.segs_sc_a = slice_caps_axial
        self.invert = invert

    def create_cap_triangles(self, vdata_values, bottom=True):
        normal = Vec3(0, 0, 1) if self.invert else Vec3(0, 0, -1)
        segs_cap = self.segs_bc if bottom else self.segs_tc

        if not bottom:
            normal *= -1

        height = 0 if bottom else self.height
        direction = -1 if self.invert else 1

        rj = self.major_axis / segs_cap
        rn = self.minor_axis / segs_cap
        vertex_cnt = 0

        # cap center and triangle vertices
        for i in range(self.segs_c + 1):
            if i == 0:
                vertex = Point3(0, 0, height)
                uv = Vec2(0.5, 0.5)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

            angle = self.delta_rad * i + (0 if self.invert else self.slice_rad)

            c = math.cos(angle)
            s = math.sin(angle) * direction
            vertex = Point3(rj * c, rn * s, height)

            u = 0.5 + c * 0.5 / segs_cap
            _direction = -direction if bottom else direction
            v = 0.5 + s * 0.5 * _direction / segs_cap

            vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])
            vertex_cnt += 1

        return vertex_cnt

    def create_cap_quad_vertices(self, vdata_values, bottom=True):
        normal = Vec3(0, 0, 1) if self.invert else Vec3(0, 0, -1)
        segs_cap = self.segs_bc if bottom else self.segs_tc

        if not bottom:
            normal *= -1

        height = 0 if bottom else self.height
        direction = -1 if self.invert else 1
        n = 0 if self.has_inner else 1
        vertex_cnt = 0

        # cap quad vertices
        for i in range(n, segs_cap + 1 - n):
            rj = self.inner_major + self.major_thickness * (i + n) / segs_cap
            rn = self.inner_minor + self.minor_thickness * (i + n) / segs_cap

            for j in range(self.segs_c + 1):
                angle = self.delta_rad * j + (0 if self.invert else self.slice_rad)
                c = math.cos(angle)
                s = math.sin(angle) * direction
                vertex = Point3(rj * c, rn * s, height)

                u = 0.5 + c * 0.5 * (rj / self.major_axis)
                _direction = -direction if bottom else direction
                v = 0.5 + s * 0.5 * _direction * (rn / self.minor_axis)

                vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])
                vertex_cnt += 1

        return vertex_cnt

    def create_bottom_cap_triangles(self, vdata_values, prim_indices):
        vertex_cnt = 0

        if not self.has_inner:
            # bottom cap center and triangle vertices
            vertex_cnt += self.create_cap_triangles(vdata_values)

            # the vertex order of the bottom cap triangles
            for i in range(1, self.segs_c + 1):
                prim_indices.extend((0, i + 1, i))

        return vertex_cnt

    def create_bottom_cap_quads(self, vdata_values, prim_indices):
        # bottom cap quad vertices
        vertex_cnt = self.create_cap_quad_vertices(vdata_values)

        # the vertex order of the bottom cap quads
        index_offset = (self.segs_c + 1) if self.has_inner else 1
        n = 0 if self.has_inner else 1

        for i in range(n, self.segs_bc):
            for j in range(self.segs_c):
                vi1 = index_offset + i * (self.segs_c + 1) + j
                vi2 = vi1 - self.segs_c - 1
                vi3 = vi2 + 1
                vi4 = vi1 + 1
                prim_indices.extend([*(vi1, vi2, vi3), *(vi1, vi3, vi4)])

        return vertex_cnt

    def create_mantle_quads(self, index_offset, vdata_values, prim_indices):
        direction = -1 if self.invert else 1
        vertex_cnt = 0

        # mantle quad vertices
        for i in range(self.segs_a + 1):
            z = self.height * i / self.segs_a
            v = i / self.segs_a

            for j in range(self.segs_c + 1):
                angle = self.delta_rad * j + (0 if self.invert else self.slice_rad)
                x = self.major_axis * math.cos(angle)
                y = self.minor_axis * math.sin(angle) * direction
                vertex = Point3(x, y, z)

                normal = Vec3(x, y, 0.0).normalized() * direction
                u = j / self.segs_c
                uv = Vec2(u, v)

                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

        # the vertex order of the mantle quads
        n = self.segs_c + 1

        for i in range(1, self.segs_a + 1):
            for j in range(self.segs_c):
                vi1 = index_offset + i * n + j
                vi2 = vi1 - n
                vi3 = vi2 + 1
                vi4 = vi1 + 1

                prim_indices.extend((vi1, vi2, vi4) if self.invert else (vi1, vi2, vi3))
                prim_indices.extend((vi2, vi3, vi4) if self.invert else (vi1, vi3, vi4))

        return vertex_cnt

    def create_top_cap_triangles(self, index_offset, vdata_values, prim_indices):
        vertex_cnt = 0

        if not self.has_inner:
            # top cap center and triangle vertices
            vertex_cnt += self.create_cap_triangles(vdata_values, bottom=False)

            # the vertex order of the top cap triangles
            for i in range(index_offset + 1, index_offset + self.segs_c + 1):
                prim_indices.extend((index_offset, i, i + 1))

        return vertex_cnt

    def create_top_cap_quads(self, index_offset, vdata_values, prim_indices):
        # the top cap quad vertices
        vertex_cnt = self.create_cap_quad_vertices(vdata_values, bottom=False)

        # the vertex order of the top cap quads
        index_offset += (self.segs_c + 1) if self.has_inner else 1
        n = 0 if self.has_inner else 1

        for i in range(n, self.segs_tc):
            for j in range(self.segs_c):
                vi1 = index_offset + i * (self.segs_c + 1) + j
                vi2 = vi1 - self.segs_c - 1
                vi3 = vi2 + 1
                vi4 = vi1 + 1

                prim_indices.extend([*(vi1, vi3, vi2), *(vi1, vi4, vi3)])

        return vertex_cnt

    def create_slice_cap_quads(self, index_offset, vdata_values, prim_indices):
        vertex_cnt = 0
        direction = -1 if self.invert else 1

        # the vertices of the slice cap quad
        for is_start in [True, False]:
            if is_start:
                normal = Vec3(0, direction, 0)
            else:
                angle = self.delta_rad * self.segs_c
                c = math.cos(angle)
                s = -math.sin(angle)
                normal = Vec3(s, -c, 0) * direction

            for i in range(self.segs_sc_a + 1):
                z = self.height * i / self.segs_sc_a
                v = i / self.segs_sc_a

                for j in range(self.segs_sc_r + 1):
                    rj = self.inner_major + (self.major_axis - self.inner_major) * j / self.segs_sc_r
                    rn = self.inner_minor + (self.minor_axis - self.inner_minor) * j / self.segs_sc_r
                    vertex = Point3(rj, 0, z) if is_start else Point3(rj * c, rn * s, z)
                    coef = 0.5 if is_start else -0.5
                    u = 0.5 + coef * rj / self.major_axis * direction * -1
                    uv = Vec2(u, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

            # the vertex order of the slice cap quads
            for i in range(self.segs_sc_a):
                for j in range(self.segs_sc_r):
                    vi1 = index_offset + j
                    vi2 = vi1 + self.segs_sc_r + 1
                    vi3 = vi1 + 1
                    vi4 = vi2 + 1

                    if is_start:
                        prim_indices.extend((vi1, vi3, vi2) if self.invert else (vi1, vi2, vi3))
                        prim_indices.extend((vi2, vi3, vi4) if self.invert else (vi2, vi4, vi3))
                    else:
                        prim_indices.extend((vi1, vi2, vi3) if self.invert else (vi1, vi3, vi2))
                        prim_indices.extend((vi2, vi4, vi3) if self.invert else (vi2, vi3, vi4))

                index_offset += self.segs_sc_r + 1
            index_offset += self.segs_sc_r + 1

        return vertex_cnt

    def define_variables(self):
        self.major_thickness = self.thickness if 0 < self.thickness < self.major_axis else self.major_axis
        self.minor_thickness = self.thickness if 0 < self.thickness < self.minor_axis else self.minor_axis

        self.inner_major = self.major_axis - self.major_thickness
        self.inner_minor = self.minor_axis - self.minor_thickness
        self.has_inner = True if self.inner_major and self.inner_minor else False

        self.slice_rad = math.pi * self.ring_slice_deg / 180
        self.delta_rad = math.pi * ((360 - self.ring_slice_deg) / 180) / self.segs_c

    def get_geom_node(self):
        self.define_variables()

        # Create an outer cylinder.
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        if self.segs_bc:
            vertex_cnt += self.create_bottom_cap_triangles(vdata_values, prim_indices)
            vertex_cnt += self.create_bottom_cap_quads(vdata_values, prim_indices)

        vertex_cnt += self.create_mantle_quads(vertex_cnt, vdata_values, prim_indices)

        if self.segs_tc:
            sub_total = vertex_cnt
            vertex_cnt += self.create_top_cap_triangles(sub_total, vdata_values, prim_indices)
            vertex_cnt += self.create_top_cap_quads(sub_total, vdata_values, prim_indices)

        if self.ring_slice_deg and self.segs_sc_r and self.segs_sc_a:
            vertex_cnt += self.create_slice_cap_quads(vertex_cnt, vdata_values, prim_indices)

        # Create an inner ellipse to connect it to the outer one.
        if self.has_inner:
            major_axis = self.major_axis - self.thickness
            minor_axis = self.minor_axis - self.thickness

            maker = Ellipse(major_axis, minor_axis, 0, self.height, self.segs_c, self.segs_a,
                            0, 0, self.ring_slice_deg, 0, 0, not self.invert)

            geom_node = maker.get_geom_node()
            self.add(geom_node, vdata_values, vertex_cnt, prim_indices)
            return geom_node

        # Create the geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'cylinder')
        return geom_node
