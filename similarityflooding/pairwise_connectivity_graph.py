import networkx as nx


def generate(G, H):

    # print(G.edges.data())
    #
    # for edge in G.edges.data():
    #     print(edge[0] + " " + edge[1] + " " + edge[2]['title'])

    graph_constructor = {}  # the keys are the title of the edges

    for edge in G.edges.data():
        if edge[2]['title'] not in graph_constructor:
            graph_constructor[edge[2]['title']] = []
            graph_constructor[edge[2]['title']].insert(0, {})
            graph_constructor[edge[2]['title']].insert(1, {})
        if edge[0] not in graph_constructor[edge[2]['title']][0]:
            graph_constructor[edge[2]['title']][0][edge[0]] = []
        graph_constructor[edge[2]['title']][0][edge[0]].append(edge[1])

    for edge in H.edges.data():
        if edge[2]['title'] not in graph_constructor:
            graph_constructor[edge[2]['title']] = []
            graph_constructor[edge[2]['title']].insert(0, {})
            graph_constructor[edge[2]['title']].insert(1, {})
        if edge[0] not in graph_constructor[edge[2]['title']][1]:
            graph_constructor[edge[2]['title']][1][edge[0]] = []
        graph_constructor[edge[2]['title']][1][edge[0]].append(edge[1])

    P = nx.DiGraph()

    # for edge_title in graph_constructor.items():
    #     print(edge_title)

    for edge_title in graph_constructor.items():
        for G_elem in edge_title[1][0].keys():
            for H_elem in edge_title[1][1].keys():
                origin_node = tuple([G_elem, H_elem])
                # print(str(G_elem) + " " + str(H_elem))
                #P.add_node(origin_node)

                for G_dest_of_elem in edge_title[1][0][G_elem]:
                    for H_dest_of_elem in edge_title[1][1][H_elem]:
                        # print(G_dest_of_elem + " " + H_dest_of_elem + " " + edge_title[0])
                        P.add_edge(origin_node, tuple([G_dest_of_elem, H_dest_of_elem]), title=edge_title[0])
                #     print()
                # print("------------------------------------")




    return P
