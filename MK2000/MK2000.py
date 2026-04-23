import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

import serial
import time
from datetime import datetime
from tool.tools import save_temperature_to_csv


class MK2000:
    def __init__(self, serial_port="COM4", baud_rate=115200, timeout=10):
        self.mk2000 = serial.Serial(
            port=serial_port,
            baudrate=baud_rate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout,
            xonxoff=False,
            rtscts=False,
            dsrdtr=True,
        )
        print(f"MK2000 Status: {'Open' if self.mk2000.is_open else 'Closed'}")

    def read_temperature_once(self, temperatures, start_time):
        if not self.mk2000.is_open:
            self.mk2000.open()

        # self.mk2000.write(b"*IDN?\n")
        # idn_response = self.mk2000.readline().decode(errors="ignore").strip()

        self.mk2000.reset_input_buffer()
        self.mk2000.write(b"temp:ctemperature?\n")
        temp_response = self.mk2000.readline().decode(errors="ignore").strip()

        mk2000_record_time = time.perf_counter() - start_time

        try:
            temperature = float(temp_response)
            temperatures[0].append(mk2000_record_time)
            temperatures[1].append(temperature)
        except ValueError as ve:
            print(f"Error converting response to float: '{temp_response}' - {ve}")

        return temperatures

    def mk2000_read_temperature(
        self,
        duration=5,
        sample_rate=10,
        temperatures=None,
        start_time=0,
        formatted_time="None",
        save_path="./",
    ):
        if temperatures is None:
            temperatures = [[], []]

        try:
            start_time2 = time.perf_counter() - start_time
            print(f"MK2000 start: {start_time2}")

            interval = 1 / sample_rate
            total_samples = int(duration * sample_rate)

            for _ in range(total_samples):
                start_time_temp = time.perf_counter()

                self.read_temperature_once(temperatures, start_time)

                elapsed_time = time.perf_counter() - start_time_temp
                sleep_time = interval - elapsed_time

                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    print("Warning: function execution took longer than the interval.")

        except Exception as e:
            print(f"Exception occurred: {e}")

        finally:
            end_time2 = time.perf_counter() - start_time
            print(f"MK2000 end: {end_time2}")
            print(f"MK2000 worked: {end_time2 - start_time2}s")
            self.close_mk2000()

        if len(temperatures[0]) == 0 or len(temperatures[1]) == 0:
            print("Data is empty, nothing to save.")
            return temperatures

        os.makedirs(save_path, exist_ok=True)
        # current_date = datetime.now().strftime("%Y%m%d_%H%M%S")

        save_temperature_to_csv(
            save_path + "./MK2000_temperature.csv",
            temperatures,
            titles=["Time", "Temperature(°C)"],
        )

        return temperatures

    def close_mk2000(self):
        if self.mk2000.is_open:
            self.mk2000.close()
        print(f"MK2000 Status: {'Open' if self.mk2000.is_open else 'Closed'}")


if __name__ == "__main__":
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y_%m_%d_%H_%M")

    mk2000 = MK2000(serial_port="COM4")
    mk2000.mk2000_read_temperature(
        duration=5, sample_rate=10, start_time=time.perf_counter(), save_path="./"
    )
