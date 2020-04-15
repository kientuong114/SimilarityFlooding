import pairwise_connectivity_graph as pcg
import _schema_graph_utils as sgu
from xml_parser import schema_tree2Graph, parse_xml
from collections import defaultdict

def generate(pair_conn_graph, prop_coeff_function=fast_inverse_product):
    raise Exception("Not implemented yet")
    return







def fast_inverse_product(nodeA, graphA, nodeB, graphB, PCG):
    node_by_labels = defaultdict(list)

    if (nodeA, nodeB) in PCG:
        node = (nodeA, nodeB)
    elif (nodeB, nodeA) in PCG:
        node = (nodeB, nodeA)
    else:
        raise ValueError("No such node in the Pairwise Connectivity Graph: ", (nodeA, nodeB))

    for *edge, data_dict in PCG.in_edges(node, data=True):
        node_by_labels[data_dict['title']].append(edge[0])

    for *edge, data_dict in PCG.out_edges(node, data=True):
        node_by_labels[data_dict['title']].append(edge[0])

    return {label: 1/float(len(nodes)) for label, nodes in node_by_labels.items()}

def inverse_product(nodeA, graphA, nodeB, graphB, PCG):
    """

    This function computes the pi-function of similarity propagation
    via inverse product for all common labels.

    """

    node_by_labels = {'graphA': {}, 'graphB': {}}

    for *edge, data_dict in graphA.in_edges(nodeA, data=True):
        if data_dict['title'] not in node_by_labels['graphA']:
            node_by_labels['graphA'][data_dict['title']] = [edge[0]]
        else:
            node_by_labels['graphA'][data_dict['title']].append(edge[0])

    for *edge, data_dict in graphA.out_edges(nodeA, data=True):
        if data_dict['title'] not in node_by_labels['graphA']:
            node_by_labels['graphA'][data_dict['title']] = [edge[1]]
        else:
            node_by_labels['graphA'][data_dict['title']].append(edge[1])

    for *edge, data_dict in graphB.in_edges(nodeB, data=True):
        if data_dict['title'] not in node_by_labels['graphB']:
            node_by_labels['graphB'][data_dict['title']] = [edge[0]]
        else:
            node_by_labels['graphB'][data_dict['title']].append(edge[0])

    for *edge, data_dict in graphB.out_edges(nodeB, data=True):
        if data_dict['title'] not in node_by_labels['graphB']:
            node_by_labels['graphB'][data_dict['title']] = [edge[1]]
        else:
            node_by_labels['graphB'][data_dict['title']].append(edge[1])

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

if __name__ == "__main__":
    G1 = schema_tree2Graph(parse_xml('test_schemas/test_schema.xml'))
    G2 = schema_tree2Graph(parse_xml('test_schemas/test_schema_2.xml'))

    pcgraph = pcg.generate(G1, G2)

    node1 = G1.nodes
    node2 = G2.nodes

    print(inverse_product('&1', G1, '&1', G2, pcgraph))
    print(fast_inverse_product('&1', G1, '&1', G2, pcgraph))





