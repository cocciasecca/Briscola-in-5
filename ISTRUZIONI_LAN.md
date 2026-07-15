# Briscola in 5 LAN — avvio rapido

## PC host Windows

Fai doppio clic su `avvia_windows.bat`.

## PC host macOS/Linux

Apri il Terminale nella cartella del progetto ed esegui:

```bash
./avvia_mac_linux.sh
```

Alla prima esecuzione vengono creati l'ambiente Python e installate le dipendenze. Dagli avvii successivi il server parte direttamente, senza rieseguire `pip`. L'installazione viene ripetuta soltanto se cambia `pyproject.toml` o se l'ambiente virtuale risulta incompleto.
Il terminale mostrerà l'indirizzo da aprire sugli altri dispositivi, per esempio:

```text
http://192.168.1.35:8000
```

Tutti i dispositivi devono essere collegati alla stessa rete locale. Sugli altri PC non serve Python: basta un browser moderno.

## Uso

1. Il primo giocatore che entra diventa host.
2. Gli altri aprono lo stesso indirizzo e inseriscono il proprio nome.
3. L'host preme **Avvia con i bot**: tutti i posti ancora vuoti vengono riempiti automaticamente.
4. Se un giocatore perde la connessione, la partita si ferma.
5. Al rientro, lo stesso browser recupera automaticamente il posto. In alternativa l'host può sostituirlo con un bot.

## Firewall

Autorizza Python sulle **reti private** quando Windows/macOS lo chiede. Non è necessario esporre porte su Internet o modificare il router.

## Nota sul rilevamento automatico

Il server risponde anche a richieste UDP di discovery sulla porta 54545, ma i browser non possono effettuare direttamente questo tipo di ricerca. L'indirizzo LAN viene quindi sempre mostrato chiaramente nel terminale e nella schermata iniziale.


## Mazzo napoletano

L'interfaccia usa un mazzo napoletano da 40 carte con i semi Denari, Coppe, Spade e Bastoni. Le figure sono numerate secondo l'uso italiano: Fante = 8, Cavallo = 9, Re = 10.

## Regole dell'inizio partita

Dopo la conclusione dell'asta, il vincitore sceglie immediatamente seme di briscola e carta chiamata. Non esiste più la prima mano coperta: tutti conservano le otto carte e la prima presa viene giocata normalmente. La carta chiamata resta mostrata nel riquadro in alto a sinistra del tavolo.

## Velocità dei bot e fine della presa

I bot attendono circa un secondo prima di ogni azione, così le carte giocate risultano leggibili anche quando più bot giocano consecutivamente. Quando viene posata la quinta carta, tutte le carte restano sul tavolo per circa un secondo e mezzo. Durante questa pausa viene mostrato chiaramente il nome del giocatore che prende e il numero di punti della presa.

## Mazzo e ordinamento della mano

Il gioco usa le 40 scansioni del mazzo napoletano provenienti da Wikimedia Commons, incluse localmente nel programma.
Non è necessaria una connessione Internet durante la partita.

La mano è divisa nell'ordine: Denari, Coppe, Spade, Bastoni.
Dentro ogni seme le carte sono ordinate così: 2, 4, 5, 6, 7, Fante, Cavallo, Re, 3, Asso.
