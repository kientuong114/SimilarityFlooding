import re
from similarityflooding.utils import utils as sgu

def parse_sql(path):
    """Clears and returns the sql input file for sql_ddl2Graph to process

    Args:
        path (str): relative file path to the sql file

    Returns:
          queries: the sql table divided in "queries"
    """

    with open(path, 'r') as file_object:
        query = file_object.read().replace('\n', ' ').replace('\t', '')

    queries = re.sub(' +', ' ', query).strip(' ').split(';')[:-1]

    return queries


def sql_ddl2Graph(data):
    """Generates the graph from the sql parsed file.

    NOTE: some edge cases are still not implemented (primary keys and other less common cases)

    The graph is represented exactly as explained in the paper: with OIDs and the edges match the nomenclature


    Args:
        data: sql file parsed by parse_sql

    Returns:
        G: the sql file in graph form
    """
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
    G.add_node('Table', type='desc')
    G.add_node('Column', type='desc')
    G.add_node('ColumnType', type='desc')
    for tables in query_elements:
        for rows in tables:
            match = creation_table.match(rows)
            if match is not None:
                # adding the new table
                name_table = match.group('tableName')
                G.add_node(name_table, type='literal')
                oid_table = next(oid)
                G.add_node(oid_table, type='object')
                key_table = (name_table, "Table")
                elements[key_table] = oid_table
                G.add_edge(oid_table, name_table, title='name')
                G.add_edge(oid_table, 'Table', title='type')
            else:
                match = creation_column.match(rows)

            # connecting the table with the column
            name_column = match.group('nameColumn')
            G.add_node(name_column, type='literal')
            key_column = (name_column, "Column")
            if key_column not in elements:
                oid_column = next(oid)
                G.add_node(oid_column, type='object')
                elements[key_column] = oid_column
            else:
                oid_column = elements[key_column]
            G.add_edge(oid_column, 'Column', title='type')
            G.add_edge(oid_column, name_column, title='name')
            G.add_edge(oid_table, oid_column, title='column')

            # connecting the column with its type
            name_SQLType = match.group('SQLtype')
            G.add_node(name_SQLType, type='literal')
            key_SQLType = (name_SQLType, "SQLtype")
            if key_SQLType not in elements:
                oid_SQLType = next(oid)
                G.add_node(oid_SQLType, type='object')
                elements[key_SQLType] = oid_SQLType
            else:
                oid_SQLType = elements[key_SQLType]
            G.add_edge(oid_SQLType, 'ColumnType', title='type')
            G.add_edge(oid_SQLType, name_SQLType, title='name')
            G.add_edge(oid_column, oid_SQLType, title='SQLtype')

    return G
