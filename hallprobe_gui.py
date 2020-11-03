import tkinter as tk
from tkinter import ttk
from zeisscmm import CMM
from nicdaq import DAQ, Constants
import numpy as np
import multiprocessing as mp
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from tooltip import ToolTip

class HallProbeApp(tk.Frame):
    def __init__(self, master):
        self.master = master
        super().__init__(master)
        self.master.title('Hall Probe Integration App')
        self.master.iconbitmap('magnet.ico')
        self.master.geometry('1200x900')
        self.create_frames()
    
    def create_frames(self):
        self.controls = ControlsFrame(self)
        self.visuals = VisualsFrame(self)
        self.pack()
        self.controls.grid(column=0, row=0, padx=5, pady=5)
        self.visuals.grid(column=1, row=0, padx=5, pady=5)
    
    def update_graph_labels(self):
        self.visuals.temp_plot.temp_frame_parent.temp_plot.update_labels()


class ControlsFrame(tk.Frame):
    def __init__(self, parent):
        self.parent_controls_frame = parent
        super().__init__(parent)
        self.create_frames()
    
    def create_frames(self):
        self.magnet_info_frame = MagnetInformation(self)
        self.zeiss_frame = ZeissControls(self)
        self.calibration_frame = CalibrationTools(self)
        self.daq_frame = DaqControls(self)
        self.program_frame = ProgramControls(self)

        self.magnet_info_frame.grid(column=0, row=0)
        self.zeiss_frame.grid(column=0, row=1)
        self.calibration_frame.grid(column=0, row=2)
        self.daq_frame.grid(column=0, row=3)
        self.program_frame.grid(column=0, row=4)

class VisualsFrame(tk.Frame):
    def __init__(self, parent):
        self.visuals_frame_parent = parent
        super().__init__(parent)
        self.create_frames()

    def create_frames(self):
        self.field_plot = FieldFrame(self)
        self.temp_plot = TemperatureFrame(self)
        self.field_plot.grid(column=0, row=0)
        self.temp_plot.grid(column=0, row=1)

class MagnetInformation(ttk.LabelFrame):
    def __init__(self, parent, title='Magnet Information'):
        self.magnet_info_parent = parent
        super().__init__(parent, text=title, labelanchor='n')
        self.create_widgets()

    def create_widgets(self):
        self.lbl_partnum = tk.Label(self, text='Part Number')
        self.ent_partnum = ttk.Entry(self)
        self.lbl_serial = tk.Label(self, text='Serial Number')
        self.ent_serial = ttk.Entry(self)

        self.lbl_partnum.grid(column=0, row=0, sticky='w', padx=5)
        self.ent_partnum.grid(column=0, row=1, sticky='w', padx=5)
        self.lbl_serial.grid(column=1, row=0, sticky='w', padx=5)
        self.ent_serial.grid(column=1, row=1, sticky='w', padx=5)

class ZeissControls(ttk.LabelFrame):
    def __init__(self, parent, title='Zeiss CMM Controls'):
        self.zeiss_controls_parent = parent
        super().__init__(parent, text=title, labelanchor='n')
        self.grid(pady=20)
        self.create_widgets()
    
    def create_widgets(self):
        self.btn_emerg_stop = ttk.Button(self, text='Emergency Stop', command=self.emergency_stop)
        self.lbl_conn_status = tk.Label(self, text='*Connection Status*')
        self.lbl_conn_status.config(relief='sunken')
        self.lbl_start_pt = tk.Label(self, text='Start Point')
        self.lbl_start_pt_x = tk.Label(self, text='X')
        self.ent_start_pt_x = ttk.Entry(self, width=9)
        self.lbl_start_pt_y = tk.Label(self, text='Y')
        self.ent_start_pt_y = ttk.Entry(self, width=9)
        self.lbl_start_pt_z = tk.Label(self, text='Z')
        self.ent_start_pt_z = ttk.Entry(self, width=9)
        self.lbl_scan_length = tk.Label(self, text='Scan Length')
        self.lbl_scan_length_x = tk.Label(self, text='X')
        self.ent_scan_length_x = ttk.Entry(self, width=9)
        self.lbl_scan_length_y = tk.Label(self, text='Y')
        self.ent_scan_length_y = ttk.Entry(self, width=9)
        self.lbl_meas_interval = tk.Label(self, text='Measurement Interval')
        self.lbl_meas_interval.tooltip = ToolTip(self.lbl_meas_interval, 'Default value 0.5mm')
        self.ent_meas_interval = ttk.Entry(self, width=5, justify='right')
        self.lbl_meas_interval_mm = tk.Label(self, text='mm')
        self.ent_meas_interval.insert(0, '0.5')
        self.lbl_scan_speed = tk.Label(self, text='Scan Speed')
        self.lbl_scan_speed.tooltip = ToolTip(self.lbl_scan_speed, 'Default value 5 mm/s')
        self.ent_scan_speed = ttk.Entry(self, width=5, justify='right')
        self.ent_scan_speed.insert(0, '5')
        self.lbl_scan_speed_mms = tk.Label(self, text='mm/s')

        self.btn_emerg_stop.grid(column=0, row=0, columnspan=6)
        self.lbl_conn_status.grid(column=0, row=1, columnspan=6, padx=5, pady=5, sticky='ew')
        self.lbl_start_pt.grid(column=0, row=2, columnspan=6)
        self.lbl_start_pt_x.grid(column=0, row=3)
        self.ent_start_pt_x.grid(column=1, row=3)
        self.lbl_start_pt_y.grid(column=2, row=3)
        self.ent_start_pt_y.grid(column=3, row=3)
        self.lbl_start_pt_z.grid(column=4, row=3)
        self.ent_start_pt_z.grid(column=5, row=3)
        self.lbl_scan_length.grid(column=0, row=4, columnspan=6)
        self.lbl_scan_length_x.grid(column=0, row=5)
        self.ent_scan_length_x.grid(column=1, row=5)
        self.lbl_scan_length_y.grid(column=2, row=5)
        self.ent_scan_length_y.grid(column=3, row=5)
        self.lbl_meas_interval.grid(column=0, row=6, columnspan=4, sticky='w')
        self.ent_meas_interval.grid(column=1, row=7, sticky='e')
        self.lbl_meas_interval_mm.grid(column=2, row=7, columnspan=2, sticky='w')
        self.lbl_scan_speed.grid(column=3, row=6, columnspan=4, sticky='e', padx=30)
        self.ent_scan_speed.grid(column=4, row=7, sticky='e')
        self.lbl_scan_speed_mms.grid(column=5, row=7, sticky='w')

    def emergency_stop(self):
        pass
    
    def connect_cmm(self):
        try:
            self.zeiss = CMM(ip='192.4.1.200', port=4712)
            self.lbl_conn_status['text'] = 'Connection Established'
        except ConnectionRefusedError:
            self.lbl_conn_status['text'] = 'Connection Refused'
        except TimeoutError:
            self.lbl_conn_status['text'] = 'Connection Timed Out'

    def disconnect_cmm(self):
        try:
            self.zeiss.close()
            self.lbl_conn_status['text'] = 'Disconnected'
        except AttributeError:
            self.lbl_conn_status['text'] = 'Already Disconnected'
    
class DaqControls(ttk.LabelFrame):
    def __init__(self, parent, title='DAQ Controls'):
        self.daq_controls_parent = parent
        super().__init__(parent, text=title, labelanchor='n')
        self.create_widgets()

    def create_widgets(self):
        self.therm_frame = ThermocoupleControls(self)
        self.volt_frame = VoltageControls(self)
        self.sampling_frame = SamplingControls(self)
        self.therm_frame.grid(column=0, row=0, rowspan=2, padx=10, pady=10, sticky='n')
        self.volt_frame.grid(column=1, row=0, padx=10, pady=10, sticky='n')
        self.sampling_frame.grid(column=1, row=1, rowspan=2, padx=10, pady=10, sticky='n')

class ThermocoupleControls(ttk.LabelFrame):
    def __init__(self, parent, title='Thermocouple Controls'):
        self.thermocouple_controls_parent = parent
        super().__init__(parent, text=title, labelanchor='n')
        # self.therm_channels = []
        self.therm_chan_var = []
        self.radio_value_temp_units = tk.StringVar()
        self.therm_types = Constants.therm_types()
        self.temp_units = Constants.temp_units()
        self.create_frame()

    def create_frame(self):
        for i in range(8): # Create Thermocouple channel check buttons
            var = tk.IntVar(value=0)
            chk_therm_channel = ttk.Checkbutton(self, text=f'Channel {i}', variable=var)
            chk_therm_channel.grid(column=0, row=1+i, sticky='w')
            # self.therm_channels.append(chk_therm_channel)
            self.therm_chan_var.append(var)
        self.therm_chan_var[0].set(1)
        self.therm_chan_var[1].set(1)

        self.therm_separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.therm_separator.grid(column=0, row=9, sticky='ew')
        self.lbl_therm_type = tk.Label(self, text='Thermocouple Type')
        self.lbl_therm_type.grid(column=0, row=10)
        self.cbox_therm_type = ttk.Combobox(self, values=[i for i in self.therm_types.keys()])
        self.cbox_therm_type['state'] = 'readonly'
        self.cbox_therm_type.grid(column=0, row=11)
        self.cbox_therm_type.current(3)
        self.lbl_temp_units = tk.Label(self, text='Units')
        self.lbl_temp_units.grid(column=0, row=12)
        self.radio_frame = tk.Frame(self)
        self.radio_frame.grid(column=0, row=13, columnspan=3)
        self.radio_btn_c = ttk.Radiobutton(self.radio_frame, text='C', variable=self.radio_value_temp_units, value='C',
                                           command=self.thermocouple_controls_parent.daq_controls_parent.parent_controls_frame.update_graph_labels)
        self.radio_btn_f = ttk.Radiobutton(self.radio_frame, text='F', variable=self.radio_value_temp_units, value='F',
                                           command=self.thermocouple_controls_parent.daq_controls_parent.parent_controls_frame.update_graph_labels)
        self.radio_btn_k = ttk.Radiobutton(self.radio_frame, text='K', variable=self.radio_value_temp_units, value='K',
                                           command=self.thermocouple_controls_parent.daq_controls_parent.parent_controls_frame.update_graph_labels)
        self.radio_value_temp_units.set('C')
        self.radio_btn_c.grid(column=0, row=0)
        self.radio_btn_f.grid(column=1, row=0, padx=10)
        self.radio_btn_k.grid(column=2, row=0)

class VoltageControls(ttk.LabelFrame):
    def __init__(self, parent, title='Voltage Controls'):
        self.voltage_controls_parent = parent
        super().__init__(parent, text=title, labelanchor='n')
        # self.volt_channels = []
        self.volt_chan_var = []
        self.create_frame()
        # print('volt channels', [i.get() for i in self.volt_chan_var])

    def create_frame(self):
        for j in range(4): # Create Voltage channel check buttons
            var = tk.IntVar(value=0)
            chk_volt_channel = ttk.Checkbutton(self, text=f'Channel {j}', variable=var)
            chk_volt_channel.grid(column=0, row=1+j, columnspan=2, sticky='w', padx=10)
            # self.volt_channels.append(chk_volt_channel)
            self.volt_chan_var.append(var)
        for i in range(3):
            self.volt_chan_var[i].set(1)
        self.lbl_volt_min = tk.Label(self, text='V Min')
        self.lbl_volt_min.tooltip = ToolTip(self.lbl_volt_min, 'Default value -5.0 V')
        self.lbl_volt_max = tk.Label(self, text='V Max')
        self.lbl_volt_max.tooltip = ToolTip(self.lbl_volt_max, 'Default value 5.0 V')
        self.ent_volt_min = ttk.Entry(self, width=5)
        self.ent_volt_max = ttk.Entry(self, width=5)
        self.ent_volt_min.insert(0, '-5.0')
        self.ent_volt_max.insert(0, '5.0')
        self.lbl_volt_min.grid(column=0, row = 5)
        self.lbl_volt_max.grid(column=1, row = 5)
        self.ent_volt_min.grid(column=0, row=6)
        self.ent_volt_max.grid(column=1, row=6)
        self.lbl_volt_units = tk.Label(self, text='Units')
        self.lbl_volt_units.grid(column=0, row=7, columnspan=2)
        self.cbox_volt_units = ttk.Combobox(self, values=['V', 'mT'])
        self.cbox_volt_units['state'] = 'readonly'
        self.cbox_volt_units.current(0)
        # print('V units', self.cbox_volt_units.get())
        self.cbox_volt_units.grid(column=0, row=8, columnspan=2)
        
class SamplingControls(ttk.LabelFrame):
    def __init__(self, parent):
        self.sampling_controls_parent = parent
        super().__init__(parent, text='Sampling Parameters', labelanchor='n')
        self.create_widgets()

    def create_widgets(self):
        self.lbl_sampling_rate = tk.Label(self, text='Sampling Rate')
        self.lbl_sampling_rate.tooltip = ToolTip(self.lbl_sampling_rate, 'Default value 1000')
        self.lbl_num_samples = tk.Label(self, text='Samples per Channel')
        self.lbl_num_samples.tooltip = ToolTip(self.lbl_num_samples, 'Default value 100')
        self.ent_sampling_rate = ttk.Entry(self)
        self.ent_num_samples = ttk.Entry(self)
        self.ent_sampling_rate.insert(0, '1000')
        self.ent_num_samples.insert(0, '100')
        self.lbl_sampling_rate.grid(column=0, row=0, padx=5, pady=5, sticky='w')
        self.ent_sampling_rate.grid(column=0, row=1, padx=5, sticky='w')
        self.lbl_num_samples.grid(column=0, row=2, padx=5, pady=5, sticky='w')
        self.ent_num_samples.grid(column=0, row=3, padx=5, pady=(0,5), sticky='w')

class PlotField(tk.Frame):
    def __init__(self, parent):
        self.plotfield_parent = parent
        super().__init__(parent)
        self.create_plot()

    def create_plot(self):
        x, y, z = np.meshgrid(np.arange(-0.8, 1, 0.2),
                              np.arange(-0.8, 1, 0.2),
                              np.arange(-0.8, 1, 0.8))
        u = np.sin(np.pi * x) * np.cos(np.pi * y) * np.cos(np.pi * z)
        v = -np.cos(np.pi * x) * np.sin(np.pi * y) * np.cos(np.pi * z)
        w = (np.sqrt(2.0 / 3.0) * np.cos(np.pi * x) * np.cos(np.pi * y) * np.sin(np.pi * z))
        self.fig = Figure(figsize=(8,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plotfield_parent)
        self.canvas.draw()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.ax.set_title('Vector Field Map')
        self.ax.set_xlabel('x axis [mm]')
        self.ax.set_ylabel('y axis [mm]')
        self.ax.set_zlabel('z axis [mm]')
        self.ax.quiver(x, y, z, u, v, w, length=0.15, normalize=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plotfield_parent)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP,
                                         fill=tk.BOTH, expand=1)

class PlotTemperature(tk.Frame):
    def __init__(self, parent):
        self.plot_temp_parent = parent
        super().__init__(parent)
        self.create_widgets()
    
    def create_widgets(self):
        '''
        change to set graph labels at start of measurement
        '''
        self.fig = Figure(figsize=(8,4))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('Magnet Temperature')
        self.ax.set_xlabel('Time [min]')
        self.ax.set_ylabel(f'Temperature [{self.plot_temp_parent.temp_frame_parent.visuals_frame_parent.controls.daq_frame.therm_frame.radio_value_temp_units.get()}]')
        self.ax.grid()
        self.graph = FigureCanvasTkAgg(self.fig, self.plot_temp_parent)
        self.graph.draw()
        # print([i.get() for i in self.plot_temp_parent.temp_frame_parent.visuals_frame_parent.controls.daq_frame.therm_frame.therm_chan_var])
        self.ax.plot([1,2,3,4,5,6,7,8], [19.8, 19.9, 20, 20, 20.5, 20.7, 20.8, 21], label='channel 0')
        self.ax.legend()
        self.toolbar = NavigationToolbar2Tk(self.graph, self.plot_temp_parent)
        self.toolbar.update()
        self.graph.get_tk_widget().pack()
    def update_ylabel(self):
        self.ax.set_ylabel(f'Temperature [{self.plot_temp_parent.temp_frame_parent.visuals_frame_parent.controls.daq_frame.therm_frame.radio_value_temp_units.get()}]')

class FieldFrame(tk.Frame):
    def __init__(self, parent):
        self.field_frame_parent = parent
        super().__init__(parent)
        self.field_plot = PlotField(self)

class TemperatureFrame(tk.Frame):
    def __init__(self, parent):
        self.temp_frame_parent = parent
        super().__init__(parent)
        self.temp_plot = PlotTemperature(self)
    
    def update_labels(self):
        self.temp_plot.update_ylabel()

class CalibrationTools(ttk.LabelFrame):
    def __init__(self, parent):
        self.calib_tools_parent = parent
        super().__init__(parent, text='Calibration Tools', labelanchor='n')
        self.create_widgets()

    def create_widgets(self):
        self.lbl_placeholder = tk.Label(self, text='Placeholder Label')
        self.lbl_placeholder.grid(column=0, row=0)

class ProgramControls(ttk.LabelFrame):
    def __init__(self, parent, title='Program Controls'):
        self.program_controls_parent = parent
        super().__init__(parent, text=title, labelanchor='n')
        self.create_widgets()

    def create_widgets(self):
        self.btn_load_alignment = ttk.Button(self, text='Load Alignment', command=self.load_alignment)
        self.btn_start_meas = ttk.Button(self, text='Start Measurement', command=self.start_measurement)
        self.btn_stop_meas = ttk.Button(self, text='Stop Measurement', command=self.stop_measurement, state='disabled')
        self.btn_load_meas = ttk.Button(self, text='Load Measurement', command=self.load_measurement)
        self.btn_save_meas = ttk.Button(self, text='Save Measurement', command=self.save_measurement)
        self.lbl_controls_status = tk.Label(self, text='*Program Controls Status*')
        self.lbl_controls_status.config(relief='sunken')
        self.btn_load_alignment.grid(column=0, row=0, padx=5, pady=5, sticky='e')
        self.btn_start_meas.grid(column=1, row=0, padx=5, pady=5, sticky='w')
        self.btn_stop_meas.grid(column=2, row=0, padx=5, pady=5, sticky='w')
        self.btn_load_meas.grid(column=0, row=1, padx=5, pady=5, sticky='e')
        self.btn_save_meas.grid(column=1, row=1, padx=5, pady=5, sticky='w')
        self.lbl_controls_status.grid(column=0, row=2, columnspan=3, padx=5, pady=5, sticky='ew')
    
    def load_alignment(self):
        self.alignment_file = tk.filedialog.askopenfilename(filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')])
        if self.alignment_file != '':
            self.lbl_controls_status.configure(text=f'Loaded alignment file\n{self.alignment_file}')

    def start_measurement(self):
        print('Thermocouple Channels:', [i.get() for i in self.program_controls_parent.daq_frame.therm_frame.therm_chan_var])
        print('Thermocouple Type:', self.program_controls_parent.daq_frame.therm_frame.cbox_therm_type.get())
        print('Temperature Units:', self.program_controls_parent.daq_frame.therm_frame.radio_value_temp_units.get())
        print('Voltage Channels:', [i.get() for i in self.program_controls_parent.daq_frame.volt_frame.volt_chan_var])
        print(f'V min: {self.program_controls_parent.daq_frame.volt_frame.ent_volt_min.get()}, \
              V max: {self.program_controls_parent.daq_frame.volt_frame.ent_volt_max.get()}')
        print('Voltage Units:', self.program_controls_parent.daq_frame.volt_frame.cbox_volt_units.get())
        print('Sampling Rate:', self.program_controls_parent.daq_frame.sampling_frame.ent_sampling_rate.get())
        print('Samps per chan:', self.program_controls_parent.daq_frame.sampling_frame.ent_num_samples.get())
        self.btn_start_meas.configure(state='disabled')
        self.btn_load_alignment.configure(state='disabled')
        self.btn_load_meas.configure(state='disabled')
        self.btn_save_meas.configure(state='disabled')
        self.btn_stop_meas.configure(state='enabled')
        StartMeasurement(self)
    
    def stop_measurement(self):
        self.program_controls_parent.zeiss_frame.zeiss.send('D99\r\n'.encode('ascii'))
        self.program_controls_parent.zeiss_frame.disconnect_cmm()
        self.btn_start_meas.configure(state='enabled')
        self.btn_load_alignment.configure(state='enabled')
        self.btn_load_meas.configure(state='enabled')
        self.btn_stop_meas.configure(state='disabled')
        self.lbl_controls_status.configure(text='Measurement stopped')

    def save_measurement(self):
        self.save_file = tk.filedialog.asksaveasfilename(filetypes=[('Text Files', '*.txt'), ('CSV Files', '*.csv')])

    def load_measurement(self):
        pass

class StartMeasurement(tk.Frame):
    def __init__(self, parent):
        self.start_meas_parent = parent
        super().__init__(parent)
        self.mp_queue = mp.Queue()
        self.mp_queue_status = mp.Queue()
        self.start_meas_parent.lbl_controls_status.configure(text='Starting measurement...')
        self.connect_cmm()
        self.configure_daq()

    def connect_cmm(self):
        self.start_meas_parent.program_controls_parent.zeiss_frame.connect_cmm() 

    def configure_daq(self):
        self.temperature_task = DAQ('Thermocouples')
        self.hallsensor_task = DAQ('HallSensor')
        self.temperature_task.add_temperature_channels([i.get() for i in self.start_meas_parent.program_controls_parent.daq_frame.therm_frame.therm_chan_var], 
                                                       self.start_meas_parent.program_controls_parent.daq_frame.therm_frame.cbox_therm_type.get(), 
                                                       self.start_meas_parent.program_controls_parent.daq_frame.therm_frame.radio_value_temp_units)
        self.hallsensor_task.add_voltage_channels([i.get() for i in self.start_meas_parent.program_controls_parent.daq_frame.volt_frame.volt_chan_var],
                                       float(self.start_meas_parent.program_controls_parent.daq_frame.volt_frame.ent_volt_min.get()),
                                       float(self.start_meas_parent.program_controls_parent.daq_frame.volt_frame.ent_volt_max.get()),
                                       Constants.voltage_units()[self.start_meas_parent.program_controls_parent.daq_frame.volt_frame.cbox_volt_units.get()])
        self.hallsensor_task.set_sampling(int(self.start_meas_parent.program_controls_parent.daq_frame.sampling_frame.ent_sampling_rate.get()), \
                                          int(self.start_meas_parent.program_controls_parent.daq_frame.sampling_frame.ent_num_samples.get()))
    
    def create_file(self):
        self.datafile = open(f'{self.start_meas_parent.program_controls_parent.magnet_info_frame.ent_partnum.get()} - \
                             SN{self.start_meas_parent.program_controls_parent.magnet_info_frame.ent_serial.get()} - ' + \
                             datetime.now().strftime('%Y-%m-%d') + '.txt', 'w')
        
if __name__ == '__main__':
    app = HallProbeApp(tk.Tk())
    app.mainloop()