import networkx as nx


def generate(G1, G2):
    """This method generates the Pairwise Connectivity Graph from two graphs

    The pairwise connectivity graph is defined in the paper as follows: ((x; y); p; (x0 ; y0)) ∈ PCG(A; B) <=>
    (x; p; x0) ∈ A and (y; p; y0) ∈ B. Each node from A which has an outer edge p is combined with other node
    from B with outer edge p, and they point to other combination of nodes A and B that have an incoming edge p.
    It is used to generate the induced propagation graph, which is then used to calculate the SF of the nodes

    Args:
        G1: first input graph
        G2: second input graph

    Returns:
        P: a NetworkX MultiDiGraph which represents the PCG
    """

    pcg_constructor = generate_pairwise_graph_constructor(G1, G2)

    PCG = nx.DiGraph()     # The Pairwise Connectivity Graph

    for edge_title in pcg_constructor.items():
        for G_elem in edge_title[1][0].keys():
            for H_elem in edge_title[1][1].keys():
                origin_node = (G_elem, H_elem)
                for G_dest_of_elem in edge_title[1][0][G_elem]:
                    for H_dest_of_elem in edge_title[1][1][H_elem]:
                        PCG.add_edge(origin_node, (G_dest_of_elem, H_dest_of_elem), title=edge_title[0])

    return PCG


def generate_pairwise_graph_constructor(G1, G2):
    """This method generates a data structure that is used to more easily build the PCG

    The pairwise_graph_constructor is a Dict where the keys are the title of the edges;
    each key has as value a list made of two dicts, each for each input graph;
    the key of each dict is the node from which the edge leaves,
    and its value is a list of the nodes to which that node is connected to

    Args:
        G1: first input graph
        G2: second input graph

    Returns:
        pairwise_graph_constructor: as explained above

    """
    pairwise_graph_constructor = {}
    build_graph_constructor(G1, 0, pairwise_graph_constructor)
    build_graph_constructor(G2, 1, pairwise_graph_constructor)

    return pairwise_graph_constructor


def build_graph_constructor(G, n_graph, pairwise_graph_constructor):
    """This method generates the pairwise_graph_constructor dict

    Args:
        G: input graph
        n_graph: 0 if it's the first input graph, 1 if it is the second
        pairwise_graph_constructor: the dict in which to place the values

    """

    # note networkX .data representation: edge[0] contains the origin node, edge[1] contains the destination node,
    #   edge[2] is a dict of all the parameters added to the edge. With edge[2]['title'] we can access the title
    #   we have given to that edge (e.g. "name", "type", ...)
    for edge in G.edges.data():
        edge_title = edge[2]['title']

        if edge_title not in pairwise_graph_constructor:  # if the key is not in pairwise_graph_constructor, add it
            pairwise_graph_constructor[edge_title] = []
            L_edge_with_title = pairwise_graph_constructor[edge_title]
            L_edge_with_title.insert(0, {})
            L_edge_with_title.insert(1, {})
        L_edge_with_title = pairwise_graph_constructor[edge_title]
        if edge[0] not in L_edge_with_title[n_graph]:     # if the node has not appeared yet as source, add it
            L_edge_with_title[n_graph][edge[0]] = []
        L_edge_with_title[n_graph][edge[0]].append(edge[1])
