import networkx as nx


def compress_graph(graph):
    """Removes the OIDs from the graph and makes all node identifiable by their names

    This function is used to explore various options in the performance assessment of the
    similarity flooding algorithm. The original graph is modified and a new graph is returned.

    Args:
        graph: The NewtorkX MultiDiGraph object which has to be compressed
    """

    mapping = {}
    to_delete = set()
    for node in graph.nodes.items():
        node_dict = node[1]
        if node_dict['type'] == 'object':
            name = list(filter(lambda x: x[2]['title'] == 'name', graph.out_edges(node[0], data=True)))[0][1]
            mapping.update({node[0]: name})  # Change OID to its name
            graph.remove_edge(node[0], name)
            to_delete.add(name)
    graph.remove_nodes_from(to_delete)
    return nx.relabel_nodes(graph, mapping)
