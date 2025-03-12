class Car:
    def __init__(self, ip: str, speed: int):
        """
        Initialize the car with its IP address and speed.
        :param ip: str - The IP address of the car
        :param speed: int - The initial speed of the car
        """
        self.ip = ip
        self.speed = speed
        self.steer_angle = 0
        print(f"Car initialized with IP: {self.ip}, Speed: {self.speed}")

    def forward(self, speed: int):
        """
        Move the car forward at the specified speed.
        :param speed: int - The speed to set
        """
        self.speed = speed
        print(f"Car at IP {self.ip} is moving forward at speed {self.speed}")

    def steer(self, degree: int):
        """
        Steer the car to the specified degree.
        :param degree: int - The degree to steer
        """
        self.steer_angle = degree
        print(f"Car at IP {self.ip} is steering at {self.steer_angle} degrees")
