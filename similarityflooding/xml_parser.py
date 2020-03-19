import xml.etree.ElementTree as et
from collections import namedtuple

class SchemaNode:
    """Node for the Schema Tree.
    
    A Schema Tree is a n-ary tree which represents a hierachical data set.
    A Schema Tree should be created only via the parsing functions (e.g. parse_xml())

    Attributes:
        tag (str): The tag associated to the node (e.g XML tag)
        attrib: The set of string attributes associated to the tag
        children: The dict of all children nodes, indexed by their tag
        father: Reference to the father of tha node
    """

    def __init__(self, tag, attrib = None):
        self.tag = tag
        self.attrib = attrib
        self.children = {}
        self.father = None

    def __repr__(self):
        s = f"""SchemaNode(tag = {self.tag},""" +\
                    f"""attrib = {list(self.attrib)},""" +\
                    f"""children = {[tag for tag in self.children.keys()]},""" +\
                    f"""father = {self.father.tag if self.father else None})"""
        return s

    def add_child(self, child):
        """Adds child to the children dict of self and updates its father reference"""
        self.children.update({child.tag: child})
        child.father = self

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
        SchemaNode.print_tree(root.children[tag])


def parse_xml(file_path):
    """Return the schema tree for the xml file located in file_path

    Args:
        file_path (str): Relative file path to the xml file
    """

    PathNode = namedtuple('PathNode', ['tag', 'attrib'])


    def leaf_paths(root, path=[]):
        # Generator of all root-leaf paths
        path = list(path)
        path.append(PathNode(root.tag, set(root.keys())))
        if not list(root):
            # Doesn't have children
            yield path
        else:
            for child in root:
                yield from leaf_paths(child, path)

    xml_tree = et.parse(file_path)
    root = xml_tree.getroot()

    schema_tree = SchemaNode(root.tag, attrib=set(root.keys()))
    g = leaf_paths(root)

    for path in g:
        curr = schema_tree
        for node in path[1:]:
            if node.tag not in curr.children_tags:
                succ = SchemaNode(node.tag, attrib = node.attrib)
                curr.add_child(succ)
            else:
                succ = curr.children[node.tag]
                succ.attrib = succ.attrib.union(node.attrib)
            curr = succ

    return schema_tree


def schema_tree2Graph():
    return


if __name__ == "__main__":
    parse_xml('test_schemas/test_schema.xml')
