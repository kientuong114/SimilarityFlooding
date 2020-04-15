import networkx as nx


def generate(G, H):

    # info about pairwise_graph_constructor: it's a dict where the keys are the title of the edges;
    #   each key has as value a list made of two dicts, each for the two graphs;
    #   the key of each dict is the node from which that edge leaves,
    #   its values is a list of the nodes to which it goes to
    # pairwise_graph_constructor is just used to facilitate the build of the pairwise_graph
    pairwise_graph_constructor = {}

    def build_graph_constructor(L, n_graph):
        # note networkX .data representation: edge[0] contains the origin node, edge[1] contains the destination node,
        #   edge[2] is a dict of all the parameters added to the edge. With edge[2]['title'] we can access the title
        #   we have given to that edge (e.g. "name", "type", ...)
        for edge in L.edges.data():
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

    build_graph_constructor(G, 0)
    build_graph_constructor(H, 1)

    P = nx.DiGraph()     # The Pairwise Connectivity Graph

    for edge_title in pairwise_graph_constructor.items():
        for G_elem in edge_title[1][0].keys():
            for H_elem in edge_title[1][1].keys():
                origin_node = tuple([G_elem, H_elem])
                for G_dest_of_elem in edge_title[1][0][G_elem]:
                    for H_dest_of_elem in edge_title[1][1][H_elem]:
                        P.add_edge(origin_node, tuple([G_dest_of_elem, H_dest_of_elem]), title=edge_title[0])

    return P
