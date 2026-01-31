import sys
import json
import math
from datetime import datetime
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QApplication
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QTextDocument

class EditorStatistiche(QtWidgets.QMainWindow):
    def __init__(self, dati_statistiche=None):
        super(EditorStatistiche, self).__init__()
        # Carica l'interfaccia originale
        try:
            uic.loadUi("finestra_dati_Gap.ui", self)
        except Exception as e:
            print(f"Errore caricamento UI: {e}")

        self.dati_statistiche = dati_statistiche

        # Configurazione pulsante Esporta
        self.pushButton_esporta.setText("Esporta PDF")
        self.pushButton_esporta.setStyleSheet("""
            QPushButton {
                background-color: #0078d7; 
                color: white; 
                font-weight: bold; 
                font-size: 13px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #005a9e; }
        """)

        # Collegamenti
        self.pushButton_esporta.clicked.connect(self.esporta_pdf)
        self.pushButton_carica.clicked.connect(self.carica_statistiche)
        self.pushButton_chiudi.clicked.connect(self.close)

        if self.dati_statistiche:
            self.popola_finestra()

    def carica_statistiche(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Carica Statistiche", "", "JSON Files (*.json)")
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    self.dati_statistiche = json.load(f)
                self.popola_finestra()
                QtWidgets.QMessageBox.information(self, "Successo", "Dati caricati correttamente!")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Errore", f"Caricamento fallito: {str(e)}")

    def popola_finestra(self):
        """Popola i widget dell'interfaccia con i dati caricati"""
        if not self.dati_statistiche:
            return

        p = self.dati_statistiche["parametri"]
        r = self.dati_statistiche["risultati"]
        s = self.dati_statistiche["statistiche"]

        # --- RIEPILOGO ---
        self.label_intervallo.setText(f"[{p['inizio']:,} - {p['fine']:,}]".replace(",", "."))
        self.label_ampiezza.setText(f"{r['ampiezza']:,}".replace(",", "."))
        self.label_count_primi.setText(str(r["count_primi"]))
        self.label_file_usati.setText(p.get("file_usati", "-"))
        self.label_divisori.setText(str(p.get("divisori_caricati", "-")))

        # --- DENSITÀ ---
        self.label_densita_reale.setText(f"{s['densita_reale']:.4f}%")
        self.label_densita_teorica.setText(f"{s['densita_teorica']:.4f}%")
        diff = s["differenza"]
        self.label_differenza.setText(f"{diff:+.4f}%")
        self.label_differenza.setStyleSheet(f"font-weight: bold; color: {'green' if diff > 0 else 'red'};")
        self.progressBar_densita.setValue(int(min(s["densita_reale"], 20)))

        # --- GAP E SPECIALI ---
        self.label_gap_min.setText(str(s["gap_min"]))
        self.label_gap_max.setText(str(s["gap_max"]))
        self.label_gap_medio.setText(f"{s['gap_medio']:.1f}")
        
        sp = s["primi_speciali"]
        self.label_gemelli.setText(f"{len(sp['gemelli'])} coppie")
        self.label_cugini.setText(f"{len(sp['cugini'])} coppie")
        self.label_sexy.setText(f"{len(sp['sexy'])} coppie")

        # --- MODULO 60 (HTML) ---
        mod60 = s["distribuzione_mod60"]
        total = sum(mod60.values())
        html = "<table border='1' width='100%' style='border-collapse: collapse; font-family: sans-serif;'>"
        html += "<tr style='background-color: #2196F3; color: white;'><th>Pos</th><th>Count</th><th>%</th></tr>"
        for pos in sorted(mod60.keys(), key=int):
            count = mod60[pos]
            perc = (count / total * 100) if total > 0 else 0
            bg = "#e3f2fd" if count > 0 else "#ffffff"
            html += f"<tr style='background-color: {bg};'><td align='center'>{pos}</td>"
            html += f"<td align='center'>{count}</td><td align='center'>{perc:.1f}%</td></tr>"
        html += "</table>"
        self.textBrowser_mod60.setHtml(html)

        # --- TABELLA PRIMI ---
        primi = r["primi_trovati"]
        gap_lista = s["gap_lista"]
        self.tableWidget_primi.setRowCount(len(primi))
        for i, primo in enumerate(primi):
            self.tableWidget_primi.setItem(i, 0, QTableWidgetItem(f"{primo:,}".replace(",", ".")))
            self.tableWidget_primi.setItem(i, 1, QTableWidgetItem(str(i + 1)))
            if i > 0:
                gap = gap_lista[i - 1]
                item_gap = QTableWidgetItem(str(gap))
                if gap == 2: item_gap.setBackground(Qt.yellow)
                elif gap == 4: item_gap.setBackground(Qt.cyan)
                elif gap == 6: item_gap.setBackground(Qt.magenta)
                self.tableWidget_primi.setItem(i, 2, item_gap)
            else:
                self.tableWidget_primi.setItem(i, 2, QTableWidgetItem("-"))
            self.tableWidget_primi.setItem(i, 3, QTableWidgetItem(str(primo % 60)))
        self.tableWidget_primi.resizeColumnsToContents()

    def esporta_pdf(self):
        """Genera il report PDF dettagliato per l'archivio"""
        if not self.dati_statistiche: return
        
        p = self.dati_statistiche["parametri"]
        s = self.dati_statistiche["statistiche"]
        r = self.dati_statistiche["risultati"]

        filepath, _ = QFileDialog.getSaveFileName(self, "Salva Report PDF", f"MicroPrime_{p['inizio']}.pdf", "PDF Files (*.pdf)")
        if not filepath: return

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setPaperSize(QPrinter.A4)
        printer.setOutputFileName(filepath)

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial; color: #333; margin: 20px; }}
                .header {{ border-bottom: 2px solid #0078d7; padding-bottom: 10px; margin-bottom: 20px; }}
                .title {{ color: #0078d7; font-size: 22pt; font-weight: bold; }}
                .section {{ margin-top: 20px; border: 1px solid #ddd; padding: 10px; background-color: #f9f9f9; }}
                .sec-title {{ font-weight: bold; color: #0078d7; border-bottom: 1px solid #ddd; margin-bottom: 10px; text-transform: uppercase; }}
                table.info {{ width: 100%; margin-top: 5px; }}
                table.info td {{ padding: 4px; font-size: 11pt; }}
                .highlight {{ color: #2e7d32; font-weight: bold; font-size: 14pt; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">Report Tecnico MicroPrime - GC-60</div>
                <div align="right"><i>Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}</i></div>
            </div>

            <div class="section">
                <div class="sec-title">Dati Ricerca e Archivio</div>
                <table class="info">
                    <tr><td><b>Intervallo:</b></td><td>{self.label_intervallo.text()}</td></tr>
                    <tr><td><b>Ampiezza Finestra:</b></td><td>{r['ampiezza']:,} numeri</td></tr>
                    <tr><td><b>Primi Trovati:</b></td><td class="highlight">{r['count_primi']}</td></tr>
                    <tr><td><b>File Archivio usati:</b></td><td>{p.get('file_usati', '-')}</td></tr>
                    <tr><td><b>Divisori Caricati:</b></td><td>{p.get('divisori_caricati', '-')}</td></tr>
                </table>
            </div>

            <div class="section">
                <div class="sec-title">Analisi Densità e Scostamento</div>
                <table class="info">
                    <tr><td><b>Densità Reale:</b></td><td>{s['densita_reale']:.4f}%</td></tr>
                    <tr><td><b>Densità Teorica:</b></td><td>{s['densita_teorica']:.4f}%</td></tr>
                    <tr><td><b>Differenza:</b></td><td>{s['differenza']:+.4f}%</td></tr>
                </table>
            </div>

            <div class="section">
                <div class="sec-title">Statistiche Gap e Coppie Speciali</div>
                <table class="info">
                    <tr><td><b>Gap Min/Max/Medio:</b></td><td>{s['gap_min']} / {s['gap_max']} / {s['gap_medio']}</td></tr>
                    <tr><td><b>Coppie Gemelli (gap 2):</b></td><td>{len(s['primi_speciali']['gemelli'])}</td></tr>
                    <tr><td><b>Coppie Cugini (gap 4):</b></td><td>{len(s['primi_speciali']['cugini'])}</td></tr>
                    <tr><td><b>Coppie Sexy (gap 6):</b></td><td>{len(s['primi_speciali']['sexy'])}</td></tr>
                </table>
            </div>

            <div class="section">
                <div class="sec-title">Distribuzione Modulo 60</div>
                {self.textBrowser_mod60.toHtml()}
            </div>

            <div align="center" style="margin-top: 40px; color: #888; font-size: 9pt;">
                Metodologia GC-60 basata su traslazione di divisori noti | Autore: Govi Claudio
            </div>
        </body>
        </html>
        """.replace(",", ".") # Formattazione italiana per le migliaia

        doc = QTextDocument()
        doc.setHtml(html)
        doc.print_(printer)
        QtWidgets.QMessageBox.information(self, "PDF", "Report d'archivio generato con successo!")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    editor = EditorStatistiche()
    editor.show()
    sys.exit(app.exec_())