from transaction_total import TX, SegWitTx
from Utils import helpers, tree_builder as tb, tree_visualizer as tv
from Utils.bitcoin_ssh_client import BitcoinSSHClient
import argparse
import os
from dotenv import load_dotenv
from timeit import default_timer as timer
from datetime import timedelta
import sys


__version__ = "1.0"
__author__ = "Franco Salvucci - Acr0n1m0"
__program_name__ = "Bitcoin Transaction Tree Builder"
__description__ = (
    "Script per costruire e visualizzare l'albero delle transazioni Bitcoin."
)
__url__ = "https://github.com/francosalvucci14/Bitcoin-TX-RecursiveTree"


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
        # Tree Visualization
        nx_tree = tv.build_nx_tree(tree)
        tv.visualize_tree(nx_tree)
        if ssh:
            client.close()
            helpers.color_print("[INFO] Chiudo connessione al full-node SSH", "green")

        break


def print_info():
    print(f"Nome: {__program_name__}")
    print(f"Versione: {__version__}")
    print(f"Autore: {__author__}")
    print(f"Descrizione: {__description__}")
    print(f"Github: {__url__}")


if __name__ == "__main__":
    # Prima parser per intercettare solo --info e --version
    pre_parser = argparse.ArgumentParser(add_help=False,allow_abbrev=False)
    pre_parser.add_argument("--info", action="store_true")
    pre_parser.add_argument("-v", "--version", action="version", version="%(prog)s v{version}".format(version=__version__),)
    
    args, remaining_args = pre_parser.parse_known_args()
    
    if args.info:
        helpers.color_print(
            "[INFO] Mostro le informazioni sul programma", "green"
        )
        print_info()
        exit(0)
    
    parser = argparse.ArgumentParser(description=__description__,allow_abbrev=False)
    

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s v{version}".format(version=__version__),
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
        help="Altezza dell'albero da costruire. Se non specificato, verrà calcolata l'intera storia della transazione. [TYPE=%(type)s]",
    )
    parser.add_argument(
        "--ssh",
        action="store_true",
        required=False,
        help="Specifica se vuoi usare la versione che si connette al full-node tramite SSH oppure usare le API di mempool.",
    )
    parser.add_argument(
        "--testnet",
        action="store_true",
        required=False,
        help="Specifica se vuoi usare la blockchain della TESTNET oppure usare la blockchain STANDARD.",
    )
    # Se non ci sono argomenti, mostra errore personalizzato
    if len(sys.argv) == 1:
        helpers.color_print("Errore: Nessun argomento fornito. Usa --help per aiuto o --info per informazioni.","red")
        #parser.print_help()
        exit(1)
    parser.add_argument("--info", action="store_true", help="Mostra le informazioni sul programma.")
    args = parser.parse_args(remaining_args)
    
    
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
