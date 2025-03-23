from data_acquisition import InfluxDBDataProvider
import tkinter as tk
from tkinter import ttk

class AlertsWindow:
    def __init__(self, root, data_acquisitor):
        self.data_acquisitor = data_acquisitor
        self.root = tk.Tk()
        self.root.title("Alarmy")
        self.root.geometry("500x350")

        self.current_page = 0;
        self.max_page = 0;
        
        self.setup_ui()
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(pady=3, padx=3, fill="both", expand=True)

        self.label = ttk.Label(main_frame, text="Strona x z y")
        self.label.grid(row=0, column=1, sticky="w")
        self.set_label();

        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky="nsew")

        columns = ("Czas", "Sensor", "Próg", "Współrzędna")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.config(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Poprzednia strona
        self.prev_button = ttk.Button(main_frame, text="Poprzednia", command=self.prev)
        self.prev_button.grid(row=2, column=0, sticky="ew")
        self.prev_button.config(state="disabled")
        # Odśwież
        self.ref_button = ttk.Button(main_frame, text="Odśwież", command=self.ref)
        self.ref_button.grid(row=2, column=1, sticky="ew")
        # Następna strona
        self.next_button = ttk.Button(main_frame, text="Następna", command=self.next)
        self.next_button.grid(row=2, column=2, sticky="ew")

        self.ref()

    def prev(self):
        if(self.current_page>0):
            self.current_page-=1
        self.ref()

    def ref(self):
        self.max_page, alerts = self.data_acquisitor.fetch_alerts(self.current_page)

        self.tree.delete(*self.tree.get_children())

        for alert in alerts:
            self.tree.insert("", "end", values=(alert["time"], alert["sensor_id"], alert["threshold"], alert["field"]))

        self.set_label()

        self.prev_button.config(state="normal" if self.current_page > 0 else "disabled")
        self.next_button.config(state="normal" if len(alerts) == 10 else "disabled")

    def next(self):
        if(self.current_page<self.max_page):
            self.current_page+=1
        self.ref()

    def set_label(self):
        self.label.config(text=f"Strona {self.current_page+1} z {self.max_page}")
