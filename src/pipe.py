import array
import math
from types import SimpleNamespace

from panda3d.core import Vec3, Point3, Vec2, Point2
from .create_geometry import ProceduralGeometry
from .cylinder import Cylinder
from .sphere import Sphere
from .capsule import CapsuleHemisphere
from .rounded_box import Sides, RoundedCornerBox
from .rounded_box import BoxEdgeCylinder



class RoundedEdgeBox(RoundedCornerBox):

    def __init__(self, corner_radius=0.5, width=2., depth=2., height=2., segs_w=4, segs_d=4, segs_z=4,
                 thickness=0., open_top=False, open_bottom=False, invert=False):
        super().__init__(
            corner_radius=corner_radius,
            width=width,
            depth=depth,
            height=height,
            segs_w=segs_w,
            segs_d=segs_d,
            segs_z=segs_z,
            thickness=thickness,
            open_top=open_top,
            open_bottom=open_bottom,
            invert=invert
        )
    

    # # needs height as one of parameters.
    def create_corner(self, vertex_cnt, vdata_values, prim_indices, height, center, start_angle, slice_deg):
        corner = BoxEdgeCylinder(
            center=center + self.center,
            start_angle_deg=start_angle,
            radius=self.c_radius,
            inner_radius=self.c_inner_radius,
            height=height,
            segs_c=20,
            segs_a=self.segs_z,
            segs_top_cap=self.c_segs_tc,
            segs_bottom_cap=self.c_segs_bc,
            ring_slice_deg=slice_deg,
            invert=self.invert
        )

        vertex_cnt = corner.create_cylinder(vertex_cnt, vdata_values, prim_indices)
        return vertex_cnt
    
    
    # # needs height as one of parameters.
    def create_rect(self, vertex_cnt, vdata_values, prim_indices, width, depth, height, center, open_sides):
        rect = RoundedCornerBox(
            width=width,
            depth=depth,
            height=height,
            segs_w=3,
            segs_d=3,
            segs_z=self.segs_z,
            thickness=self.thickness,
            # open_top=self.open_top,
            # open_bottom=self.open_bottom,
            corner_radius=0,
            rounded_f_left=False,
            rounded_f_right=False,
            rounded_b_left=False,
            rounded_b_right=False,
            invert=self.invert
        )

        for k, v in open_sides.items():
            rect.__dict__[k] = v

        rect.define_variables()
        rect.center = center + self.center
        vertex_cnt = rect.create_sides(vertex_cnt, vdata_values, prim_indices)
        return vertex_cnt

    def create_corner_sphere(self, vertex_cnt, vdata_values, prim_indices, center, start_angle, slice_deg,
                             bottom_clip=-1., top_clip=1.):

        corner = BoxCornerQuarteredHemisphere(
            center=center,
            start_angle_deg=start_angle,
            radius=self.c_radius,
            inner_radius=self.c_inner_radius,
            segs_h=20,
            segs_v=21,
            segs_slice_caps=0,
            slice_deg=slice_deg,
            bottom_clip=bottom_clip,
            top_clip=top_clip,
            invert=self.invert
        )

        vertex_cnt, offset = corner.create_bottom(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt += corner.create_mantle_quads(offset, vdata_values, prim_indices)
        vertex_cnt += corner.create_top(vertex_cnt, vdata_values, prim_indices)
        return vertex_cnt

    def create_hor_edge(self, vertex_cnt, vdata_values, prim_indices, center, height, start_angle,
                        slice_deg, x_axis):
        edge = HorizontalBoxEdgeCylinder(
            center=center + self.center,
            start_angle_deg=start_angle,
            radius=self.c_radius,
            inner_radius=self.c_inner_radius,
            height=height,
            segs_c=20,
            segs_a=2,
            segs_top_cap=0,     #self.c_segs_tc,
            segs_bottom_cap=0,  # self.c_segs_bc,
            ring_slice_deg=slice_deg,
            invert=self.invert,
            x_axis=x_axis
        )
        vertex_cnt = edge.create_cylinder(vertex_cnt, vdata_values, prim_indices)
        return vertex_cnt

    def create_bottom(self, vertex_cnt, vdata_values, prim_indices):

        # center = Point3(0, 0, -(self.height + self.c_radius) / 2)
        # open_sides = dict(open_left=True, open_right=True, open_front=True, open_back=True, open_top=True)
        # vertex_cnt = self.create_rect(
        #     vertex_cnt, vdata_values, prim_indices, self._width, self._depth, self.c_radius, center, open_sides)

        center = Point3(self._width * 0.5, -self._depth * 0.5, -self._height * 0.5)
        start_angle = 0
        slice_deg = 270

        vertex_cnt += self.create_corner_sphere(
            vertex_cnt, vdata_values, prim_indices, center, start_angle, slice_deg,
            bottom_clip=-1., top_clip=0)


        center = Point3(self._width * 0.5, self._depth * 0.5, -self._height * 0.5)
        start_angle = 90
        slice_deg = 270
        vertex_cnt += self.create_corner_sphere(
            vertex_cnt, vdata_values, prim_indices, center, start_angle, slice_deg,
            bottom_clip=-1., top_clip=0)


        center = Point3(-self._width * 0.5, self._depth * 0.5, -self._height * 0.5)
        start_angle = 180
        slice_deg = 270
        vertex_cnt += self.create_corner_sphere(
            vertex_cnt, vdata_values, prim_indices, center, start_angle, slice_deg,
            bottom_clip=-1., top_clip=0)



        center = Point3(-self._width * 0.5, -self._depth * 0.5, -self._height * 0.5)
        start_angle = 270
        slice_deg = 270
        vertex_cnt += self.create_corner_sphere(
            vertex_cnt, vdata_values, prim_indices, center, start_angle, slice_deg,
            bottom_clip=-1., top_clip=0)


        # left
        x_axis = False
        height = self._depth
        start_angle = 270
        slice_deg = 270
        center = Point3(-self._width * 0.5, -self._depth * 0.5, -self._height * 0.5)
        vertex_cnt = self.create_hor_edge(
            vertex_cnt, vdata_values, prim_indices, center, height, start_angle, slice_deg, x_axis
        )

        # back
        x_axis = True
        height = self._width
        start_angle = 270
        slice_deg = 270
        center = Point3(-self._width * 0.5, -self._depth * 0.5, -self._height * 0.5)
        vertex_cnt = self.create_hor_edge(
            vertex_cnt, vdata_values, prim_indices, center, height, start_angle, slice_deg, x_axis
        )


        # right
        x_axis = False
        height = self._depth
        start_angle = 180
        slice_deg = 270
        center = Point3(self._width * 0.5, -self._depth * 0.5, -self._height * 0.5)
        vertex_cnt = self.create_hor_edge(
            vertex_cnt, vdata_values, prim_indices, center, height, start_angle, slice_deg, x_axis
        )

        # front
        x_axis = True
        height = self._width
        start_angle = 0
        slice_deg = 270
        center = Point3(-self._width * 0.5, self._depth * 0.5, -self._height * 0.5)
        vertex_cnt = self.create_hor_edge(
            vertex_cnt, vdata_values, prim_indices, center, height, start_angle, slice_deg, x_axis
        )
        

        center = Point3(0, 0, -(self._height + self.c_radius) / 2)
        open_sides = dict(open_left=True, open_right=True, open_front=True, open_back=True, open_top=True)
        vertex_cnt = self.create_rect(
            vertex_cnt, vdata_values, prim_indices, self._width, self._depth, self.c_radius, center, open_sides)
        
        return vertex_cnt

    def create_rounded_corners(self, vertex_cnt, vdata_values, prim_indices, side):
        center = Point3(0, 0, -self._height * 0.5)

        match side:
            case Sides.FRONT_LEFT:
                angle = 180
                center.xy = Point2(-self._width, self._depth) * 0.5

            case Sides.BACK_LEFT:
                angle = 270 if not self.invert else 90
                center.xy = Point2(-self._width, -self._depth) * 0.5

            case Sides.BACK_RIGHT:
                angle = 0
                center.xy = Point2(self._width, -self._depth) * 0.5

            case Sides.FRONT_RIGHT:
                angle = 90 if not self.invert else 270
                center.xy = Point2(self._width, self._depth) * 0.5

        vertex_cnt = self.create_corner(vertex_cnt, vdata_values, prim_indices, self._height, center, angle, 270)
        return vertex_cnt


    def create_rect_sides(self, vertex_cnt, vdata_values, prim_indices, side):
        common_open_sides = dict(open_top=True, open_bottom=True)
        center = Point3()
        x = (self._width + self.c_radius) * 0.5
        y = (self._depth + self.c_radius) * 0.5

        match side:
            case Sides.LEFT:
                center.xy = Point2(-x, 0)
                w, d = self.c_radius, self._depth
                open_sides = dict(open_right=True, open_front=True, open_back=True)

            case Sides.BACK:
                center.xy = Point2(0, -y)
                w, d = self._width, self.c_radius
                open_sides = dict(open_left=True, open_right=True, open_front=True)

            case Sides.RIGHT:
                center.xy = Point2(x, 0)
                w, d = self.c_radius, self._depth
                open_sides = dict(open_left=True, open_front=True, open_back=True)

            case Sides.FRONT:
                center.xy = Point2(0, y)
                w, d = self._width, self.c_radius
                open_sides = dict(open_left=True, open_right=True, open_back=True)

        # import pdb; pdb.set_trace()
        open_sides = {**open_sides, **common_open_sides}
        vertex_cnt = self.create_rect(
            vertex_cnt, vdata_values, prim_indices, w, d, self._height, center, open_sides)
        return vertex_cnt


    def define_variables(self):
        if self.thickness > 0 and self.c_radius > 0:
            self.thickness = min(self.c_radius, self.thickness)

        # Variables for the box.
        self._depth = self.depth - self.c_radius * 2
        self._width = self.width - self.c_radius * 2
        self._height = self.height - self.c_radius * 2    # **********************

        self.dims = (self.width, self._depth, self._height)  # **********************
        self.segs = {'x': self.segs_w, 'y': self.segs_d, 'z': self.segs_z}

        self.open_sides = {
            '-yz': self.open_left,
            'yz': self.open_right,
            '-zx': self.open_back,
            'zx': self.open_front,
            '-xy': self.open_bottom,
            'xy': self.open_top
        }

        if self.thickness > 0:
            outer_box_details = [
                ['x', self._width, self.open_left, self.open_right],
                ['y', self._depth, self.open_back, self.open_front],
                ['z', self._height, self.open_bottom, self.open_top]  # **********************
            ]
            self.define_inner_details(outer_box_details)

        # Variables for the corner cylinders.
        self.c_inner_radius = 0 if self.thickness <= 0 else self.c_radius - self.thickness
        # self.c_segs_tc = 0 if self.thickness <= 0 and self.open_top else self.segs_d
        # self.c_segs_bc = 0 if self.thickness <= 0 and self.open_bottom else self.segs_d
        self.c_segs_tc = 0
        self.c_segs_bc = 0
    
    def get_geom_node(self):
        self.define_variables()

        # Create outer rounded box.
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        vertex_cnt = self.create_bottom(vertex_cnt, vdata_values, prim_indices)
        # center box
        # vertex_cnt += self.create_sides(vertex_cnt, vdata_values, prim_indices)

        vertex_cnt = self.create_corners(vertex_cnt, vdata_values, prim_indices)
        
        
        
        # if self.c_radius > 0:
        #     vertex_cnt = self.create_corners(vertex_cnt, vdata_values, prim_indices)

        # if self.thickness > 0:
        #     maker = RoundedCornerBox(
        #         width=self._width + self.c_inner_radius * 2,
        #         depth=self._depth + self.c_inner_radius * 2,
        #         height=self.height,
        #         segs_w=self.segs_w,
        #         segs_d=self.segs_d,
        #         segs_z=self.segs_z,
        #         thickness=0,
        #         open_top=True,
        #         open_bottom=True,
        #         invert=not self.invert,
        #         corner_radius=self.c_inner_radius,
        #         rounded_f_left=self.rf_left,
        #         rounded_f_right=self.rf_right,
        #         rounded_b_left=self.rb_left,
        #         rounded_b_right=self.rb_right
        #     )

        #     # Define the inner box center.
        #     maker.center = self.calc_inner_box_center()

            # geom_node = maker.get_geom_node()
            # self.add(geom_node, vdata_values, vertex_cnt, prim_indices)
            # return geom_node

        # Create the geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'box')

        return geom_node




class HorizontalBoxEdgeCylinder(Cylinder):
    """Creates a cylinder model.
       Args:
            radius (float): the radius of the cylinder; must be more than zero
            inner_radius (float): the radius of the inner cylinder; must be less than radius or equal
            height (float): length of the cylinder
            segs_c (int): subdivisions of the mantle along a circular cross-section; mininum is 3
            segs_a (int): subdivisions of the mantle along the axis of rotation; minimum is 1
            segs_top_cap (int): radial subdivisions of the top cap; minimum = 0
            segs_bottom_cap (int): radial subdivisions of the bottom cap; minimum = 0
            ring_slice_deg (int): the angle of the pie slice removed from the cylinder, in degrees; must be from 0 to 360
            slice_caps_radial (int): subdivisions of both slice caps, along the radius; minimum = 0
            slice_caps_axial (int): subdivisions of both slice caps, along the axis of rotation; minimum=0
            invert (bool): whether or not the geometry should be rendered inside-out; default is False
    """

    def __init__(self, center, start_angle_deg, radius=1., inner_radius=0., height=1., segs_c=40, segs_a=2, segs_top_cap=3,
                 segs_bottom_cap=3, ring_slice_deg=0, slice_caps_radial=3, slice_caps_axial=2, invert=False, x_axis=True):
        super().__init__()
        self.radius = radius
        self.inner_radius = inner_radius
        self.height = height
        self.segs_c = segs_c
        self.segs_a = segs_a

        self.segs_tc = segs_top_cap
        self.segs_bc = segs_bottom_cap

        self.ring_slice_deg = ring_slice_deg
        self.segs_sc_r = slice_caps_radial
        self.segs_sc_a = slice_caps_axial
        self.invert = invert

        # If True, tilt a vertical cylinder, whose bottom center is the point (0, 0, 0),
        # 90 degrees in the x-axis direction, and if not, 90 degrees in the y-axis direction.
        self.x_axis = x_axis
        self.center = center
        self.start_angle_deg = start_angle_deg
        self.start_angle_rad = math.pi * self.start_angle_deg / 180
        self.define_variables()

    def get_cap_normal(self):
        if self.x_axis:
            normal = Vec3(1, 0, 0) if self.invert else Vec3(-1, 0, 0)
        else:
            normal = Vec3(0, 1, 0) if self.invert else Vec3(0, -1, 0)

        return normal

    def create_cap_triangles(self, vdata_values, bottom=True):
        # normal = Vec3(0, 0, 1) if self.invert else Vec3(0, 0, -1)
        # normal = Vec3(1, 0, 0) if self.invert else Vec3(-1, 0, 0)
        normal = self.get_cap_normal()

        segs_cap = self.segs_bc if bottom else self.segs_tc

        if not bottom:
            normal *= -1

        # height = 0 if bottom else self.height
        # x = 0 if bottom else self.height
        val = 0 if bottom else self.height

        direction = -1 if self.invert else 1
        r = self.radius / segs_cap
        vertex_cnt = 0

        # cap center and triangle vertices
        for i in range(self.segs_c + 1):
            if i == 0:
                # vertex = Point3(x, 0, 0)
                vertex = Point3(val, 0, 0) if self.x_axis else Point3(0, val, 0) + self.center  # Add center.
                uv = Vec2(0.5, 0.5)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

            angle = self.delta_rad * i + (0 if self.invert else self.slice_rad) + self.start_angle_rad  # ******
            c = math.cos(angle)
            s = math.sin(angle) * direction
            # vertex = Point3(r * c, r * s, height)
            # vertex = Point3(x, r * c, r * s)

            if self.x_axis:
                vertex = Point3(val, r * c, r * s)
            else:
                vertex = Point3(r * s, val, r * c)
            vertex += self.center  # Add center. 

            u = 0.5 + c * 0.5 / segs_cap
            _direction = -direction if bottom else direction
            v = 0.5 + s * 0.5 * _direction / segs_cap

            vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])
            vertex_cnt += 1

        return vertex_cnt

    def create_cap_quad_vertices(self, vdata_values, bottom=True):
        # normal = Vec3(0, 0, 1) if self.invert else Vec3(0, 0, -1)
        # normal = Vec3(1, 0, 0) if self.invert else Vec3(-1, 0, 0)
        normal = self.get_cap_normal()
        segs_cap = self.segs_bc if bottom else self.segs_tc

        if not bottom:
            normal *= -1

        # height = 0 if bottom else self.height
        # x = 0 if bottom else self.height
        val = 0 if bottom else self.height

        direction = -1 if self.invert else 1  # bottom
        n = 0 if self.inner_radius else 1
        vertex_cnt = 0

        # cap quad vertices
        for i in range(n, segs_cap + 1 - n):
            r = self.inner_radius + self.thickness * (i + n) / segs_cap

            for j in range(self.segs_c + 1):
                angle = self.delta_rad * j + (0 if self.invert else self.slice_rad) + self.start_angle_rad  # ******
                c = math.cos(angle)
                s = math.sin(angle) * direction
                # vertex = Point3(r * c, r * s, height)
                # vertex = Point3(x, r * c, r * s)

                if self.x_axis:
                    vertex = Point3(val, r * c, r * s)
                else:
                    vertex = Point3(r * s, val, r * c)
                vertex += self.center  # Add center.


                _r = r / self.radius
                u = 0.5 + c * 0.5 * _r
                _direction = -direction if bottom else direction
                v = 0.5 + s * 0.5 * _direction * _r

                vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])
                vertex_cnt += 1

        return vertex_cnt

    # def create_bottom_cap_triangles(self, index_offset, vdata_values, prim_indices):
    #     vertex_cnt = 0

    #     if not self.inner_radius:
    #         # bottom cap center and triangle vertices
    #         vertex_cnt += self.create_cap_triangles(vdata_values)

    #         # the vertex order of the bottom cap triangles
    #         for i in range(index_offset + 1, index_offset + self.segs_c + 1):
    #             prim_indices.extend((index_offset, i + 1, i))

    #     return vertex_cnt

    # def create_bottom_cap_quads(self, index_offset, vdata_values, prim_indices):
    #     # bottom cap quad vertices
    #     vertex_cnt = self.create_cap_quad_vertices(vdata_values)

    #     # the vertex order of the bottom cap quads
    #     index_offset += (self.segs_c + 1) if self.inner_radius else 1
    #     n = 0 if self.inner_radius else 1

    #     for i in range(n, self.segs_bc):
    #         for j in range(self.segs_c):
    #             vi1 = index_offset + i * (self.segs_c + 1) + j
    #             vi2 = vi1 - self.segs_c - 1
    #             vi3 = vi2 + 1
    #             vi4 = vi1 + 1
    #             prim_indices.extend([*(vi1, vi2, vi3), *(vi1, vi3, vi4)])

    #     return vertex_cnt

    def create_mantle_quads(self, index_offset, vdata_values, prim_indices):
        direction = -1 if self.invert else 1
        vertex_cnt = 0

        # mantle quad vertices
        for i in range(self.segs_a + 1):
            # z = self.height * i / self.segs_a
            # x = self.height * i / self.segs_a
            f1 = self.height * i / self.segs_a

            v = i / self.segs_a

            for j in range(self.segs_c + 1):
                angle = self.delta_rad * j + (0 if self.invert else self.slice_rad)  + self.start_angle_rad  # ******
                # x = self.radius * math.cos(angle)
                # y = self.radius * math.sin(angle) * direction

                # y = self.radius * math.cos(angle)
                # z = self.radius * math.sin(angle) * direction

                f2 = self.radius * math.cos(angle)
                f3 = self.radius * math.sin(angle) * direction

                # vertex = Point3(x, y, z)
                vertex = Point3(f1, f2, f3) if self.x_axis else Point3(f3, f1, f2)
                vertex += self.center  # Add center.

                vec = Vec3(0.0, f2, f3) if self.x_axis else Vec3(f3, 0.0, f2)
                normal = vec.normalized() * direction

                # normal = Vec3(x, y, 0.0).normalized() * direction
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

    # def create_top_cap_triangles(self, index_offset, vdata_values, prim_indices):
    #     vertex_cnt = 0

    #     if not self.inner_radius:
    #         # top cap center and triangle vertices
    #         vertex_cnt += self.create_cap_triangles(vdata_values, bottom=False)

    #         # the vertex order of the top cap triangles
    #         for i in range(index_offset + 1, index_offset + self.segs_c + 1):
    #             prim_indices.extend((index_offset, i, i + 1))

    #     return vertex_cnt

    # def create_top_cap_quads(self, index_offset, vdata_values, prim_indices):
    #     # the top cap quad vertices
    #     vertex_cnt = self.create_cap_quad_vertices(vdata_values, bottom=False)

    #     # the vertex order of the top cap quads
    #     index_offset += (self.segs_c + 1) if self.inner_radius else 1
    #     n = 0 if self.inner_radius else 1

    #     for i in range(n, self.segs_tc):
    #         for j in range(self.segs_c):
    #             vi1 = index_offset + i * (self.segs_c + 1) + j
    #             vi2 = vi1 - self.segs_c - 1
    #             vi3 = vi2 + 1
    #             vi4 = vi1 + 1

    #             prim_indices.extend([*(vi1, vi3, vi2), *(vi1, vi4, vi3)])

    #     return vertex_cnt

    def create_slice_cap_quads(self, index_offset, vdata_values, prim_indices):
        vertex_cnt = 0
        direction = -1 if self.invert else 1

        # the vertices of the slice cap quad
        for is_start in [True, False]:
            if is_start:
                normal = Vec3(0, direction, 0)
            else:
                angle = self.delta_rad * self.segs_c + self.start_angle_deg  # **********
                c = math.cos(angle)
                s = -math.sin(angle)
                normal = Vec3(s, -c, 0) * direction

            for i in range(self.segs_sc_a + 1):
                # z = self.height * i / self.segs_sc_a
                # x = self.height * i / self.segs_sc_a
                f = self.height * i / self.segs_sc_a
                v = i / self.segs_sc_a

                for j in range(self.segs_sc_r + 1):
                    r = self.inner_radius + (self.radius - self.inner_radius) * j / self.segs_sc_r
                    # vertex = Point3(r, 0, z) if is_start else Point3(r * c, r * s, z)
                    # vertex = Point3(x, r, 0) if is_start else Point3(x, r * c, r * s)
                    if self.x_axis:
                        vertex = Point3(f, r, 0) if is_start else Point3(f, r * c, r * s)
                    else:
                        vertex = Point3(0, f, r) if is_start else Point3(r * s, f, r * c)
                    vertex += self.center  # Add center.

                    coef = 0.5 if is_start else -0.5
                    u = 0.5 + coef * r / self.radius * direction * -1
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

    # def create_cylinder(self, vertex_cnt, vdata_values, prim_indices):
    #     if self.segs_bc:
    #         sub_total = vertex_cnt
    #         vertex_cnt += self.create_bottom_cap_triangles(sub_total, vdata_values, prim_indices)
    #         vertex_cnt += self.create_bottom_cap_quads(sub_total, vdata_values, prim_indices)

    #     vertex_cnt += self.create_mantle_quads(vertex_cnt, vdata_values, prim_indices)

    #     if self.segs_tc:
    #         sub_total = vertex_cnt
    #         vertex_cnt += self.create_top_cap_triangles(sub_total, vdata_values, prim_indices)
    #         vertex_cnt += self.create_top_cap_quads(sub_total, vdata_values, prim_indices)

    #     return vertex_cnt

    def define_variables(self):
        self.thickness = self.radius - self.inner_radius
        self.slice_rad = math.pi * self.ring_slice_deg / 180
        self.delta_rad = math.pi * ((360 - self.ring_slice_deg) / 180) / self.segs_c

    # def get_geom_node(self):
    #     self.define_variables()

    #     # Create an outer cylinder.
    #     vdata_values = array.array('f', [])
    #     prim_indices = array.array('H', [])
    #     vertex_cnt = 0

    #     vertex_cnt = self.create_cylinder(vertex_cnt, vdata_values, prim_indices)

    #     if self.ring_slice_deg and self.segs_sc_r and self.segs_sc_a:
    #         vertex_cnt += self.create_slice_cap_quads(vertex_cnt, vdata_values, prim_indices)

    #     # Create an inner cylinder to connect to the outer one.
    #     if self.inner_radius:
    #         cylinder_maker = CylinderPipe(
    #             radius=self.inner_radius,
    #             inner_radius=0,
    #             height=self.height,
    #             segs_c=self.segs_c,
    #             segs_a=self.segs_a,
    #             segs_top_cap=0,
    #             segs_bottom_cap=0,
    #             ring_slice_deg=self.ring_slice_deg,
    #             slice_caps_radial=0,
    #             slice_caps_axial=0,
    #             invert=not self.invert
    #         )

    #         geom_node = cylinder_maker.get_geom_node()
    #         self.add(geom_node, vdata_values, vertex_cnt, prim_indices)
    #         return geom_node

    #     # Create the geom node.
    #     geom_node = self.create_geom_node(
    #         vertex_cnt, vdata_values, prim_indices, 'cylinder')
    #     return geom_node


class BoxCornerQuarteredHemisphere(CapsuleHemisphere):
# class BoxCornerQuarteredHemisphere(Sphere):

    """Create a sphere model.
       Args:
            radius (float): the radius of sphere; more than 0;
            inner_radius (float): the radius of the inner sphere; cannot be negative; must be in [0., radius]
            segs_h(int): subdivisions along horizontal circles; minimum = 3
            segs_v (int): subdivisions along vertical semicircles; minimum = 2
            segs_bottom_cap (int): radial subdivisions of the bottom clipping cap; minimum = 0 (no cap)
            segs_top_cap (int): radial subdivisions of the top clipping cap; minimum = 0 (no cap)
            segs_slice_caps (int): radial subdivisions of the slice caps; minimum = 0 (no caps)
            slice_deg (float): the angle of the pie slice removed from the sphere, in degrees; must be in [0., 360.]
            bottom_clip (float):
                relative height of the plane that cuts off a bottom part of the sphere;
                must be in [-1., 1.] range;
                -1. (no clipping)
            top_clip (float):
                relative height of the plane that cuts off a top part of the sphere;
                must be in [bottom_clip, 1.] range;
                1. (no clipping);
            invert (bool): whether or not the geometry should be rendered inside-out; default is False
    """

    def __init__(self, center, start_angle_deg=0, radius=1., inner_radius=0, segs_h=40, segs_v=20,
                 segs_slice_caps=2, slice_deg=0, bottom_clip=-1., top_clip=1., invert=False):
        super().__init__(
            center=center,
            radius=radius,
            inner_radius=inner_radius,
            segs_h=segs_h,
            segs_v=segs_v,
            segs_slice_caps=segs_slice_caps,
            slice_deg=slice_deg,
            bottom_clip=bottom_clip,
            top_clip=top_clip,
            invert=invert
        )

        # self.center = center

        self.start_angle_deg = start_angle_deg
        self.start_angle_rad = math.pi * self.start_angle_deg / 180

        # self.define_variables()

    def create_top_edge_quads(self, index_offset, prim_indices):
        index_offset -= (self.segs_h - 1) + self.segs_h + 2

        # Define the vertex order of the polygon along the top cap.
        for i in range(self.segs_h):
            vi1 = i + index_offset
            vi2 = vi1 + 1
            vi3 = vi2 + self.segs_h
            vi4 = vi3 + 1

            prim_indices.extend((vi1, vi2, vi4) if self.invert else (vi1, vi2, vi3))
            prim_indices.extend((vi1, vi4, vi3) if self.invert else (vi2, vi4, vi3))


    # def create_bottom(self, index_offset, vdata_values, prim_indices):
    #     # import pdb; pdb.set_trace()
    #     cap = SimpleNamespace(
    #         z=self.bottom_height,
    #         normal=Vec3(0., 0., -1.),
    #         pole_vertex=Point3(0, 0, -self.radius) + self.center,
    #         is_bottom=True
    #     )
    #     vertex_cnt = 0

    #     if self.bottom_clip > -1:
    #         offset_cnt = self.create_cap_edge_vertices(vdata_values, prim_indices, cap)
    #         vertex_cnt += self.create_bottom_edge_quads(index_offset, vdata_values, prim_indices)
    #     else:
    #         offset_cnt = self.create_cap_pole(vdata_values, prim_indices, cap)
    #         vertex_cnt += self.create_bottom_pole_triangles(index_offset, vdata_values, prim_indices)

    #     return vertex_cnt + offset_cnt, index_offset + offset_cnt

    # def create_top(self, index_offset, vdata_values, prim_indices):
    #     print(self.top_height)
    #     cap = SimpleNamespace(
    #         z=self.top_height,
    #         normal=Vec3(0., 0., 1.),
    #         pole_vertex=Point3(0, 0, self.radius) + self.center,
    #         is_bottom=False
    #     )
    #     vertex_cnt = 0

    #     if self.top_clip < 1.:
    #         vertex_cnt += self.create_cap_edge_vertices(vdata_values, prim_indices, cap)
    #         self.create_top_edge_quads(index_offset + vertex_cnt - 1, prim_indices)
    #         # self.create_top_edge_quads(index_offset + vertex_cnt + 2, prim_indices)
    #     else:
    #         vertex_cnt += self.create_cap_pole(vdata_values, prim_indices, cap)
    #         self.create_top_pole_triangles(index_offset + vertex_cnt - 1, prim_indices)

    #     return vertex_cnt

    def get_cap_edge_vertices(self, vdata_values):
        direction = -1 if self.invert else 1
        angle_v = self.bottom_angle + self.delta_angle_v  #  + self.start_angle_rad  # ********
        z = self.radius * -math.cos(angle_v)

        radius_h = self.radius * math.sin(angle_v)
        _delta = 0 if self.invert else self.slice_rad
        v = angle_v / math.pi

        # *************************
        _delta += self.start_angle_rad
        # *************************

        # Define the triangle vertices along the bottom pole.
        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + _delta
            x = radius_h * math.cos(angle_h)
            y = radius_h * math.sin(angle_h) * direction

            vertex = Point3(x, y, z) + self.center  # add center.
            normal = Vec3(x, y, z).normalized() * direction
            uv = Vec2(i / self.segs_h, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 1

    def create_cap_edge_vertices(self, vdata_values, prim_indices, cap):
        radius_h = math.sqrt(self.radius ** 2 - cap.z ** 2)
        direction = -1 if self.invert else 1
        _delta = 0 if self.invert else self.slice_rad

        # *************************
        _delta += self.start_angle_rad
        # *************************

        v = (math.pi - math.acos(cap.z / self.radius)) / math.pi

        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + _delta
            x = radius_h * math.cos(angle_h)
            y = radius_h * math.sin(angle_h) * direction
            vertex = Point3(x, y, cap.z) + self.center   # add center.
            normal = Vec3(x, y, cap.z).normalized() * direction
            uv = Vec2(i / self.segs_h, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 1

    def create_mantle_quads(self, index_offset, vdata_values, prim_indices):
        n = self.segs_h + 1
        direction = -1 if self.invert else 1
        _delta = 0 if self.invert else self.slice_rad

        # *************************
        _delta += self.start_angle_rad
        # *************************

        vertex_cnt = 0

        # Define the mantle quad vertices.
        # ************************************
        # for i in range(1, self.segs_v - 1):
        for i in range(1, self.segs_v):
        # ***********************************

            angle_v = self.bottom_angle + self.delta_angle_v * (i + 1)  #  + self.start_angle_rad  # ********
            z = self.radius * -math.cos(angle_v)
            radius_h = self.radius * math.sin(angle_v)
            v = angle_v / math.pi

            for j in range(self.segs_h + 1):
                angle_h = self.delta_angle_h * j + _delta
                x = radius_h * math.cos(angle_h)
                y = radius_h * math.sin(angle_h) * direction

                vertex = Point3(x, y, z)
                normal = vertex.normalized() * direction
                # Center must be added after normalize. Otherwise, the shadows will go wrong.
                vertex = Point3(x, y, z) + self.center

                uv = Vec2(j / self.segs_h, v)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

            if i > 0:
                for j in range(self.segs_h):
                    vi1 = i * n + j + index_offset
                    vi2 = vi1 - n
                    vi3 = vi2 + 1
                    vi4 = vi1 + 1

                    prim_indices.extend((vi1, vi2, vi4) if self.invert else (vi1, vi2, vi3))
                    prim_indices.extend((vi2, vi3, vi4) if self.invert else (vi1, vi3, vi4))

        return vertex_cnt