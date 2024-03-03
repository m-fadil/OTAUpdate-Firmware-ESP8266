import serial
import time
import threading

def read_serial(port, baudrate):
    try:
        ser = serial.Serial(port, baudrate)
        print("Terhubung ke port serial: " + ser.portstr)
        
        while True:
            data = ser.readline().decode('latin1').strip()
            millis = int(round(time.time() * 1000))
            millis_time = time.strftime("%Y-%m-%d %H:%M:%S.{:03d}", time.localtime(millis / 1000.0))
            print(f"[{millis_time.format(millis % 1000)}] {data}")

    except serial.SerialException as e:
        print("Kesalahan pada port serial: ", e)

def process_input():
    while True:
        command = input()
        if command.lower() == 'clear':
            print("\033[H\033[J")

if __name__ == "__main__":
    port = 'COM5'
    baudrate = 115200
    
    serial_thread = threading.Thread(target=read_serial, args=(port, baudrate))
    serial_thread.start()
    
    input_thread = threading.Thread(target=process_input)
    input_thread.start()
    
    serial_thread.join()
    input_thread.join()
