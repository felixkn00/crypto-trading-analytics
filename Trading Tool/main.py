## einbinden der benötigten bibiliotheken
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import filedialog
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import Calendar
from grab_data_from_binance import get_all_binance, OHLCV
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

class Plot:
    def __init__(self, root):
        print("initialize plot")
        self.root = root
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        self.toolbar.update()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.coin = "BTCUSDT"
        self.kline_size = '1d'
        self.select_color = '#006400'
        self.start_date = (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d')
        self.volume_label = None

        self.update_plot()


    def update_plot(self):
        # lade daten von funktion, get all binance
        ohlcv_data = get_all_binance(self.coin, self.kline_size, self.start_date, save=False)

        timestamps = [ohlcv.timestamp for ohlcv in ohlcv_data]
        close_prices = [ohlcv.close for ohlcv in ohlcv_data]

        # axen werden geleert# axen werden geleert
        self.ax.clear()
        # plot daten zuweisen und erstellen
        self.ax.plot(timestamps, close_prices, color=self.select_color)
        # setze titel# setze titel
        self.ax.set_title(f"Preis {self.coin} ({self.kline_size})")
        # datum format definieren
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        # anzahl elemente axe
        self.ax.xaxis.set_major_locator(ticker.MaxNLocator(10))
        self.fig.autofmt_xdate()
        self.ax.set_ylabel('Preis (USDT)')
        # format tick to string (00)
        self.ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:,.2f}'))
        self.ax.yaxis.set_major_locator(ticker.MaxNLocator(10))

        # marker points
        max_price = max(close_prices)  # save largest one
        print(close_prices)
        max_price_index = timestamps[close_prices.index(max_price)]
        self.ax.plot(max_price_index, max_price, 'ro')  # set marker point
        self.ax.annotate(f'Max: {max_price:.2f}\n{max_price_index.strftime("%Y-%m-%d %H:%M")}',  # description
                         xy=(max_price_index, max_price),
                         xytext=(max_price_index, max_price),
                         fontsize=6, color='black')

        min_price = min(close_prices)  # save minimum one
        min_price_index = timestamps[close_prices.index(min_price)]
        self.ax.plot(min_price_index, min_price, 'go')  # set marker point
        self.ax.annotate(f'Min: {min_price:.2f}\n{min_price_index.strftime("%Y-%m-%d %H:%M")}',  # description
                         xy=(min_price_index, min_price),
                         xytext=(min_price_index, min_price),
                         fontsize=6, color='black')

        average_price = sum(close_prices) / len(close_prices)  # avg price
        self.ax.axhline(average_price, color='orange', linestyle='--', linewidth=2)
        self.ax.annotate(f'Durchschnitt: {average_price:.2f}',  # description
                         xy=(0.5, 0.05), xycoords='axes fraction',
                         fontsize=6, color='blue',
                         bbox=dict(facecolor='white', alpha=1))

        self.canvas.draw()

    def set_kline_size(self, kline_size):
        self.kline_size = kline_size
        self.update_plot()

    def set_coin(self, coin):
        self.coin = coin
        self.update_plot()

    def set_color(self, select_color):
        self.select_color = select_color
        self.update_plot()

    def set_start_date(self, start_date):
        self.start_date = start_date
        print(f"Start date set to: {self.start_date}")
        self.update_plot()

    def get_price_above_threshold(self, threshold):
        data_fetch = get_all_binance(self.coin, self.kline_size, self.start_date, save=False)

        timestamps = [item.timestamp for item in data_fetch]
        close_prices = [item.close for item in data_fetch]

        above_threshold = [(ts, price) for ts, price in zip(timestamps, close_prices) if price > threshold]

        if not above_threshold:
            print(f"Keine Preise über {threshold} gefunden.")
            return [], []

        timestamps, prices = zip(*above_threshold)
        return timestamps, prices

    def get_volume_above_threshold(self, threshold):
        data_fetch = get_all_binance(self.coin, self.kline_size, self.start_date, save=False)

        timestamps = [item.timestamp for item in data_fetch]
        volumes = [item.volume for item in data_fetch]

        above_threshold = [(ts, volume) for ts, volume in zip(timestamps, volumes) if volume > threshold]

        timestamps, volumes = zip(*above_threshold) if above_threshold else ([], [])
        return timestamps, volumes


class Windows:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Trading Tool")
        self.root.geometry("1200x950")

        self.options = ["BTCUSDT", "ETHUSDT", "LTCUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ETCUSDT", "KSMUSDT","ENSUSDT", "SUIUSDT", "PHBUSDT", "ZILUSDT", "YGGUSDT", "DOGEUSDT", "ICPUSDT", "AAVEUSDT", "XTZUSDT", "SUSHIUSDT", "MANAUSDT", "DYDXUSDT", "CRVUSDT", "EGLDUSDT", "PEOPLEUSDT", "INJUSDT", "UNFIUSDT", "ONGUSDT", "JUPUSDT", "QNTUSDT", "SCRUSDT", "PYRUSDT"]
        self.kline_sizes = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "1d"]
        self.select_color = ["red", "blue", "green", "black", "silver"]

        # Frame Diagramm
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame für die Steuerelemente
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        tk.Label(self.control_frame, text="Coin:").pack(pady=10)

        # Suchfeld für Coin-Suche
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.control_frame, textvariable=self.search_var)
        self.search_entry.pack(pady=10)
        self.search_entry.bind("<KeyRelease>", self.filter_coins)

        # Listbox für die Coin-Auswahl
        self.coin_listbox = tk.Listbox(self.control_frame)
        self.coin_listbox.pack(pady=10)
        self.coin_listbox.bind("<<ListboxSelect>>", self.select_coin)
        self.populate_coins()

        # Kline-Größe Dropdown Widget
        self.kline_label = tk.Label(self.control_frame, text="Kline-Größe:")
        self.kline_label.pack(pady=10)
        self.kline_size_var = tk.StringVar(value=self.kline_sizes[0])
        self.kline_size_dropdown = ttk.Combobox(self.control_frame, textvariable=self.kline_size_var,
                                                values=self.kline_sizes, state="readonly")
        self.kline_size_dropdown.pack(pady=10)
        self.kline_size_dropdown.bind("<<ComboboxSelected>>", self.change_kline_size)

        # Farbauswahl Widget
        self.color_label = tk.Label(self.control_frame, text="Farbe:")
        self.color_label.pack(pady=10)
        self.select_color_var = tk.StringVar(value=self.select_color[0])
        self.color_dropdown = ttk.Combobox(self.control_frame, textvariable=self.select_color_var,
                                           values=self.select_color, state="readonly")
        self.color_dropdown.pack(pady=10)
        self.color_dropdown.bind("<<ComboboxSelected>>", self.change_color)

        # Volume Input Widget
        self.volume_label = tk.Label(self.control_frame, text="")
        self.volume_label.pack(pady=10)

        # Kalender Datum Widget
        self.start_date_label = tk.Label(self.control_frame, text="Startdatum:")
        self.start_date_label.pack(pady=10)
        self.calendar = Calendar(self.control_frame, selectmode='day', year=datetime.now().year,
                                 month=datetime.now().month, day=datetime.now().day)
        self.calendar.pack(pady=10)

        # Button "Datum setzen" Widget
        self.set_date_button = tk.Button(self.control_frame, text="Datum setzen", command=self.set_start_date)
        self.set_date_button.pack(pady=10)

        # Schwellenwert Preis Widget
        self.price_threshold_label = tk.Label(self.control_frame, text="Preis-Schwellenwert:")
        self.price_threshold_label.pack(pady=10)
        self.price_threshold_entry = tk.Entry(self.control_frame)
        self.price_threshold_entry.pack(pady=10)
        self.price_threshold_button = tk.Button(self.control_frame, text="Preise über Schwelle anzeigen",
                                                command=self.show_prices_above_threshold)
        self.price_threshold_button.pack(pady=10)

        # Schwellenwert Volume Widget
        self.volume_threshold_label = tk.Label(self.control_frame, text="Volumen-Schwellenwert:")
        self.volume_threshold_label.pack(pady=10)
        self.volume_threshold_entry = tk.Entry(self.control_frame)
        self.volume_threshold_entry.pack(pady=10)
        self.volume_threshold_button = tk.Button(self.control_frame, text="Volumen über Schwelle anzeigen",
                                                 command=self.show_volumes_above_threshold)
        self.volume_threshold_button.pack(pady=10)

        self.plot = Plot(self.plot_frame)

    def populate_coins(self):
        for coin in self.options:
            self.coin_listbox.insert(tk.END, coin)

    def filter_coins(self, event):
        print(f"{event.keysm}")
        search_term = self.search_var.get().lower()
        self.coin_listbox.delete(0, tk.END) # delete all coins from list
        for coin in self.options:
            if search_term in coin.lower():
                self.coin_listbox.insert(tk.END, coin) # insert only coins, by term

    def select_coin(self, event):
        selected_coin = self.coin_listbox.get(self.coin_listbox.curselection())
        self.plot.set_coin(selected_coin)

    def change_kline_size(self, event):
        selected_kline_size = self.kline_size_var.get()
        self.plot.set_kline_size(selected_kline_size)

    def change_color(self, event):
        selected_color = self.select_color_var.get()
        self.plot.set_color(selected_color)

    def set_start_date(self):

        new_date = self.calendar.get_date()
        # convert date string to date-object
        try:
            new_date = datetime.strptime(new_date, '%d.%m.%y')
            formatted_date = new_date.strftime('%Y-%m-%d')
            self.plot.set_start_date(formatted_date)
        except ValueError as e:
            messagebox.showerror("Fehler", f"Ungültiges Datum: {e}")

    def show_prices_above_threshold(self):
        threshold = self.price_threshold_entry.get()
        try:
            threshold = float(threshold)
            timestamps, prices = self.plot.get_price_above_threshold(threshold)
            if timestamps:
                # create new window tab
                save_window = tk.Toplevel(self.root)
                save_window.title("Preise über Schwelle")
                save_window.geometry("400x400")

                # list content
                price_text = tk.Text(save_window, wrap=tk.WORD)
                price_text.insert(tk.END, f"Preise über {threshold}:\n")
                price_text.insert(tk.END, "\n".join(f"{ts}: {price:.2f}" for ts, price in zip(timestamps, prices)))
                price_text.config(state=tk.DISABLED)  # show text field
                price_text.pack(pady=10, fill=tk.BOTH, expand=True)

                # save list
                save_button = tk.Button(save_window, text="Liste speichern",
                                        command=lambda: self.save_price_list(timestamps, prices))
                save_button.pack(pady=10)
            else:
                messagebox.showinfo("Preise über Schwelle", f"Keine Preise über {threshold} gefunden.")
        except ValueError:
            messagebox.showerror("Fehler", "Bitte einen gültigen Preis eingeben.")

    def save_price_list(self, timestamps, prices):
        # open dialog windows to name and save area
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")],
                                                title="Speichern unter",
                                                initialfile="preise_liste.csv")
        if filename:
            # save data
            df = pd.DataFrame({'timestamp': timestamps, 'price': prices})
            df.to_csv(filename, index=False)
            messagebox.showinfo("Erfolg", f"Die Liste wurde erfolgreich unter {filename} gespeichert.")

    def show_volumes_above_threshold(self):
        threshold = self.volume_threshold_entry.get()
        try:
            threshold = float(threshold)
            timestamps, volumes = self.plot.get_volume_above_threshold(threshold)
            if timestamps:
                # create new tab window
                save_window = tk.Toplevel(self.root)
                save_window.title("Volumen über Schwelle")
                save_window.geometry("400x400")

                # list content
                volume_text = tk.Text(save_window, wrap=tk.WORD)
                volume_text.insert(tk.END, f"Volumen über {threshold}:\n")
                volume_text.insert(tk.END, "\n".join(f"{ts}: {volume:.2f}" for ts, volume in zip(timestamps, volumes)))
                volume_text.config(state=tk.DISABLED)  # text visible
                volume_text.pack(pady=10, fill=tk.BOTH, expand=True)

                # save list
                save_button = tk.Button(save_window, text="Liste speichern",
                                        command=lambda: self.save_volume_list(timestamps, volumes))
                save_button.pack(pady=10)
            else:
                messagebox.showinfo("Volumen über Schwelle", f"Keine Volumen über {threshold} gefunden.")
        except ValueError:
            messagebox.showerror("Fehler", "Bitte einen gültigen Volumenwert eingeben.")

    def save_volume_list(self, timestamps, volumes):
        # open dialog windows to name and save area
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")],
                                                title="Speichern unter",
                                                initialfile="volumen_liste.csv")
        if filename:
            # save it
            df = pd.DataFrame({'timestamp': timestamps, 'volume': volumes})
            df.to_csv(filename, index=False)
            messagebox.showinfo("Erfolg", f"Die Liste wurde erfolgreich unter {filename} gespeichert.")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    windows = Windows()
    windows.run()
