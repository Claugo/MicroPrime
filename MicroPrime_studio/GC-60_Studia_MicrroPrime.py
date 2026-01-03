import sys
import os
import glob
import pickle
import json
import math
from datetime import datetime
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem


# --- CLASSE DELLA SECONDA PAGINA (STATISTICHE) ---
class FinestraDati(QtWidgets.QMainWindow):
    def __init__(self, main_window, dati_statistiche=None):
        super(FinestraDati, self).__init__()
        # Carichiamo il file .ui della seconda pagina
        uic.loadUi("finestra_dati.ui", self)

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
                "versione": "1.0",
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
            self, "Carica Statistiche", "", "JSON Files (*.json);;All Files (*)"
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
        uic.loadUi("main_PRA.ui", self)

        # Personalizzazione estetica
        self.pushButton.setStyleSheet("background-color: #4CAF50; color: white;")
        self.pushButton_2.setStyleSheet("background-color: #f44336; color: white;")

        # Collegamento azioni
        self.pushButton.clicked.connect(self.elabora_dati)
        self.pushButton_2.clicked.connect(self.apri_dati_ui)

        # Avvio automatico lettura archivio
        self.inizializza_archivio()

    def inizializza_archivio(self):
        """Controlla i file pickle lista_* e aggiorna le label"""
        files = glob.glob("lista_*.pkl")
        dimensione_archivio = 0

        if not files:
            self.label_8.setText(f"Archivio non trovato (Dim: {dimensione_archivio})")
            self.label_8.setStyleSheet("color: red;")
            return

        files.sort()

        try:
            with open(files[0], "rb") as f:
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
            dimensione_2 = int(valore_end * 60 + 10)
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

        # ===== FUNZIONE CALCOLO =====
        def esegui_calcolo(radice, inizio, fine):
            primi_trovati = []
            divisori_salvati = [7]
            trappola = fine - inizio
            radice_max = 0
            file_usati = []

            for i in range(1000):
                file_path = f"lista_{i:04d}.pkl"
                if not os.path.exists(file_path):
                    break
                file_usati.append(file_path)

                with open(file_path, "rb") as file:
                    lista = pickle.load(file)
                    riferimento = lista[-1][0]

                    for ii in range(len(lista) - 1):
                        for iii in lista[ii]:
                            divisore = (riferimento * 60 + 10) + 60 * ii + iii

                            if divisore < (trappola * 2):
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
                    if radice_max == 1:
                        break

            if inizio % 2 == 0:
                inizio += 1
            for ii in range(inizio, fine, 2):
                if ii % 3 == 0 or ii % 5 == 0:
                    continue

                is_primo = True
                for div in divisori_salvati:
                    if ii % div == 0:
                        is_primo = False
                        break

                if is_primo:
                    # DEBUG: Validazione con gmpy2 (opzionale)
                    try:
                        import gmpy2

                        if gmpy2.is_prime(ii):
                            primi_trovati.append(ii)
                        else:
                            print(f"⚠️ BUG: {ii}")
                    except ImportError:
                        primi_trovati.append(ii)

            return primi_trovati, file_usati, len(divisori_salvati)

        # ===== ESEGUI CALCOLO =====
        radice = parametri_validati["radice"]
        inizio = parametri_validati["inizio"]
        fine = parametri_validati["fine"]

        primi_trovati, file_usati, divisori_count = esegui_calcolo(radice, inizio, fine)

        parametri = {
            "base": parametri_validati["base"],
            "finestra_a": parametri_validati["f_a"],
            "finestra_b": parametri_validati["f_b"],
            "inizio": inizio,
            "fine": fine,
            "radice": radice,
            "file_usati": f"{len(file_usati)} file",
            "divisori_caricati": divisori_count,
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
