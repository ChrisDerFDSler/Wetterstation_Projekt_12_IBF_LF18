import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import matplotlib.dates as mdates

# --- DATENBANK KONFIGURATION ---
DB_CONFIG = {
    'host': '10.118.49.89',
    'user': 'wetterstation2026_db',
    'password': '54tzck232026',
    'database': 'wetterstation2026_db',
    'port': 3306
}

class WetterAnalyseLive:
    def __init__(self, root):
        self.root = root
        self.root.title("Wetterstation 2026 - LIVE MONITORING")
        self.root.geometry("1600x950")
        
        # Einstellungen
        self.view_mode = tk.StringVar(value="user") 
        self.auto_refresh = tk.BooleanVar(value=True) # Live-Update standardmäßig an
        self.refresh_interval = 5000 # Intervall in Millisekunden (5 Sekunden)
        
        self.user_vars = {} 
        self.ort_vars = {}
        self.det_vars = {k: tk.BooleanVar(value=v) for k, v in [('id',True), ('ort',True), ('str',False), ('nr',False), ('plz',False)]}
        self.show_vars = {k: tk.BooleanVar(value=v) for k, v in [('temp',True), ('hum',False), ('press',False), ('gas',False)]}

        self.setup_ui()
        self.load_data()
        
        # Live-Loop starten
        self.run_live_update()

    def setup_ui(self):
        # TOP BAR für Status & Live-Settings
        top_bar = tk.Frame(self.root, bg="#2c3e50", height=40)
        top_bar.pack(side=tk.TOP, fill=tk.X)
        
        tk.Label(top_bar, text="LIVE-MONITORING:", fg="white", bg="#2c3e50", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(top_bar, text="Aktiv", variable=self.auto_refresh, bg="#2c3e50", fg="white", selectcolor="#34495e", activebackground="#2c3e50").pack(side=tk.LEFT)
        
        self.status_label = tk.Label(top_bar, text="Letztes Update: --:--:--", fg="#ecf0f1", bg="#2c3e50")
        self.status_label.pack(side=tk.RIGHT, padx=20)

        # Linke Sidebar (Filter)
        sidebar = tk.Frame(self.root, width=320, bg="#f0f0f0")
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        tk.Label(sidebar, text="SORTIERUNG", bg="#f0f0f0", font=("Arial", 9, "bold")).pack(pady=5)
        self.sort_combo = ttk.Combobox(sidebar, values=["ID", "Name", "Straße", "Ort"], state="readonly")
        self.sort_combo.current(0)
        self.sort_combo.pack(fill=tk.X, padx=5)
        self.sort_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_selection_list())

        tk.Label(sidebar, text="\nZEITRAUM", bg="#f0f0f0", font=("Arial", 9, "bold")).pack()
        times = ["Alles", "Jahr", "6 Monate", "3 Monate", "Monat", "Woche", "Tag", "12 Stunden", "6 Stunden", "3 Stunden", "1 Stunde", "30 Min"]
        self.time_filter = ttk.Combobox(sidebar, values=times, state="readonly")
        self.time_filter.current(6) # Standardmäßig auf "Tag"
        self.time_filter.pack(fill=tk.X, padx=5)

        # Auswahl-Liste
        list_container = tk.Frame(sidebar, bg="white", borderwidth=1, relief="sunken")
        list_container.pack(fill=tk.BOTH, expand=True, pady=10)
        self.canvas_list = tk.Canvas(list_container, bg="white")
        self.scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas_list.yview)
        self.scrollable_content = tk.Frame(self.canvas_list, bg="white")
        self.canvas_list.create_window((0, 0), window=self.scrollable_content, anchor="nw")
        self.canvas_list.configure(yscrollcommand=self.scrollbar.set)
        self.canvas_list.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Rechte Sidebar (Details)
        right_sidebar = tk.Frame(self.root, width=220, bg="#f0f0f0")
        right_sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        tk.Label(right_sidebar, text="ANZEIGE", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(pady=5)
        for k, txt in [('temp','Temperatur'), ('hum','Feuchte'), ('press','Druck'), ('gas','Gas')]:
            tk.Checkbutton(right_sidebar, text=txt, variable=self.show_vars[k], bg="#f0f0f0").pack(anchor="w")

        tk.Label(right_sidebar, text="\nINFO-DETAILS", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(pady=5)
        for k, txt in [('id','ID'), ('ort','Ort'), ('str','Str.'), ('nr','Nr.'), ('plz','PLZ')]:
            tk.Checkbutton(right_sidebar, text=txt, variable=self.det_vars[k], bg="#f0f0f0").pack(anchor="w")

        # Mitte: Plot
        self.fig = plt.figure(figsize=(10, 8))
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_plot.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    def run_live_update(self):
        """Der Herzschlag des Programms: Aktualisiert das Diagramm alle X Sekunden."""
        if self.auto_refresh.get():
            self.update_chart()
            now_str = datetime.now().strftime("%H:%M:%S")
            self.status_label.config(text=f"Letztes Update: {now_str}")
        
        # Sich selbst wieder aufrufen (Loop)
        self.root.after(self.refresh_interval, self.run_live_update)

    def load_data(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM messstation")
            self.users_info = cursor.fetchall()
            conn.close()
            self.refresh_selection_list()
        except Error: pass

    def refresh_selection_list(self):
        for widget in self.scrollable_content.winfo_children(): widget.destroy()
        # Sortier-Logik (einfach nach ID oder Name)
        s_crit = self.sort_combo.get()
        sorted_list = sorted(self.users_info, key=lambda x: x['mid' if s_crit=="ID" else 'nachname'])
        
        self.user_vars = {}
        for u in sorted_list:
            var = tk.BooleanVar(value=True)
            self.user_vars[u['mid']] = var
            tk.Checkbutton(self.scrollable_content, text=f"ID:{u['mid']} | {u['vorname']} {u['nachname']}", variable=var, bg="white").pack(anchor="w")
        
        self.canvas_list.update_idletasks()
        self.canvas_list.configure(scrollregion=self.canvas_list.bbox("all"))

    def update_chart(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            self.fig.clear()

            # Zeitfenster
            t_sel = self.time_filter.get()
            start_time = None
            if t_sel != "Alles":
                time_map = {"Jahr":365, "6 Monate":180, "3 Monate":90, "Monat":30, "Woche":7, "Tag":1, "12 Stunden":0.5, "6 Stunden":0.25, "3 Stunden":0.125, "1 Stunde":1/24, "30 Min":1/48}
                start_time = datetime.now() - timedelta(days=time_map[t_sel])

            active_plots = [(k, c, l) for k, c, l in [('temp','temperatur','Temperatur'), ('hum','feuchte','Feuchte'), ('press','druck','Druck'), ('gas','qualitaet','Gas')] if self.show_vars[k].get()]
            target_mids = [mid for mid, var in self.user_vars.items() if var.get()]

            if not target_mids or not active_plots:
                self.canvas_plot.draw()
                conn.close()
                return

            for idx, (key, col, title) in enumerate(active_plots):
                ax = self.fig.add_subplot(len(active_plots), 1, idx + 1)
                if start_time: ax.set_xlim(start_time, datetime.now())
                
                for mid in target_mids:
                    query = f"SELECT timestamp, {col} FROM messungen WHERE mid = %s" + (" AND timestamp >= %s" if start_time else "") + " ORDER BY timestamp ASC"
                    cursor.execute(query, [mid, start_time] if start_time else [mid])
                    res = cursor.fetchall()
                    if res:
                        u = next(u for u in self.users_info if u['mid'] == mid)
                        # Label bauen
                        lbl = f"{u['vorname']} {u['nachname']}"
                        if self.det_vars['id'].get(): lbl += f" (ID{u['mid']})"
                        if self.det_vars['ort'].get(): lbl += f" ({u['ort']})"
                        
                        ax.plot([r['timestamp'] for r in res], [r[col] for r in res], label=lbl, marker='o', markersize=2)

                ax.set_title(title, loc='left', fontsize=9, fontweight='bold')
                ax.legend(fontsize='6', loc='upper left', bbox_to_anchor=(1, 1))
                ax.grid(True, alpha=0.2)

            self.fig.tight_layout()
            self.canvas_plot.draw()
            conn.close()
        except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = WetterAnalyseLive(root)
    root.mainloop()