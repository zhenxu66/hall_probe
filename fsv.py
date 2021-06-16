from calibration import filter_data, get_xyz_calib_values, calib_data
from nicdaq import HallDAQ
from pathlib import Path
from time import sleep
import numpy as np
import zeisscmm
import os, re

class FSV:
    CERAMIC_THK = 1.0
    TRACE_THK = 0.06
    GLAZE_THK = 0.01
    TRACE_Z_OFFSET = 0.242

    def __init__(self, fsv_filename: str, probe_calibration_path: str):
        self.daq = HallDAQ(1, 10000, start_trigger=True, acquisition='finite')
        self.daq.power_on()
        self.cmm = zeisscmm.CMM()
        self.rotation, self.translation = self.import_fsv_alignment(fsv_filename)
        self.calibration_coeffs = get_xyz_calib_values(probe_calibration_path)
    
    def calc_offset(self, data_pos: np.ndarray, data_neg: np.ndarray, filter_cutoff=500, fit_lc=175):
        '''
        data_pos: (n, 2) array of sample data (ex. [x, bz])
        data_neg: (n, 2) array of sample data (current reversed)
        filter_cutoff: integer value used for smoothing raw sensor data,
            default set to 500
        fit_lc: extra samples to cut off for better linear fit
        returns: offset value for the respective CMM axis
        '''
        # Filter hallsensor data
        dpf = filter_data(data_pos[:, 1], filter_cutoff)
        dnf = filter_data(data_neg[:, 1], filter_cutoff)
        # Filter noisy data and cutoff beginning/end
        dpf_cutoff = dpf[filter_cutoff:-filter_cutoff]
        dnf_cutoff = dnf[filter_cutoff:-filter_cutoff]
        # Find min/max indices of filtered data and incorporate additional sample cutoff (fit_lc)
        dpf_min_index = np.where(dpf_cutoff == dpf_cutoff.min())[0][0] + filter_cutoff + fit_lc
        dpf_max_index = np.where(dpf_cutoff == dpf_cutoff.max())[0][0] + filter_cutoff - fit_lc
        dnf_min_index = np.where(dnf_cutoff == dnf_cutoff.min())[0][0] + filter_cutoff + fit_lc
        dnf_max_index = np.where(dnf_cutoff == dnf_cutoff.max())[0][0] + filter_cutoff - fit_lc
        # dpf_polyfit = np.polyfit(data_pos[:, 0][dpf_min_index:dpf_max_index], dpf[dpf_min_index:dpf_max_index], 3)
        # dnf_polyfit = np.polyfit(data_neg[:, 0][dnf_min_index:dnf_max_index], dnf[dnf_min_index:dnf_max_index], 3)
        # diff = dpf_polyfit - dnf_polyfit
        # offset = np.roots(diff)[1]
        dpf_polyfit = np.polyfit(data_pos[:, 0][dpf_min_index:dpf_max_index], dpf[dpf_min_index:dpf_max_index], 5)
        dnf_polyfit = np.polyfit(data_neg[:, 0][dnf_min_index:dnf_max_index], dnf[dnf_min_index:dnf_max_index], 5)
        diff = dpf_polyfit - dnf_polyfit
        offset = np.roots(diff)[2].real
        return offset

    def import_fsv_alignment(self, filename: str):
        diff = np.genfromtxt(filename, delimiter=' ')
        rotation = diff[:-3].reshape((3,3))
        translation = diff[-3:]
        return (rotation, translation)

    def fsv2mcs(self, coordinate: np.ndarray):
        return (coordinate - self.translation)@self.rotation

    def mcs2fsv(self, coordinate: np.ndarray):
        return coordinate@np.linalg.inv(self.rotation) + self.translation

    def perform_scan(self, start_pt, end_pt, speed=5, sensitivity=5, direction='positive'):
        '''
        direction can either be 'positive' or 'negative'
        sensitivity should either be 5 V/T or 100 V/T
        '''
        self.cmm.cnc_on()
        self.cmm.set_speed(speed)
        self.cmm.goto_position(start_pt)
        while np.linalg.norm(start_pt - self.cmm.get_position()) > 0.025:
            pass
        self.daq.fsv_on(v=direction)
        self.daq.start_hallsensor_task()
        sleep(1) # Allow time for task to start.
        self.cmm.goto_position(end_pt)
        sleep(1) # Allow time for CMM to finish accelerating
        self.daq.pulse()
        start_position = self.mcs2fsv(self.cmm.get_position())
        data = self.daq.read_hallsensor()
        end_position = self.mcs2fsv(self.cmm.get_position())
        self.daq.fsv_off()
        self.daq.stop_hallsensor_task()
        self.cmm.set_speed(70)
        self.cmm.cnc_off()
        cal_data = calib_data(self.calibration_coeffs, data, sensitivity=sensitivity)
        return (start_position, end_position, cal_data)

    def run_x_routine(self):
        half_length = np.array([20, 0, 0])
        current_pos_fsv = self.mcs2fsv(self.cmm.get_position())
        start_pos_mcs = self.fsv2mcs(current_pos_fsv - half_length)
        end_pos_mcs = self.fsv2mcs(current_pos_fsv + half_length)
        # Scan +
        start_p, end_p, data_p = self.perform_scan(start_pos_mcs, end_pos_mcs)
        x_p = np.linspace(start_p[0], end_p[0], data_p.shape[0])
        sleep(1)
        # Scan -
        start_n, end_n, data_n = self.perform_scan(end_pos_mcs, start_pos_mcs, direction='negative')
        x_n = np.linspace(start_n[0], end_n[0], data_n.shape[0])
        # Combine CMM and hallsensor data into one array
        combined_p = np.insert(data_p, 0, x_p, axis=1) # (x, Bx, By, Bz)
        combined_n = np.insert(data_n, 0, x_n, axis=1) # (x, Bx, By, Bz)
        data_pn_offset = self.calc_offset(combined_p[:, [0, 3]], combined_n[:, [0, 3]])
        self.x_offset_fsv = data_pn_offset
        return data_pn_offset

    def run_y_routine(self):
        half_length = np.array([0, 20, 0])
        current_pos_fsv = self.mcs2fsv(self.cmm.get_position())
        start_pos_mcs = self.fsv2mcs(current_pos_fsv - half_length)
        end_pos_mcs = self.fsv2mcs(current_pos_fsv + half_length)
        # Scan +
        start_p, end_p, data_p = self.perform_scan(start_pos_mcs, end_pos_mcs)
        y_p = np.linspace(start_p[1], end_p[1], data_p.shape[0])
        sleep(1)
        # Scan -
        start_n, end_n, data_n = self.perform_scan(end_pos_mcs, start_pos_mcs, direction='negative')
        y_n = np.linspace(start_n[1], end_n[1], data_n.shape[0])
        combined_p = np.insert(data_p, 0, y_p, axis=1) # (y, Bx, By, Bz)
        combined_n = np.insert(data_n, 0, y_n, axis=1) # (y, Bx, By, Bz)
        data_pn_offset = self.calc_offset(combined_p[:, [0, 3]], combined_n[:, [0, 3]])
        self.y_offset_fsv = data_pn_offset
        return data_pn_offset

    def run_z_routine(self):
        half_length = np.array([0, 0, 20])
        current_pos_fsv = self.mcs2fsv(self.cmm.get_position())
        start_pos_mcs = self.fsv2mcs(current_pos_fsv - half_length)
        end_pos_mcs = self.fsv2mcs(current_pos_fsv + half_length)
        # Set hall probe to high sensitivity
        self.daq.change_sensitivity(sensitivity='100MT')
        # Scan +
        start_p, end_p, data_p = self.perform_scan(start_pos_mcs, end_pos_mcs, sensitivity=100, direction='negative')
        z_p = np.linspace(start_p[2], end_p[2], data_p.shape[0])
        sleep(1)
        # Scan -
        start_n, end_n, data_n = self.perform_scan(end_pos_mcs, start_pos_mcs, sensitivity=100)
        z_n = np.linspace(start_n[2], end_n[2], data_n.shape[0])
        combined_p = np.insert(data_p, 0, z_p, axis=1) # (z, Bx, By, Bz)
        combined_n = np.insert(data_n, 0, z_n, axis=1) # (z, Bx, By, Bz)
        data_pn_offset = self.calc_offset(combined_p[:, [0, 1]], combined_n[:, [0, 1]])
        self.z_offset_fsv = data_pn_offset
        return data_pn_offset

    def save_probe_offset(self, filepath):
        offset_mcs = np.array([self.x_offset_fsv, self.y_offset_fsv, self.z_offset_fsv])@self.rotation
        np.savetxt(Path(filepath) / 'hallsensor_offset.txt', offset_mcs)

    def shutdown(self):
        self.cmm.close()
        self.daq.power_off()
        self.daq.close_tasks()

if __name__ == '__main__':
    test = FSV(r'D:\CMM Programs\FSV Calibration\fsv_alignment.txt', r'C:\Users\dyeagly\Documents\hall_probe\hall_probe\Hall probe 444-20')
    
    num_iter = input('Position probe above Y-axis.\nEnter number of iterations: ')
    start_point = test.cmm.get_position()
    for i in range(num_iter):
        offset = test.run_x_routine()
        print(f'offset {i}: {round(offset, 3)}')
        with open('polyfit_offset_x.txt', 'a') as file:
            file.write(f'{round(offset, 6)}\n')
        test.cmm.goto_position(start_point)
        while np.linalg.norm(start_point - test.cmm.get_position()) > 0.025:
            pass
    test.shutdown()
    test.save_probe_offset(r'D:\CMM Programs\FSV Calibration\fsv_alignment.txt')