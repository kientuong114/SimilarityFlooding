import networkx as nx
import pylab


def OID_generator(char = 'a', start_num = 1):
    n = start_num
    while True:
        yield char + str(n)
        n += 1


def schema_graph_draw(G, title='title'):
    pos = nx.spring_layout(G, k=3)
    edge_labels = nx.get_edge_attributes(G, 'title')
    nx.draw(G, pos, with_labels=True, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    pylab.show()


