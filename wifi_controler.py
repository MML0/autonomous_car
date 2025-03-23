import socket
import struct
import threading
import time

class Car:
    def __init__(self, ip: str, port: int = 12345):
        """
        Initialize the car with its IP address and speed.
        :param ip: str - The IP address of the car
        :param port: int - The UDP port number (default 12345)
        """
        self.ip = ip
        self.steer_angle = 0
        self.speed = 0

        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.04)  
        self.servo1 = 0
        self.servo2 = 0
        self.sensor1 = 0
        self.sensor2 = 0
        self.sensor3 = 0

        self.running = True
        threading.Thread(target=self._receive_data, daemon=True).start()

        print(f"Car initialized with IP: {self.ip}, Speed: {self.speed}")
    def _receive_data(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(16)
                self.servo1, self.servo2, self.speed, self.sensor1, self.sensor2, self.sensor3 = struct.unpack("bbbHHH", data)
            except socket.timeout:
                pass
            time.sleep(0.01)

    def forward(self, speed: int):
        """
        Move the car forward at the specified speed.
        :param speed: int - The speed to set
        """
        self.speed = speed
        self.send_control(self.steer_angle, self.steer_angle, self.speed)
        print(f"Car at IP {self.ip} is moving forward at speed {self.speed}")

    def steer(self, degree: int):
        """
        Steer the car to the specified degree.
        :param degree: int - The degree to steer
        """
        self.steer_angle = degree
        self.send_control(degree, degree, self.speed)
        print(f"Car at IP {self.ip} is steering at {self.steer_angle} degrees")


    def send_control(self, servo1: int, servo2: int, speed: int):
        self.servo1 = max(-128, min(128, servo1))
        self.servo2 = max(-128, min(128, servo2))
        self.speed = max(-128, min(128, speed))

        data = struct.pack("bbb10x", self.servo1, self.servo2, self.speed)
        self.sock.sendto(data, (self.ip, self.port))

    def stop(self):
        self.running = False
        self.sock.close()

# Example usage
if __name__ == "__main__":
    # Example code
    car = Car("192.168.1.100", 12345)

    while True:
        car.send_control(50, -50, 100)  # Example command
        time.sleep(1)
        print(12)
