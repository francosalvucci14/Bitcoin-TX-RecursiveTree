# 🧠 Presentazione del Progetto

## **Bitcoin Transaction Tree Visualizer**

### 🔍 Obiettivo

Il progetto ha l'obiettivo di visualizzare **l'albero delle transazioni Bitcoin** a partire da un dato `txid`, permettendo di esplorare la genealogia delle transazioni in modo grafico e interattivo.

---

### 🛠️ Tecnologie Utilizzate

* **Python 3**
* **NetworkX** per la struttura del grafo
* **Matplotlib** per la visualizzazione
* **Tkinter** per l’interfaccia grafica (GUI)
* **Paramiko + SSH** per connettersi a un full-node remoto
* **.env + dotenv** per la configurazione sicura delle credenziali SSH

---

### 🌐 Modalità di Accesso alla Blockchain

Il programma può accedere alla blockchain Bitcoin in **tre modalità distinte**:

1. **MainNet (default)**: connessione pubblica alla blockchain principale.
2. **TestNet**: rete di test pubblica per transazioni senza valore.
3. **SSH**: accesso diretto a un full-node remoto Bitcoin via chiave privata.

> ⚠️ La modalità SSH e Testnet sono **mutualmente esclusive** per evitare conflitti di contesto nella struttura dei blocchi.

---

### 🧱 Costruzione dell’Albero

L’albero viene costruito in profondità a partire da una transazione (`txid`), seguendo ricorsivamente gli input delle transazioni, fino a:

* una certa **altezza massima** (se specificata), oppure
* la **radice** (coinbase) nel caso di altezza indefinita.

Le classi `TX` e `SegWitTx` nel modulo `transaction_total.py` permettono il parsing corretto di transazioni legacy e SegWit.

---

### 🖼️ Interfaccia Grafica (GUI)

La GUI consente:

* Inserimento del TXID
* Costruzione e visualizzazione dell’albero con un solo click
* Colorazione automatica dei nodi
* Chiusura sicura dell’applicazione (inclusa chiusura del processo `main.py`)
* Output dei log direttamente nel pannello inferiore

---

### 📂 Struttura del Progetto

```
Bitcoin_Transaction_Tree_Visualizer/
├── main.py                   # Ingresso principale CLI/GUI
├── transaction_total.py      # Parser TX e SegWitTX
├── Utils/
│   ├── helpers.py
│   ├── tree_builder.py
│   ├── tree_visualizer.py
│   ├── bitcoin_ssh_client.py
│   └── logger.py
├── GUI/
│   └── Bitcoin_Tree_Gui_Clean.py
├── logs/
│   └── log.txt
├── .env                      # Configurazione variabili SSH
└── requirements.txt
```

---

### 🔄 Comportamento dinamico

* L’albero viene disegnato in **stile gerarchico (GraphViz - dot)**.
* I nodi hanno attributi dinamici: `label`, `color`, `linewidth`.
* Gli errori vengono gestiti elegantemente, anche in caso di TX non trovate o SSH mal configurato.

---

### 📈 Esempi di Utilizzo

```bash
# Esecuzione base da terminale
python main.py -t <txid>

# Esecuzione con limite di profondità
python main.py -t <txid> -a 3

# Accesso a full-node remoto via SSH
python main.py -t <txid> --ssh

# Avvio GUI
python main.py --gui
```

---

### ✅ Stato del Progetto

Il progetto è **completo e funzionante**, con:

* Parsing robusto di transazioni Bitcoin (incluso SegWit).
* Supporto completo per MainNet/TestNet/SSH.
* Interfaccia utente grafica semplificata ma efficace.
* Logging automatico delle operazioni.

---

### 📌 Possibili estensioni future

* Esportazione dell’albero in formato PDF/PNG.
* Modalità interattiva con click su nodi.
* Analisi dei valori trasferiti tra nodi.
* Supporto per Ricerca inversa (dati un indirizzo → albero delle spese).


