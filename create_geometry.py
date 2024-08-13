import abc

from panda3d.core import NodePath
from panda3d.core import Geom, GeomNode, GeomTriangles
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexArrayFormat


class ProceduralGeometry(abc.ABC):

    @abc.abstractmethod
    def get_geom_node(self):
        pass

    def create(self):
        geom_node = self.get_geom_node()
        model = NodePath(geom_node)
        model.set_two_sided(True)
        return model

    def create_format(self):
        arr_format = GeomVertexArrayFormat()
        arr_format.add_column('vertex', 3, Geom.NTFloat32, Geom.CPoint)
        arr_format.add_column('color', 4, Geom.NTFloat32, Geom.CColor)
        arr_format.add_column('normal', 3, Geom.NTFloat32, Geom.CColor)
        arr_format.add_column('texcoord', 2, Geom.NTFloat32, Geom.CTexcoord)
        fmt = GeomVertexFormat.register_format(arr_format)
        return fmt

    def create_geom_node(self, fmt, vertex_count, vdata_values, prim_indices, name='vertex'):
        """Args:
            fmt (GeomVertexFormat): physical layout of the vertex data stored within a Geom
            name (str): the name of data
            vertex_count (int): the number of vertices
            vdata_values (array.array): vertex information
            prim_indices (array.array): vertex order
        """
        vdata = GeomVertexData(name, fmt, Geom.UHStatic)
        vdata.unclean_set_num_rows(vertex_count)
        vdata_mem = memoryview(vdata.modify_array(0)).cast('B').cast('f')
        vdata_mem[:] = vdata_values

        prim = GeomTriangles(Geom.UHStatic)
        prim_array = prim.modify_vertices()
        prim_array.unclean_set_num_rows(len(prim_indices))
        prim_mem = memoryview(prim_array).cast('B').cast('H')
        prim_mem[:] = prim_indices

        node = GeomNode('geomnode')
        geom = Geom(vdata)
        geom.add_primitive(prim)
        node.add_geom(geom)
        return node