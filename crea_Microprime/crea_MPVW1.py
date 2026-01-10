# GC-60 Progetto MicroPrime - Ottimizzato Gennaio 2026 V3
# Versione con sistema CREA/AGGIUNGI archivi
# CORREZIONE: In modalità Aggiungi, cerca_in viene rilevato automaticamente
# Test 08/2026 superato
import time
import numpy as np
import pickle
import tkinter as tk
from tkinter import messagebox
from numba import njit
import os
import glob


# ============================================================================
# FUNZIONI UTILITÀ ARCHIVIO
# ============================================================================


def trova_archivi_esistenti():
    """
    Trova tutti i file lista_*.pkl nella directory.
    Ritorna: (ultimo_numero, lista_numeri_ordinata)
    """
    files = glob.glob("lista_*.pkl")
    if not files:
        return -1, []

    numeri = []
    for f in files:
        try:
            num = int(f.split("_")[1].split(".")[0])
            numeri.append(num)
        except:
            continue

    if not numeri:
        return -1, []

    numeri.sort()
    return max(numeri), numeri


def verifica_integrita_archivi(numeri_archivi):
    """
    Verifica che la sequenza sia completa (0, 1, 2, 3... senza buchi).
    Ritorna: True se OK, False se ci sono buchi
    """
    if not numeri_archivi:
        return True

    for i in range(len(numeri_archivi)):
        if numeri_archivi[i] != i:
            return False
    return True


def cancella_archivi_esistenti():
    """Cancella tutti i file lista_*.pkl"""
    files = glob.glob("lista_*.pkl")
    count = 0
    for f in files:
        try:
            os.remove(f)
            count += 1
        except:
            pass
    return count


def leggi_info_ultimo_archivio(numero):
    """Legge informazioni dall'ultimo archivio includendo cerca_in"""
    try:
        with open(f"lista_{numero:04d}.pkl", "rb") as f:
            lista = pickle.load(f)
        riferimento = lista[-1][0]
        lunghezza = len(lista) - 1
        capacita = (riferimento * 60 + 10) + (lunghezza * 60)

        # FORMULA CORRETTA: cerca_in = lunghezza * 60 + 10
        # Esempio: se lunghezza = 1667, cerca_in = 1667 * 60 + 10 = 100030
        cerca_in_originale = (lunghezza-1) * 60 + 10

        return {
            "riferimento": riferimento,
            "lunghezza": lunghezza,
            "capacita": capacita,
            "cerca_in": cerca_in_originale,
        }
    except:
        return None


# ============================================================================
# FINESTRA INPUT PARAMETRI CON RADIO BUTTON
# ============================================================================


def richiedi_parametri():
    """Apre finestra per inserire i parametri di ricerca con modalità Crea/Aggiungi"""
    parametri = {
        "cerca_in": None,
        "crea_archivio": None,
        "modalita": None,  # "crea" o "aggiungi"
    }

    def aggiorna_modalita():
        """Chiamata quando si cambia il radio button"""
        modalita = modalita_var.get()

        if modalita == "aggiungi":
            # Controlla se esiste archivio
            ultimo_arch, _ = trova_archivi_esistenti()
            if ultimo_arch >= 0:
                # Leggi info dall'archivio
                info = leggi_info_ultimo_archivio(ultimo_arch)
                if info:
                    # Imposta cerca_in automaticamente e blocca il campo
                    entry_cerca.config(state="normal")
                    entry_cerca.delete(0, tk.END)
                    entry_cerca.insert(0, str(info["cerca_in"]))
                    entry_cerca.config(state="readonly", fg="blue")
                    label_info.config(
                        text=f"ℹ️ Valore rilevato\ndall'archivio esistente", fg="blue"
                    )
                else:
                    entry_cerca.config(state="normal", fg="black")
                    label_info.config(text="", fg="black")
            else:
                entry_cerca.config(state="normal", fg="black")
                label_info.config(text="", fg="black")
        else:
            # Modalità crea: campo editabile
            entry_cerca.config(state="normal", fg="black")
            label_info.config(text="", fg="black")

    def conferma():
        try:
            cerca = int(entry_cerca.get())
            archivi = int(entry_archivi.get())

            if cerca <= 0:
                messagebox.showerror(
                    "Errore", "Il valore di ricerca deve essere maggiore di 0"
                )
                return
            if archivi < 1 or archivi > 20:
                messagebox.showerror(
                    "Errore", "Il numero di archivi deve essere tra 1 e 20"
                )
                return

            # Leggi modalità dai radio button
            modalita = modalita_var.get()

            # Trova archivi esistenti
            ultimo_arch, numeri_arch = trova_archivi_esistenti()
            archivio_esiste = ultimo_arch >= 0

            # ===== MODALITÀ CREA NUOVO =====
            if modalita == "crea":
                if archivio_esiste:
                    # Conferma cancellazione
                    msg = (
                        f"⚠️ ATTENZIONE - CREAZIONE NUOVO ARCHIVIO\n\n"
                        f"Trovati {len(numeri_arch)} file esistenti (lista_0000 - lista_{ultimo_arch:04d})\n\n"
                        f"TUTTI i file lista_*.pkl verranno CANCELLATI!\n\n"
                        f"Nuovi parametri:\n"
                        f"• Ricerca fino a: {cerca:,}\n"
                        f"• Archivi da creare: {archivi}\n\n"
                        f"Sei sicuro di voler procedere?".replace(",", ".")
                    )
                    risposta = messagebox.askyesno(
                        "⚠️ Conferma Cancellazione", msg, icon="warning"
                    )
                    if not risposta:
                        return

                    # Cancella archivi
                    count = cancella_archivi_esistenti()
                    print(f"\n🗑️  Cancellati {count} file esistenti")
                else:
                    # Nessun archivio esistente, solo conferma
                    msg = (
                        f"Creazione nuovo archivio\n\n"
                        f"Parametri:\n"
                        f"• Ricerca fino a: {cerca:,}\n"
                        f"• Archivi da creare: {archivi}\n\n"
                        f"Procedere?".replace(",", ".")
                    )
                    risposta = messagebox.askyesno("Conferma", msg)
                    if not risposta:
                        return

            # ===== MODALITÀ AGGIUNGI =====
            elif modalita == "aggiungi":
                if not archivio_esiste:
                    messagebox.showerror(
                        "Errore",
                        "❌ Nessun archivio esistente trovato!\n\n"
                        "Usa la modalità 'Crea Nuovo Archivio' per iniziare.",
                    )
                    return

                # Verifica integrità
                if not verifica_integrita_archivi(numeri_arch):
                    messagebox.showerror(
                        "Errore Archivio",
                        f"❌ Archivio corrotto!\n\n"
                        f"Trovati file: {numeri_arch}\n"
                        f"La sequenza non è completa (ci sono buchi).\n\n"
                        f"Usa 'Crea Nuovo Archivio' per ricominciare.",
                    )
                    return

                # Leggi info ultimo archivio
                info = leggi_info_ultimo_archivio(ultimo_arch)
                if not info:
                    messagebox.showerror(
                        "Errore",
                        f"❌ Impossibile leggere lista_{ultimo_arch:04d}.pkl\n\n"
                        f"File corrotto o inaccessibile.",
                    )
                    return

                # VERIFICA CHE cerca_in SIA UGUALE
                if cerca != info["cerca_in"]:
                    messagebox.showerror(
                        "Errore Parametri",
                        f"❌ Valore 'Ricerca fino a' non corretto!\n\n"
                        f"Valore richiesto: {info['cerca_in']:,}\n"
                        f"Valore inserito: {cerca:,}\n\n"
                        f"Gli archivi devono avere la stessa dimensione.\n"
                        f"Il campo dovrebbe essere bloccato automaticamente.".replace(
                            ",", "."
                        ),
                    )
                    return

                # Conferma aggiunta
                nuova_capacita = info["capacita"] + (archivi * info["lunghezza"] * 60)
                msg = (
                    f"📂 AGGIUNGI ARCHIVI\n\n"
                    f"Archivio attuale:\n"
                    f"• Ultimo file: lista_{ultimo_arch:04d}.pkl\n"
                    f"• Capacità attuale: {info['capacita']:,}\n"
                    f"• Ricerca fino a: {info['cerca_in']:,}\n\n"
                    f"Nuovi archivi da aggiungere: {archivi}\n"
                    f"• Nuovi file: lista_{ultimo_arch+1:04d}.pkl - lista_{ultimo_arch+archivi:04d}.pkl\n"
                    f"• Nuova capacità: {nuova_capacita:,}\n\n"
                    f"Procedere?".replace(",", ".")
                )
                risposta = messagebox.askyesno("Conferma Aggiunta", msg)
                if not risposta:
                    return

            parametri["cerca_in"] = cerca
            parametri["crea_archivio"] = archivi
            parametri["modalita"] = modalita
            root.destroy()

        except ValueError:
            messagebox.showerror("Errore", "Inserire solo numeri interi")

    root = tk.Tk()
    root.title("Parametri MicroPrime V3")
    root.attributes("-topmost", True)
    root.geometry("450x400")
    root.resizable(False, False)

    # Titolo
    tk.Label(
        root, text="Parametri di ricerca", font=("Arial", 14, "bold"), pady=10
    ).pack()

    # Frame per i campi
    frame = tk.Frame(root)
    frame.pack(pady=10)

    # Campo cerca_in
    tk.Label(frame, text="Ricerca fino a:", font=("Arial", 11)).grid(
        row=0, column=0, sticky="e", padx=10, pady=10
    )
    entry_cerca = tk.Entry(frame, font=("Arial", 11), width=15)
    entry_cerca.insert(0, "100000")
    entry_cerca.grid(row=0, column=1, padx=10, pady=10)

    # Label info per modalità aggiungi
    label_info = tk.Label(frame, text="", font=("Arial", 9))
    label_info.grid(row=0, column=2, padx=5)

    # Campo crea_archivio
    tk.Label(frame, text="Numero archivi (1-20):", font=("Arial", 11)).grid(
        row=1, column=0, sticky="e", padx=10, pady=10
    )
    entry_archivi = tk.Entry(frame, font=("Arial", 11), width=15)
    entry_archivi.insert(0, "2")
    entry_archivi.grid(row=1, column=1, padx=10, pady=10)

    # Frame per radio button
    frame_radio = tk.LabelFrame(
        root, text="Modalità", font=("Arial", 11, "bold"), padx=10, pady=10
    )
    frame_radio.pack(pady=10, padx=20, fill="x")

    modalita_var = tk.StringVar(value="crea")

    tk.Radiobutton(
        frame_radio,
        text="🆕 Crea Nuovo Archivio",
        variable=modalita_var,
        value="crea",
        font=("Arial", 10),
        command=aggiorna_modalita,
    ).pack(anchor="w", pady=5)

    tk.Radiobutton(
        frame_radio,
        text="➕ Aggiungi ad Archivio Esistente",
        variable=modalita_var,
        value="aggiungi",
        font=("Arial", 10),
        command=aggiorna_modalita,
    ).pack(anchor="w", pady=5)

    # Pulsante conferma
    tk.Button(
        root,
        text="AVVIA",
        font=("Arial", 12, "bold"),
        width=15,
        command=conferma,
        bg="#4CAF50",
        fg="white",
    ).pack(pady=15)

    root.mainloop()

    return parametri["cerca_in"], parametri["crea_archivio"], parametri["modalita"]


# ============================================================================
# RESTO DEL CODICE (INVARIATO)
# ============================================================================


class ArchivioMicroPrime:
    """Classe per memorizzare i dati di ogni archivio creato"""

    def __init__(self):
        self.archivi = []

    def aggiungi_archivio(
        self, numero_iterazione, indice_ultima_lista, grandezza_archivio, riferimento
    ):
        """Memorizza i dati di un archivio completato"""
        archivio_dati = {
            "iterazione": numero_iterazione,
            "indice_ultima_lista": indice_ultima_lista,
            "grandezza_archivio": grandezza_archivio,
            "riferimento": riferimento,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        }
        self.archivi.append(archivio_dati)
        print(f"\n{'='*60}")
        print(f"ARCHIVIO {numero_iterazione} MEMORIZZATO NELLA CLASSE")
        print(f"{'='*60}")
        print(f"Indice ultima lista: {indice_ultima_lista:,}".replace(",", "."))
        print(f"Grandezza archivio: {grandezza_archivio:,}".replace(",", "."))
        print(f"Riferimento: {riferimento:,}".replace(",", "."))
        print(f"Timestamp: {archivio_dati['timestamp']}")
        print(f"{'='*60}\n")

    def mostra_riepilogo(self):
        """Mostra il riepilogo di tutti gli archivi creati"""
        if not self.archivi:
            print("Nessun archivio creato.")
            return

        print(f"\n{'='*60}")
        print(f"RIEPILOGO ARCHIVI CREATI: {len(self.archivi)}")
        print(f"{'='*60}")
        for arch in self.archivi:
            print(
                f"Archivio {arch['iterazione']:04d} - "
                f"Liste: {arch['indice_ultima_lista']:,} - "
                f"Grandezza: {arch['grandezza_archivio']:,} - "
                f"Riferimento: {arch['riferimento']:,} - "
                f"Ore: {arch['timestamp']}".replace(",", ".")
            )
        print(f"{'='*60}\n")


def leggi_riferimento_da_pickle(iterazione):
    """Legge il riferimento dall'ultimo file pickle salvato"""
    if iterazione == 0:
        return 0

    nome_file_precedente = f"lista_{iterazione-1:04d}.pkl"

    try:
        with open(nome_file_precedente, "rb") as f:
            lista_precedente = pickle.load(f)

        riferimento_precedente = lista_precedente[-1][0]
        len_lista_precedente = len(lista_precedente) - 1
        nuovo_rif = riferimento_precedente + len_lista_precedente

        print(f"📖 Riferimento letto da {nome_file_precedente}:")
        print(f"   - Riferimento salvato: {riferimento_precedente}")
        print(f"   - Lunghezza lista: {len_lista_precedente}")
        print(f"   - Nuovo riferimento: {nuovo_rif}")

        return nuovo_rif

    except FileNotFoundError:
        print(f"❌ ERRORE: File {nome_file_precedente} non trovato!")
        raise


def salva_lista(lista_np, nome_file, iterazione):
    """Salva la lista in formato pickle"""
    lista_pickle = []
    sottoliste_non_vuote = 0
    ultimo_indice_non_vuoto = -1

    for i in range(len(lista_np) - 1):
        sottolista = [int(n) for n in lista_np[i] if n != 0]
        lista_pickle.append(sottolista)
        if sottolista:
            sottoliste_non_vuote += 1
            ultimo_indice_non_vuoto = i

    if iterazione == 0:
        riferimento_val = [0]
    else:
        riferimento_val = [leggi_riferimento_da_pickle(iterazione)]

    lista_pickle.append(riferimento_val)

    nome_pickle = nome_file.replace(".txt", ".pkl")
    with open(nome_pickle, "wb") as file:
        pickle.dump(lista_pickle, file)

    print(f"💾 Salvataggio: {nome_pickle}")
    print(f"   Sottoliste: {len(lista_pickle)-1:,}".replace(",", "."))
    print(f"   Con primi: {sottoliste_non_vuote:,}".replace(",", "."))
    print(f"   Riferimento: {riferimento_val[0]}")


@njit
def scremare_lista_0000(lista_np, numero_partenza, limite, cerca_in):
    """Scrematura lista_0000 - OTTIMIZZATA"""
    len_lista = len(lista_np)

    for i in range(numero_partenza, limite, 2):
        if i % 3 == 0 or i % 5 == 0:
            continue

        ii = i

        while True:
            while ii % 3 == 0 or ii % 5 == 0:
                ii += 2

            n_prodotto = i * ii

            if n_prodotto >= cerca_in + 60:
                break

            p_lista = (n_prodotto - 10) // 60
            p_numero = (n_prodotto - 10) % 60

            if p_lista >= len_lista:
                break

            ver = False
            for idx in range(16):
                if lista_np[p_lista, idx] == p_numero:
                    ver = True
                    break

            if ver:
                for idx in range(16):
                    if lista_np[p_lista, idx] == p_numero:
                        lista_np[p_lista, idx] = 0
                        break

            ii += 2

    return lista_np


@njit
def scremare_lista_successive(
    lista_np, numero_partenza, limite, cerca_in, nuovo_riferimento, ciclo
):
    """Scrematura liste successive - OTTIMIZZATA"""

    def recupera_moltiplicatore(hi):
        h = nuovo_riferimento * 60 + 10
        h1 = h % hi
        h2 = h - h1
        if h2 % 2 == 0:
            h2 = h2 + hi
        else:
            h2 = h2 + hi * 2
        hii = h2 // hi
        return hii

    len_lista = len(lista_np)
    ce_in = (cerca_in * ciclo) // 60 * 60 + 60

    h = nuovo_riferimento * 60 + 10
    h1 = h % numero_partenza
    h2 = h - h1
    if h2 % 2 == 0:
        h2 = h2 + numero_partenza
    else:
        h2 = h2 + numero_partenza * 2

    ii = h2 // numero_partenza

    for i in range(numero_partenza, limite, 2):
        if i % 3 == 0 or i % 5 == 0:
            continue

        if i > 7:
            ii = recupera_moltiplicatore(i)

        while True:
            while ii % 3 == 0 or ii % 5 == 0:
                ii += 2

            n_prodotto = i * ii

            if n_prodotto > ce_in + (60 * (ciclo + 1)):
                break

            p_lista = (n_prodotto - 10) // 60
            p_numero = (n_prodotto - 10) % 60
            pp_lista = p_lista - nuovo_riferimento

            if pp_lista < 0:
                pass
            elif pp_lista >= len_lista:
                break
            else:
                ver = False
                for idx in range(16):
                    if lista_np[pp_lista, idx] == p_numero:
                        ver = True
                        break

                if ver:
                    for idx in range(16):
                        if lista_np[pp_lista, idx] == p_numero:
                            lista_np[pp_lista, idx] = 0
                            break

            ii += 2

    return lista_np


# ============================================================================
# MAIN - CON SUPPORTO CREA/AGGIUNGI
# ============================================================================

cerca_in, crea_archivio, modalita = richiedi_parametri()

if cerca_in is None or crea_archivio is None:
    print("Programma annullato")
    exit()

# Determina da dove partire
if modalita == "aggiungi":
    # Trova ultimo archivio e parti da lì
    ultimo_arch, _ = trova_archivi_esistenti()
    iterazione_start = ultimo_arch + 1
    print(f"\n📂 MODALITÀ AGGIUNGI: Continuo da archivio {iterazione_start}")
else:
    # Parte da zero
    iterazione_start = 0
    print(f"\n🆕 MODALITÀ CREA: Nuovo archivio da zero")

gestore = ArchivioMicroPrime()
num_archivi = crea_archivio

print("=" * 60)
print("GC-60 MICROPRIME V3 - Sistema Crea/Aggiungi")
print("=" * 60)
print(f"Archivi da creare: {num_archivi}")
print(f"Ricerca su: {cerca_in:,}".replace(",", "."))
print(f"{'='*60}\n")

riferimento = 0

# CALCOLO CICLO CORRETTO
if modalita == "aggiungi":
    # Se aggiungo, ciclo deve partire dall'archivio successivo
    ultimo_arch, _ = trova_archivi_esistenti()
    ciclo = ultimo_arch + 2
    print(f"🔄 Ciclo iniziale: {ciclo} (ultimo archivio: lista_{ultimo_arch:04d})")
else:
    # Se creo da zero, ciclo parte da 1
    ciclo = 1

for i in range(num_archivi):
    iterazione = iterazione_start + i

    print(f"\n{'#'*60}")
    print(f"CREAZIONE ARCHIVIO {iterazione:04d}")
    print(f"{'#'*60}\n")

    tempo = time.strftime("%H:%M:%S", time.localtime())
    start_time = time.monotonic()

    # Sottoliste
    if iterazione == 0:
        sottoliste = [
            [1, 3, 7, 9, 13, 19, 21, 27, 31, 33, 37, 0, 43, 49, 51, 57],
            [1, 3, 0, 9, 13, 19, 0, 27, 31, 33, 37, 39, 43, 0, 51, 57],
            [1, 0, 7, 9, 13, 19, 21, 27, 0, 33, 37, 39, 43, 49, 51, 57],
            [1, 3, 7, 9, 0, 19, 21, 0, 31, 33, 37, 39, 43, 49, 51, 57],
            [1, 3, 7, 0, 13, 19, 21, 27, 31, 33, 0, 39, 43, 49, 0, 57],
            [1, 3, 7, 9, 13, 0, 21, 27, 31, 0, 37, 39, 43, 49, 51, 57],
            [0, 3, 7, 9, 13, 19, 21, 27, 31, 33, 37, 39, 0, 49, 51, 0],
        ]
        numero_partenza = 11
    else:
        sottolista_base = [1, 3, 7, 9, 13, 19, 21, 27, 31, 33, 37, 39, 43, 49, 51, 57]
        sottoliste = [sottolista_base] * 7
        numero_partenza = 7

    # Calcolo dimensioni
    calcolo_sottoliste = cerca_in // 60 * 60
    n_sottoliste = cerca_in // 60
    if calcolo_sottoliste < cerca_in:
        n_sottoliste += 1

    grandezza_archivio = n_sottoliste * 60 + 10

    print(f"Ricerca su: {grandezza_archivio:,}".replace(",", "."))

    # Creazione lista
    sottoliste_np = np.array(sottoliste, dtype=np.int32)
    n_ripetizioni = (n_sottoliste // 7) + 1
    lista_np = np.tile(sottoliste_np, (n_ripetizioni, 1))[:n_sottoliste]

    print(
        f"Liste: {n_sottoliste:,} ({n_sottoliste * 16 * 4 / 1024**3:.2f} GB)".replace(
            ",", "."
        )
    )

    # Scrematura
    if crea_archivio > 20 or crea_archivio < 1:
        print("Errore: archivi fuori range")
        exit()

    if ciclo == 1:
        limite = int((n_sottoliste * 60 + 10) ** 0.5) + 1
    else:
        limite = int(((n_sottoliste * 60 + 10) * ciclo) ** 0.5) + 1

    print(f"Ciclo: {ciclo}, Limite: {limite:,}".replace(",", "."))

    if iterazione == 0:
        print("🔧 Compilazione JIT...")
        lista_np = scremare_lista_0000(lista_np, numero_partenza, limite, cerca_in)
    else:
        nuovo_riferimento = leggi_riferimento_da_pickle(iterazione)
        print(f"🔧 Scrematura (rif={nuovo_riferimento})")
        lista_np = scremare_lista_successive(
            lista_np, numero_partenza, limite, cerca_in, nuovo_riferimento, ciclo
        )

    ciclo += 1

    # Salvataggio
    riga_riferimento = np.zeros(16, dtype=np.int32)
    riga_riferimento[0] = riferimento
    lista_np = np.vstack([lista_np, riga_riferimento])

    nome_file = f"lista_{iterazione:04d}.txt"
    salva_lista(lista_np, nome_file, iterazione)

    lista_np = lista_np[:-1]

    indice_ultima_lista = n_sottoliste - 1
    gestore.aggiungi_archivio(
        iterazione, indice_ultima_lista, grandezza_archivio, riferimento
    )

    tempo_totale = time.monotonic() - start_time
    print(f"Tempo: {tempo_totale:.2f}s")

    riferimento = indice_ultima_lista

gestore.mostra_riepilogo()

print("\n" + "=" * 60)
print("✅ COMPLETATO!")
print("=" * 60)
