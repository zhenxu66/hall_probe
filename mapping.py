import tkinter as tk
from tkinter import ttk

class MapFrames(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.density_list = ['0.1', '0.25', '0.5', '1.0', '2.0', 'full res']
        self.frm_scan_point = tk.Frame(self)
        self.frm_scan_line = tk.Frame(self)
        self.frm_scan_area_volume = tk.Frame(self)
        self.scan_point_widgets()
        self.scan_line_widgets()
        self.scan_area_volume_widgets()
    
    def scan_point_widgets(self):
        self.lbl_scan_point = tk.Label(self.frm_scan_point, text='Scan Point')
        self.lbl_x = tk.Label(self.frm_scan_point, text='X')
        self.lbl_y = tk.Label(self.frm_scan_point, text='Y')
        self.lbl_z = tk.Label(self.frm_scan_point, text='Z')
        self.ent_x = ttk.Entry(self.frm_scan_point, width=9)
        self.ent_y = ttk.Entry(self.frm_scan_point, width=9)
        self.ent_z = ttk.Entry(self.frm_scan_point, width=9)
        self.btn_measure_point = ttk.Button(self.frm_scan_point, text='Measure', command=self.measure_point)
        # Place widgets within grid
        self.lbl_scan_point.grid(column=0, row=0, columnspan=6)
        self.lbl_x.grid(column=0, row=1, sticky='e')
        self.lbl_y.grid(column=2, row=1, sticky='e')
        self.lbl_z.grid(column=4, row=1, sticky='e')
        self.ent_x.grid(column=1, row=1, sticky='w', padx=(5,10))
        self.ent_y.grid(column=3, row=1, sticky='w', padx=(5,10))
        self.ent_z.grid(column=5, row=1, sticky='w', padx=(5,10))
        self.btn_measure_point.grid(column=0, row=2, columnspan=6, padx=5, pady=5)
    
    def measure_point(self):
        pass

    def scan_line_widgets(self):
        self.lbl_start_point = tk.Label(self.frm_scan_line, text='Start Point')
        self.lbl_sp_x = tk.Label(self.frm_scan_line, text='X')
        self.lbl_sp_y = tk.Label(self.frm_scan_line, text='Y')
        self.lbl_sp_z = tk.Label(self.frm_scan_line, text='Z')
        self.lbl_end_point = tk.Label(self.frm_scan_line, text='End Point')
        self.lbl_ep_x = tk.Label(self.frm_scan_line, text='X')
        self.lbl_ep_y = tk.Label(self.frm_scan_line, text='Y')
        self.lbl_ep_z = tk.Label(self.frm_scan_line, text='Z')
        self.lbl_point_density = tk.Label(self.frm_scan_line, text='Point Density')
        self.ent_sp_x = ttk.Entry(self.frm_scan_line, width=9)
        self.ent_sp_y = ttk.Entry(self.frm_scan_line, width=9)
        self.ent_sp_z = ttk.Entry(self.frm_scan_line, width=9)
        self.ent_ep_x = ttk.Entry(self.frm_scan_line, width=9)
        self.ent_ep_y = ttk.Entry(self.frm_scan_line, width=9)
        self.ent_ep_z = ttk.Entry(self.frm_scan_line, width=9)
        self.cbox_point_density = ttk.Combobox(self.frm_scan_line, values=self.density_list, width=9)
        self.btn_measure_line = ttk.Button(self.frm_scan_line, text='Measure')
        # Place widgets within grid
        self.lbl_start_point.grid(column=0, row=0, columnspan=6)
        self.lbl_sp_x.grid(column=0, row=1, sticky='e')
        self.lbl_sp_y.grid(column=2, row=1, sticky='e')
        self.lbl_sp_z.grid(column=4, row=1, sticky='e')
        self.ent_sp_x.grid(column=1, row=1, sticky='w', padx=(5,10))
        self.ent_sp_y.grid(column=3, row=1, sticky='w', padx=(5,10))
        self.ent_sp_z.grid(column=5, row=1, sticky='w', padx=(5,10))
        self.lbl_end_point.grid(column=0, row=6, columnspan=6)
        self.lbl_ep_x.grid(column=0, row=7, sticky='e')
        self.lbl_ep_y.grid(column=2, row=7, sticky='e')
        self.lbl_ep_z.grid(column=4, row=7, sticky='e')
        self.ent_ep_x.grid(column=1, row=7, sticky='w', padx=(5,10))
        self.ent_ep_y.grid(column=3, row=7, sticky='w', padx=(5,10))
        self.ent_ep_z.grid(column=5, row=7, sticky='w', padx=(5,10))
        self.lbl_point_density.grid(column=0, row=8, columnspan=2, sticky='e')
        self.cbox_point_density.grid(column=2, row=8, columnspan=2, sticky='w', padx=5, pady=5)
        self.cbox_point_density.set('full res')
        self.btn_measure_line.grid(column=4, row=8, columnspan=2)
    
    def scan_area_volume_widgets(self):
        self.lbl_sav_sp = tk.Label(self.frm_scan_area_volume, text='Start Point')
        self.lbl_sav_sp_x = tk.Label(self.frm_scan_area_volume, text='X')
        self.lbl_sav_sp_y = tk.Label(self.frm_scan_area_volume, text='Y')
        self.lbl_sav_sp_z = tk.Label(self.frm_scan_area_volume, text='Z')
        self.lbl_sav_distance = tk.Label(self.frm_scan_area_volume, text='Scan Distance')
        self.lbl_sav_sd_x = tk.Label(self.frm_scan_area_volume, text='X')
        self.lbl_sav_sd_y = tk.Label(self.frm_scan_area_volume, text='Y')
        self.lbl_sav_sd_z = tk.Label(self.frm_scan_area_volume, text='Z')
        self.ent_sav_sp_x = ttk.Entry(self.frm_scan_area_volume, width=9)
        self.ent_sav_sp_y = ttk.Entry(self.frm_scan_area_volume, width=9)
        self.ent_sav_sp_z = ttk.Entry(self.frm_scan_area_volume, width=9)
        self.ent_sav_sd_x = ttk.Entry(self.frm_scan_area_volume, width=9)
        self.ent_sav_sd_y = ttk.Entry(self.frm_scan_area_volume, width=9)
        self.ent_sav_sd_z = ttk.Entry(self.frm_scan_area_volume, width=9)
        self.lbl_sav_pd = tk.Label(self.frm_scan_area_volume, text='Point Density')
        self.cbox_sav_pd = ttk.Combobox(self.frm_scan_area_volume, values=self.density_list, width=9)
        self.lbl_sav_scan_plane = tk.Label(self.frm_scan_area_volume, text='Scan Plane')
        self.cbox_sav_scan_plane = ttk.Combobox(self.frm_scan_area_volume, values=['xy', 'yz', 'zx'], state='readonly', width=9)
        self.btn_sav_measure = ttk.Button(self.frm_scan_area_volume, text='Measure')
        self.btn_sav_stop = ttk.Button(self.frm_scan_area_volume, text='Stop')
        # Place widgets within grid
        self.lbl_sav_sp.grid(column=0, row=0, columnspan=6)
        self.lbl_sav_sp_x.grid(column=0, row=1, sticky='e')
        self.lbl_sav_sp_y.grid(column=2, row=1, sticky='e')
        self.lbl_sav_sp_z.grid(column=4, row=1, sticky='e')
        self.ent_sav_sp_x.grid(column=1, row=1, padx=(5,10), sticky='w')
        self.ent_sav_sp_y.grid(column=3, row=1, padx=(5,10), sticky='w')
        self.ent_sav_sp_z.grid(column=5, row=1, padx=(5,10), sticky='w')
        self.lbl_sav_distance.grid(column=0, row=2, columnspan=6)
        self.lbl_sav_sd_x.grid(column=0, row=3, sticky='e')
        self.lbl_sav_sd_y.grid(column=2, row=3, sticky='e')
        self.lbl_sav_sd_z.grid(column=4, row=3, sticky='e')
        self.ent_sav_sd_x.grid(column=1, row=3, padx=(5,10), sticky='w')
        self.ent_sav_sd_y.grid(column=3, row=3, padx=(5,10), sticky='w')
        self.ent_sav_sd_z.grid(column=5, row=3, padx=(5,10), sticky='w')
        self.lbl_sav_pd.grid(column=0, row=4, columnspan=2, pady=(10,5), sticky='e')
        self.cbox_sav_pd.grid(column=2, row=4, columnspan=2, padx=5, pady=(10,5), sticky='w')
        self.cbox_sav_pd.set('0.5')
        self.lbl_sav_scan_plane.grid(column=0, row=5, columnspan=2, pady=(0,5), sticky='e')
        self.cbox_sav_scan_plane.grid(column=2, row=5, columnspan=2, padx=5, pady=(0,5), sticky='w')
        self.cbox_sav_scan_plane.set('xy')
        self.btn_sav_measure.grid(column=4, row=4, columnspan=2, padx=5, pady=(5,0), sticky='ew')
        self.btn_sav_stop.grid(column=4, row=5, columnspan=2, padx=5, pady=(0,5), sticky='ew')