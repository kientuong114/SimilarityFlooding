import xml.etree.ElementTree as et
from collections import namedtuple
import _schema_graph_utils as sgu

class STNode:
    """Schema Tree Node

    A Schema Tree is a n-ary tree which represents a hierachical data set.
    A Schema Tree should be created only via the parsing functions (e.g. parse_xml())
    Note that since Python 3.7 dicts are now ordered by default.
    This means that attrib will have the same order of the input file.

    Attributes:
        tag (str): The tag associated to the node (e.g XML tag)
        attrib: The dict of string attributes associated to the tag
        children: The dict of all children nodes, indexed by their tag
        father: Reference to the father of tha node
    """

    def __init__(self, tag, attrib = None):
        self.tag = tag
        self.attrib = attrib
        self.children = {}
        self.father = None

    def __repr__(self):
        s = f"""STNode(tag = {self.tag}, """ +\
                    f"""attrib = {list(self.attrib)}, """ +\
                    f"""children = {[tag for tag in self.children.keys()]}, """ +\
                    f"""father = {self.father.tag if self.father else None})"""
        return s

    def add_child(self, child):
        """Adds child to the children dict of self and updates its father reference"""
        self.children.update({child.tag: child})
        child.father = self

    @classmethod
    def from_path_node(cls, path_node):
        return STNode(path_node.tag, path_node.attrib)

    @property
    def children_tags(self):
        return self.children.keys()


def print_tree(root):
    """Print all nodes of the Schema Tree in pre-order

    Args:
        root (str): the root node of the tree to be printed
    """
    print(root)
    for tag in sorted(root.children.keys()):
        print_tree(root.children[tag])


def post_order_walk(root):
    """Generator of STNode objects, from a post-order walk of the tree starting from root

    Args:
        root (str): the root node of the tree to be printed
    """

    for tag, child in root.children.items():
        yield from post_order_walk(child)
    yield root

def pre_order_walk(root):
    """Generator of STNode objects, from a pre-order walk of the tree starting from root

    Args:
        root (str): the root node of the tree to be printed
    """

    yield root
    for tag, child in root.children.items():
        yield from post_order_walk(child)



def parse_xml(file_path):
    """Return the schema tree for the xml file located in file_path

    Args:
        file_path (str): Relative file path to the xml file
    """

    PathNode = namedtuple('PathNode', ['tag', 'attrib'])

    def leaf_paths(root, path=[]):
        # Generator of all root-leaf paths
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

    schema_tree = STNode.from_path_node(root)
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


def schema_tree2Graph(root):
    import networkx as nx

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
    st = parse_xml('test_schemas/test_schema.xml')
    sgu.schema_graph_draw(schema_tree2Graph(st))
