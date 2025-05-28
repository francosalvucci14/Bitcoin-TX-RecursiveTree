from transaction_total import TX, SegWitTx
from Utils import helpers, tree_builder as tb, tree_visualizer as tv
from Utils.bitcoin_ssh_client import BitcoinSSHClient
import argparse
import os
from dotenv import load_dotenv
from timeit import default_timer as timer
from datetime import timedelta

def main(tx_id, altezza, ssh, testnet):
    # 1. ottieni l'hex da cui partire con la generazione dell'albero
    # 2. vedi che tipo di tx è, se SegWit oppure no
    # 3. se è SegWit, chiama la funzione parse di SegWitTx
    # 4. se non è SegWit, chiama la funzione parse di TX
    # 5. crea l'albero con la funzione buildTree
    # 6. visualizza l'albero con la funzione visualize

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
            HOST = os.getenv("BITCOIN_HOST") # Indirizzo IP o hostname del server SSH
            USER = os.getenv("USER_SSH") # Nome utente SSH
            KEY_FILE = os.getenv("KEY_FILE") # Percorso della chiave privata SSH

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
        # Tree Visualization
        nx_tree = tv.build_nx_tree(tree)
        tv.visualize_tree(nx_tree)
        helpers.color_print("[INFO] Chiudo connessione al full-node SSH", "green")
        client.close() if ssh else None
        break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script per costruire e visualizzare l'albero delle transazioni Bitcoin."
    )

    parser.add_argument(
        "-t",
        "--txid",
        required=True,
        type=str,
        help="ID della transazione da analizzare. [OBBLIGATORIO]",
    )
    parser.add_argument(
        "-a",
        type=int,
        required=False,
        help="Altezza dell'albero da costruire.",
    )
    parser.add_argument(
        "-s",
        "--ssh",
        action="store_true",
        required=False,
        help="Specifica se vuoi usare la versione che si connette al full-node tramite SSH oppure usare le API di mempool.",
    )
    parser.add_argument(
        "-tn",
        "--testnet",
        action="store_true",
        required=False,
        help="Specifica se vuoi usare la blockchain della TESTNET oppure usare la blockchain STANDARD.",
    )
    args = parser.parse_args()

    if args.txid is None:
        helpers.color_print(
            "[ERROR] ID della transazione non fornito. Utilizzare l'opzione -t o --txid.",
            "red",
        )
        exit(1)
    if args.a is None:
        helpers.color_print(
            "[ALERT] Altezza non fornita. Verrà calcolata l'intera storia della transazione",
            "purple",
        )
    if not args.ssh:
        helpers.color_print(
            "[ALERT] Non è stata fornita l'opzione SSH. Utilizzerò le API di mempool.",
            "purple",
        )
    if not args.testnet:
        helpers.color_print(
            "[ALERT] Non è stata fornita l'opzione Testnet. Utilizzerò la blockchain standard.",
            "purple",
        )
    # mettere anche testnet 3
    main(args.txid, args.a, args.ssh, args.testnet)
