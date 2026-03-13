# 🤝 Contribuire a Briscola in 5

Grazie per l'interesse nel contribuire a **Briscola in 5**! Che tu stia risolvendo un bug, aggiungendo una nuova strategia per i bot o migliorando la documentazione, il tuo aiuto è prezioso.

---

## 🛠️ Workflow di Sviluppo

### 1. Fork e Clone
Per prima cosa, esegui il **Fork** della repository sul tuo profilo GitHub e clona il fork localmente:
```bash
git clone https://github.com/tuo-username/Briscola-in-5.git
cd Briscola-in-5
```

### 2. Configurazione Ambiente
Crea un ambiente virtuale e installa il progetto con le dipendenze di sviluppo:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

# Installa il progetto
pip install -e .
```

### 3. Creare un Branch
Crea un branch dedicato alla tua modifica:
```bash
git checkout -b feature/nome-della-tua-feature
```

---

## 📝 Regole per i Commit
Utilizziamo lo standard **Conventional Commits** per mantenere la cronologia pulita e leggibile. I messaggi devono seguire questo formato:

`<tipo>(<ambito>): <descrizione>`

**Tipi comuni**:
- `feat`: Aggiunta di una nuova funzionalità
- `fix`: Correzione di un bug
- `docs`: Modifiche alla documentazione
- `style`: Modifiche che non influenzano il significato del codice (spazi bianchi, formattazione, ecc.)
- `refactor`: Modifiche al codice che non aggiungono funzionalità né correggono bug
- `test`: Aggiunta o correzione di test

**Esempio**: ` feat(bot): aggiunta strategia di gioco basata su probabilità`

---

## 🧪 Test e Qualità del Codice
Prima di sottoporre le tue modifiche, assicurati che tutto funzioni correttamente.

1. Esegui i test unitari:
```bash
pytest tests/
```

2. Linting e formattazione:
```bash
isort src/ tests/
black src/ tests/
flake8 src/ tests/
```

---

## 📢 Inviare una Pull Request

1. Esegui il **Push** del tuo branch sul tuo fork:
```bash
git push origin feature/nome-della-tua-feature
```

2. Vai sulla repository originale su GitHub.
3. Clicca su **"Compare & pull request"**.
4. Descrivi chiaramente le modifiche apportate e fai riferimento a eventuali Issue aperte.

---
## 🙌 Grazie per il tuo contributo!

Se hai domande o hai bisogno di aiuto, non esitare a contattarci aprendo un Issue o partecipando alla discussione su GitHub. Ogni contributo, grande o piccolo, è molto apprezzato!