import xml.etree.ElementTree as et
from collections import namedtuple

class SchemaNode:
    # Represents a node of the schema tree

    def __init__(self, tag, attrib = None):
        self.tag = tag
        self.attrib = attrib
        self.children = {}
        self.father = None

    def __repr__(self):
        s = f"""SchemaNode(tag = {self.tag}, attrib = {list(self.attrib)},""" +\
                    f"""children = {[tag for tag in self.children.keys()]}, father = {self.father.tag if self.father else None})"""
        return s

    def addChild(self, child):
        self.children.update({child.tag: child})
        child.father = self

    @property
    def childrenTags(self):
        return self.children.keys()

    @staticmethod
    def printTree(root):
        print(root)
        for tag in sorted(root.children.keys()):
            SchemaNode.printTree(root.children[tag])


def parse_xml(file_path):
    PathNode = namedtuple('PathNode', ['tag', 'attrib'])
    def leafPaths(root, path = []):
        # Generator of all root-leaf paths
        path = list(path)
        path.append(PathNode(root.tag, set(root.keys())))
        if not list(root):
            # Doesn't have children
            yield path
        else:
            for child in root:
                yield from leafPaths(child, path)

    xml_tree = et.parse(file_path)
    root = xml_tree.getroot()

    schema_tree = SchemaNode(root.tag, attrib = set(root.keys()))
    g = leafPaths(root)

    for path in g:
        curr = schema_tree
        for node in path[1:]:
            if node.tag not in curr.childrenTags:
                succ = SchemaNode(node.tag, attrib = node.attrib)
                curr.addChild(succ)
            else:
                succ = curr.children[node.tag]
                succ.attrib = succ.attrib.union(node.attrib)
            succ = curr
    SchemaNode.printTree(schema_tree)

if __name__ == "__main__":
    parse_xml('test.xml')
