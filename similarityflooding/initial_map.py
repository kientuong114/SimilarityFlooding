from fuzzywuzzy import fuzz


def generate(G1, G2):
    """This method generates the bare similarity values (initial_map) for all the nodes combination of the
    two input graphs

    It is used to calculate the initial SF values of each node, from which then iterate through the algorithm

    The initial similarity values can range from 0 (minimum) to 1 (maximum)

    NOTES: currently it excluded all the OID from the initial values generations, and uses fuzzywuzzy in its
    most simplistic way to generate the similarities. Also, as a test, we included the "string" and "varchar"
    similarity as the maximum similarity possible (1), while the rest are computed with fuzzywuzzy.

    Args:
        G1: first input graph
        G2: second input graph

    Returns:
        IM: initial_map
    """

    IM = {}
    for g_node in G1.nodes:
        if g_node[0] != '&':
            for h_node in G2.nodes:
                if h_node[0] != '&':
                    # In the first if we can add the options of most common values that we consider similar/identical
                    if g_node == "string" and h_node[0:7] == "varchar":
                        IM[(g_node, h_node)] = 1
                    elif g_node == "int" and h_node[0:7] == "varchar" or g_node == "string" and h_node == "int":
                        IM[(g_node, h_node)] = 0
                    else:
                        val = fuzz.ratio(g_node.lower(), h_node.lower())
                        IM[tuple([g_node, h_node])] = val / 100

    return IM


def print_IM(IM):
    """Prints each element of IM and its values line by line

    Args:
        IM: initial map
    """
    for comb in IM.items():
        print(comb)
