#!/bin/python3
from transaction_total import TX, SegWitTx
from Utils import helpers, tree_builder as tb, tree_visualizer as tv
from Utils.bitcoin_ssh_client import BitcoinSSHClient
import argparse
import os
from dotenv import load_dotenv
from timeit import default_timer as timer
from datetime import timedelta
import sys
import GUI.BitcoinTreeGUI as gui
from Utils.logger import log_info, log_alert, log_error, log_exception


__version__ = "2.2.1"
__author__ = "Franco Salvucci - Acr0n1m0"
__program_name__ = "Bitcoin Transaction Tree Builder"
__description__ = "Script to build and display Bitcoin transaction tree."
__url__ = "https://github.com/francosalvucci14/Bitcoin-TX-RecursiveTree"


def main_proc(tx_id, altezza, ssh, testnet):

    while True:
        # Transaction Retrieval
        if ssh and testnet:
            helpers.color_print(
                "[ALERT] It is not possible to use SSH and Testnet together. I will use TESTNET.",
                "purple",
            )
            log_alert(
                "[ALERT] It is not possible to use SSH and Testnet together. I will use TESTNET."
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
                    "[ERROR] Environment variables not set. Make sure you have HOST, USER and KEY_FILE.",
                    "red",
                )
                log_error(
                    "Environment variables not set. Make sure you have HOST, USER and KEY_FILE."
                )
                exit(1)
            helpers.color_print(
                "[INFO] Connecting to the Bitcoin full-node via SSH", "green"
            )
            log_info("Connecting to the Bitcoin full-node via SSH")
            client = BitcoinSSHClient(host=HOST, user=USER, key_filename=KEY_FILE)

        elif testnet:
            ssh = False
        start = timer()
        try:
            tx = helpers.get_tx_tot(tx_id, ssh, None if not ssh else client, testnet)

        except Exception as e:
            helpers.color_print(
                f"[ERROR] Error while retrieving transaction: {e}", "red"
            )
            log_exception(e)
            continue

        # Set Tree Height
        if altezza is not None:
            altezza = int(altezza)
            altezza_Tot = False
        else:
            altezza_Tot = True

        # Transaction Parsing
        if SegWitTx.isSegWit(tx):
            tx = SegWitTx.parse(tx, tx_id)
        else:
            tx = TX.parse(tx, tx_id)

        # Tree Building
        if not altezza_Tot:
            tree = tb.TreeBuilder.buildTree(
                tx, altezza, ssh, testnet, None if not ssh else client
            )
        else:
            tree = tb.TreeBuilder.buildTree(
                tx, float("inf"), ssh, testnet, None if not ssh else client
            )

        helpers.color_print("[INFO] Successfully built tree", "green")
        log_info("Successfully built tree")
        end = timer()
        elapsed_time = timedelta(seconds=end - start)
        helpers.color_print(
            f"[ALERT] Time taken to build the tree: {elapsed_time}", "purple"
        )
        if ssh:
            client.close()
            helpers.color_print("[INFO] Closing connection to full-node SSH", "green")
            log_info("Closing connection to full-node SSH")
        # Tree Visualization
        nx_tree = tv.build_nx_tree(tree)
        tv.visualize_tree(nx_tree)

        break


def print_info():
    print(f"Name: {__program_name__}")
    print(f"Version: {__version__}")
    print(f"Autor: {__author__}")
    print(f"Description: {__description__}")
    print(f"Github: {__url__}")


if __name__ == "__main__":
    # Prima parser per intercettare solo --info e --version
    pre_parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    pre_parser.add_argument("-i", "--info", action="store_true")
    pre_parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s v{version}".format(version=__version__),
    )
    pre_parser.add_argument(
        "-g",
        "--gui",
        action="store_true",
    )
    args, remaining_args = pre_parser.parse_known_args()

    if args.info:
        helpers.color_print("[INFO] Showing the program information", "green")
        print_info()
        exit(0)
    if args.gui:
        helpers.color_print(
            "[INFO] Starting the graphical interface for building the transaction tree.",
            "green",
        )
        log_info("Starting the graphical interface for building the transaction tree.")
        gui.main()

        exit(1)
    parser = argparse.ArgumentParser(description=__description__, allow_abbrev=False)

    parser.add_argument(
        "-t",
        "--txid",
        required=True,
        type=str,
        help="ID of the transaction to analyze. [REQUIRED]",
    )
    parser.add_argument(
        "-a",
        type=int,
        required=False,
        help="Height of the tree to build. If not specified, the entire transaction history will be calculated. [TYPE=%(type)s]",
    )
    parser.add_argument(
        "--ssh",
        action="store_true",
        required=False,
        help="Specify whether you want to use the version that connects to the full-node via SSH or use the mempool APIs.",
    )
    parser.add_argument(
        "--testnet",
        action="store_true",
        required=False,
        help="Specify whether you want to use the TESTNET blockchain or use the STANDARD blockchain.",
    )

    # Se non ci sono argomenti, mostra errore personalizzato
    if len(sys.argv) == 1:
        helpers.color_print(
            "[Error] No arguments provided. Use --help or --info",
            "red",
        )
        # parser.print_help()
        exit(1)
    parser.add_argument(
        "-i", "--info", action="store_true", help="Show the program info."
    )
    parser.add_argument("-g", "--gui", action="store_true", help="Start the GUI.")
    args = parser.parse_args(remaining_args)

    if args.a is None:
        helpers.color_print(
            "[ALERT] Height not provided. The entire transaction history will be calculated",
            "purple",
        )
    if not args.ssh:
        helpers.color_print(
            "[ALERT] SSH option not provided. I will use mempool API.",
            "purple",
        )
    if not args.testnet:
        helpers.color_print(
            "[ALERT] Testnet option not provided. I will use standard blockchain.",
            "purple",
        )
    # mettere anche testnet 3
    main_proc(args.txid, args.a, args.ssh, args.testnet)
