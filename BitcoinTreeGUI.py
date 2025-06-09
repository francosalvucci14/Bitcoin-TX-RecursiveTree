import tkinter as tk
from tkinter import ttk, messagebox
import os
from dotenv import load_dotenv
from datetime import timedelta
from timeit import default_timer as timer
import Utils.helpers as helpers
import Utils.tree_builder as tb
import Utils.tree_visualizer as tv
from transaction_total import TX,SegWitTx
from Utils.bitcoin_ssh_client import BitcoinSSHClient
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import transaction_total as transaction
import transaction_total as transaction

import matplotlib.pyplot as plt

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

def visualize_tree_in_gui(nx_tree, tk_text_widget):
    # Clear previous matplotlib figures in the widget's parent
    parent = tk_text_widget.master
    for widget in parent.winfo_children():
        if isinstance(widget, FigureCanvasTkAgg):
            widget.get_tk_widget().destroy()

    pos = nx.drawing.nx_agraph.graphviz_layout(nx_tree, prog="dot")
    pos = {node: (x, -y) for node, (x, y) in pos.items()}
    labels = nx.get_node_attributes(nx_tree, "label")
    colors = nx.get_node_attributes(nx_tree, "color")
    border_thicknesses = nx.get_node_attributes(nx_tree, "linewidth")

    colors = [colors[node] for node in nx_tree.nodes()]
    border_thicknesses = [border_thicknesses[node] for node in nx_tree.nodes()]

    fig, ax = plt.subplots(figsize=(6, 4))
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

    # Click event for nodes
    def on_click(event):
        if event.inaxes != ax:
            return
        click_x, click_y = event.xdata, event.ydata
        for node, (x, y) in pos.items():
            dist = ((click_x - x) ** 2 + (click_y - y) ** 2) ** 0.5
            if dist < 15:
                try:
                    tx_data = str(node.root)
                    coinbase = node.root.isCoinbase()
                    segwit = isinstance(node.root, transaction.SegWitTx)
                    show_json_popup_in_gui(tx_data, node.root.id, coinbase, segwit, parent)
                except Exception as e:
                    print(f"Errore nel parsing: {e}")
                break

    def show_json_popup_in_gui(json_text, id, coinbase, segwit, parent):
        popup = tk.Toplevel(parent)
        popup.title("Dati Transazione")
        popup.geometry("600x500")
        text = tk.Text(popup, wrap="word")
        text.insert("1.0", json_text)
        text.insert("1.0", f"ID Transazione: {id}\n\n")
        text.insert(
            "1.0", f"Tipo Transazione: {'Coinbase' if coinbase else 'Non Coinbase'}\n\n"
        )
        text.insert("1.0", f"SegWit: {'True' if segwit else 'False'}\n\n")
        text.config(state="disabled")
        text.pack(expand=True, fill="both")

    fig.canvas.mpl_connect("button_press_event", on_click)
    plt.title("Clicca su un nodo per vedere i dettagli JSON della transazione")
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

    # Embed the matplotlib figure in the Tkinter GUI
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def main_construction_tree(tx_id, altezza, ssh, testnet):

    while True:
        # Transaction Retrieval
        if ssh and testnet:
            helpers.color_print(
                "[ALERT] Non è possibile usare SSH e Testnet insieme. Utilizzerò TESTNET.",
                "purple",
            )
            ssh = False
            testnet = True
        if ssh:
            testnet = False
            load_dotenv()

            # Parametri di connessione
            HOST = os.getenv("BITCOIN_HOST")  # Indirizzo IP o hostname del server SSH
            USER = os.getenv("USER_SSH")  # Nome utente SSH
            KEY_FILE = os.getenv("KEY_FILE")  # Percorso della chiave privata SSH

            if not HOST or not USER or not KEY_FILE:
                helpers.color_print(
                    "[ERROR] Variabili d'ambiente non impostate. Assicurati di avere HOST, USER e KEY_FILE.",
                    "red",
                )
                exit(1)
            helpers.color_print(
                "[INFO] Connessione al full-node Bitcoin tramite SSH", "green"
            )

            client = BitcoinSSHClient(host=HOST, user=USER, key_filename=KEY_FILE)

        elif testnet:
            ssh = False
        start = timer()
        try:
            if ssh:
                tx = helpers.get_tx_ssh(tx_id, client)
            else:
                if testnet:
                    tx = helpers.get_tx_testnet(tx_id)
                else:
                    tx = helpers.get_tx(tx_id)

        except Exception as e:
            helpers.color_print(
                f"[ERROR] Errore durante il recupero della transazione: {e}", "red"
            )
            continue

        # Set Tree Height
        if altezza is not None:
            altezza = int(altezza)
            altezza_noTot = True
        else:
            altezza_noTot = False

        # Transaction Parsing
        if SegWitTx.isSegWit(tx):

            tx = SegWitTx.parse(tx, tx_id)
        else:

            tx = TX.parse(tx, tx_id)

        # Tree Building
        if not testnet and not ssh:
            if altezza_noTot == True:
                tree = tb.TreeBuilder.buildTree(tx, altezza)
            else:
                tree = tb.TreeBuilder.buildTree(tx)
        if testnet:
            if altezza_noTot == True:
                tree = tb.TreeBuilder.buildTreeTESTNET(tx, altezza)
            else:
                tree = tb.TreeBuilder.buildTreeTESTNET(tx)
        if ssh:
            if altezza_noTot == True:
                tree = tb.TreeBuilder.buildTreeSSH(tx, client, altezza)
            else:
                tree = tb.TreeBuilder.buildTreeSSH(tx, client)
        helpers.color_print("[INFO] Albero costruito con successo", "green")
        end = timer()
        elapsed_time = timedelta(seconds=end - start)
        helpers.color_print(
            f"[ALERT] Tempo impiegato per costruire l'albero: {elapsed_time}", "purple"
        )
        if ssh:
            client.close()
            helpers.color_print("[INFO] Chiudo connessione al full-node SSH", "green")

        # Tree Visualization
        nx_tree = tv.build_nx_tree(tree)
        return nx_tree  # Return the tree for GUI handling



PROGRAM_INFO = (
    "BitcoinTreeGUI\n"
    "Progetto Esame PCD - Tor Vergata\n"
    "Permette di costruire l'albero Merkle di una transazione Bitcoin.\n"
    "Inserisci il TXID, opzionalmente l'altezza, scegli SSH o Testnet e premi 'Costruisci Albero'."
)

class BitcoinTreeGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BitcoinTreeGUI")
        self.geometry("600x400")
        self.create_widgets()

    def create_widgets(self):
        # TXID
        txid_frame = ttk.Frame(self)
        txid_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(txid_frame, text="TXID:").pack(side='left')
        self.txid_entry = ttk.Entry(txid_frame)
        self.txid_entry.pack(side='left', fill='x', expand=True)

        # Altezza (opzionale)
        height_frame = ttk.Frame(self)
        height_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(height_frame, text="Altezza (opzionale):").pack(side='left')
        self.height_entry = ttk.Entry(height_frame)
        self.height_entry.pack(side='left', fill='x', expand=True)
        self.height_entry.insert(0, "")

        # Opzioni SSH / Testnet
        options_frame = ttk.LabelFrame(self, text="Opzioni")
        options_frame.pack(fill='x', padx=10, pady=5)
        self.ssh_var = tk.BooleanVar()
        self.testnet_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Usa SSH", variable=self.ssh_var).pack(side='left', padx=5)
        ttk.Checkbutton(options_frame, text="Usa Testnet", variable=self.testnet_var).pack(side='left', padx=5)

        # Pulsanti
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill='x', padx=10, pady=5)
        self.build_button = ttk.Button(buttons_frame, text="Costruisci Albero", command=self.on_build)
        self.build_button.pack(side='left', padx=5)
        self.info_button = ttk.Button(buttons_frame, text="INFO", command=self.on_info)
        self.info_button.pack(side='left', padx=5)

        # Output
        self.output_text = tk.Text(self, height=15, wrap='word', state='disabled')
        self.output_text.pack(fill='both', expand=True, padx=10, pady=5)

    def on_build(self):
        self.set_output("Costruzione dell'albero in corso...")
        txid = self.txid_entry.get().strip()
        height = self.height_entry.get().strip()
        use_ssh = self.ssh_var.get()
        use_testnet = self.testnet_var.get()

        if not txid:
            self.set_output("Errore: inserire un TXID valido.")
            return

        height_val = height if height else None
        nx_tree = main_construction_tree(txid, height_val, use_ssh, use_testnet)
        if nx_tree is not None:
            visualize_tree_in_gui(nx_tree, self.output_text)
        else:
            self.set_output("Errore durante la costruzione dell'albero.")
        self.set_output("Albero costruito con successo. Clicca sui nodi per vedere i dettagli.")
        # cancella albero dopo un'altro click

    def on_info(self):
        self.set_output(PROGRAM_INFO)

    def set_output(self, text):
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.config(state='disabled')

def main():
    # Main function to run the GUI
    app = BitcoinTreeGUI()
    app.mainloop()
    
    

if __name__ == "__main__":
    app = BitcoinTreeGUI()
    app.mainloop()
