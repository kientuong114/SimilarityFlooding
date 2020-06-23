import xml.etree.ElementTree as et
from utils import schema_graph_utils as sgu
from parse.STNode import *

FilePath = str

# TODO: update naming convention child -> element

def parse_xml(file_path: FilePath):
    """Return the schema tree for the xml file located in file_path

    Args:
        file_path (str): Relative file path to the xml file
    """

    def leaf_paths(root, path:List[PathNode]=[]):
        # Generator of all root-leaf paths, given an ElementTree node
        path = list(path)
        path.append(PathNode(root.tag, {k:None for k in root.keys()}))
        if not list(root):
            # Doesn't have children
            yield path
        else:
            for child in root:
                yield from leaf_paths(child, path)

    xml_tree = et.parse(file_path)
    root = xml_tree.getroot()
    schema_tree = STNode.from_path_node(PathNode(root.tag, root.attrib))
    g = leaf_paths(root)

    for path in g:
        curr = schema_tree
        for node in path[1:]:
            if node.tag not in curr.children_tags:
                succ = STNode.from_path_node(node)
                curr.add_child(succ)
            else:
                succ = curr.children[node.tag]
                succ.attrib.update(node.attrib)
            curr = succ

    return schema_tree


def schema_tree2Graph(root: STNode):
    import networkx as nx # type: ignore

    oid = sgu.OID_generator(char='&')
    G = nx.DiGraph()

    oid_map = {}

    for node in post_order_walk(root):
        curr_oid = next(oid)
        oid_map.update({node.tag: curr_oid})

        G.add_node(curr_oid, type='object')
        G.add_node(node.tag, type='literal')
        G.add_edge(curr_oid, node.tag, title='name')

        for i, atb in enumerate(node.attrib.keys()):
            G.add_node(atb, type='literal')
            G.add_edge(curr_oid, atb, title='attrib', prog_num = i)

        for i, child in enumerate(node.children_tags):
            #Given the post-order walk, each child will already have a node
            child_oid = oid_map[child]
            G.add_edge(curr_oid, child_oid, title='child', prog_num = i)

    return G

if __name__ == "__main__":
    st = parse_xml('test/test_schemas/test_schema.xml')
    sgu.schema_graph_draw(schema_tree2Graph(st))
