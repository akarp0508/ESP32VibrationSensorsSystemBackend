import tkinter as tk
from tkinter import simpledialog

class MQTTDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Podaj dane brokera MQTT")
        self.geometry("300x300")

        self.ip_label = tk.Label(self, text="IP Brokera:")
        self.ip_label.pack(pady=5)
        self.ip_entry = tk.Entry(self)
        self.ip_entry.pack(pady=5)

        self.port_label = tk.Label(self, text="Port Brokera:")
        self.port_label.pack(pady=5)
        self.port_entry = tk.Entry(self)
        self.port_entry.pack(pady=5)

        self.username_label = tk.Label(self, text="Nazwa użytkownika:")
        self.username_label.pack(pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        self.password_label = tk.Label(self, text="Hasło:")
        self.password_label.pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        self.submit_button = tk.Button(self, text="Połącz", command=self.on_submit)
        self.submit_button.pack(pady=10)

        self.result = None

    def on_submit(self):
        ip = self.ip_entry.get()
        port = self.port_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if ip and port:
            self.result = (ip, port, username, password)
            self.destroy()
        else:
            self.show_error("IP i port są wymagane")

    def show_error(self, message):
        error_window = tk.Toplevel(self)
        error_window.title("Błąd")
        error_label = tk.Label(error_window, text=message)
        error_label.pack(pady=20)
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack(pady=5)

def get_mqtt_credentials():
    root = tk.Tk()
    root.withdraw()

    dialog = MQTTDialog(root)
    root.wait_window(dialog)

    if dialog.result:
        ip, port, username, password = dialog.result
        return ip, port, username, password
    else:
        print("Nie otrzymano danych.")
        return None, None, None, None

if __name__ == "__main__":
    get_mqtt_credentials()
