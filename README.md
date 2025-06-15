[English Version](#english-version) | [Versione Italiana](#versione-italiana)

---

# Versione Italiana

# Bitcoin Transaction Tree Visualizer

Questo progetto permette di generare e visualizzare l'albero delle transazioni a partire da un ID di transazione della blockchain di Bitcoin. È compatibile con la rete principale (MainNet), la testnet e può anche connettersi a un full-node remoto tramite SSH.

## 📦 Requisiti

Installa i pacchetti richiesti con:

```bash
pip/pip3 install -r requirements.txt
```

## Variabili d'ambiente
Se usi la connessione SSH, assicurati di creare un file .env nella root del progetto con le seguenti variabili:

```bash
BITCOIN_HOST=indirizzo_del_full_node
USER_SSH=nome_utente_ssh
KEY_FILE=percorso_della_chiave_privata
```

## Utilizzo

Puoi stampare le informazioni sul programma con il comando:
```bash
python main.py --info
```
Puoi anche stampare la pagina di help con il comando:
```bash
python main.py -h
```
Una volta fatto questo, puoi eseguire il programma passando i parametri desiderati:

```bash
python main.py -t <txid> [-a <altezza>] [--ssh] [--testnet] [-g/--gui]
```

Parametri:
1. `-t`, `--txid`: (Obbligatorio) ID della transazione da cui partire.
2. `-a` : (Opzionale) Altezza massima dell’albero (intero). Se non specificata, verrà calcolata l'intera storia.
3. `--ssh`: (Opzionale) Abilita connessione a un full-node remoto tramite SSH.
4. `--testnet`: (Opzionale) Usa la blockchain della Testnet (in alternativa alla MainNet).
5. `-g/--gui`: Se impostato, avvia l'interfaccia grafica dell'applicazione

**Nota:**
***Attualmente*** l'opzione `--ssh` non può essere usata insieme a ``--testnet``. In tal caso verrà forzata la modalità testnet.

## Struttura del progetto

- **main.py**: punto di ingresso del programma. Gestisce il parsing degli argomenti, la connessione alla rete, la costruzione e visualizzazione dell’albero.
- **transaction_total.py**: definisce le classi TX e SegWitTx per il parsing delle transazioni Bitcoin
- **Utils/**: contiene i moduli di supporto:
    - **helpers.py**: funzioni comuni come get_tx, get_tx_ssh, color_print, ecc..  
    - **tree_builder.py**: costruzione dell’albero delle transazioni 
    - **tree_visualizer.py**: visualizzazione del grafo delle transazioni con NetworkX e MatplotLib.   
    - **bitcoin_ssh_client.py**: gestisce la connessione a un full-node tramite SSH tramite Paramiko
    - **logger.py**: crea e gestisce il file di log
- **GUI/**: Contiene tutti i file relativi alla GUI
- **logs/**: Contiene il file di log

## Output

Il programma costruisce e visualizza un grafo delle transazioni che mostra l’albero delle transazioni collegate a quella specificata. Usa librerie come `networkx` e `matplotlib` per la visualizzazione.

## Esempio

Un'esempio di esecuzione è il seguente: 
```bash
python main.py -t a1075db55d416d3ca199f55b6084e2115b9345e16c874700461d613b3f5f5aaf -a 3 --ssh
```


Questo comando genera e visualizza l’intero albero delle transazioni,di altezza 3, a partire dalla transazione specificata. Usa il collegamento al full-node SSH.

Per avviare l'interfaccia grafica (GUI):
```bash
python main.py -g/--gui
```
---

# English Version
# Bitcoin Transaction Tree Visualizer

This project allows you to generate and visualize the transaction tree starting from a Bitcoin blockchain transaction ID. It's compatible with MainNet, TestNet, and can also connect to a remote full-node via SSH.

## 📦 Requirements

To get started, install the necessary packages with:
```bash
pip/pip3 install -r requirements.txt
```
## Environment Variables

If you plan to use an SSH connection, create a .env file in the project root with the following variables:
```bash
BITCOIN_HOST=full_node_address
USER_SSH=ssh_username
KEY_FILE=path_to_ssh_private_key
```
## Usage

You can display program information or the help page with these commands:
```Bash

python main.py --info
# Or
python main.py -h
```

Once set up, you can run the program by passing the desired parameters:
```Bash

python main.py -t <txid> [-a <height>] [--ssh] [--testnet] [-g/--gui]
```
## Parameters:

1. `-t, --txid`: (Required) The transaction ID to start from.
2. `-a`: (Optional) The maximum tree height (an integer). If not specified, the entire transaction history will be calculated.
3. `--ssh`: (Optional) Enables connection to a remote full-node via SSH.
4. `--testnet`: (Optional) Uses the TestNet blockchain instead of MainNet.
5. `-g, --gui`: (Optional) Launches the application with a graphical user interface. If this option is used, other parameters will be ignored and configured directly from the GUI.

**Please Note**:
***Currently***, the `--ssh` option cannot be used simultaneously with `--testnet`. In such a case, TestNet mode will be enforced.
## Project Structure

The project is organized as follows:

- **main.py**: The main entry point of the program. It handles argument parsing, network connection, tree building, and visualization.
- **transaction_total.py**: Defines the TX and SegWitTx classes for parsing Bitcoin transactions.
- **Utils/**: Contains supporting modules:
    - **helpers.py**: Common functions like get_tx, get_tx_ssh, color_print, etc.
    - **tree_builder.py**: Handles the building of the transaction tree.
    - **tree_visualizer.py**: Manages the visualization of the transaction graph using NetworkX and Matplotlib.
    - **bitcoin_ssh_client.py**: Manages the connection to a full-node via SSH.
    - **logger.py**: creates and manages the log file
- **GUI/**: Contains all files related to the graphical interface.
- **logs/**: Contains the log file

## Output

The program builds and visualizes a graph that shows the tree of transactions linked to the specified one. Libraries such as networkx and matplotlib are used for visualization.
## Example

An example of CLI execution is as follows:
```Bash

python main.py -t a1075db55d416d3ca199f55b6084e2115b9345e16c874700461d613b3f5f5aaf -a 3 --ssh
```
This command generates and displays the transaction tree with a maximum height of 3, starting from the specified transaction and using a connection to a full-node via SSH.

To launch the ***Graphical User Interface (GUI)***:
```Bash

python main.py --gui
```
