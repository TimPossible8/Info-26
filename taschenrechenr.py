"""
Grafischer Taschenrechner
--------------------------
Nutzt ausschließlich die Python-Standardbibliothek (tkinter ist Teil
der Standardinstallation von Python, keine externe Bibliothek nötig).

Start:  python taschenrechner.py
"""

import tkinter as tk


class Taschenrechner:
    def __init__(self, root):
        self.root = root
        self.root.title("Taschenrechner")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e1e")

        # interner Zustand
        self.aktuelle_eingabe = ""
        self.ausdruck = ""

        # Anzeige
        self.anzeige_var = tk.StringVar(value="0")
        anzeige = tk.Entry(
            root,
            textvariable=self.anzeige_var,
            font=("Segoe UI", 28),
            justify="right",
            bd=0,
            bg="#1e1e1e",
            fg="white",
            insertbackground="white",
            state="readonly",
            readonlybackground="#1e1e1e",
        )
        anzeige.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=20, ipady=15)

        # Tastenlayout: (Beschriftung, Zeile, Spalte, Spannweite)
        tasten = [
            ("C", 1, 0, 1, "#c0392b"), ("←", 1, 1, 1, "#555555"),
            ("%", 1, 2, 1, "#555555"), ("÷", 1, 3, 1, "#e67e22"),

            ("7", 2, 0, 1, "#333333"), ("8", 2, 1, 1, "#333333"),
            ("9", 2, 2, 1, "#333333"), ("×", 2, 3, 1, "#e67e22"),

            ("4", 3, 0, 1, "#333333"), ("5", 3, 1, 1, "#333333"),
            ("6", 3, 2, 1, "#333333"), ("-", 3, 3, 1, "#e67e22"),

            ("1", 4, 0, 1, "#333333"), ("2", 4, 1, 1, "#333333"),
            ("3", 4, 2, 1, "#333333"), ("+", 4, 3, 1, "#e67e22"),

            ("±", 5, 0, 1, "#333333"), ("0", 5, 1, 1, "#333333"),
            (",", 5, 2, 1, "#333333"), ("=", 5, 3, 1, "#27ae60"),
        ]

        for text, r, c, span, farbe in tasten:
            btn = tk.Button(
                root,
                text=text,
                font=("Segoe UI", 16),
                bg=farbe,
                fg="white",
                activebackground="#666666",
                activeforeground="white",
                bd=0,
                relief="flat",
                command=lambda t=text: self.taste_gedrueckt(t),
            )
            btn.grid(row=r, column=c, columnspan=span, sticky="nsew", padx=4, pady=4, ipady=10)

        # Spalten/Zeilen gleichmäßig verteilen
        for i in range(4):
            root.grid_columnconfigure(i, weight=1)
        for i in range(6):
            root.grid_rowconfigure(i, weight=1)

        # Tastatureingabe unterstützen
        root.bind("<Key>", self.tastatur_eingabe)

    # ------------------------------------------------------------------
    def taste_gedrueckt(self, taste):
        if taste == "C":
            self.aktuelle_eingabe = ""
            self.ausdruck = ""
            self.anzeige_var.set("0")

        elif taste == "←":
            self.aktuelle_eingabe = self.aktuelle_eingabe[:-1]
            self.anzeige_var.set(self.aktuelle_eingabe if self.aktuelle_eingabe else "0")

        elif taste == "±":
            if self.aktuelle_eingabe.startswith("-"):
                self.aktuelle_eingabe = self.aktuelle_eingabe[1:]
            elif self.aktuelle_eingabe:
                self.aktuelle_eingabe = "-" + self.aktuelle_eingabe
            self.anzeige_var.set(self.aktuelle_eingabe if self.aktuelle_eingabe else "0")

        elif taste == "=":
            self.berechnen()

        elif taste in ("÷", "×", "+", "-", "%"):
            if self.aktuelle_eingabe:
                op = {"÷": "/", "×": "*"}.get(taste, taste)
                self.ausdruck += self.aktuelle_eingabe + op
                self.aktuelle_eingabe = ""
                self.anzeige_var.set(self.ausdruck)

        else:  # Ziffern und Komma
            zeichen = "." if taste == "," else taste
            self.aktuelle_eingabe += zeichen
            self.anzeige_var.set(self.aktuelle_eingabe)

    # ------------------------------------------------------------------
    def berechnen(self):
        voller_ausdruck = self.ausdruck + self.aktuelle_eingabe
        if not voller_ausdruck:
            return
        try:
            ergebnis = self.sichere_auswertung(voller_ausdruck)
            # Ganze Zahlen ohne Nachkommastellen anzeigen
            if isinstance(ergebnis, float) and ergebnis.is_integer():
                ergebnis = int(ergebnis)
            self.anzeige_var.set(str(ergebnis))
            self.aktuelle_eingabe = str(ergebnis)
            self.ausdruck = ""
        except (ZeroDivisionError, ValueError, SyntaxError):
            self.anzeige_var.set("Fehler")
            self.aktuelle_eingabe = ""
            self.ausdruck = ""

    # ------------------------------------------------------------------
    def sichere_auswertung(self, ausdruck):
        """
        Wertet einen einfachen arithmetischen Ausdruck aus, der nur
        Zahlen sowie + - * / % enthält – ganz ohne eval() oder
        externe Bibliotheken. Einfacher Shunting-Yard-Algorithmus.
        """
        erlaubte_zeichen = set("0123456789.+-*/% ")
        if not set(ausdruck) <= erlaubte_zeichen:
            raise ValueError("Ungültiges Zeichen")

        zahlen, operatoren = [], []
        rangfolge = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2}

        def anwenden():
            op = operatoren.pop()
            b = zahlen.pop()
            a = zahlen.pop()
            if op == "+":
                zahlen.append(a + b)
            elif op == "-":
                zahlen.append(a - b)
            elif op == "*":
                zahlen.append(a * b)
            elif op == "/":
                zahlen.append(a / b)
            elif op == "%":
                zahlen.append(a % b)

        i, n = 0, len(ausdruck)
        erwartet_zahl = True  # steuert Vorzeichen am Anfang / nach Operator
        while i < n:
            ch = ausdruck[i]
            if ch == " ":
                i += 1
                continue
            if ch.isdigit() or ch == "." or (ch == "-" and erwartet_zahl):
                j = i + 1
                if ch == "-":
                    j = i + 1
                while j < n and (ausdruck[j].isdigit() or ausdruck[j] == "."):
                    j += 1
                zahlen.append(float(ausdruck[i:j]))
                i = j
                erwartet_zahl = False
            elif ch in rangfolge:
                while (operatoren and rangfolge[operatoren[-1]] >= rangfolge[ch]):
                    anwenden()
                operatoren.append(ch)
                i += 1
                erwartet_zahl = True
            else:
                raise ValueError("Unerwartetes Zeichen")

        while operatoren:
            anwenden()

        if len(zahlen) != 1:
            raise ValueError("Ungültiger Ausdruck")
        return zahlen[0]

    # ------------------------------------------------------------------
    def tastatur_eingabe(self, event):
        zuordnung = {
            "\r": "=", "Return": "=",
            "BackSpace": "←",
            "Escape": "C",
        }
        char = event.char
        if char in "0123456789.+-*/%":
            taste = {"*": "×", "/": "÷", ".": ","}.get(char, char)
            self.taste_gedrueckt(taste)
        elif event.keysym in zuordnung:
            self.taste_gedrueckt(zuordnung[event.keysym])


if __name__ == "__main__":
    root = tk.Tk()
    app = Taschenrechner(root)
    root.mainloop()