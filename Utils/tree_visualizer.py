import networkx as nx
import transaction_total as transaction
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO
import tkinter as tk


def add_edges(graph, node, parent=None, count=0):
    # if transaction.TX.isSegWit(node.root):
    if isinstance(node.root, transaction.SegWitTx):
        linewidth = 2
        color = "red"
    else:
        linewidth = 1
        color = "blue"
    if node.root.isCoinbase():
        linewidth = 3.5
        color = "green"
    if isinstance(node.root, transaction.SegWitTx) and node.root.isCoinbase():
        linewidth = 4
        color = "orange"
    # graph.add_node(node, label=node.root.id, color=color,linewidth=linewidth)
    graph.add_node(node, label=count, color=color, linewidth=linewidth)
    if parent is not None:
        graph.add_edge(node, parent)

    for child in node.children:
        count = count + 1
        add_edges(graph, child, node, count)


def build_nx_tree(tree_root):
    graph = nx.DiGraph()
    add_edges(graph, tree_root)
    return graph


def visualize_tree(nx_tree):
    pos = nx.drawing.nx_agraph.graphviz_layout(nx_tree, prog="dot")
    pos = {node: (x, -y) for node, (x, y) in pos.items()}
    labels = nx.get_node_attributes(nx_tree, "label")
    colors = nx.get_node_attributes(nx_tree, "color")
    border_thicknesses = nx.get_node_attributes(nx_tree, "linewidth")

    colors = [colors[node] for node in nx_tree.nodes()]
    border_thicknesses = [border_thicknesses[node] for node in nx_tree.nodes()]

    fig, ax = plt.subplots()
    nx.draw(
        nx_tree,
        pos,
        with_labels=True,
        labels=labels,
        linewidths=border_thicknesses,
        node_size=2000,
        node_color=colors,
        edgecolors="black",
        font_size=8,
        ax=ax,
    )

    # Evento di click
    def on_click(event):
        if event.inaxes != ax:
            return
        click_x, click_y = event.xdata, event.ydata
        for node, (x, y) in pos.items():
            dist = ((click_x - x) ** 2 + (click_y - y) ** 2) ** 0.5
            if dist < 15:  # raggio di tolleranza in coordinate di layout
                try:
                    tx_data = str(node.root)  # serializzazione a JSON
                    if node.root.isCoinbase():
                        coinbase = True
                    else:
                        coinbase = False
                    if isinstance(node.root, transaction.SegWitTx):
                        segwit = True
                    else:
                        segwit = False
                    show_json_popup(tx_data, node.root.id, coinbase, segwit)
                except Exception as e:
                    print(f"Parsing Error: {e}")
                break

    def show_json_popup(json_text, id, coinbase=False, segwit=False):
        popup = tk.Tk()
        popup.title("Transaction Data")
        popup.geometry("600x500")
        text = tk.Text(popup, wrap="word")
        text.insert("1.0", json_text)

        text.insert("1.0", f"Transaction ID: {id}\n\n")
        text.insert(
            "1.0", f"Transaction Type: {'Coinbase' if coinbase else 'Non Coinbase'}\n\n"
        )
        text.insert("1.0", f"SegWit: {'True' if segwit else 'False'}\n\n")
        text.config(state="disabled")
        text.pack(expand=True, fill="both")
        popup.mainloop()

    fig.canvas.mpl_connect("button_press_event", on_click)
    plt.title("Click on a node for see the transaction details in JSON format")
    # legenda
    legend_labels = {
        "red": "SegWit",
        "blue": "Non SegWit",
        "green": "Coinbase",
        "orange": "SegWit Coinbase",
    }
    legend_handles = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label=label,
            markerfacecolor=color,
            markersize=10,
        )
        for color, label in legend_labels.items()
    ]
    ax.legend(handles=legend_handles, loc="upper right")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    matplotlib.use("TkAgg")
    g = nx.bull_graph()
    visualize_tree(g)
