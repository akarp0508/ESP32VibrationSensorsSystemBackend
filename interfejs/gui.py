import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
from data_acquisition import InfluxDBDataProvider
from datetime import datetime  
import MQTTDialog
from message_sender import MQTT_data_provider;
import InfluxDialog
from analysis_helper import fft_analysis

class MainWindow:
    def __init__(self, root):
        self.message_controller = None
        self.data_acquisitor = None
        self.root = root
        self.root.title("System Rozproszonych Czujników Inercyjnych")
        self.root.geometry("1000x800")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.setup_ui()

    def setup_ui(self):
        # Utworzono frame dla lepszego ułożenia elementów w oknie
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        ttk.Label(main_frame, text="Odczyt danych:", font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Wybór współrzędnej
        ttk.Label(main_frame, text="Wybierz współrzędną:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.combobox_var = tk.StringVar()
        self.combobox = ttk.Combobox(main_frame, textvariable=self.combobox_var, values=["x", "y", "z"], state="readonly")
        self.combobox.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        self.combobox.current(0)

        # Wybór czujnika
        ttk.Label(main_frame, text="Wybierz czujnik:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.sensor_combobox = ttk.Combobox(main_frame)
        self.sensor_combobox.grid(row=2, column=1, columnspan=2, padx=5, pady=5)
        self.sensor_combobox.set("Odśwież czujniki...")

        # Przycisk do odświeżenia czujników
        self.refresh_button = ttk.Button(main_frame, text="Odśwież czujniki", command=self.refresh_combobox)
        self.refresh_button.grid(row=3, column=0, columnspan=3, pady=10, padx=78, sticky="ew")

        # Opis pól
        ttk.Label(main_frame, text="Dzień").grid(row=4, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(main_frame, text="Czas (hh:mm:ss)").grid(row=4, column=2, padx=5, pady=5, sticky="w")

        # Wybór daty od
        ttk.Label(main_frame, text="Od:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.start_date_entry = DateEntry(main_frame, showsecond=True, date_pattern="yyyy-mm-dd")
        self.start_date_entry.grid(row=5, column=1, padx=5, pady=5)

        self.start_hour = ttk.Combobox(main_frame, values=[f"{i:02}" for i in range(24)], width=3)
        self.start_hour.set("0")
        self.start_minute = ttk.Combobox(main_frame, values=[f"{i:02}" for i in range(60)], width=3)
        self.start_minute.set("0")
        self.start_second = ttk.Combobox(main_frame, values=[f"{i:02}" for i in range(60)], width=3)
        self.start_second.set("0")

        self.start_hour.grid(row=5, column=2, padx=2, pady=5, sticky="w")
        self.start_minute.grid(row=5, column=2, padx=40, pady=5, sticky="w")
        self.start_second.grid(row=5, column=2, padx=80, pady=5, sticky="w")

        # Wybór daty do
        ttk.Label(main_frame, text="Do:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.end_date_entry = DateEntry(main_frame, showsecond=True, date_pattern="yyyy-mm-dd")
        self.end_date_entry.grid(row=6, column=1, padx=5, pady=5)

        self.end_hour = ttk.Combobox(main_frame, values=[f"{i:02}" for i in range(24)], width=3)
        self.end_hour.set("23")
        self.end_minute = ttk.Combobox(main_frame, values=[f"{i:02}" for i in range(60)], width=3)
        self.end_minute.set("59")
        self.end_second = ttk.Combobox(main_frame, values=[f"{i:02}" for i in range(60)], width=3)
        self.end_second.set("59")

        self.end_hour.grid(row=6, column=2, padx=2, pady=5, sticky="w")
        self.end_minute.grid(row=6, column=2, padx=40, pady=5, sticky="w")
        self.end_second.grid(row=6, column=2, padx=80, pady=5, sticky="w")

        ttk.Label(main_frame, text="Wygląd wykresu:").grid(row=7, column=0, padx=5, pady=5, sticky="w")

        self.lines_var = tk.IntVar(value = 1)
        self.points_var = tk.IntVar()
        
        ttk.Checkbutton(main_frame, text="Linie", variable=self.lines_var).grid(row=7, column=1)
        ttk.Checkbutton(main_frame, text="Punkty", variable=self.points_var).grid(row=7, column=2)

        # Wybór analizy
        ttk.Label(main_frame, text="Wybierz rodzaj wykresu:").grid(row=8, column=0, padx=5, pady=5, sticky="w")
        self.analysis_combobox_var = tk.StringVar()
        self.analysis_combobox = ttk.Combobox(main_frame, textvariable=self.analysis_combobox_var, values=["Dane", "FFT", "Amplitudowa"], state="readonly")
        self.analysis_combobox.grid(row=8, column=1, columnspan=2, padx=5, pady=5)
        self.analysis_combobox.set("Dane")

        # Przycisk Pokaż
        self.get_button = ttk.Button(main_frame, text="Pokaż", command=self.on_get_button)
        self.get_button.grid(row=9, column=0, columnspan=3, pady=15, padx=78, sticky="ew")

        # Wykres
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()

        # --------------------
        # ELEMENTY DO STEROWANIA URZĄDZENIAMI
        ttk.Label(main_frame, text="Kontrola czujników:", font=("TkDefaultFont", 12, "bold")).grid(row=0, column=7, padx=5, pady=5, sticky="w")

        # ComboBox do wyboru czujnika
        ttk.Label(main_frame, text="Wybierz czujnik:").grid(row=1, column=7, padx=5, pady=5, sticky="w")
        self.combobox_var2 = tk.StringVar()
        self.combobox2 = ttk.Combobox(main_frame, textvariable=self.combobox_var2, values=["Wszystkie"], state="readonly")
        self.combobox2.grid(row=1, column=8, columnspan=2, padx=5, pady=5)
        self.combobox2.current(0)

        # Przycisk do odświeżenia czujników
        self.refresh_button2 = ttk.Button(main_frame, text="Odśwież czujniki", command=self.refresh_combobox2)
        self.refresh_button2.grid(row=2, column=7, columnspan=3, pady=10, padx=78, sticky="ew")

        # ComboBox do trybu odczytu
        ttk.Label(main_frame, text="Wybierz tryb odczytu:").grid(row=3, column=7, padx=5, pady=5, sticky="w")
        self.read_type_combobox_var = tk.StringVar()
        self.read_type_combobox = ttk.Combobox(main_frame, textvariable=self.read_type_combobox_var, values=["Wyłączony", "Ciągły", "Aktywowany"], state="readonly")
        self.read_type_combobox.grid(row=3, column=8, columnspan=2, padx=5, pady=5)
        self.read_type_combobox.current(0)
        # Bind the event to the method
        self.read_type_combobox.bind("<<ComboboxSelected>>", self.read_type_changed)

        # Ilość pomiarów na sekunde
        ttk.Label(main_frame, text="Ilość pomiarów na sekunde:").grid(row=4, column=7, padx=5, pady=5, sticky="w")
        self.read_freq_combobox_var = tk.StringVar()
        self.read_freq_combobox = ttk.Combobox(main_frame, textvariable=self.read_freq_combobox_var, values=["100", "10", "1"], state="readonly")
        self.read_freq_combobox.grid(row=4, column=8, columnspan=2, padx=5, pady=5)
        self.read_freq_combobox.current(0)
        self.read_freq_combobox.config(state="disabled")

        # Wartość do aktywacji pomiaru
        ttk.Label(main_frame, text="Wartość do aktywacji pomiaru:").grid(row=5, column=7, padx=5, pady=5, sticky="w")
        self.threshold_var = tk.DoubleVar()
        self.threshold_entry = ttk.Entry(main_frame, textvariable=self.threshold_var)
        self.threshold_entry.grid(row=5, column=8, columnspan=2, padx=5, pady=5)
        self.threshold_entry.config(state="disabled")

        # Przycisk do wysłania wiadomości
        self.send_button = ttk.Button(main_frame, text="Ustaw", command=self.send_read_type_data)
        self.send_button.grid(row=6, column=7, columnspan=3, pady=10, padx=78, sticky="ew")

    def read_type_changed(self, event):
        selected_value = self.read_type_combobox.get()
        if(selected_value == "Aktywowany"):
            self.threshold_entry.config(state="enabled")
        else:
            self.threshold_entry.config(state="disabled")
        if(selected_value=="Wyłączony"):
            self.read_freq_combobox.config(state="disabled")
        else:
            self.read_freq_combobox.config(state="enabled")

    def send_read_type_data(self):
        read_type = self.read_type_combobox["values"].index(self.read_type_combobox_var.get())
        sensor_id = self.combobox_var2.get()
        freq = int(self.read_freq_combobox_var.get())
        threshold = self.threshold_var.get()
        self.message_controller.send_read_type_data(read_type,sensor_id,freq,threshold)

    def on_get_button(self):
        self.update_plot()

    def refresh_combobox2(self):
        self.combobox2["values"] = list(["Wszystkie"])
        self.combobox2.set("Wszystkie")
        self.create_message_controller_if_it_does_not_exist();
        self.message_controller.request_active()

    def create_message_controller_if_it_does_not_exist(self):
        if(self.message_controller == None):
            ip, port, username, password = MQTTDialog.get_mqtt_credentials();
            self.message_controller = MQTT_data_provider(ip,port,username = username,password = password,main_window = self);
    
    def create_data_aquisitor_if_it_does_not_exist(self):
        if(self.data_acquisitor == None):
            ip, port, username, password = InfluxDialog.get_influxdb_credentials();
            self.data_acquisitor = InfluxDBDataProvider(ip,port,username = username,password = password);
        
    def add_new_sensor_to_combobox2(self, sensor_id):
        values = list(self.combobox2["values"])
        if(sensor_id not in values):
            values.append(sensor_id)
            self.combobox2["values"] = values

    def update_plot(self):
        selected_value = self.combobox_var.get()

        start_datetime, end_datetime = self.get_selected_dates()
        sensor_id = self.sensor_combobox.get()
        
        # Pozyskanie danych
        self.create_data_aquisitor_if_it_does_not_exist();
        x_data, y_data = self.data_acquisitor.fetch_data(selected_value, start_datetime, end_datetime, sensor_id)
        if(self.analysis_combobox_var.get()=="FFT"):
            x_data, y_data = fft_analysis(x_data, y_data);

        marker = "o" if self.points_var.get()==1 else ""
        linestyle = "-" if self.lines_var.get()==1 else ""

        # Aktualizacja wykresu
        self.ax.clear()
        self.ax.plot(x_data, y_data, marker=marker, linestyle=linestyle, label=f"Wykres wartości {selected_value}")
        self.ax.legend()

        # Ograniczenie wartości wypisanych na osiach
        self.ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        self.ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

        # Formatowanie daty na osi X
        if(self.analysis_combobox_var.get()=="Dane"):
            plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d-%m %H:%M:%S'))

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
        self.create_data_aquisitor_if_it_does_not_exist();
        new_options = self.data_acquisitor.get_sensor_ids()
        self.sensor_combobox["values"] = new_options
        if(len(new_options)>0):
            self.sensor_combobox.set(new_options[0])
        print("Odświeżono czujniki: ", new_options)

    def on_close(self):
        print("Zamykanie okna")
        self.root.quit()
        self.root.destroy()
