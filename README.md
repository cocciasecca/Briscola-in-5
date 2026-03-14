# Briscola in 5

![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

**Briscola in 5** è una implementazione digitale del classico gioco di carte siciliano "Briscola in 5", sviluppata in Python. Il progetto include sia il **motore di gioco** (engine) che un'interfaccia a riga di comando (CLI) e bot giocabili.

---

## ⚙️ Come funziona

1. **Distribuzione:** Il mazzo siciliano da 40 carte viene diviso equamente tra i 5 giocatori.
2. **L'Asta:** I giocatori competono per dichiarare il punteggio obiettivo (da 71 a 120) e la carta di Briscola.
3. **Il Socio:** Chi vince l'asta "chiama" una carta; chi la possiede diventa il suo socio segreto.
4. **Gameplay:** 8 mani di gioco dove la strategia e il conteggio dei punti sono fondamentali.
5. **Valutazione:** Calcolo finale dei punti per determinare se la coppia (Chiamante+Socio) ha raggiunto l'obiettivo.

---

## 🚀 Avvio del gioco
Per avviare una partita rapida direttamente nel tuo terminale:
```bash
python -m briscola5.cli.main
```

---

## 🛠️ Architettura del Progetto
```text
briscola5/
├── .github/workflows/    # Pipeline CI (GitHub Actions)
├── src/
│   ├── domain/           # Logica di gioco, gestione mazzo e regole
│   ├── application/      # Orchestrazione partite
│   ├── bots/             # Implementazione bot di gioco
│   └── cli/              # Interfaccia a riga di comando
├── tests/                # Test unitari
├── README.md
├── .gitignore
├── .flake8               # Configurazione per linting
└── pyproject.toml        # Configurazione del progetto e dipendenze
```

---

## 🔭 Prossimi Passi
- [ ] **Nuova GUI**: Implementazione con Pygame, Tkinter o altre librerie.
- [ ] **IA Avanzata**: Bot basati su probabilità e conteggio carte rimaste.
- [ ] **Multiplayer**: Supporto per giocare in rete locale tramite Socket.

---

## 🤝 Contribuire

Amiamo i contributi! Che tu sia un esperto di Briscola o un appassionato di Python, il tuo aiuto è il benvenuto. 

Prima di iniziare, dai un'occhiata alle nostre **[Linee guida per il contributo](./CONTRIBUTING.md)** per dettagli su:
- Come configurare l'ambiente di sviluppo.
- Standard per i **Conventional Commits**.
- Come eseguire test e linting.

---

## ❤️ Supporta il progetto
Se questo simulatore ti è stato utile per un esame o per divertimento, lascia una ⭐ su GitHub!
