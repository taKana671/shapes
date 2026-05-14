import numpy as np
import math

from ..polyhedron import Polyhedron
from ..spherical_polyhedron.spherical_polyhedron import SphericalVertexData
from ..convex_polyhedron.convex_polyhedron import PolyhedralVertexData

from panda3d.core import Point3


class ShatteredSphere(SphericalVertexData, PolyhedralVertexData, Polyhedron):
    """A class to create a random convex polyhedron.

        Args:
            polygons (list): A list of numpy.ndarray; vertex coordinates of a polyhedron.
            spherical_idx (int): index indicating where the spherical face is located in the above list.
            max_depth (int): the number of divisions of one triangle; cannot be negative.
            scale (float): the scale of the polyhedron; greater than 0.
    """

    def __init__(self, polygons, spherical_idx, max_depth=4, scale=2.):
        super().__init__(max_depth, scale)
        self.color = (1, 1, 1, 1)
        self.normal = np.zeros(3)
        self.polygons = polygons
        self.spherical_polygon = [] if spherical_idx is None else self.polygons[spherical_idx]
        self.spherical_idx = spherical_idx

        self.is_spherical = False
        self.define_variables()

    def define_variables(self):
        self.polyhedron_org_center = np.mean(np.concatenate(self.polygons), axis=0)

        # This will be used to determine whether a vertex is included
        # in the polygon to be converted into a spherical face.
        if len(self.spherical_polygon) > 0:
            face_center = np.mean(self.spherical_polygon, axis=0)
            length = len(self.spherical_polygon)
            self.spherical_tri_areas = []

            for i, p1 in enumerate(self.spherical_polygon):
                p2 = self.spherical_polygon[(i + 1) % length]

                tri = [face_center, p1, p2]
                area = self.calc_triangle_area(*tri)
                self.spherical_tri_areas.append((tri, area))

    def is_inside(self, pt, tolerance=1e-5):
        for tri, area_master in self.spherical_tri_areas:
            area_target = sum(self.calc_triangle_area(
                pt, tri[i], tri[(i + 1) % 3]) for i in range(3))

            if abs(area_target - area_master) < tolerance:
                return True

    def get_uv_coords(self, tri_vertices):
        uvs = [self.calc_uv(Point3(*self.normalize(vert))) for vert in tri_vertices]
        self.fix_uv(*uvs)

        return uvs

    def normalize(self, vertex):
        norm = math.hypot(*vertex)
        return vertex / norm

    def create_polyhedron(self, vdata_values, prim_indices):
        for i, tri in enumerate(self.generate_divided_tri()):
            sphere_uv = None

            for j, vert in enumerate(tri):
                if len(self.spherical_polygon) > 0 and self.is_inside(vert):
                    vert = self.normalize(vert)
                    normal = vert if self.is_spherical else self.normal

                    if sphere_uv is None:
                        sphere_uv = self.get_uv_coords(tri)
                    uv = sphere_uv[j]
                else:
                    normal = self.normal
                    uv = self.project_to_uv(vert, self.normal)

                vertex = (vert - self.polyhedron_org_center) * self.scale
                vdata_values.extend([*vertex, *self.color, *normal, *uv])

            indices = (idx := i * 3, idx + 1, idx + 2)
            prim_indices.extend(indices)

    def generate_triangles(self):
        for i, vertices in enumerate(self.polygons):
            center = np.mean(vertices, axis=0)
            self.normal = self.calc_outward_normal(vertices, self.polyhedron_org_center)

            if self.spherical_idx == i:
                self.is_spherical = True

            for j, v in enumerate(vertices):
                next_v = vertices[(j + 1) % len(vertices)]
                tri = [center, v, next_v]
                yield tri

            self.is_spherical = False

    def get_geom_node(self):
        faces = sum(len(face) for face in self.polygons)
        return self.create_polyhedron_geom_node(faces)
