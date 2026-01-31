# ==============================================================
# MicroPrime – modulo studia
# --------------------------------------------------------------
# Versione : 3.0.0
# Data     : Febbraio / 2026
# Autore   : Govi Claudio
# Progetto : MicroPrime - GC-60
#
# * Struttura di lettura basata sui gap tra numeri primi
#
# // Documentazione ufficiale su GitHub \\
# # ==============================================================
# ==============================================================
import sys
import os
import glob
import pickle
import json
import math
from datetime import datetime
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QApplication


# --- CLASSE DELLA SECONDA PAGINA (STATISTICHE) ---
class FinestraDati(QtWidgets.QMainWindow):
    def __init__(self, main_window, dati_statistiche=None):
        super(FinestraDati, self).__init__()
        # Carichiamo il file .ui della seconda pagina
        uic.loadUi("finestra_dati_Gap.ui", self)

        # Salviamo un riferimento alla finestra principale
        self.main_window = main_window

        # Dati delle statistiche
        self.dati_statistiche = dati_statistiche

        # Collegamento pulsanti
        self.pushButton_esporta.clicked.connect(self.salva_statistiche)
        self.pushButton_carica.clicked.connect(self.carica_statistiche)
        self.pushButton_chiudi.clicked.connect(self.close)

        # Se abbiamo dati, popoliamo la finestra
        if self.dati_statistiche:
            self.popola_finestra()

    def calcola_statistiche(self, primi_trovati, parametri):
        """Calcola tutte le statistiche dai primi trovati"""

        if not primi_trovati:
            return None

        inizio = parametri["inizio"]
        fine = parametri["fine"]
        ampiezza = fine - inizio

        # ===== STATISTICHE BASE =====
        count_primi = len(primi_trovati)
        densita_reale = (count_primi / ampiezza) * 100

        # Densità teorica (Teorema dei numeri primi)
        medio = (inizio + fine) / 2
        densita_teorica = (1 / math.log(medio)) * 100
        differenza = densita_reale - densita_teorica

        # ===== ANALISI GAP =====
        gap_lista = []
        for i in range(1, len(primi_trovati)):
            gap = primi_trovati[i] - primi_trovati[i - 1]
            gap_lista.append(gap)

        gap_min = min(gap_lista) if gap_lista else 0
        gap_max = max(gap_lista) if gap_lista else 0
        gap_medio = sum(gap_lista) / len(gap_lista) if gap_lista else 0

        # ===== DISTRIBUZIONE MODULO 60 =====
        distribuzione_mod60 = {}
        posizioni_valide = [
            1,
            7,
            11,
            13,
            17,
            19,
            23,
            29,
            31,
            37,
            41,
            43,
            47,
            49,
            53,
            59,
        ]

        for pos in posizioni_valide:
            distribuzione_mod60[pos] = 0

        for primo in primi_trovati:
            mod = primo % 60
            if mod in distribuzione_mod60:
                distribuzione_mod60[mod] += 1

        # ===== PRIMI SPECIALI =====
        gemelli = []  # gap = 2
        cugini = []  # gap = 4
        sexy = []  # gap = 6

        for i in range(len(gap_lista)):
            gap = gap_lista[i]
            coppia = (primi_trovati[i], primi_trovati[i + 1])

            if gap == 2:
                gemelli.append(coppia)
            elif gap == 4:
                cugini.append(coppia)
            elif gap == 6:
                sexy.append(coppia)

        # ===== COSTRUISCI DIZIONARIO COMPLETO =====
        statistiche = {
            "metadata": {
                "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "versione": "2.0",
            },
            "parametri": parametri,
            "risultati": {
                "primi_trovati": primi_trovati,
                "count_primi": count_primi,
                "ampiezza": ampiezza,
            },
            "statistiche": {
                "densita_reale": round(densita_reale, 2),
                "densita_teorica": round(densita_teorica, 2),
                "differenza": round(differenza, 2),
                "gap_min": gap_min,
                "gap_max": gap_max,
                "gap_medio": round(gap_medio, 2),
                "gap_lista": gap_lista,
                "distribuzione_mod60": distribuzione_mod60,
                "primi_speciali": {
                    "gemelli": [f"({a}, {b})" for a, b in gemelli],
                    "cugini": [f"({a}, {b})" for a, b in cugini],
                    "sexy": [f"({a}, {b})" for a, b in sexy],
                },
            },
        }

        return statistiche

    def popola_finestra(self):
        """Popola tutti i widget con le statistiche"""

        if not self.dati_statistiche:
            return

        params = self.dati_statistiche["parametri"]
        risultati = self.dati_statistiche["risultati"]
        stats = self.dati_statistiche["statistiche"]

        # ===== RIEPILOGO =====
        inizio = params["inizio"]
        fine = params["fine"]
        self.label_intervallo.setText(f"[{inizio:,} - {fine:,}]".replace(",", "."))
        self.label_ampiezza.setText(f"{risultati['ampiezza']:,}".replace(",", "."))
        self.label_count_primi.setText(str(risultati["count_primi"]))
        self.label_file_usati.setText(params.get("file_usati", "-"))
        self.label_divisori.setText(str(params.get("divisori_caricati", "-")))

        # ===== DENSITÀ =====
        self.label_densita_reale.setText(f"{stats['densita_reale']:.2f}%")
        self.label_densita_teorica.setText(f"{stats['densita_teorica']:.2f}%")

        diff = stats["differenza"]
        diff_text = f"+{diff:.2f}%" if diff > 0 else f"{diff:.2f}%"
        diff_color = "green" if diff > 0 else "red"
        self.label_differenza.setText(diff_text)
        self.label_differenza.setStyleSheet(f"font-weight: bold; color: {diff_color};")

        # Progress bar (max 20% per visualizzazione)
        self.progressBar_densita.setValue(int(min(stats["densita_reale"], 20)))

        # ===== GAP =====
        self.label_gap_min.setText(str(stats["gap_min"]))
        self.label_gap_max.setText(str(stats["gap_max"]))
        self.label_gap_medio.setText(f"{stats['gap_medio']:.1f}")

        # ===== PRIMI SPECIALI =====
        gemelli = stats["primi_speciali"]["gemelli"]
        cugini = stats["primi_speciali"]["cugini"]
        sexy = stats["primi_speciali"]["sexy"]

        self.label_gemelli.setText(f"{len(gemelli)} coppie" if gemelli else "Nessuno")
        self.label_cugini.setText(f"{len(cugini)} coppie" if cugini else "Nessuno")
        self.label_sexy.setText(f"{len(sexy)} coppie" if sexy else "Nessuno")

        # ===== DISTRIBUZIONE MODULO 60 =====
        html = "<table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%;'>"
        html += "<tr style='background-color: #2196F3; color: white;'>"
        html += "<th>Posizione</th><th>Count</th><th>%</th></tr>"

        mod60 = stats["distribuzione_mod60"]
        total = sum(mod60.values())

        for pos in sorted(mod60.keys()):
            count = mod60[pos]
            perc = (count / total * 100) if total > 0 else 0
            color = "#e3f2fd" if count > 0 else "#ffebee"
            html += f"<tr style='background-color: {color};'>"
            html += f"<td align='center'>{pos}</td>"
            html += f"<td align='center'>{count}</td>"
            html += f"<td align='center'>{perc:.1f}%</td>"
            html += "</tr>"

        html += "</table>"
        self.textBrowser_mod60.setHtml(html)

        # ===== TABELLA PRIMI =====
        primi = risultati["primi_trovati"]
        gap_lista = stats["gap_lista"]

        self.tableWidget_primi.setRowCount(len(primi))

        for i, primo in enumerate(primi):
            # Numero
            item_numero = QTableWidgetItem(f"{primo:,}".replace(",", "."))
            self.tableWidget_primi.setItem(i, 0, item_numero)

            # Posizione
            item_pos = QTableWidgetItem(str(i + 1))
            self.tableWidget_primi.setItem(i, 1, item_pos)

            # Gap
            if i > 0:
                gap = gap_lista[i - 1]
                item_gap = QTableWidgetItem(str(gap))
                # Colora gap speciali
                if gap == 2:
                    item_gap.setBackground(Qt.yellow)
                elif gap == 4:
                    item_gap.setBackground(Qt.cyan)
                elif gap == 6:
                    item_gap.setBackground(Qt.magenta)
            else:
                item_gap = QTableWidgetItem("-")
            self.tableWidget_primi.setItem(i, 2, item_gap)

            # Mod 60
            mod = primo % 60
            item_mod = QTableWidgetItem(str(mod))
            self.tableWidget_primi.setItem(i, 3, item_mod)

        # Ridimensiona colonne
        self.tableWidget_primi.resizeColumnsToContents()

    def salva_statistiche(self):
        """Salva le statistiche in formato JSON"""
        if not self.dati_statistiche:
            QtWidgets.QMessageBox.warning(self, "Errore", "Nessun dato da salvare!")
            return

        # Dialog per scegliere nome file
        inizio = self.dati_statistiche["parametri"]["inizio"]
        fine = self.dati_statistiche["parametri"]["fine"]
        nome_default = f"microprime_stats_{inizio}-{fine}.json"

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Salva Statistiche",
            nome_default,
            "JSON Files (*.json);;All Files (*)",
        )

        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(self.dati_statistiche, f, indent=2, ensure_ascii=False)
                QtWidgets.QMessageBox.information(
                    self, "Successo", f"Statistiche salvate in:\n{filepath}"
                )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Errore", f"Errore durante il salvataggio:\n{str(e)}"
                )

    def carica_statistiche(self):
        """Carica le statistiche da un file JSON"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Carica Statistiche",
            "",
            "JSON Files (*.json);;All Files (*)",
        )

        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    self.dati_statistiche = json.load(f)
                self.popola_finestra()
                QtWidgets.QMessageBox.information(
                    self, "Successo", "Statistiche caricate con successo!"
                )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Errore", f"Errore durante il caricamento:\n{str(e)}"
                )

    def closeEvent(self, event):
        """Questa funzione viene chiamata automaticamente quando premi la X"""
        # Mostriamo di nuovo la finestra principale
        self.main_window.show()
        # Accettiamo l'evento di chiusura della finestra attuale
        event.accept()


# --- CLASSE DELLA PAGINA PRINCIPALE ---
class ApplicazionePrincipale(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicazionePrincipale, self).__init__()
        uic.loadUi("main_Gap.ui", self)

        # Personalizzazione estetica
        self.pushButton.setStyleSheet("background-color: #4CAF50; color: white;")
        self.pushButton_2.setStyleSheet("background-color: #f44336; color: white;")

        # Collegamento azioni
        self.pushButton.clicked.connect(self.elabora_dati)
        self.pushButton_2.clicked.connect(self.apri_dati_ui)

        # Avvio automatico lettura archivio
        self.inizializza_archivio()

        # Inizializza progress bar a 0
        try:
            self.progressBar.setValue(0)
            self.progressBar_2.setValue(0)
        except:
            pass

    def inizializza_archivio(self):
        """Controlla i file pickle lista_* e aggiorna le label"""
        files = glob.glob("f:/file_gap/lista_*.pkl")
        dimensione_archivio = 0

        if not files:
            self.label_8.setText("Nessun Archivio Trovato")
            self.label_8.setStyleSheet("color: red;")
            self.label_10.setText("0")
            return

        files.sort()

        try:
            with open(files[1], "rb") as f:
                dati_primo = pickle.load(f)
                valore_start = (
                    dati_primo[-1][0]
                    if isinstance(dati_primo[-1], list)
                    else dati_primo[-1]
                )

            with open(files[-1], "rb") as f:
                dati_ultimo = pickle.load(f)
                valore_end = (
                    dati_ultimo[-1][0]
                    if isinstance(dati_ultimo[-1], list)
                    else dati_ultimo[-1]
                )

            dimensione_1 = int(valore_start * 60 + 10)
            # print(dimensione_1)
            dimensione_2 = int(valore_end * 60 + 10)
            # print(dimensione_2)
            dimensione_archivio = dimensione_1 + dimensione_2
            massima_esplorazione = dimensione_archivio**2

            testo_formattato = f"{dimensione_archivio:,}".replace(",", ".")
            self.label_8.setText(str(testo_formattato))
            self.label_8.setStyleSheet("color: black;")

            testo_formattato = f"{massima_esplorazione:,}".replace(",", ".")
            self.label_10.setText(testo_formattato)
            self.label_10.setStyleSheet("color: black;")

        except Exception as e:
            self.label_8.setText(f"Errore lettura dati: {str(e)}")

    def esegui_scrematura_rapida(self, inizio, fine, divisori_salvati):
        """
        Scrematura veloce con matrice - metodo ottimizzato per finestre grandi
        Ritorna la lista dei primi candidati trovati
        """
        print(
            f"🚀 Avvio scrematura rapida: [{inizio:,}".replace(",", ".")
            + f", {fine:,}]".replace(",", ".")
        )
        print(f"📊 Usando {len(divisori_salvati)} divisori")

        # Crea matrice di tutti i numeri nell'intervallo
        m = fine - inizio
        if m > 10**7:
            raise MemoryError(f"Intervallo troppo grande per la scrematura rapida: {m} numeri. Usa metodo standard o intervallo più piccolo.")
        
        matrice = list(range(0, m))

        conta_divisori = 0
        total_divisori = len(divisori_salvati)

        # Applica ogni divisore per segnare i multipli
        for divisore in divisori_salvati:
            conta_divisori += 1

            # Aggiorna progress bar ogni 100 divisori
            if conta_divisori % 100 == 0:
                progresso = int((conta_divisori / total_divisori) * 100)
                try:
                    self.progressBar_2.setValue(progresso)
                    QApplication.processEvents()
                except:
                    pass

            # Calcola il primo multiplo di 'divisore' >= inizio
            p_divisore = inizio % divisore
            sottrai = inizio - p_divisore

            if sottrai % 2 == 0:
                primo_multiplo = inizio - p_divisore + divisore
            else:
                primo_multiplo = inizio - p_divisore + divisore * 2

            # Segna tutti i multipli nella matrice
            p_lista = primo_multiplo - inizio
            while p_lista < len(matrice):
                if 0 <= p_lista < len(matrice) and matrice[p_lista] != 0:
                    matrice[p_lista] = 0
                p_lista += divisore * 2

        # Estrai i sopravvissuti (candidati primi)
        sopravvissuti = []
        for i in range(len(matrice)):
            if matrice[i] != 0 and matrice[i] % 2 != 0:
                val = inizio + matrice[i]
                # Salta multipli di 3 e 5
                if val % 3 != 0 and val % 5 != 0:
                    sopravvissuti.append(val)

        try:
            self.progressBar_2.setValue(100)
            QApplication.processEvents()
        except:
            pass

        print(f"✅ Scrematura completata: {len(sopravvissuti)} candidati primi trovati")
        return sopravvissuti

    def elabora_dati(self):
        """Esegue il calcolo e apre la finestra statistiche"""

        # ===== VALIDAZIONE INPUT =====
        def valida_input():
            """Valida gli input dell'utente e ritorna i valori o None se errore"""

            # Leggi parametri
            base_partenza = self.lineEdit.text().strip()
            finestra_a = self.lineEdit_2.text().strip()
            finestra_b = self.lineEdit_3.text().strip()

            # Controlla che tutti i campi siano compilati
            if not base_partenza or not finestra_a or not finestra_b:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Campi Mancanti",
                    "⚠️ Compila tutti i campi:\n"
                    "• Base di Ricerca\n"
                    "• Finestra Da\n"
                    "• Finestra A",
                )
                return None

            # Pulizia input
            base_partenza = base_partenza.replace(".", "").replace(" ", "")
            finestra_a = finestra_a.replace(".", "").replace(" ", "")
            finestra_b = finestra_b.replace(".", "").replace(" ", "")

            # Validazione caratteri
            def contiene_solo_numeri(testo, nome_campo, campo_widget):
                """Verifica che il testo contenga solo numeri"""
                if testo.startswith("-"):
                    testo_da_controllare = testo[1:]
                else:
                    testo_da_controllare = testo

                if not testo_da_controllare.isdigit():
                    caratteri_invalidi = [
                        c for c in testo_da_controllare if not c.isdigit()
                    ]
                    QtWidgets.QMessageBox.critical(
                        self,
                        "Caratteri Non Validi",
                        f"❌ Errore nel campo '{nome_campo}'!\n\n"
                        f"Valore inserito: '{testo}'\n"
                        f"Caratteri non validi: {set(caratteri_invalidi)}\n\n"
                        f"💡 Inserisci solo numeri interi.\n"
                        f"Esempio: 1000000 oppure 1.000.000",
                    )
                    campo_widget.setFocus()
                    campo_widget.selectAll()
                    return False
                return True

            if not contiene_solo_numeri(
                base_partenza, "Base di Ricerca", self.lineEdit
            ):
                return None
            if not contiene_solo_numeri(finestra_a, "Finestra Da", self.lineEdit_2):
                return None
            if not contiene_solo_numeri(finestra_b, "Finestra A", self.lineEdit_3):
                return None

            # Conversione
            try:
                base = int(base_partenza)
                f_a = int(finestra_a)
                f_b = int(finestra_b)
            except ValueError as e:
                QtWidgets.QMessageBox.critical(
                    self, "Errore Conversione", f"❌ Errore imprevisto:\n{str(e)}"
                )
                return None

            inizio = base + f_a
            fine = base + f_b

            # CONTROLLO: Finestra A < Finestra B
            if f_a >= f_b:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Intervallo Non Valido",
                    f"❌ Finestra Da ({f_a:,}) deve essere MINORE di Finestra A ({f_b:,})\n\n"
                    f"Intervallo: [{inizio:,} - {fine:,}]\n\n"
                    f"💡 Inverti i valori!".replace(",", "."),
                )
                self.lineEdit_2.setFocus()
                return None

            # CONTROLLO: Numeri negativi
            if inizio < 0 or fine < 0:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Valori Negativi",
                    f"❌ L'intervallo contiene numeri negativi!\n\n"
                    f"Base: {base:,}\n"
                    f"Intervallo: [{inizio:,} - {fine:,}]\n\n"
                    f"💡 Usa valori positivi.".replace(",", "."),
                )
                return None

            # CONTROLLO: Capacità archivio
            capacita_archivio_text = self.label_8.text().replace(".", "")
            try:
                capacita_archivio = int(capacita_archivio_text)
            except:
                capacita_archivio = 0

            radice = int(inizio**0.5)

            if radice > capacita_archivio:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Archivio Insufficiente",
                    f"❌ L'archivio non è sufficiente!\n\n"
                    f"📊 Dettagli:\n"
                    f"• Intervallo: [{inizio:,} - {fine:,}]\n"
                    f"• Radice necessaria: {radice:,}\n"
                    f"• Capacità archivio: {capacita_archivio:,}\n\n"
                    f"💡 Estendi l'archivio MicroPrime\n"
                    f"oppure cerca in un intervallo più basso.".replace(",", "."),
                )
                return None

            # CONTROLLO: Intervallo grande
            ampiezza = fine - inizio
            if ampiezza > 1000000:
                risposta = QtWidgets.QMessageBox.question(
                    self,
                    "Intervallo Molto Grande",
                    f"⚠️ Intervallo molto grande!\n\n"
                    f"Ampiezza: {ampiezza:,} numeri\n"
                    f"Tempo stimato: alcuni minuti\n\n"
                    f"Procedere?".replace(",", "."),
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                )
                if risposta == QtWidgets.QMessageBox.No:
                    return None

            # CONTROLLO: Intervallo piccolo
            if ampiezza < 10:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Intervallo Piccolo",
                    f"⚠️ Intervallo molto piccolo ({ampiezza} numeri).\n\n"
                    f"Potresti non trovare primi.\n"
                    f"Consiglio: almeno 100 numeri.",
                )

            # CONTROLLO: Base piccola
            if base < 100:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Base Piccola",
                    f"⚠️ Base molto piccola ({base}).\n\n"
                    f"MicroPrime è ottimizzato per numeri >10.000.",
                )

            return {
                "base": base,
                "f_a": f_a,
                "f_b": f_b,
                "inizio": inizio,
                "fine": fine,
                "radice": radice,
            }

        # ===== ESEGUI VALIDAZIONE =====
        parametri_validati = valida_input()
        if parametri_validati is None:
            return

        # LEGGI STATO CHECKBOX DEBUG
        try:
            debug_attivo = self.radioButton.isChecked()
        except:
            debug_attivo = False  # Default: debug disattivato

        # ===== FUNZIONE CALCOLO CON PROGRESS BAR =====
        def esegui_calcolo(radice, inizio, fine, debug=False):
            primi_trovati = []
            divisori_salvati = [7]
            trappola = fine - inizio
            radice_max = 0
            file_usati = []

            # Conta i file totali per progress bar
            files_totali = 0
            for i in range(10000):
                if os.path.exists(f"f:/file_gap/lista_{i:04d}.pkl"):
                    files_totali += 1
                else:
                    break

            # ===== FASE 1: CARICAMENTO ARCHIVIO =====
            print(f"\n🔍 FASE 1: Caricamento archivio ({files_totali} file)")

            # IMPORTANTE: Imposta il massimo della progress bar alla radice

            try:
                self.progress_step = 0.01          # 1%
                self.progress_steps_total = int(1 / self.progress_step)  # 100
                self.progress_step_size = radice * self.progress_step

                self.progressBar.setMinimum(0)
                self.progressBar.setMaximum(self.progress_steps_total)
                self.progressBar.setValue(0)

                self._next_progress_threshold = self.progress_step_size
                self._progress_counter = 0

                QApplication.processEvents()
            except:
                pass


            for i in range(10000):
                file_path = f"f:/file_gap/lista_{i:04d}.pkl"
                if not os.path.exists(file_path):
                    break
                file_usati.append(file_path)
                print(file_path)
                with open(file_path, "rb") as file:
                    lista = pickle.load(file)
                    riferimento = lista[-2]
                    divisore=riferimento
                    
                    for ii in range(len(lista) - 2):
                        divisore +=lista[ii]

                        # AGGIORNA PROGRESS BAR ad ogni divisore
                        if divisore >= self._next_progress_threshold:
                            self._progress_counter += 1
                            self.progressBar.setValue(self._progress_counter)

                            self._next_progress_threshold += self.progress_step_size
                            QApplication.processEvents()
    
                        if divisore < (trappola):
                            divisori_salvati.append(divisore)
                        elif divisore > radice:
                            radice_max = 1
                            break
                        else:
                            c = inizio - (inizio % divisore)
                            if c % 2 == 0:
                                c += divisore
                            else:
                                c += divisore * 2
                            if inizio < c < fine:
                                    divisori_salvati.append(c)
                    if radice_max == 1:
                        break

            # FORZA 100% PROGRESS BAR ARCHIVIO (imposta al valore massimo = radice)
            try:
                self.progressBar.setValue(int(radice))
                QApplication.processEvents()
            except:
                pass
            # ******************************************************************
            # **************** Controllo Finestra Grande per uscita ************
            # ******************************************************************
            if trappola > 5000:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setWindowTitle("⚠️ Finestra Molto Grande")
                msg.setText(
                    f"La finestra di ricerca è molto grande ({fine - inizio:,} numeri).\n\n"
                    f"Metodo standard potrebbe richiedere molto tempo.\n\n"
                    f"Vuoi usare il metodo di SCREMATURA RAPIDA?".replace(",", ".")
                )
                msg.setInformativeText(
                    "• SÌ: Usa scrematura rapida (consigliato)\n"
                    "• NO: Usa metodo standard (più lento)"
                )
                msg.setStandardButtons(
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                )
                msg.setDefaultButton(QtWidgets.QMessageBox.Yes)

                risposta = msg.exec_()

                if risposta == QtWidgets.QMessageBox.Yes:
                    # ═══════════════════════════════════════════════════════
                    # METODO RAPIDO: Scrematura con matrice
                    # ═══════════════════════════════════════════════════════
                    print("🚀 Metodo RAPIDO selezionato")
                    primi_trovati = self.esegui_scrematura_rapida(
                        inizio, fine, divisori_salvati
                    )

                    # Verifica con gmpy2 se debug attivo
                    if debug:
                        print("🔍 Verifica debug attiva...")
                        try:
                            import gmpy2

                            verificati = []
                            for primo in primi_trovati:
                                if gmpy2.is_prime(primo):
                                    verificati.append(primo)
                                else:
                                    print(f"❌ Bug trovato: {primo} non è primo!")
                            primi_trovati = verificati
                            print(
                                f"✅ Verifica completata: {len(primi_trovati)} primi confermati"
                            )
                        except ImportError:
                            print("⚠️ gmpy2 non disponibile, salto verifica")

                    # Salta l'analisi standard
                    skip_analisi_standard = True
                else:
                    print("🐌 Metodo STANDARD selezionato")
                    skip_analisi_standard = False
            else:
                skip_analisi_standard = False
            # ******************************************************************

            print(
                f"✅ Caricati {len(divisori_salvati)} divisori da {len(file_usati)} file"
            )

            # ===== FASE 2: ANALISI FINESTRA =====
            if inizio % 2 == 0:
                inizio += 1

            # ═══════════════════════════════════════════════════════════
            # METODO STANDARD: Analisi numero per numero
            # ═══════════════════════════════════════════════════════════
            if not skip_analisi_standard:
                numeri_da_analizzare = list(range(inizio, fine, 2))
                totale_numeri = len(numeri_da_analizzare)
                errori_debug = []

                for idx, ii in enumerate(numeri_da_analizzare):
                    if ii % 3 == 0 or ii % 5 == 0:
                        continue

                    is_primo = True
                    for div in divisori_salvati:
                        if ii % div == 0:
                            is_primo = False
                            break

                    if is_primo:
                        # DEBUG OPZIONALE
                        if debug:
                            try:
                                import gmpy2

                                if gmpy2.is_prime(ii):
                                    primi_trovati.append(ii)
                                else:
                                    errori_debug.append(ii)
                                    print(f"⚠️ BUG RILEVATO: {ii} non è primo!")
                            except ImportError:
                                primi_trovati.append(ii)
                                print("⚠️ gmpy2 non installato, debug disabilitato")
                        else:
                            primi_trovati.append(ii)

                    # AGGIORNA PROGRESS BAR FINESTRA ogni 100 numeri
                    if idx % 100 == 0:
                        try:
                            progresso = int((idx + 1) / totale_numeri * 100)
                            self.progressBar_2.setValue(progresso)
                            QApplication.processEvents()
                        except:
                            pass

                # Completa progress bar finestra
                try:
                    self.progressBar_2.setValue(100)
                    QApplication.processEvents()
                except:
                    pass

                # Mostra risultato debug
                if debug and errori_debug:
                    print(f"\n{'='*60}")
                    print(f"⚠️ DEBUG: TROVATI {len(errori_debug)} ERRORI!")
                    print(f"{'='*60}")
                    for err in errori_debug:
                        print(f"  - {err}")
                    print(f"{'='*60}\n")

            return primi_trovati, file_usati, len(divisori_salvati)

        # ===== ESEGUI CALCOLO =====
        radice = parametri_validati["radice"]
        inizio = parametri_validati["inizio"]
        fine = parametri_validati["fine"]

        # Reset progress bar
        try:
            self.progressBar.setValue(0)
            self.progressBar_2.setValue(0)
        except:
            pass

        try:
            primi_trovati, file_usati, divisori_count = esegui_calcolo(
                radice, inizio, fine, debug=debug_attivo
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Errore durante il calcolo",
                f"Si è verificato un errore durante l'elaborazione:\n\n{str(e)}\n\n"
                "Possibili cause:\n"
                "• Intervallo troppo grande (memoria insufficiente)\n"
                "• File archivio corrotti\n"
                "• Errore di sistema\n\n"
                "Prova con un intervallo più piccolo o verifica l'archivio."
            )
            return

        parametri = {
            "base": parametri_validati["base"],
            "finestra_a": parametri_validati["f_a"],
            "finestra_b": parametri_validati["f_b"],
            "inizio": inizio,
            "fine": fine,
            "radice": radice,
            "file_usati": f"{len(file_usati)} file",
            "divisori_caricati": divisori_count,
            "debug_attivo": debug_attivo,
        }

        self.apri_finestra_statistiche(primi_trovati, parametri)

    def apri_finestra_statistiche(self, primi_trovati, parametri):
        """Apre la finestra statistiche con i dati calcolati"""
        self.seconda_finestra = FinestraDati(self)

        # Calcola statistiche
        dati = self.seconda_finestra.calcola_statistiche(primi_trovati, parametri)
        self.seconda_finestra.dati_statistiche = dati
        self.seconda_finestra.popola_finestra()

        # Nascondi finestra principale e mostra statistiche
        self.hide()
        self.seconda_finestra.show()

    def apri_dati_ui(self):
        """Apre finestra statistiche vuota (per caricare dati)"""
        self.seconda_finestra = FinestraDati(self)
        self.hide()
        self.seconda_finestra.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    finestra = ApplicazionePrincipale()
    finestra.show()
    sys.exit(app.exec_())
