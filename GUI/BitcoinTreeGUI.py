import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import networkx as nx
from Utils import tree_builder as tb, tree_visualizer as tv, helpers
from Utils.logger import log_error, log_exception, log_info, log_alert
from Utils.bitcoin_ssh_client import BitcoinSSHClient
from transaction_total import TX, SegWitTx
import os
from dotenv import load_dotenv
import threading
from main import __version__, __author__, __program_name__, __description__, __url__


class BitcoinTreeGUI:
    def __init__(self, master):
        self.master = master
        master.title("Bitcoin Transaction Tree Builder")
        master.geometry("800x700")  # Dimensione iniziale della finestra

        self.log_text_widget = None  # Initialize to None

        self.create_widgets()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # Input Frame - Contiene tutti gli input e i bottoni di controllo
        input_frame = tk.Frame(self.master, padx=15, pady=15, bd=2, relief="groove")
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Configura le colonne per un allineamento migliore
        input_frame.grid_columnconfigure(
            0, weight=0
        )  # Colonna per le label, non espandibile
        input_frame.grid_columnconfigure(
            1, weight=1
        )  # Colonna per gli input, espandibile
        input_frame.grid_columnconfigure(
            2, weight=0
        )  # Colonna per i bottoni, non espandibile

        # Transaction ID
        tk.Label(input_frame, text="Transaction ID:").grid(
            row=0, column=0, sticky="w", pady=5, padx=5
        )
        self.txid_entry = tk.Entry(input_frame, width=60)
        self.txid_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        # Tree Height
        tk.Label(input_frame, text="Tree Height (optional):").grid(
            row=1, column=0, sticky="w", pady=5, padx=5
        )
        self.height_entry = tk.Entry(input_frame, width=60)
        self.height_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        # SSH and Testnet Checkbuttons
        self.ssh_var = tk.BooleanVar()
        self.ssh_check = tk.Checkbutton(input_frame, text="Use SSH", var=self.ssh_var)
        self.ssh_check.grid(row=2, column=0, sticky="w", pady=5, padx=5)

        self.testnet_var = tk.BooleanVar()
        self.testnet_check = tk.Checkbutton(
            input_frame, text="Use Testnet", var=self.testnet_var
        )
        self.testnet_check.grid(row=2, column=1, sticky="w", pady=5, padx=5)

        # Buttons Frame (per raggruppare Build Tree, Info, Exit)
        buttons_frame = tk.Frame(input_frame)
        buttons_frame.grid(
            row=3, column=0, columnspan=2, pady=10
        )  # Centrato sotto gli input

        self.build_button = tk.Button(
            buttons_frame,
            text="Build Tree",
            command=self.start_build_tree_thread,
            width=15,
            height=2,
        )
        self.build_button.pack(side=tk.LEFT, padx=10)

        self.info_button = tk.Button(
            buttons_frame, text="Info", command=self.display_info, width=15, height=2
        )
        self.info_button.pack(side=tk.LEFT, padx=10)

        self.exit_button = tk.Button(
            buttons_frame, text="Exit", command=self.on_closing, width=15, height=2
        )
        self.exit_button.pack(side=tk.LEFT, padx=10)

        # Log Frame
        log_frame = tk.LabelFrame(
            self.master, text="Logs", padx=10, pady=10, bd=2, relief="groove"
        )
        log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False, padx=10, pady=5)

        self.log_text_widget = tk.Text(
            log_frame, height=8, state="disabled", wrap="word"
        )
        self.log_text_widget.pack(fill=tk.BOTH, expand=True)
        # Configure tags for colors
        self.log_text_widget.tag_config("red", foreground="red")
        self.log_text_widget.tag_config("green", foreground="green")
        self.log_text_widget.tag_config("blue", foreground="blue")
        self.log_text_widget.tag_config("cyan", foreground="cyan")
        self.log_text_widget.tag_config("purple", foreground="purple")

        # Matplotlib Canvas Frame
        self.canvas_frame = tk.Frame(self.master, bd=2, relief="groove")
        self.canvas_frame.pack(
            side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10
        )

        self.figure = plt.Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # AGGIUNGI LA TOOLBAR DI NAVIGAZIONE QUI
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.canvas_frame)
        self.toolbar.update()
        self.toolbar.pack(
            side=tk.BOTTOM, fill=tk.X
        )  # Posiziona la toolbar sotto il canvas

    def log_message(self, message, color="black"):
        if self.log_text_widget:
            self.log_text_widget.config(state="normal")
            self.log_text_widget.insert(tk.END, message + "\n", color)
            self.log_text_widget.config(state="disabled")
            self.log_text_widget.see(tk.END)  # Auto-scroll to the end

    def display_info(self):
        self.log_text_widget.config(state="normal")
        self.log_text_widget.delete("1.0", tk.END)
        self.log_text_widget.config(state="disabled")
        self.log_message("[INFO] Displaying program information:", "green")
        self.log_message(f"Name: {__program_name__}", "blue")  # Program Name
        self.log_message(f"Version: {__version__}", "blue")  # Version
        self.log_message(f"Autor: {__author__}", "blue")  # Author
        self.log_message(f"Description: {__description__}", "blue")  # Description
        self.log_message(f"Github: {__url__}", "blue")  # Github URL

    def start_build_tree_thread(self):
        tx_id = self.txid_entry.get().strip()
        height_str = self.height_entry.get().strip()
        ssh = self.ssh_var.get()
        testnet = self.testnet_var.get()

        if not tx_id:
            messagebox.showerror("Input Error", "Transaction ID cannot be empty.")
            log_error("Transaction ID cannot be empty.")
            self.log_message("[ERROR] Transaction ID cannot be empty.", "red")
            return

        self.clear_plot()
        self.log_text_widget.config(state="normal")
        self.log_text_widget.delete("1.0", tk.END)
        self.log_text_widget.config(state="disabled")
        self.log_message("[INFO] Starting tree building process...", "green")

        # Disable buttons during processing
        self.build_button.config(state="disabled")
        self.info_button.config(state="disabled")

        # Use a thread for the long-running operation
        thread = threading.Thread(
            target=self.build_tree, args=(tx_id, height_str, ssh, testnet)
        )
        thread.daemon = True  # Allow thread to exit when the main program exits
        thread.start()  # Start the thread

    def build_tree(self, tx_id, height_str, ssh, testnet):
        try:
            altezza = int(height_str) if height_str else None
            if not altezza:
                self.log_message(
                    "[ALERT] Height not provided. The entire transaction history will be calculated",
                    "purple",
                )  # Alert message
            # Handle SSH and Testnet conflict
            if ssh and testnet:
                self.log_message(
                    "[ALERT] Cannot use SSH and Testnet together. Using TESTNET.",
                    "purple",
                )  # Alert message
                ssh = False
                testnet = True

            client = None
            if ssh:
                load_dotenv()
                HOST = os.getenv("BITCOIN_HOST")
                USER = os.getenv("USER_SSH")
                KEY_FILE = os.getenv("KEY_FILE")

                if not HOST or not USER or not KEY_FILE:
                    self.log_message(
                        "[ERROR] Environment variables not set for SSH. Ensure HOST, USER, and KEY_FILE are configured.",
                        "red",
                    )  # Error message
                    messagebox.showerror(
                        "SSH Error", "Environment variables for SSH are not set."
                    )
                    log_error(
                        "Environment variables for SSH are not set. Ensure HOST, USER, and KEY_FILE are configured."
                    )
                    # Re-enable buttons
                    self.build_button.config(state="normal")
                    self.exit_button.config(state="normal")
                    self.info_button.config(state="normal")
                    return
                self.log_message(
                    "[INFO] Connecting to Bitcoin full-node via SSH", "green"
                )  # Info message
                log_info("Connecting to Bitcoin full-node via SSH")  # Log info
                client = BitcoinSSHClient(
                    host=HOST, user=USER, key_filename=KEY_FILE
                )  # SSH client connection
            elif not testnet:  # Only if not testnet, indicate standard blockchain
                self.log_message(
                    "[ALERT] Not using Testnet. Will use the standard blockchain.",
                    "purple",
                )  # Alert message

            if ssh:
                self.log_message(
                    "[INFO] Retrieving transactions via SSH...", "green"
                )  # Info message
            elif testnet:
                self.log_message(
                    "[INFO] Retrieving transactions from Testnet API...", "green"
                )
            else:  # Default to Mempool API if neither SSH nor Testnet
                self.log_message(
                    "[INFO] Retrieving transactions from Mempool API...", "green"
                )
            tx_hex_stream = helpers.get_tx_tot(
                tx_id,
                ssh,
                client if ssh else None,
                testnet,
                log_func=self.log_message,
                gui=True,
            )  # Get transaction via Mempool API

            if SegWitTx.isSegWit(tx_hex_stream):  # Check if SegWit transaction
                tx = SegWitTx.parse(tx_hex_stream, tx_id)  # Parse as SegWit transaction
            else:
                tx = TX.parse(tx_hex_stream, tx_id)  # Parse as standard transaction

            tree = None
            if altezza:
                tree = tb.TreeBuilder.buildTree(
                    tx,
                    altezza,
                    ssh,
                    testnet,
                    None if not ssh else client,
                    log_func=self.log_message,
                    gui=True,
                )
            else:
                altezza = float("inf")  # Set to infinity if height not specified
                tree = tb.TreeBuilder.buildTree(
                    tx,
                    altezza,
                    ssh,
                    testnet,
                    None if not ssh else client,
                    log_func=self.log_message,
                    gui=True,
                )

            self.log_message("[INFO] Tree built successfully.", "green")  # Info message
            log_info("Successfully built tree")  # Log info

            if client:
                client.close()  # Close SSH client
                self.log_message(
                    "[INFO] Closed SSH connection to full-node.", "green"
                )  # Info message
                log_info("Closed SSH connection to full-node")  # Log info

            # Visualize the tree
            # self.log_message("[INFO] Visualizing the tree...", "blue")
            self.display_tree(tree)  # Display the generated tree
            # self.log_message("[INFO] Tree visualization complete.", "green")

        except Exception as e:
            self.log_message(f"[ERROR] An error occurred, see the log: {e}", "red")
            log_exception(e)  # Log the exception
            messagebox.showerror("Error", f"An error occurred, see the log: {e}")
        finally:
            self.build_button.config(state="normal")
            self.exit_button.config(state="normal")
            self.info_button.config(state="normal")

    def clear_plot(self):
        self.ax.clear()
        self.canvas.draw_idle()

    def display_tree(self, tree_root):
        self.ax.clear()  # Clear previous plot
        nx_tree = tv.build_nx_tree(tree_root)  # Build NetworkX tree

        pos = nx.drawing.nx_agraph.graphviz_layout(nx_tree, prog="dot")
        # Inverti l'asse Y per un layout più intuitivo (radice in alto)
        pos = {node: (x, -y) for node, (x, y) in pos.items()}
        labels = nx.get_node_attributes(nx_tree, "label")
        colors = nx.get_node_attributes(nx_tree, "color")
        border_thicknesses = nx.get_node_attributes(nx_tree, "linewidth")

        node_colors = [colors[node] for node in nx_tree.nodes()]
        node_border_thicknesses = [border_thicknesses[node] for node in nx_tree.nodes()]

        nx.draw(
            nx_tree,
            pos,
            with_labels=True,
            labels=labels,
            linewidths=node_border_thicknesses,
            node_size=2000,
            node_color=node_colors,
            edgecolors="black",
            font_size=8,
            ax=self.ax,
        )

        self.ax.set_title(
            "Click on a node for see the transaction details in JSON format",
            fontsize=10,
        )

        # Legend
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
        self.ax.legend(handles=legend_handles, loc="upper right", fontsize=8)
        self.ax.axis("off")  # Rimuovi gli assi per una visualizzazione più pulita
        self.figure.tight_layout()  # Adatta i margini per evitare tagli
        self.canvas.draw()  # Disegna il canvas

        # >>>>>> INIZIO MODIFICA PER IL RESET CORRETTO <<<<<<
        # Ottieni i limiti correnti degli assi dopo il disegno
        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()

        # Aggiungi un piccolo padding per non tagliare i nodi ai bordi
        padding_x = (x_max - x_min) * 0.05  # 5% di padding
        padding_y = (y_max - y_min) * 0.05  # 5% di padding

        self.ax.set_xlim(x_min - padding_x, x_max + padding_x)
        self.ax.set_ylim(y_min - padding_y, y_max + padding_y)

        # Assicurati che Matplotlib registri questa come la vista "home"
        self.canvas.draw()
        self.toolbar.push_current()  # Forza la toolbar a salvare la vista corrente come "home"
        # >>>>>> FINE MODIFICA PER IL RESET CORRETTO <<<<<<

        # Connect click event to the Matplotlib canvas
        def on_click(event):
            if event.inaxes != self.ax:
                return
            click_x, click_y = event.xdata, event.ydata
            # Considera tutti i nodi e le loro posizioni
            for node, (x, y) in pos.items():
                # Calcola la distanza dal clic al centro del nodo
                dist = ((click_x - x) ** 2 + (click_y - y) ** 2) ** 0.5
                # Se il clic è sufficientemente vicino al nodo
                if (
                    dist < 15
                ):  # Radius around the node to consider a click (adjust as needed)
                    try:
                        tx_data = str(node.root)
                        coinbase = node.root.isCoinbase()
                        segwit = isinstance(node.root, SegWitTx)
                        node_uuid = labels[node]
                        self.log_message(
                            f"[ALERT] Clicked on node: {node_uuid} with TXID: {node.root.id}",
                            "purple",
                        )  # Log the clicked node
                        self.show_json_popup(
                            tx_data, node.root.id, node_uuid, coinbase, segwit
                        )
                    except Exception as e:
                        self.log_message(f"Error parsing transaction data: {e}", "red")
                    break

        self.figure.canvas.mpl_connect("button_press_event", on_click)

    def show_json_popup(
        self, json_text, tx_id, node_uuid, coinbase=False, segwit=False
    ):
        popup = tk.Toplevel(self.master)
        popup.title("Transaction Data")
        popup.geometry("600x500")

        header_info = f"Transaction ID: {tx_id}\n\n"
        header_info += (
            f"Transaction Type: {'Coinbase' if coinbase else 'No Coinbase'}\n\n"
        )
        header_info += f"SegWit: {'True' if segwit else 'False'}\n\n"
        header_info += f"Node UUID: {node_uuid}\n\n"

        text_widget = tk.Text(popup, wrap="word")
        text_widget.insert("1.0", header_info)
        text_widget.insert(tk.END, json_text)
        text_widget.config(state="disabled")
        text_widget.pack(expand=True, fill="both")

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.master.destroy()
            plt.close("all")  # Close all matplotlib figures


def main():
    root = tk.Tk()
    gui = BitcoinTreeGUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()
