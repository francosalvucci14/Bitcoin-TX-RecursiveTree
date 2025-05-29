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
KEY_FILE=percorso_della_chiave_privata_per_SSH
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
python main.py -t <txid> [-a <altezza>] [--ssh] [--testnet]
```

Parametri:
1. `-t`, `--txid`: (Obbligatorio) ID della transazione da cui partire.
2. `-a` : (Opzionale) Altezza massima dell’albero (intero). Se non specificata, verrà calcolata l'intera storia.
3. `--ssh`: (Opzionale) Abilita connessione a un full-node remoto tramite SSH.
4. `--testnet`: (Opzionale) Usa la blockchain della Testnet (in alternativa alla MainNet).

**Nota:**
***Attualmente*** l'opzione `--ssh` non può essere usata insieme a ``--testnet``. In tal caso verrà forzata la modalità testnet.

## Struttura del progetto

- **main.py**: punto di ingresso del programma. Gestisce il parsing degli argomenti, la connessione alla rete, la costruzione e visualizzazione dell’albero.
- **transaction_total.py**: definisce le classi TX e SegWitTx per il parsing delle transazioni Bitcoin
- **Utils/**: contiene i moduli di supporto:
    - **helpers.py**: funzioni comuni come get_tx, get_tx_ssh, color_print, ecc..  
    - **tree_builder.py**: costruzione dell’albero delle transazioni 
    - **tree_visualizer.py**: visualizzazione del grafo delle transazioni con NetworkX e MatplotLib.   
    - **bitcoin_ssh_client.py**: gestisce la connessione a un full-node tramite SSH

## Output

Il programma costruisce e visualizza un grafo delle transazioni che mostra l’albero delle transazioni collegate a quella specificata. Usa librerie come `networkx` e `matplotlib` per la visualizzazione.

## Esempio

Un'esempio di esecuzione è il seguente: 
```bash
python main.py -t a1075db55d416d3ca199f55b6084e2115b9345e16c874700461d613b3f5f5aaf -a 3 --ssh
```

Questo comando genera e visualizza l’intero albero delle transazioni,di altezza 3, a partire dalla transazione specificata. Usa il collegamento al full-node SSH.
