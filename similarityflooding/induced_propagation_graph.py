import pairwise_connectivity_graph as pcg
import schema_graph_utils as sgu
from xml_parser import schema_tree2Graph, parse_xml
from sql_parser import parse_sql
from collections import defaultdict
from functools import partial
import initial_map as im
import networkx as nx
from math import sqrt


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

    return {label: 1 / float(len(nodes)) for label, nodes in node_by_labels.items()}


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

    node_by_labels['graphA'].update(_partition_neighbours_by_labels(nodeA, sfg.graphA))
    node_by_labels['graphB'].update(_partition_neighbours_by_labels(nodeB, sfg.graphB))

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


def generate(sfg, default_sim=0.00001, prop_func=fast_inverse_product):
    """This method generates the Induced Propagation Graph from the Pairwise Connectivity Graph

    An Induced Propagation Graph has the same nodes of the PCG but, for each edge, it instead has
    two edges of opposite direction, with attribute coeff equal to the propagation coefficient
    calculated via prop_func, the propagation coefficient function

    Args:
        sfg: the SFGraph instance which holds the current graphs
        sim: a constant value that will be used as similarity for all nodes in IPG.
        prop_func: a function which takes a SFGraphs object and returns a dictionary
                with edge labels as keys and the coefficient as value

    Returns:
        nx.MultiDiGraph: a NetworkX MultiDiGraph which represents the IPG
    """

    initial_map = im.generate(sfg.graphA, sfg.graphB)

    ipg = nx.MultiDiGraph()

    for edge in sfg.PCG.in_edges(data=True):
        if edge[0] not in ipg:
            init_sim = initial_map[edge[0]] if (edge[0] in initial_map) else default_sim
            ipg.add_node(edge[0], init_sim=init_sim, curr_sim=init_sim, next_sim=0)
        if edge[1] not in ipg:
            init_sim = initial_map[edge[1]] if (edge[1] in initial_map) else default_sim
            ipg.add_node(edge[1], init_sim=init_sim, curr_sim=init_sim, next_sim=0)
        edge_label = edge[2]['title']
        ipg.add_edge(edge[0], edge[1], coeff=prop_func(*edge[0], sfg)[edge_label])
        ipg.add_edge(edge[1], edge[0], coeff=prop_func(*edge[1], sfg)[edge_label])

    return ipg


def fixpoint_incremental(node, ipg, norm_factor=None):
    """This method is used to calculate the new similarity for a given node, with the base formula

    This method calculates the new similarity by computing the increment, given by the sum, over all neighbors,
    of their similarity multiplied by the propagation coefficient on the edge.
    This increment is summed to the current similarity of the node.

    Args:
        node: the node of which the new similarity will be calculated
        ipg: the Induced Propagation Graph
        norm_factor: a normalization factor, by which the newly computed similarity will be divided, if provided

    Returns:
        float: the similarity value after a flooding step
    """
    node_data = ipg.nodes[node]
    increment = 0
    for node1, node2, data in ipg.in_edges(node, data=True):
        increment += ipg.nodes[node1]['curr_sim'] * data['coeff']

    if norm_factor:
        return (node_data['curr_sim'] + increment) / norm_factor
    else:
        return node_data['curr_sim'] + increment


def fixpoint_A(node, ipg, norm_factor=None):
    """This method is used to calculate the new similarity for a given node, with the base formula

    This method calculates the new similarity by computing the increment, given by the sum, over all neighbors,
    of their similarity multiplied by the propagation coefficient on the edge.
    This increment is summed to the initial similarity of the node.

    Args:
        node: the node of which the new similarity will be calculated
        ipg: the Induced Propagation Graph
        norm_factor: a normalization factor, by which the newly computed similarity will be divided, if provided

    Returns:
        float: the similarity value after a flooding step
    """

    node_data = ipg.nodes[node]
    increment = 0
    for node1, node2, data in ipg.in_edges(node, data=True):
        increment += ipg.nodes[node1]['curr_sim'] * data['coeff']

    if norm_factor:
        return (node_data['init_sim'] + increment) / norm_factor
    else:
        return node_data['init_sim'] + increment


def fixpoint_B(node, ipg, norm_factor=None):
    """This method is used to calculate the new similarity for a given node, with the base formula

    This method calculates the new similarity by computing the increment, given by the sum, over all neighbors,
    of their current similarity plus their initial similarity, multiplied by the propagation coefficient on the edge.
    This increment is the resulting similarity.

    Args:
        node: the node of which the new similarity will be calculated
        ipg: the Induced Propagation Graph
        norm_factor: a normalization factor, by which the newly computed similarity will be divided, if provided

    Returns:
        float: the similarity value after a flooding step
    """

    node_data = ipg.nodes[node]
    increment = 0
    for node1, node2, data in ipg.in_edges(node, data=True):
        increment += (ipg.nodes[node1]['curr_sim'] + ipg.nodes[node1]['init_sim']) * data['coeff']

    if norm_factor:
        return increment / norm_factor
    else:
        return increment


def fixpoint_C(node, ipg, norm_factor=None):
    """This method is used to calculate the new similarity for a given node, with the base formula

    This method calculates the new similarity by computing the increment, given by the sum, over all neighbors,
    of their current similarity plus their initial similarity, multiplied by the propagation coefficient on the edge.
    This increment is summed to the sum of the initial similarity and the current similarity.

    Args:
        node: the node of which the new similarity will be calculated
        ipg: the Induced Propagation Graph
        norm_factor: a normalization factor, by which the newly computed similarity will be divided, if provided

    Returns:
        float: the similarity value after a flooding step
    """

    node_data = ipg.nodes[node]
    increment = 0
    for node1, node2, data in ipg.in_edges(node, data=True):
        increment += (ipg.nodes[node1]['curr_sim'] + ipg.nodes[node1]['init_sim']) * data['coeff']

    if norm_factor:
        return (node_data['init_sim'] + node_data['curr_sim'] + increment) / norm_factor
    else:
        return node_data['init_sim'] + node_data['curr_sim'] + increment


def flooding_step(ipg, fixpoint_formula, epsilon=0.0002):
    """This method is used to execute a single step of the flooding algorithm.

    This method computes, for each node, the new similarity by using fixpoint_formula and assigns the new
    value to the new_sim field of the node.

    After each node has been passed over, the new similarity is normalized by dividing by the greatest new
    similarity seen and then assigned to the curr_sim field of the node.

    If the square root of the sum of squares of all the similarity differences (between the new one and the old one)
    is greater than epsilon, then this method returns False, otherwise it returns True.

    In other words, if the euclidean norm of the similarity difference vector is less than epsilon, the computation is to be stopped.

    Args:
        ipg: the Induced Propagation Graph
        fixpoint_formula: the function used to calculate the new similarity
        epsilon: the value of the euclidean norm of the similarity difference vector below which the algorithm is stopped.

    Returns:
        boolean: True if the computation should continue, otherwise False.
    """

    max_sim = 0
    delta_norm = 0
    for node, node_data in ipg.nodes(data=True):
        new_sim = fixpoint_formula(node, ipg)
        max_sim = max(max_sim, new_sim)
        nx.set_node_attributes(ipg, {node: new_sim}, 'next_sim')

    for node, node_data in ipg.nodes(data=True):
        new_curr_sim = node_data['next_sim'] / max_sim
        delta_norm += (node_data['curr_sim'] - new_curr_sim) ** 2
        nx.set_node_attributes(ipg, {node: new_curr_sim}, 'curr_sim')

    if sqrt(delta_norm) < epsilon:
        return False

    return True


def similarityFlooding(sf, max_steps=1000, verbose=False, fixpoint_formula=fixpoint_incremental):
    """This method executes the similarity flooding algorithm, given SFGraphs instance containing at least the starting Graphs.

    This method generates the Pairwise Connectivity Graph and the Induced Propagation Graph, if not already present in sf.
    It then computes at most max_steps of the flooding algorithm by calling flooding_step.
    The algorithm stop either if max_steps have been executed, or if flooding_step returned false, meaning that the precision bound
    has been reached.

    Args:
        sf: the SFGraphs instance which contains at least the starting Graphs
        max_steps: the maximum number of steps for which to execute the algorithm
        verbose: if True, debug messages will be printed
        fixpoint_formula: a function taking a node and an Induced Propagation Graph and returns the new similarity value for that node
    """

    if not sf.PCG:
        sf.PCG = pcg.generate(sf.graphA, sf.graphB)
    if not sf.IPG:
        sf.IPG = generate(sf)

    if verbose:
        print("INITIAL GRAPHS")
        print("---")
        print("PAIRWISE CONNECTIVITY GRAPH")
        for edge in sf.PCG.in_edges(data=True):
            print(edge)
        for edge in sf.PCG.out_edges(data=True):
            print(edge)
        print("---")
        print("INDUCED PROPAGATION GRAPH")
        for node in sf.IPG.nodes(data=True):
            print(node)
        for edge in sf.IPG.in_edges(data=True):
            print(edge)
        for edge in sf.IPG.out_edges(data=True):
            print(edge)
        print("---")
        print("Starting computation of similarity flooding...")

    for i in range(max_steps):
        cont = flooding_step(sf.IPG, fixpoint_formula)
        if verbose:
            print("---")
            print(f"INDUCED PROPAGATION GRAPH AT STEP {i + 1}")
            for node in sorted(sf.IPG.nodes(data=True), key=lambda x: x[1]['curr_sim']):
                print(node)
        if not cont:
            print("Terminated: residual vector has length less than epsilon")
            break
    print("Terminated: max steps reached")


if __name__ == "__main__":
    G1 = schema_tree2Graph(parse_xml('test_schemas/test_schema.xml'))
    G2 = schema_tree2Graph(parse_xml('test_schemas/test_schema_2.xml'))
    similarityFlooding(SFGraphs(G1, G2), max_steps=1000, verbose=True, fixpoint_formula=fixpoint_incremental)
