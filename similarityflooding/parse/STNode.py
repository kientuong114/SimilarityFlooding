from collections import namedtuple
from typing import Generator, Dict, Optional, List, KeysView

PathNode = namedtuple('PathNode', ['tag', 'attrib'])


class STNode:
    """Schema Tree Node

    A Schema Tree is a n-ary tree which represents a hierarchical data set.
    A Schema Tree should be created only via the parsing functions (e.g. parse_xml())
    Note that since Python 3.7 dicts are now ordered by default.
    This means that attrib will have the same order of the input file.

    Attributes:
        tag (str): The tag associated to the node (e.g XML tag)
        attrib: The dict of string attributes associated to the tag
        children: The dict of all children nodes, indexed by their tag
        father: Reference to the father of tha node
    """

    def __init__(self, tag: str, attrib: Dict[str, str] = None) -> None:
        self.tag: str = tag
        if not attrib:
            self.attrib: Dict[str, str] = {}
        else:
            self.attrib = attrib
        self.children: Dict[str, 'STNode'] = {}
        self.father: Optional['STNode'] = None

    def __repr__(self):
        s = f"""STNode(tag = {self.tag}, """ + \
            f"""attrib = {list(self.attrib)}, """ + \
            f"""children = {[tag for tag in self.children.keys()]}, """ + \
            f"""father = {self.father.tag if self.father else None})"""
        return s

    def add_child(self: 'STNode', child: 'STNode') -> None:
        """Adds child to the children dict of self and updates its father reference"""
        self.children.update({child.tag: child})
        child.father = self

    @classmethod
    def from_path_node(cls, path_node: PathNode) -> 'STNode':
        return STNode(path_node.tag, path_node.attrib)

    @classmethod
    def add_prefix_to_node(cls, node: 'STNode', prefix: str) -> 'STNode':
        return STNode(prefix + '.' + node.tag, node.attrib)

    @property
    def children_tags(self) -> KeysView[str]:
        return self.children.keys()


def merge_path_nodes(node1: STNode, node2: STNode) -> STNode:
    """Merges two trees by linking a node

    Args:
        node1 (STNode): first node to merge
        node2 (STNode): second node to merge

    Returns:
        STNode: merged node
    """

    if node2.tag not in node1.tag:
        raise Exception("Cannot merge: nodes have differing tags")
    if node1.father and node2.father:
        raise Exception("Cannot merge: both nodes have father")
    if len(node1.children) and len(node2.children) and node1.children != node2.children:
        raise Exception("Cannot merge: nodes have differing children")

    prefix = node1.tag[:node1.tag.rfind('.')]

    for child_tag, child in node2.children.items():
        new_child = STNode.add_prefix_to_node(child, prefix)
        node1.children.update({prefix + '.' + child_tag: new_child})
        new_child.father = node1

    return node1


def print_tree(root: STNode) -> None:
    """Print all nodes of the Schema Tree in pre-order

    Args:
        root (STNode): the root node of the tree to be printed
    """
    print(root)
    for tag in sorted(root.children.keys()):
        print_tree(root.children[tag])


def post_order_walk(root: STNode) -> Generator[STNode, None, None]:
    """Generator of STNode objects, from a post-order walk of the tree starting from root

    Args:
        root (STNode): the root node of the tree to be printed
    """

    for tag, child in root.children.items():
        yield from post_order_walk(child)
    yield root


def pre_order_walk(root: STNode) -> Generator[STNode, None, None]:
    """Generator of STNode objects, from a pre-order walk of the tree starting from root

    Args:
        root (STNode): the root node of the tree to be printed
    """

    yield root
    for tag, child in root.children.items():
        yield from post_order_walk(child)
