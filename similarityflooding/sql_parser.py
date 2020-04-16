import re
import _schema_graph_utils as sgu
import induced_propagation_graph as ipg


def parse_sql(file_path):

    with open(file_path, 'r') as file_object:
        query = file_object.read().replace('\n', ' ').replace('\t', '')

    queries = re.sub(' +', ' ', query).strip(' ').split(';')[:-1]

    G = sql_ddl2graph(queries)

    return G


def sql_ddl2graph(data):
    import networkx as nx

    G = nx.DiGraph()

    oid = sgu.OID_generator(char='&')

    query_elements = []
    for table in data:
        temp = table.split(',')
        temp[-1] = temp[-1][:-2]    # Fixing open parenthesis of last element
        query_elements.append(temp)

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
                key_table = (name_table, "Table")
                elements[key_table] = oid_table
                G.add_edge(oid_table, name_table, title='name')
                G.add_edge(oid_table, 'Table', title='type')
            else:
                match = creation_column.match(rows)

            # connecting the table with the column
            name_column = match.group('nameColumn')
            key_column = (name_column, "Column")
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
            key_SQLType = (name_SQLType, "SQLtype")
            if key_SQLType not in elements:
                oid_SQLType = next(oid)
                elements[key_SQLType] = oid_SQLType
            else:
                oid_SQLType = elements[key_SQLType]
            G.add_edge(oid_SQLType, 'ColumnType', title='type')
            G.add_edge(oid_SQLType, name_SQLType, title='name')
            G.add_edge(oid_column, oid_SQLType, title='SQLtype')

    return G


def main():
    import initial_map as im
    import pairwise_connectivity_graph as pcg

    file_path = "test_schemas/test_schema_from_paper1.sql"
    G = parse_sql(file_path)
    file_path = "test_schemas/test_schema_from_paper2.sql"
    H = parse_sql(file_path)

    pairwise_graph = pcg.generate(G, H)

    induced_propagation_graph = ipg.generate(ipg.SimilarityFlooding(G, H, pairwise_graph))


if __name__ == '__main__':
    main()
