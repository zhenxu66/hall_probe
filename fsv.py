from calibration import filter_data
from nicdaq import HallDAQ
from time import sleep
import numpy as np
import zeisscmm

class FSV:
    CERAMIC_THK = 1.0
    TRACE_THK = 0.06
    GLAZE_THK = 0.01
    def __init__(self, fsv_filename: str, probe_offset_filename: str):
        self.daq = HallDAQ(1, 10000, start_trigger=True, acquisition='finite')
        self.daq.power_on()
        self.cmm = zeisscmm.CMM()
        self.rotation, self.translation = self.import_fsv_alignment(fsv_filename)
        self.probe_offset = self.import_probe_offset(probe_offset_filename)

    def import_fsv_alignment(self, filename: str):
        diff = np.genfromtxt(filename, delimiter=' ')
        rotation = diff[:-3].reshape((3,3))
        translation = diff[-3:]
        return (rotation, translation)
    
    def import_probe_offset(self, filename: str):
        offset = np.genfromtxt(filename, delimiter=' ')
        return offset

    def fsv2mcs(self, coordinate: np.ndarray):
        return (coordinate - self.translation)@self.rotation

    def mcs2fsv(self, coordinate: np.ndarray):
        return coordinate@np.linalg.inv(self.rotation) + self.translation

    def perform_scan(self, start_pt, end_pt, direction='positive'):
        '''
        direction can either be 'positive' or 'negative'
        '''
        self.cmm.cnc_on()
        self.cmm.set_speed(5)
        self.cmm.goto_position(start_pt)
        while np.linalg.norm(start_pt - self.cmm.get_position()) > 0.012:
            pass
        self.daq.fsv_on(v=direction)
        self.daq.start_hallsensor_task()
        sleep(1)
        self.cmm.goto_position(end_pt)
        sleep(1)
        self.daq.pulse()
        start_position = self.mcs2fsv(self.cmm.get_position())
        data = self.daq.read_hallsensor()
        end_position = self.mcs2fsv(self.cmm.get_position())
        self.daq.fsv_off()
        self.daq.stop_hallsensor_task()
        self.cmm.set_speed(70)
        self.cmm.cnc_off()
        return (start_position, end_position, data)

    def bx_routine(self):
        half_length = np.array([20, 0, 0])
        current_pos_fsv = self.mcs2fsv(self.cmm.get_position())
        start_pos_mcs = self.fsv2mcs(current_pos_fsv - half_length)
        end_pos_mcs = self.fsv2mcs(current_pos_fsv + half_length)
        start_p, end_p, data_p = self.perform_scan(start_pos_mcs, end_pos_mcs)
        x_p = np.linspace(start_p[0], end_p[0], data_p.shape[0])
        sleep(1)
        start_n, end_n, data_n = self.perform_scan(end_pos_mcs, start_pos_mcs, direction='negative')
        x_n = np.linspace(start_n[0], end_n[0], data_n.shape[0])
        combined_p = np.insert(data_p, 0, x_p, axis=1)
        combined_n = np.insert(data_n, 0, x_n, axis=1)
        return (combined_p, combined_n)

    def by_routine(self):
        current_pos = self.cmm.get_position()

    def bz_routine(self):
        current_pos = self.cmm.get_position()

    def save_probe_offset(self):
        pass

    def shutdown(self):
        self.cmm.close()
        self.daq.power_off()
        self.daq.close_tasks()

if __name__ == '__main__':
    test = FSV(r'D:\CMM Programs\FSV Calibration\fsv_alignment.txt', r'D:\CMM Programs\FSV Calibration\probe_offset.txt')
    data_p, data_n = test.bx_routine()
    print(data_p.shape, data_n.shape)
    np.savetxt('bx_positive.txt', data_p, fmt='%.6f', delimiter=' ')
    np.savetxt('bx_negative.txt', data_n, fmt='%.6f', delimiter=' ')
    test.shutdown()