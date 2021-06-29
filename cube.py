from nicdaq import HallDAQ
from calibration import get_xyz_calib_values, calib_data, orthogonalize
import zeisscmm
import numpy as np
from time import sleep
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import os

class Cube:
    def __init__(self, cube_alignment_filename: str,\
                 calibration_array: np.ndarray,\
                 probe_offset_filename: str):
        self.daq = HallDAQ(1, 20000, start_trigger=True, acquisition='finite')
        self.daq.power_on()
        self.cmm = zeisscmm.CMM()
        self.calib_coeffs = calibration_array
        self.rotation, self.translation = self.load_cube_alignment(cube_alignment_filename)
        self.probe_offset = np.genfromtxt(probe_offset_filename)
    
    def cube2mcs(self, coordinate):
        return (coordinate - self.translation)@self.rotation

    def mcs2cube(self, coordinate):
        return coordinate@np.linalg.inv(self.rotation) + self.translation

    def load_cube_alignment(self, filename: str):
        diff = np.genfromtxt(filename, delimiter=' ')
        rotation = diff[:-3].reshape((3,3))
        translation = diff[-3:]
        return (rotation, translation)
    
    def measure_cube_center(self):
        pass

    def shutdown(self):
        self.cmm.close()
        self.daq.power_off()
        self.daq.close_tasks()
    
class CubeWindow(tk.Toplevel):
    def __init__(self, parent):
        self.cube = None
        self.calib_array = np.load('zg_calib_coeffs.npy')
        self.images = self.__create_image_dict__()
        super().__init__(parent)
        self.title('Sensor Orthogonalization')
        self.frm_cube_window = tk.Frame(self)
        self.frm_cube_window.pack()
        self.create_widgets()
    
    def __create_image_dict__(self):
        image_dict = {}
        keys = ['x1', 'x2', 'x3', 'x4', 'y1', 'y2', 'y3', 'y4', 'z1', 'z2', 'z3', 'z4']
        images = ['images/cube_x1.jpg', 'images/cube_x2.jpg', 'images/cube_x3.jpg', 'images/cube_x4.jpg',
                  'images/cube_y1.jpg', 'images/cube_y2.jpg', 'images/cube_y3.jpg', 'images/cube_y4.jpg',
                  'images/cube_z1.jpg', 'images/cube_z2.jpg', 'images/cube_z3.jpg', 'images/cube_z4.jpg']
        for i in range(12):
            image_dict[keys[i]] = ImageTk.PhotoImage(Image.open(images[i]))
        return image_dict
    
    def create_widgets(self):
        self.btn_load_alignment = ttk.Button(self.frm_cube_window,
                                             text='Load Cube Alignment',
                                             command=self.load_alignment)
        self.btn_measure_cube_center = ttk.Button(self.frm_cube_window,
                                                  text='Measure Cube Center',
                                                  command=self.measure)
        self.btn_close = ttk.Button(self.frm_cube_window, text='Close', command=self.destroy)
        self.lbl_img_desc = tk.Label(self.frm_cube_window, text='Load alignment, calibration, and offsets')
        self.lbl_img = tk.Label(self.frm_cube_window)
        # Place widgets within grid
        self.btn_load_alignment.grid(column=0, row=0, padx=5, pady=5)
        self.btn_measure_cube_center.grid(column=0, row=3, padx=5, pady=5)
        self.btn_close.grid(column=0, row=4, padx=5, pady=5)
        self.lbl_img_desc.grid(column=1, row=0, padx=5, pady=5, sticky='w')
        self.lbl_img.grid(column=1, row=1, rowspan=5, padx=5, pady=5)
    
    def load_alignment(self):
        self.cube_filename = filedialog.askopenfilename(filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')])
        self.lbl_img.configure(image=self.images['x1'])
        self.lbl_img_desc.configure(text='Manually guide hallprobe into cube.')
        self.focus()
    
    def measure(self):
        if self.cube is None:
            self.cube = Cube(self.cube_filename, self.calib_array, 'fsv_offset.txt')
    
    def select_calib_folder(self):
        self.calib_folder = filedialog.askdirectory()
        self.calib_array = get_xyz_calib_values(self.calib_folder)
        self.focus()
        

if __name__ == '__main__':
    test = Cube(r'D:\CMM Programs\Cube Calibration\cube_alignment.txt', r'C:\Users\dyeagly\Documents\hall_probe\hall_probe\Hall probe 444-20', r'D:\CMM Programs\FSV Calibration\hallsensor_offset_mcs.txt')
    
    test.daq.start_hallsensor_task()
    sleep(1)
    test.daq.pulse()
    data = test.daq.read_hallsensor()[7500:15000]
    cal_data = calib_data(test.calib_coeffs, data)
    cal_mean = np.mean(cal_data, axis=0)
    data_mean = np.mean(data, axis=0)
    # np.savetxt('cube_data_raw_05.txt', data, fmt='%.6f', delimiter=' ')
    with open('cube_data_2021-06-17.txt', 'a') as file:
        file.write(f'{cal_mean[0]} {cal_mean[1]} {cal_mean[2]}\n')
    # with open('zg.txt', 'a') as file:
    #     file.write(f'{data_mean[0]} {data_mean[1]} {data_mean[2]}\n')
    # print(data_mean)
    # print(data_mean)
    print(cal_mean)
    print(np.linalg.norm(cal_mean))
    # print(np.std(cal_data, axis=0, ddof=1))
    test.shutdown()