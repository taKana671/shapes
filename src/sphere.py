import array
import math

from panda3d.core import Vec3, Point3, Vec2

from .create_geometry import ProceduralGeometry


class Sphere(ProceduralGeometry):
    """Create a sphere model.
       Args:
            radius (int): the radius of sphere;
            segments (int): the number of surface subdivisions;
    """

    def __init__(self, radius=1.5, segments=22):
        super().__init__()
        self.radius = radius
        self.segments = segments
        self.color = (1, 1, 1, 1)

    def create_bottom_pole(self, vdata_values, prim_indices):
        # the bottom pole vertices
        normal = Vec3(0.0, 0.0, -1.0)
        vertex = Point3(0.0, 0.0, -self.radius)

        for i in range(self.segments):
            u = i / self.segments
            vdata_values.extend(vertex)
            vdata_values.extend(self.color)
            vdata_values.extend(normal)
            vdata_values.extend((u, 0.0))

            # the vertex order of the pole vertices
            prim_indices.extend((i, i + self.segments + 1, i + self.segments))

        return self.segments

    def create_quads(self, index_offset, vdata_values, prim_indices):
        delta_angle = 2 * math.pi / self.segments
        vertex_cnt = 0

        # the quad vertices
        for i in range((self.segments - 2) // 2):
            angle_v = delta_angle * (i + 1)
            radius_h = self.radius * math.sin(angle_v)
            z = self.radius * -math.cos(angle_v)
            v = 2.0 * (i + 1) / self.segments

            for j in range(self.segments + 1):
                angle = delta_angle * j
                c = math.cos(angle)
                s = math.sin(angle)
                x = radius_h * c
                y = radius_h * s
                normal = Vec3(x, y, z).normalized()
                u = j / self.segments

                vdata_values.extend((x, y, z))
                vdata_values.extend(self.color)
                vdata_values.extend(normal)
                vdata_values.extend((u, v))

                # the vertex order of the quad vertices
                if i > 0 and j <= self.segments:
                    px = i * (self.segments + 1) + j + index_offset
                    prim_indices.extend((px, px - self.segments - 1, px - self.segments))
                    prim_indices.extend((px, px - self.segments, px + 1))

            vertex_cnt += self.segments + 1

        return vertex_cnt

    def create_top_pole(self, index_offset, vdata_values, prim_indices):
        vertex = Point3(0.0, 0.0, self.radius)
        normal = Vec3(0.0, 0.0, 1.0)

        # the top pole vertices
        for i in range(self.segments):
            u = i / self.segments
            vdata_values.extend(vertex)
            vdata_values.extend(self.color)
            vdata_values.extend(normal)
            vdata_values.extend((u, 1.0))

            # the vertex order of the top pole vertices
            x = i + index_offset
            prim_indices.extend((x, x + 1, x + self.segments + 1))

        return self.segments

    def get_geom_node(self):
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        # create vertices of the bottom pole, quads, and top pole
        vertex_cnt += self.create_bottom_pole(vdata_values, prim_indices)
        vertex_cnt += self.create_quads(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt += self.create_top_pole(vertex_cnt - self.segments - 1, vdata_values, prim_indices)

        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'sphere')

        return geom_node


class QuickSphere(ProceduralGeometry):
    """Create a sphere model from icosahedron quickly.
        Arges:
            divnum (int): the number of divisions of one triangle; cannot be negative;
    """

    def __init__(self, divnum=3):
        super().__init__()
        self.divnum = divnum
        self.color = (1, 1, 1, 1)

    def calc_midpoints(self, face):
        """face (list): list of Vec3; having 3 elements like below.
           [(0, 1), (1, 2), (2, 0)]
        """
        for i, pt1 in enumerate(face):
            j = i + 1 if i < len(face) - 1 else 0
            pt2 = face[j]
            mid_pt = (pt1 + pt2) / 2

            yield mid_pt

    def subdivide(self, face, divnum=0):
        if divnum == self.divnum:
            yield face
        else:
            midpoints = [pt for pt in self.calc_midpoints(face)]

            for i, vertex in enumerate(face):
                j = len(face) - 1 if i == 0 else i - 1
                face = [vertex, midpoints[i], midpoints[j]]
                yield from self.subdivide(face, divnum + 1)
            yield from self.subdivide(midpoints, divnum + 1)

    def load_obj(self, file_path):
        vertices = []
        faces = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                li = [val for val in line.split(' ') if val]

                match li[0]:
                    case 'v':
                        vertices.append(tuple(float(val) for val in li[1:]))

                    case 'f':
                        faces.append(tuple(int(val) - 1 for val in li[1:]))

        return vertices, faces

    def get_geom_node(self):
        vertices, faces = self.load_obj('src/objs/icosahedron.obj')
        vertex_cnt = 4 ** self.divnum * 20 * 3
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        start = 0

        for face in faces:
            face_verts = [Vec3(vertices[n]) for n in face]
            for subdiv_face in self.subdivide(face_verts):
                for vert in subdiv_face:
                    normal = vert.normalized()
                    vdata_values.extend(normal)
                    vdata_values.extend(self.color)
                    vdata_values.extend(normal)
                    vdata_values.extend((0, 0))

                indices = (start, start + 1, start + 2)
                prim_indices.extend(indices)
                start += 3

        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'sphere')

        return geom_node
