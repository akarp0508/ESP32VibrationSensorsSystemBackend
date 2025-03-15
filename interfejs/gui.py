import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
from data_acquisition import fetch_data, get_sensor_ids
from datetime import datetime  

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("System Rozproszonych Czujników Inercyjnych")
        self.root.geometry("1000x800")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.setup_ui()

    def setup_ui(self):
        # Create a frame for better layout
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Wybór współrzędnej
        ttk.Label(main_frame, text="Wybierz współrzędną:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combobox_var = tk.StringVar()
        self.combobox = ttk.Combobox(main_frame, textvariable=self.combobox_var, values=["x", "y", "z"], state="readonly")
        self.combobox.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        self.combobox.current(0)

        # Wybór czujnika
        ttk.Label(main_frame, text="Wybierz czujnik:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.sensor_combobox = ttk.Combobox(main_frame)
        self.sensor_combobox.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        self.sensor_combobox.set("Odśwież czujniki...")

        # Przycisk do odświeżenia czujników
        self.refresh_button = ttk.Button(main_frame, text="Odśwież czujniki", command=self.refresh_combobox)
        self.refresh_button.grid(row=2, column=0, columnspan=3, pady=10, padx=78, sticky="ew")

        # Opis pól
        ttk.Label(main_frame, text="Dzień").grid(row=3, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(main_frame, text="Czas (hh:mm:ss)").grid(row=3, column=2, padx=5, pady=5, sticky="w")

        # Wybór daty od
        ttk.Label(main_frame, text="Od:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.start_date_entry = DateEntry(main_frame, showsecond=True, date_pattern="yyyy-mm-dd")
        self.start_date_entry.grid(row=4, column=1, padx=5, pady=5)

        self.start_hour = ttk.Combobox(main_frame, values=[f"{i:02}" for i in range(24)], width=3)
        self.start_hour.set("0")
        self.start_minute = ttk.Combobox(main_frame, values=[f"{i:02}" for i in range(60)], width=3)
        self.start_minute.set("0")
        self.start_second = ttk.Combobox(main_frame, values=[f"{i:02}" for i in range(60)], width=3)
        self.start_second.set("0")

        self.start_hour.grid(row=4, column=2, padx=2, pady=5, sticky="w")
        self.start_minute.grid(row=4, column=2, padx=40, pady=5, sticky="w")
        self.start_second.grid(row=4, column=2, padx=80, pady=5, sticky="w")

        # Wybór daty do
        ttk.Label(main_frame, text="Do:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.end_date_entry = DateEntry(main_frame, showsecond=True, date_pattern="yyyy-mm-dd")
        self.end_date_entry.grid(row=5, column=1, padx=5, pady=5)

        self.end_hour = ttk.Combobox(main_frame, values=[f"{i:02}" for i in range(24)], width=3)
        self.end_hour.set("23")
        self.end_minute = ttk.Combobox(main_frame, values=[f"{i:02}" for i in range(60)], width=3)
        self.end_minute.set("59")
        self.end_second = ttk.Combobox(main_frame, values=[f"{i:02}" for i in range(60)], width=3)
        self.end_second.set("59")

        self.end_hour.grid(row=5, column=2, padx=2, pady=5, sticky="w")
        self.end_minute.grid(row=5, column=2, padx=40, pady=5, sticky="w")
        self.end_second.grid(row=5, column=2, padx=80, pady=5, sticky="w")

        ttk.Label(main_frame, text="Wygląd wykresu:").grid(row=6, column=0, padx=5, pady=5, sticky="w")

        self.lines_var = tk.IntVar(value = 1)
        self.points_var = tk.IntVar()
        
        ttk.Checkbutton(main_frame, text="Linie", variable=self.lines_var).grid(row=6, column=1)
        ttk.Checkbutton(main_frame, text="Punkty", variable=self.points_var).grid(row=6, column=2)

        # Przycisk Pokaż
        self.get_button = ttk.Button(main_frame, text="Pokaż", command=self.on_get_button)
        self.get_button.grid(row=7, column=0, columnspan=3, pady=15, padx=78, sticky="ew")

        # Wykres
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()

        # --------------------
        # ELEMENTY DO STEROWANIA URZĄDZENIAMI

    def on_get_button(self):
        self.update_plot()

    def update_plot(self):
        """Updates the plot based on the selected value from the combobox."""
        selected_value = self.combobox_var.get()

        start_datetime, end_datetime = self.get_selected_dates()
        sensor_id = self.sensor_combobox.get()
        
        # Pozyskanie danych
        x_data, y_data = fetch_data(selected_value, start_datetime, end_datetime, sensor_id)

        marker = "o" if self.points_var.get()==1 else ""
        linestyle = "-" if self.lines_var.get()==1 else ""

        # Aktualizacja wykresu
        self.ax.clear()
        self.ax.plot(x_data, y_data, marker=marker, linestyle=linestyle, label=f"Wykres wartości {selected_value}")
        self.ax.legend()

        # Ograniczenie wartości wypisanych na osiach
        self.ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        self.ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

        self.canvas.draw()

    def get_selected_dates(self):
        """Fetches selected start and end date-time values as datetime objects."""
        
        # Data
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()

        # Czas w formacie string
        start_time = f"{self.start_hour.get()}:{self.start_minute.get()}:{self.start_second.get()}"
        end_time = f"{self.end_hour.get()}:{self.end_minute.get()}:{self.end_second.get()}"

        # Data + czas
        start_datetime_str = f"{start_date} {start_time}"
        end_datetime_str = f"{end_date} {end_time}"

        # Konwersja do obiektu typu datetime
        start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M:%S")

        print(f"Selected Start Date-Time: {start_datetime}")
        print(f"Selected End Date-Time: {end_datetime}")

        return start_datetime, end_datetime

    def refresh_combobox(self):
        """Fetch new options for the editable combobox and update it."""
        new_options = get_sensor_ids()
        self.sensor_combobox["values"] = new_options
        self.sensor_combobox.set(new_options[0])
        print("Odświeżono czujniki: ", new_options)

    def on_close(self):
        """Handle window close event."""
        print("Zamykanie okna")
        self.root.quit()
        self.root.destroy()
