import pairwise_connectivity_graph as pcg
import _schema_graph_utils as sgu
from xml_parser import schema_tree2Graph, parse_xml
from collections import defaultdict
from enum import Enum, auto
from functools import partial

class PropFunc(Enum):
    FAST_INVERSE_PROD = auto()
    INVERSE_PROD = auto()
    INVERSE_AVG = auto()
    INVERSE_TOT_PROD = auto()
    INVERSE_TOT_AVG = auto()
    STOCHASTIC = auto()
    CONSTANT = auto()

class SimilarityFlooding:
    def __init__(self, graphA, graphB, PCG=None, IPG=None):
        self.graphA = graphA
        self.graphB = graphB
        self.PCG = PCG
        self.IPG = IPG

def _partition_neighbours_by_labels(node, graph, bidirection=True):
    node_by_labels = defaultdict(list)

    if bidirection:
        for *edge, data_dict in graph.in_edges(node, data=True):
            node_by_labels[data_dict['title']].append(edge[0])
        for *edge, data_dict in graph.out_edges(node, data=True):
            node_by_labels[data_dict['title']].append(edge[1])
    else:
        for *edge, data_dict in graph.edges(node, data=True):
            node_by_labels[data_dict['title']].append(edge[0])

    return node_by_labels

def fast_inverse_product(nodeA, nodeB, PCG):

    if (nodeA, nodeB) in PCG:
        node = (nodeA, nodeB)
    elif (nodeB, nodeA) in PCG:
        node = (nodeB, nodeA)
    else:
        raise ValueError("No such node in the Pairwise Connectivity Graph: ", (nodeA, nodeB))

    node_by_labels = _partition_neighbours_by_labels(node, PCG)

    return {label: 1/float(len(nodes)) for label, nodes in node_by_labels.items()}

def inverse_product(nodeA, graphA, nodeB, graphB):
    """

    This function computes the pi-function of similarity propagation
    via inverse product for all common labels.

    """

    node_by_labels = {'graphA': {}, 'graphB': {}}

    node_by_labels['graphA'].update(_partition_neighbours_by_labels(nodeA, graphA))
    node_by_labels['graphB'].update(_partition_neighbours_by_labels(nodeB, graphB))

    label_set_A = set(node_by_labels['graphA'].keys())
    label_set_B = set(node_by_labels['graphB'].keys())

    common_labels = set.intersection(label_set_A, label_set_B)

    label_coeffs = {}

    for label in common_labels:
        card_A = len(node_by_labels['graphA'][label])
        card_B = len(node_by_labels['graphB'][label])
        prop_coeff = 1 / float(card_A * card_B)
        label_coeffs.update({label: prop_coeff})

    return label_coeffs

def generate(sf, default_sim=1.0, prop_method=PropFunc.FAST_INVERSE_PROD):
    import networkx as nx

    if prop_method == PropFunc.FAST_INVERSE_PROD:
        prop_func = partial(fast_inverse_product, PCG=sf.PCG)
    elif prop_method == PropFunc.INVERSE_PROD:
        prop_func = partial(inverse_product, graphA=sf.graphA, graphB=sf.graphB)
    else:
        raise ValueError(f"Propagation function {prop_coeff} not yet implemented")

    ipg = nx.MultiDiGraph()

    for edge in sf.PCG.in_edges(data=True):
        if edge[0] not in ipg:
            ipg.add_node(edge[0], sim=default_sim)
        if edge[1] not in ipg:
            ipg.add_node(edge[1], sim=default_sim)
        edge_label = edge[2]['title']
        ipg.add_edge(edge[0], edge[1], coeff=prop_func(*edge[0])[edge_label])
        ipg.add_edge(edge[1], edge[0], coeff=prop_func(*edge[1])[edge_label])

    return ipg

if __name__ == "__main__":
    G1 = schema_tree2Graph(parse_xml('test_schemas/test_schema.xml'))
    G2 = schema_tree2Graph(parse_xml('test_schemas/test_schema_2.xml'))

    pcgraph = pcg.generate(G1, G2)

    ipg = generate(SimilarityFlooding(G1, G2, pcgraph))
    sgu.schema_graph_draw(ipg)
