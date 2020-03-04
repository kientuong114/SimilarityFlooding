import re
import pprint
import pylab

rx_dict = {
    'tableName': re.compile(r'CREATE TABLE (?P<tableName>.*)\n'),   # regex for SQL
}


def parse_sql(file_path):
    # todo: discuss a better schema to use for all parsing options
    """
    The schema is organized as a dict whose keys are the name of the corresponding tables.
    Each dict has as value a list of tuples.
    Each tuple is composed of the name of the column and of its SQLType
    :param: filepath
    :return: returns the schema
    """

    def _parse_line(line):
        for key, rx in rx_dict.items():
            match = rx.search(line)
            if match:
                return key, match

        return None, None

    schema = {}

    with open(file_path, 'r') as file_object:
        query = file_object.read().replace('\n', ' ').replace('\t', '')

    queries = re.sub(' +', ' ', query).strip(' ').split(';')[:-1]
    print(queries)

    """
    line = file_object.readline()
    while line:
        key, match = _parse_line(line)
        if key == 'tableName':
            table_name = match.group('tableName').split()[0]
            print(table_name)
            prep_table = []
            line = file_object.readline()

            while line[0] != ')':
                print(line, end='')
                prep_table.append(line.strip().replace(',', '').split(' '))
                line = file_object.readline()

            schema.setdefault(table_name, prep_table)
        line = file_object.readline()
    """

    return schema


def sql_ddl2graph(data, G):
    # todo: index nodes for now are connected to each other only for 'column' and SQLtype relations
    # todo: the nodes 'Table', 'Column', 'ColumnType' may be added in the schema from the parser to get a unique
    #   2graph for all input files type. This should also facilitate the previous to_do
    # todo: apply other libraries or external software for more beautiful graph drawings
    """
    Nodes and edges are added to G
    :param data: schema SQL of the element
    :param G: networkx's graph
    :return: None
    """
    G.add_node('Table')
    G.add_node('Column')
    G.add_node('ColumnType')

    index = 1

    for key, elements in data.items():
        print(key)
        name_elem = '&' + str(index)
        index += 1
        G.add_node(name_elem)

        G.add_node(key)
        G.add_edge(name_elem, 'Table', title='type')
        G.add_edge(name_elem, key, title='name')

        for name, SQLType in elements:
            print(name + " " + SQLType)
            name_column = '&' + str(index)  # To keep similar to the one on the paper
            index += 1
            type_column = '&' + str(index)
            index += 1

            # Creating the nodes
            G.add_node(name_column)
            G.add_node(name)
            G.add_node(type_column)
            G.add_node(SQLType)

            # Adding the edges of the elements
            G.add_edge(name_elem, name_column, title='column')
            G.add_edge(name_column, 'Column', title='type')
            G.add_edge(name_column, name, title='name')
            G.add_edge(name_column, type_column, title='SQLType')
            G.add_edge(type_column, 'ColumnType', title='type')
            G.add_edge(type_column, SQLType, title='name')

    # Displaying the graph
    pos = nx.spring_layout(G, k=3)
    edge_labels = nx.get_edge_attributes(G, 'title')
    nx.draw(G, pos, with_labels=True, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    pylab.show()


def main():
    """
    print("Please insert the file path of the SQL DLL file")
    file_path = input()
    data = parse_file(file_path)
    pprint.pprint(data)
    """
    import networkx as nx

    G = nx.DiGraph()
    sql_ddl2graph(data, G)


if __name__ == '__main__':
    main()
