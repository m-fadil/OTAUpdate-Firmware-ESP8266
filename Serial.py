import serial
import serial.tools.list_ports
import threading
import time
import os
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import PromptSession

def clear(withText=None):
    os.system('cls' if os.name == 'nt' else 'clear')
    if withText: print(withText)

class SerialX:
    def __init__(self) -> None:
        raw_ports = serial.tools.list_ports.comports()

        self.ports = [port for port, desc, hwid in sorted(raw_ports)]
        self.baudrate = 115200
        self.connect = True

    def read_serial(self, port, baudrate):
        try:
            self.ser = serial.Serial(port, baudrate)
            print("Terhubung ke port serial: " + self.ser.portstr)
            
            while self.connect:
                data = self.ser.readline().decode('latin1').strip()
                millis = int(round(time.time() * 1000))
                millis_time = time.strftime("%Y-%m-%d %H:%M:%S.{:03d}", time.localtime(millis / 1000.0))
                print(f"[{millis_time.format(millis % 1000)}] {data}")

        except serial.SerialException as e:
            print("Kesalahan pada port serial: ", e)

    def _close(self):
        self.connect = False
        self.ser.close()
        exit(0)

    def process_input(self):
        session = PromptSession()
        while True:
            try:
                command = session.prompt(">> ")
                if command.lower() == 'clear':
                    clear()
                elif command.lower() == 'exit':
                    self._close()
            except KeyboardInterrupt:
                self._close()
                
            

    def run(self):
        for idx, port in enumerate(self.ports):
            print(f"{idx + 1}. {port}")
        while True:
            try:
                inp = int(input(">> "))
                break
            except:
                print("error")

        port = self.ports[inp - 1]
        baudrate = 115200
        
        serial_thread = threading.Thread(target=self.read_serial, args=(port, baudrate))
        input_thread = threading.Thread(target=self.process_input)

        with patch_stdout():
            serial_thread.start()
            input_thread.start()
            serial_thread.join()
            input_thread.join()


if __name__ == "__main__":
    mySerial = SerialX()
    mySerial.run()
