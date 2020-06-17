from sql_parser import sql_ddl2Graph
from sql_parser import parse_sql
import induced_propagation_graph as ipg
import schema_graph_utils as sgu
import networkx as nx


def select_filter(SF, option="marriage", verbose=True):
    """Selects the filter by adding typing the option. Currently only stable marriage is implemented

    Args:
        SF: similarity flooding output
        option: the type of filter requested
        verbose: True if the result of the single steps are requested
    Returns:
        the result of the filter
    """
    if option.lower() == "marriage":
        return filter_stable_marriage(SF, verbose)


# filter_schema contains a dict of OIDs connection as tuples and their SF values
def clear_sf(SF, min_sim=0.001):
    """This method is used to extract a reduced data structure of SF to use in the filter

    filtered_schema is a dict which has as keys tuples of OIDs, and as value their SF value

    """

    filtered_schema = {}
    for node in SF.IPG.nodes(data=True):
        # Ignores the values that are lower than min_sim, and only does the pairing with OID values
        if node[1]["curr_sim"] > min_sim and sgu.is_OID(node[0][0]) and sgu.is_OID(node[0][1]):
            filtered_schema[(node[0][0], node[0][1])] = node[1]["curr_sim"]

    return filtered_schema


def clear_sf_compressed(SF, min_sim=0.00000000000001):
    """This method is used to extract a reduced data structure of SF to use in the filter

    filtered_schema is a dict which has as keys tuples of OIDs, and as value their SF value

    """

    filtered_schema = {}
    node_attributes_A = nx.get_node_attributes(SF.graphA, 'type')
    node_attributes_B = nx.get_node_attributes(SF.graphB, 'type')
    for node in SF.IPG.nodes(data=True):
        if node[1]["curr_sim"] > min_sim and node_attributes_A[node[0][0]] == 'object' and node_attributes_B[node[0][1]] == 'object':
            filtered_schema[(node[0][0], node[0][1])] = node[1]["curr_sim"]

    return filtered_schema


def init_engagements_schemas(SF, schema1_engagements, schema2_engagements):
    """Initialized schema1_engagements and schema2_engagements used by stable marriage

    schema1_engagement keeps track of the possible pair the element from the first graph may be pair with, and
    schema2_engagement keeps track of the elements it has paired with

    schema1_engagement has as keys the nodes in SF associated with the first graph, and as value a list made of:
        [0]: None (where the current engagement element will be stored)
        [1]: tuples of sf value and the corresponding element in the second graph

    schema2_engagement has as keys the nodes in SF associated with the second graph, and as value the element to it
    is "engaged" with (initialized as None)

    Args:
        SF: The Similarity Flooding structure initialized and run
        schema1_engagements: the dict where to put the results of the first schema
        schema2_engagements: the dict where to put the results of the second schema
    """

    schema = clear_sf_compressed(SF)
    for key in schema.keys():
        if key[0] not in schema1_engagements:
            schema1_engagements[key[0]] = [None, []]
        schema1_engagements[key[0]][1].append([schema[(key[0], key[1])], key[1]])
        if key[1] not in schema2_engagements:
            schema2_engagements[key[1]] = None
    for el in schema1_engagements.values():
        el[1].sort(reverse=True)

    print(schema1_engagements)


def filter_stable_marriage(SF, verbose=True):
    """This method returns the pairs combination generated by the typical stable marriage algorithm.
    NOTE: The number of elements in the first graph has to be smaller or equal to the number of elements of the
    second graph to ensure that all the elements of the first are combined with one element of the second

    Args:
        SF: The Similarity Flooding structure initialized and run
        verbose: True if the result of the single steps are requested

    Returns:
        engagements: a list of all the pairs
    """

    schema1_engagements = {}
    schema2_engagements = {}
    init_engagements_schemas(SF, schema1_engagements, schema2_engagements)

    if verbose:
        print("Step 0 result:")
        for elem in schema1_engagements.items():
            print(elem)
        print()

    change = True
    step = 0
    while change:
        step += 1
        change = False
        for elem in schema1_engagements.items():
            if elem[1][0] is None and len(elem[1][1]) > 0:
                possible_marriages = elem[1][1]
                proposal = possible_marriages[0]
                del possible_marriages[0]
                if schema2_engagements[proposal[1]] is None:
                    schema2_engagements[proposal[1]] = (proposal[0], elem[0])
                    elem[1][0] = proposal[1]
                else:
                    if schema2_engagements[proposal[1]][0] < proposal[0]:
                        schema1_engagements[schema2_engagements[proposal[1]][1]][0] = None
                        schema2_engagements[proposal[1]] = (proposal[0], elem[0])
                        elem[1][0] = proposal[1]
                change = True

        if verbose:
            print("Step " + str(step) + " result:")
            for elem in schema1_engagements.items():
                print(elem)
            print()

    if verbose:
        print("Schema 2 engagements")
        print(schema2_engagements)

    engagements = []
    for elem in schema1_engagements.items():
        engagements.append((elem[0], elem[1][0]))
    # Adding the nodes of the second graph that have no engagement with the nodes of the first
    for elem in schema2_engagements.items():
        if elem[1] is None:
            engagements.append((None, elem[0]))

    return engagements


def print_pairs(pairs):
    print("\nFinal result after filter application:")
    for p in pairs:
        if p[0] is None:
            print("no_match_found", end="")
        else:
            print(p[0], end="")
        print(end=" <-> ")
        if p[1] is None:
            print("no_match_found")
        else:
            print(p[1])


if __name__ == "__main__":
    G1 = sql_ddl2Graph(parse_sql('test_schemas/test_schema_from_paper1.sql'))
    G2 = sql_ddl2Graph(parse_sql('test_schemas/test_schema_from_paper2.sql'))
    sf = ipg.SFGraphs(G1, G2)
    ipg.similarityFlooding(sf, max_steps=1000, verbose=False, fixpoint_formula=ipg.fixpoint_incremental)

    pairs = select_filter(sf)

    print(sgu.combine_oid_to_name_pairs(G1, G2, pairs))
