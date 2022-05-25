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
    # filename argument
    ap.add_argument("-f", 
                    "--filename", 
                    required = False, 
                    help = "The file you want to work with")
    # directory argument
    ap.add_argument("-d",
                    "--directory_name",
                    required = False,
                    help = "The directory you want to work within")
    # sort CSV by...
    ap.add_argument("-s",
                    "--sort_csv_by",
                    default = "degree_centrality",
                    help = "The centrality metric you wish to sort the data by, 'degree_centrality', 'eigenvector_centrality', or 'betweenness_centrality'")
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
def visualisation(data, filename):
    # create figure
    fig, ax = plt.subplots(1, 1, figsize=(12, 10));
    fig.tight_layout()
    # create graph from pandas edgelist
    G = nx.from_pandas_edgelist(data, "Source", "Target", ["Weight"], create_using=nx.Graph())
    # positioning method (Fruchterman-Reingold force-directed algorithm)
    pos = nx.spring_layout(G, k=0.9)
    # draw the network
    nx.draw_networkx(G, # NetworkX graph
                     ax=ax, # axes
                     pos=pos, # node positions
                     node_size=2700, # size of nodes
                     node_color="orange", # fill colour of nodes
                     edgecolors = "saddlebrown", # edge colour of nodes
                     edge_color="dimgrey", # colour of edges
                     node_shape="$\u2B2C$", # node shape = horisontal ellipse
                     width=1, # line width of edges
                     font_size=8, # font size of names
                     font_weight="bold") # font style
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
    centrality_metric = args['sort_csv_by']
    # if filename argument is given and ends with "-csv"
    if args["filename"] is not None and args["filename"].endswith(".csv"):
        # get filename
        filename = args["filename"]
        # load the file
        path = load_edgelist_filename(filename)
        # read the file
        data = read_the_csv(path)
        # make and save network visualisation
        visualisation(data, filename)
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
            visualisation(data, filename)
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
