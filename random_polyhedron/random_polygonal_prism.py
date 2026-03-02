import array
import math

import numpy as np
from panda3d.core import Vec3, Point3, Vec2

from ..create_geometry import ProceduralGeometry
from ..cylinder import BasicCylinder


class RandomPolygonalPrism(BasicCylinder, ProceduralGeometry):
    """A class to create a prism from 3D vertex coordinates of a polygonal base with height 0.

        Args:
            vertices: (list): a list of numpy.ndarray of double; coordinates of the Voronoi vertices.
            thickness (float):
                radial offset of inner cylinder;
                results in a straight tube with an inner radius equal to radius minus thickness;
                must be in [0., radius] range; default is 0.0.
            height (float): length of the cylinder, greater than 0; default is 1.
            segs_a (int): subdivisions of the mantle along the axis of rotation; minimum is 1; default is 2.
            segs_top_cap (int): radial subdivisions of the top cap; minimum = 0; default is 3.
            segs_bottom_cap (int): radial subdivisions of the bottom cap; minimum = 0; default is 3.
            invert (bool): whether or not the geometry should be rendered inside-out; default is False.
    """

    def __init__(self, vertices, thickness=0.0, height=1, segs_a=2, segs_top_cap=3, segs_bottom_cap=3, invert=False):
        self.vertices = vertices
        segs_c = len(self.vertices)
        self.center = sum(self.vertices) / segs_c
        # self.center = np.mean(vertices, axis=0)
        # import pdb; pdb.set_trace()
        radius = math.hypot(*(self.vertices[0] - self.center))
        self.thickness = radius if not thickness else max(0, min(radius, thickness))

        super().__init__(
            radius=radius,
            inner_radius=radius - self.thickness,
            height=height,
            segs_c=segs_c,
            segs_a=segs_a,
            segs_top_cap=segs_top_cap,
            segs_bottom_cap=segs_bottom_cap,
            start_slice_cap=False,
            end_slice_cap=False,
            invert=invert
        )

    def create_cap_triangles(self, vdata_values, bottom=True):
        normal = Vec3(0, 0, 1) if self.invert else Vec3(0, 0, -1)
        segs_cap = self.segs_bc if bottom else self.segs_tc

        if not bottom:
            normal *= -1

        height = 0 if bottom else self.height
        direction = -1 if self.invert else 1
        r = self.radius / segs_cap
        vertex_cnt = 0

        # cap center and triangle vertices
        for i, shifted_vert in enumerate(self.shifted_vertices):
            if i == 0:
                vertex = Point3(0, 0, height)
                uv = Vec2(0.5, 0.5)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

            vertex = Point3(*shifted_vert[:2] / segs_cap, height)
            u = 0.5 + vertex.x / r * 0.5 / segs_cap
            _direction = -direction if bottom else direction
            v = 0.5 + vertex.y / r * 0.5 * _direction / segs_cap

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
        n = 0 if self.inner_radius else 1
        vertex_cnt = 0

        # cap quad vertices
        for i in range(n, segs_cap + 1 - n):
            r = self.inner_radius + self.thickness * (i + n) / segs_cap

            for shifted_vert in self.shifted_vertices:
                _r = r / self.radius
                vertex = Point3(*shifted_vert[:2] * _r, height)
                u = 0.5 + vertex.x / r * 0.5 * _r
                _direction = -direction if bottom else direction
                v = 0.5 + vertex.y / r * 0.5 * _direction * _r

                vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])
                vertex_cnt += 1

        return vertex_cnt

    def create_mantle_quad_vertices(self, index_offset, vdata_values, prim_indices):
        direction = -1 if self.invert else 1
        vertex_cnt = 0

        # mantle quad vertices
        for i in range(self.segs_a + 1):
            z = self.height * i / self.segs_a
            v = i / self.segs_a
            total_edge_length = 0

            for j, shifted_vert in enumerate(self.shifted_vertices):
                vertex = Point3(*shifted_vert[:2], z)
                normal = Vec3(vertex.x, vertex.y, 0.0).normalized() * direction

                if j > 0:
                    total_edge_length += self.edge_lengths[j - 1]

                u = total_edge_length / self.edge_length

                # u = j / self.segs_c
                uv = Vec2(u, v)

                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

        return vertex_cnt

    def calc_perimeter(self):
        edges = np.diff(self.vertices, axis=0, append=[self.vertices[0]])
        edge_lengths = np.sqrt(np.sum(edges ** 2, axis=1))
        edge_length = np.sum(edge_lengths)
        return edge_length, edge_lengths

    def define_variables(self):
        self.shifted_vertices = [v - self.center for v in self.vertices + self.vertices[:1]]
        self.edge_length, self.edge_lengths = self.calc_perimeter()

    def get_geom_node(self):
        self.define_variables()

        # Create an outer cylinder.
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0
        vertex_cnt = self.create_cylinder(vertex_cnt, vdata_values, prim_indices)

        if self.inner_radius:
            cylinder_maker = RandomPolygonalPrism(
                vertices=[v * (self.inner_radius / self.radius) for v in self.vertices],
                thickness=0.0,
                height=self.height,
                segs_a=self.segs_a,
                segs_top_cap=0,
                segs_bottom_cap=0,
                invert=not self.invert
            )

            geom_node = cylinder_maker.get_geom_node()
            self.add(geom_node, vdata_values, vertex_cnt, prim_indices)
            return geom_node

        # Create the geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, self.__class__.__name__.lower())
        return geom_node
