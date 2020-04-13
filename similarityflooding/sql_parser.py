import re
import _schema_graph_utils as sgu


def parse_sql(file_path):

    with open(file_path, 'r') as file_object:
        query = file_object.read().replace('\n', ' ').replace('\t', '')

    queries = re.sub(' +', ' ', query).strip(' ').split(';')[:-1]

    G = sql_ddl2graph(queries)

    return G


def sql_ddl2graph(data):
    import networkx as nx

    G = nx.DiGraph()

    G.add_node('Table')
    G.add_node('Column')
    G.add_node('ColumnType')

    oid = sgu.OID_generator(char='&')

    query_elements = []
    #print(data)
    for table in data:
        temp = table.split(',')
        temp[-1] = temp[-1][:-2]    # Fixing open parenthesis of last element
        query_elements.append(temp)
    #print(query_elements)

    creation_table = re.compile(r'\s*(CREATE TABLE )(?P<tableName>\w*)\s*(\()\s(?P<nameColumn>\w*)\s('
                                r'?P<SQLtype>\S+)\s*(?P<other>.*)')
    creation_column = re.compile(r'\s*(?P<nameColumn>\w*)\s(?P<SQLtype>\S+)\s*(?P<other>.*)')

    elements = {}
    for tables in query_elements:
        for rows in tables:
            match = creation_table.match(rows)
            if match is not None:
                # adding the new table
                name_table = match.group('tableName')
                oid_table = next(oid)
                key_table = str(name_table) + " ; " + str("Table")
                elements[key_table] = oid_table
                G.add_edge(oid_table, name_table, title='name')
                G.add_edge(oid_table, 'Table', title='type')
            else:
                match = creation_column.match(rows)

            # connecting the table with the column
            name_column = match.group('nameColumn')
            key_column = str(name_column) + " ; " + str("Column")
            if key_column not in elements:
                oid_column = next(oid)
                elements[key_column] = oid_column
            else:
                oid_column = elements[key_column]
            G.add_edge(oid_column, 'Column', title='type')
            G.add_edge(oid_column, name_column, title='name')
            G.add_edge(oid_table, oid_column, title='column')

            # connecting the column with its type
            name_SQLType = match.group('SQLtype')
            key_SQLType = str(name_SQLType) + " ; " + str("SQLtype")
            if key_SQLType not in elements:
                oid_SQLType = next(oid)
                elements[key_SQLType] = oid_SQLType
            else:
                oid_SQLType = elements[key_SQLType]
            G.add_edge(oid_SQLType, 'ColumnType', title='type')
            G.add_edge(oid_SQLType, name_SQLType, title='name')
            G.add_edge(oid_column, oid_SQLType, title='SQLtype')

    # sgu.schema_graph_draw(G)

    return G


def main():
    import initial_map as im
    import pairwise_connectivity_graph as pcg

    file_path = "test_schemas/test_schema_from_paper1.sql"
    G = parse_sql(file_path)
    file_path = "test_schemas/test_schema_from_paper2.sql"
    H = parse_sql(file_path)

    initial_map = im.generate(G, H)
    #print(initial_map)

    pairwise_graph = pcg.generate(G, H)
    # sgu.schema_graph_draw(pairwise_graph)
    # print(pairwise_graph.number_of_nodes())
    for edge in pairwise_graph.edges.data():
        print(str(edge[0:2]) + " ; Edge Title: " + edge[2]['title'])



if __name__ == '__main__':
    main()
