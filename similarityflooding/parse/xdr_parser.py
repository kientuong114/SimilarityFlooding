import xml.etree.ElementTree as et
from similarityflooding.utils import utils as sgu
from similarityflooding.parse import STNode
from typing import Dict

FilePath = str
blacklist = ('minOccurs', 'maxOccurs')


def parse_xdr(file_path: FilePath):
    """Return the schema tree for the xdr file located in file_path

    Args:
        file_path (str): Relative file path to the xml file
    """

    global blacklist

    xdr_tree = et.parse(file_path)
    root = xdr_tree.getroot()
    root_node = STNode.STNode.from_path_node(STNode.PathNode(root.tag, root.attrib))

    # This is a dict containing the ElementType name as key and its hierarchy
    # as value
    schema_trees: Dict[str, STNode] = {}

    for node in root.iter():
        # We navigate the tree, creating the ElementType and AttributeType trees
        # then merging them together

        if 'ElementType' in node.tag or 'AttributeType' in node.tag:
            schema_subtree = STNode.STNode.from_path_node(
                STNode.PathNode(
                    node.attrib['name'],
                    {k: v for k, v in node.attrib.items() if k != 'name' and k not in blacklist}
                )
            )

            for child in node:
                if 'description' in child.tag or 'AttributeType' in child.tag or 'ElementType' in child.tag:
                    # We currently ignore natural language descriptions and we defer the
                    # analysis of Attribute and Element Typs on successive iterations
                    continue
                child_node = STNode.STNode.from_path_node(
                    STNode.PathNode(
                        node.attrib['name'] + '.' + child.attrib['type'],
                        {k: v for k, v in child.attrib.items() if k != 'type' and k not in blacklist}
                    )
                )
                schema_subtree.add_child(child_node)
            schema_trees.update({schema_subtree.tag: schema_subtree})
        else:
            # We currently ignore other kinds of tags
            continue

    def get_last_tag(tag):
        return tag.split('.')[-1]

    # We now have a list of all ElementTypes, we now merge all entities to obtain
    # the schema.

    # We start by finding the candidate roots i.e. the trees whose root is not a leaf
    # of any other tree.

    candidate_roots = []

    for tree_tag, tree in schema_trees.items():
        pseudo_leaves = set()
        for tag, tr in schema_trees.items():
            if tag != tree_tag:
                pseudo_leaves.update(
                    map(get_last_tag, tr.children.keys())
                )
        if tree_tag not in pseudo_leaves:
            candidate_roots.append(tree)

    def tree_merge(tree):
        for child in tree.children.values():
            # Check if the children can be prolonged by merging with another tree
            tag = get_last_tag(child.tag)
            if tag in schema_trees:
                # We can merge trees:
                new_root = STNode.merge_path_nodes(child, schema_trees[tag])
                del schema_trees[tag]
                tree_merge(new_root)

    result = []

    for root in candidate_roots:
        tree_merge(root)
        result.append(root)

    assert (len(result) == 1)  # We expect to have actually

    return result[0]


def schema_tree2Graph(root: STNode):
    import networkx as nx  # type: ignore

    oid = sgu.OID_generator(char='&')
    G = nx.DiGraph()

    oid_map = {}

    for node in STNode.post_order_walk(root):
        curr_oid = next(oid)
        oid_map.update({node.tag: curr_oid})

        G.add_node(curr_oid, type='object')
        G.add_node(node.tag, type='literal')
        G.add_edge(curr_oid, node.tag, title='name')

        for i, atb in enumerate(node.attrib.keys()):
            G.add_node(atb, type='literal')
            G.add_edge(curr_oid, atb, title='attrib', prog_num=i)

        for i, child in enumerate(node.children_tags):
            # Given the post-order walk, each child will already have a node
            child_oid = oid_map[child]
            G.add_edge(curr_oid, child_oid, title='child', prog_num=i)

    return G
