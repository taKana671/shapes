from panda3d.core import NodePath
from panda3d.core import Geom, GeomNode, GeomTriangles
from panda3d.core import Mat4, Vec3
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexArrayFormat


class ProceduralGeometry:

    def __init__(self):
        self.fmt, self.stride = self.create_format()

    def __init_subclass__(cls):
        super().__init_subclass__()
        if 'get_geom_node' not in cls.__dict__:
            raise NotImplementedError('Subclasses must override get_geom_node method.')

    def create(self):
        geom_node = self.get_geom_node()
        model = self.modeling(geom_node)
        return model

    def modeling(self, geom_node):
        model = NodePath(geom_node)
        model.set_two_sided(True)
        return model

    def create_format(self):
        """Return physical layout of the vertex data stored within a Geom
           and the number of floats on each vertex data row.
        """
        arr_format = GeomVertexArrayFormat()
        arr_format.add_column('vertex', 3, Geom.NTFloat32, Geom.CPoint)
        arr_format.add_column('color', 4, Geom.NTFloat32, Geom.CColor)
        arr_format.add_column('normal', 3, Geom.NTFloat32, Geom.CColor)
        arr_format.add_column('texcoord', 2, Geom.NTFloat32, Geom.CTexcoord)

        fmt = GeomVertexFormat.register_format(arr_format)
        stride = 12  # number of floats on each vertex data row
        return fmt, stride

    def create_geom_node(self, vertex_count, vdata_values, prim_indices, name='vertex'):
        """Args:
            fmt (GeomVertexFormat): physical layout of the vertex data stored within a Geom.
            name (str): the name of data.
            vertex_count (int): the number of vertices.
            vdata_values (array.array): vertex information.
            prim_indices (array.array): vertex order.
        """
        vdata = GeomVertexData(name, self.fmt, Geom.UHStatic)
        vdata.unclean_set_num_rows(vertex_count)
        vdata_mem = memoryview(vdata.modify_array(0)).cast('B').cast('f')
        vdata_mem[:] = vdata_values

        prim = GeomTriangles(Geom.UHStatic)
        prim_array = prim.modify_vertices()
        prim_array.unclean_set_num_rows(len(prim_indices))
        prim_mem = memoryview(prim_array).cast('B').cast('H')
        prim_mem[:] = prim_indices

        geom_node = GeomNode('geomnode')
        geom = Geom(vdata)
        geom.add_primitive(prim)
        geom_node.add_geom(geom)
        return geom_node

    def tranform_vertices(self, vdata, axis_vec, bottom_center, rotation_deg):
        mat = Mat4(Mat4.ident_mat())

        if rotation_deg:
            mat *= Mat4.rotate_mat(rotation_deg, Vec3.up())

        if axis_vec.normalize():
            cross_vec = axis_vec.cross(Vec3.up())
            ref_vec = cross_vec if cross_vec.normalize() else Vec3.right()
            # The angle is positive if the rotation from this vector to other is clockwise
            # when looking in the direction of the ref vector.
            if angle := Vec3.up().signed_angle_deg(axis_vec, ref_vec):
                mat *= Mat4.rotate_mat(angle, ref_vec)

        if any(v for v in bottom_center):
            mat *= Mat4.translate_mat(*bottom_center)

        vdata.transform_vertices(mat)

    def add(self, geom_node, add_vdata, add_vert_cnt, add_prim, add_prim_cnt):
        """Add geometry data to geom node.
            Args:
                geom_node (GeomNode): geom node to which geometry data are added.
                stride (int)        : number of floats on each vertex data row.
                add_vdata (array.array or memoryview): vertices that will be added to the geom node.
                add_vert_cnt (int): the number of vertex data rows that will be added to the geom node.
                add_prim (array.array or memoryview): vertex order that will be added to the geom node.
                add_prim_cnt (int): the number of primitives that will be added to the geom node.
        """
        geom = geom_node.modify_geom(0)
        vdata = geom.modify_vertex_data()
        old_vert_cnt = vdata.get_num_rows()
        old_vert_size = old_vert_cnt * self.stride
        vdata.set_num_rows(old_vert_cnt + add_vert_cnt)
        vdata_mem = memoryview(vdata.modify_array(0)).cast('B').cast('f')
        vdata_mem[old_vert_size:] = add_vdata

        prim = geom.modify_primitive(0)
        old_prim_cnt = prim.get_num_vertices()
        new_prim_cnt = old_prim_cnt + add_prim_cnt
        prim_array = prim.modify_vertices()
        prim_array.set_num_rows(new_prim_cnt)
        prim_mem = memoryview(prim_array).cast('B').cast('H')
        prim_mem[old_prim_cnt:] = add_prim
        prim.offset_vertices(old_vert_cnt, old_prim_cnt, new_prim_cnt)
