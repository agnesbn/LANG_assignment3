"""
Network analysis
"""
""" Import relevant packages """
 # system tool
import os
 # argument parser
import argparse
 # data analysis
import pandas as pd
 # network analysis tools
import networkx as nx
 # plotting
import matplotlib.pyplot as plt
  
""" Basic functions """
# Argument parser
def parse_args():
    ap = argparse.ArgumentParser()
    """ 
    Data loading arguments 
    """
    # filename argument
    ap.add_argument("-f", 
                    "--filename", 
                    type=str,
                    required = False, 
                    help = "The file you want to work with")
    # directory argument
    ap.add_argument("-d",
                    "--directory_name",
                    type=str,
                    required = False,
                    help = "The directory you want to work within")
    
    """ 
    Data saving argument 
    """
    # sort CSV by...
    ap.add_argument("-s",
                    "--sort_csv_by",
                    type=str,
                    default = "degree_centrality",
                    help = "The centrality metric you wish to sort the data by, 'degree_centrality', 'eigenvector_centrality', or 'betweenness_centrality'")
    
    """
    Network plotting arguments
    """
    # node colour argument
    ap.add_argument("-n",
                    "--node_color",
                    default = "orange",
                    help = "The colour of the nodes in the network plot")
    # node edge colour arguement
    ap.add_argument("-c",
                    "--edgecolors",
                    default = "saddlebrown",
                    help = "The colour of the edge of the nodes in the network plot")
    # edge colour arguement
    ap.add_argument("-e",
                    "--edge_color",
                    default = "dimgrey",
                    help = "The colour of the edges (i.e. lines between nodes) in the network plot")
    # node shape arguement
    ap.add_argument("-o",
                    "--node_shape",
                    type=str,
                    default = "$\u2B2C$",
                    help = "The shape of the nodes, see documentation for matplotlib.markers to see different possibilities for marker shapes")
    # node size argument
    ap.add_argument("-z",
                    "--node_size",
                    type=int,
                    default = 2700,
                    help = "The size of the nodes")
    # edge line width argument
    ap.add_argument("-w",
                    "--width",
                    default = 1,
                    type=float,
                    help = "The line width of the edges")
    # font size argument
    ap.add_argument("-t",
                    "--font_size",
                    type=float,
                    default = 8,
                    help = "The size of the font")
    # font weight argument
    ap.add_argument("-i",
                    "--font_weight",
                    default = "heavy",
                    help = "The weight of the font")
    # node distance argument
    ap.add_argument("-k",
                    "--node_distance",
                    type=float,
                    default = 0.9,
                    help = "The distance between nodes")
    args = vars(ap.parse_args())
    return args

# Loading directory
def load_edgelist_directory(directory_name):
    # define path
    path = os.path.join("in", directory_name)
    # get list of filenames
    file_list = os.listdir(path)
    # get list of only CSV files
    clean_list = []
    for name in file_list:
        if name.endswith(".csv"):
            clean_list.append(name)
    return path, clean_list
    
# Loading an edgelist    
def load_edgelist_filename(filename):
    # get path
    path = os.path.join("in", "network_data", filename)
    return path

# Reading a CSV
def read_the_csv(path):
    # read tab-separated CSV without index column
    data = pd.read_csv(path, sep="\t", index_col=False)
    # add a new line between names, i.e. before capital letters
    data["Source"] = data["Source"].replace(r'([A-Z])', r'\n\1', regex=True)
    data["Target"] = data["Target"].replace(r'([A-Z])', r'\n\1', regex=True)
    # remove new line at the beginning of a string
    data["Source"] = data["Source"].replace(r'^\n?', r'', regex=True)
    data["Target"] = data["Target"].replace(r'^\n?', r'', regex=True)
    # remove new line between V and I in 'Ghost Henry VI'
    data["Source"] = data["Source"].replace(r'\bV\nI$', r'VI', regex=True)
    data["Target"] = data["Target"].replace(r'\bV\nI$', r'VI', regex=True)
    return data

# Edgelist visualisation
def visualisation(data, filename, node_color, edgecolors, edge_color, node_shape, node_size, width, font_size, font_weight, node_distance):
    # create figure
    fig, ax = plt.subplots(1, 1, figsize=(12, 10));
    fig.tight_layout()
    # create graph from pandas edgelist
    G = nx.from_pandas_edgelist(data, "Source", "Target", ["Weight"], create_using=nx.Graph())
    # positioning method (Fruchterman-Reingold force-directed algorithm)
    pos = nx.spring_layout(G, k=node_distance)
    # draw the network
    nx.draw_networkx(G, # NetworkX graph
                     ax=ax, # axes
                     pos=pos, # node positions
                     node_size=node_size, # size of nodes
                     node_color=node_color, # fill colour of nodes
                     edgecolors=edgecolors, # edge colour of nodes
                     edge_color=edge_color, # colour of edges
                     node_shape=node_shape, # node shape = horisontal ellipse
                     width=width, # line width of edges
                     font_size=font_size, # font size of names
                     font_weight=font_weight) # font style
    # add title
    plt.title(f"Network Analysis – {filename}", fontsize=24)
    # specify outpath
    outpath_viz = os.path.join("out", "plots", f"network_{filename[0:filename.index(f'.')]}.png")
    # save figure
    plt.savefig(outpath_viz, dpi=200, bbox_inches="tight")
    # clear and close figure
    plt.clf()
    plt.close()

# Create and save dataframe    
def csv_node(data, filename, centrality_metric):
    # create graph from pandas edgelist
    G = nx.from_pandas_edgelist(data, "Source", "Target", ["Weight"])
    # compute the degree centrality for nodes
    dg = nx.degree_centrality(G)  
    # compute the eigenvector centrality for the graph
    ev = nx.eigenvector_centrality(G)
    # compute the shortest-path betweenness centrality for nodes
    bc = nx.betweenness_centrality(G)
    # create dataframes for each centrality metric
    dg_df = pd.DataFrame(dg.items(), columns = ["name", "degree_centrality"])
    ev_df = pd.DataFrame(ev.items(), columns = ["name", "eigenvector_centrality"])
    bc_dg = pd.DataFrame(bc.items(), columns = ["name", "betweenness_centrality"])
    df = dg_df
    # merge the dataframes
    df_dgev = pd.merge_ordered(df, ev_df, left_by = "name")
    df_complete = pd.merge_ordered(df_dgev, bc_dg, left_by = "name")
    # sort dataframe by user-defined centrality metric
    output_df = df_complete.sort_values(by=[centrality_metric], ascending=False)
    # round the centrality metrics
    output_round = output_df.round(8)
    # specify outpath
    outpath_csv = os.path.join("out", "tables", f"network_{filename[0:filename.index(f'.')]}.csv")
    # save results dataframe
    output_round.to_csv(outpath_csv, index=False)

    
""" Main function"""
def main():
    # parse arguments
    args = parse_args()
    # get arguments
    centrality_metric = args['sort_csv_by']
    node_color = args["node_color"]
    edgecolors = args["edgecolors"]
    edge_color = args["edge_color"]
    node_shape = args["node_shape"]
    node_size = args["node_size"]
    width = args["width"]
    font_size = args["font_size"]
    font_weight = args["font_weight"]
    node_distance = args["node_distance"]
    # if filename argument is given and ends with "-csv"
    if args["filename"] is not None and args["filename"].endswith(".csv"):
        # get filename
        filename = args["filename"]
        # load the file
        path = load_edgelist_filename(filename)
        # read the file
        data = read_the_csv(path)
        # make and save network visualisation
        visualisation(data, filename, node_color, edgecolors, edge_color, node_shape, node_size, width, font_size, font_weight, node_distance)
        # create and save output CSV
        csv_node(data, filename, centrality_metric)
    # otherwise, if the directory argument is given
    elif args["directory_name"] is not None:
        # get directory name
        directory_name = args["directory_name"]
        # load list of edgelist names and the path to the directory
        results = load_edgelist_directory(directory_name)
        # start counter
        counter = 0
        # get number of edgelists
        lists_count = len(results[1])
        # for each filename in the list
        for filename in results[1]:
            # add 1 to the counter
            counter += 1
            # get path to edgelist
            path = f"{results[0]}/{filename}"
            # read the CSV
            data = read_the_csv(path)
            # make and save network visualisations
            visualisation(data, filename, node_color, edgecolors, edge_color, node_shape, node_size, width, font_size, font_weight, node_distance)
            # create and save output CSVs
            csv_node(data, filename, centrality_metric)
            # print message 
            print(f"[INFO] {(counter):02}/{lists_count} - {filename}")
        # print final message
        print("[INFO] Finished!")
    else:
        pass

    
if __name__ == "__main__":
    main()
