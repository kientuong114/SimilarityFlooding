import pairwise_connectivity_graph as pcg
import _schema_graph_utils as sgu
from xml_parser import schema_tree2Graph, parse_xml
from collections import defaultdict
from functools import partial
import initial_map as im


class SFGraphs:
    """Similarity Flooding Graphs class

    This class holds a reference to all graphs necessary to apply the
    Similarity Flooding algorithm and which are created step by step.

    Attributes:
        graphA: The first networkx graph on which to apply the algorithm
        graphB: The second networkx graph on which to apply the algorithm
        PCG: The Pairwise Connectivity Graph
        IPG: The Induced Propagation Graph
    """
    def __init__(self, graphA, graphB, PCG=None, IPG=None):
        self.graphA = graphA
        self.graphB = graphB
        self.PCG = PCG
        self.IPG = IPG


def _partition_neighbours_by_labels(node, graph, bidirection=True):
    """This method queries for all neighbours of node and splits them by edge label

    Args:
        node: the node from which to query the neighbours
        graph: the graph from which the node is taken

    Returns:
        node_by_labels: a dict which has the edge labels as key and a list of the nodes
                that have node at the other end of the edge, with that given label
    """
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


def fast_inverse_product(nodeA, nodeB, sfg):
    """Algorithm to calculate the pi propagation function by Inverse Product, fast version which uses PCG

    This method computes the propagation coefficients for outward edges in the induced propagation graph.
    With fast inverse product the propagation coefficient is 1/number_of_neighbors_in_PCG

    Args:
        nodeA: the first part of the PCG node
        nodeB: the second part of the PCG node
        sfg: the SFGraph instance which holds the current graphs

    Returns:
        dict: a dict with label as key and the propagation coefficient for that label as value
    """
    PCG = sfg.PCG

    if (nodeA, nodeB) in PCG:
        node = (nodeA, nodeB)
    elif (nodeB, nodeA) in PCG:
        node = (nodeB, nodeA)
    else:
        raise ValueError("No such node in the Pairwise Connectivity Graph: ", (nodeA, nodeB))

    node_by_labels = _partition_neighbours_by_labels(node, PCG)

    return {label: 1/float(len(nodes)) for label, nodes in node_by_labels.items()}


def inverse_product(nodeA, nodeB, sfg):
    """Algorithm to calculate the pi propagation function by Inverse Product, slower but more general version.

    This method computes the propagation coefficients for outward edges in the induced propagation graph.
    The propagation coefficient, for each label, is the reciprocal of the product of cardinality (inbound or outbound)
    of node A for that label and the cardinality (in or outbound) of nodeb for that label

    Args:
        nodeA: the first part of the PCG node
        nodeB: the second part of the PCG node
        sfg: the SFGraph instance which holds the current graphs

    Returns:
        dict: a dict with label as key and the propagation coefficient for that label as value
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


def generate(sfg, sim=None, prop_func=fast_inverse_product):
    """This method generates the Induced Propagation Graph from the Pairwise Connectivity Graph

    An Induced Propagation Graph has the same nodes of the PCG but, for each edge, it instead has
    two edges of opposite direction, with attribute coeff equal to the propagation coefficient
    calculated via prop_func, the propagation coefficient function

    Args:
        sfg: the SFGraph instance which holds the current graphs
        sim: a constant value that will be used as similarity for all nodes in IPG.
                This value should be in range [0, 1]
        prop_func: a function which takes a SFGraphs object and returns a dictionary
                with edge labels as keys and the coefficient as value

    Returns:
        nx.MultiDiGraph: a NetworkX MultiDiGraph which represents the IPG
    """
    import networkx as nx

    if sim == None:
        initial_map = im.generate(sfg.graphA, sfg.graphB)
    else:
        initial_map = defaultdict(lambda: sim)
    ipg = nx.MultiDiGraph()

    for edge in sfg.PCG.in_edges(data=True):
        if edge[0] not in ipg:
            ipg.add_node(edge[0], sim=initial_map[edge[0]] if (edge[0] in initial_map) else default_sim)
        if edge[1] not in ipg:
            ipg.add_node(edge[1], sim=initial_map[edge[1]] if (edge[1] in initial_map) else default_sim)
        edge_label = edge[2]['title']
        ipg.add_edge(edge[0], edge[1], coeff=prop_func(*edge[0], sfg)[edge_label])
        ipg.add_edge(edge[1], edge[0], coeff=prop_func(*edge[1], sfg)[edge_label])

    return ipg


if __name__ == "__main__":
    G1 = schema_tree2Graph(parse_xml('test_schemas/test_schema.xml'))
    G2 = schema_tree2Graph(parse_xml('test_schemas/test_schema_2.xml'))

    pcgraph = pcg.generate(G1, G2)

    ipg = generate(SFGraphs(G1, G2, PCG=pcgraph))
    sgu.schema_graph_draw(ipg)
