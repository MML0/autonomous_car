import matplotlib.pyplot as plt
import time

class Controller:
    def __init__(self, name, debug_mode=True, k_p=1, k_i=0.1, k_d=0.1):
        self.name = name
        self.debug_mode = debug_mode
        self.k_p = k_p
        self.k_i = k_i
        self.k_d = k_d
        self.error = 0
        self.error_prev = 0
        self.integral = 0
        if self.debug_mode:
            plt.ion()  # Enable interactive mode
            self.fig, self.ax = plt.subplots()
            self.setpoints = []
            self.measurements = []
            self.outputs = []

    def calculate(self, setpoint, measurement):
        if self.debug_mode:
            self.setpoints.append(setpoint)
            self.measurements.append(measurement)
        self.error = setpoint - measurement
        self.integral += self.error
        derivative = self.error - self.error_prev
        self.error_prev = self.error
        output = self.k_p * self.error + self.k_i * self.integral + self.k_d * derivative
        if self.debug_mode:
            self.outputs.append(output)
            self._update_graph()
        return output

    def _update_graph(self):
        self.ax.clear()
        self.ax.plot(self.setpoints, label="Setpoint", color="blue")
        self.ax.plot(self.measurements, label="Measurement", color="orange")
        self.ax.plot(self.outputs, label="Output", color="green")
        self.ax.set_title(f"Controller: {self.name}")
        self.ax.set_xlabel("Time Steps")
        self.ax.set_ylabel("Values")
        self.ax.legend()
        plt.pause(0.01)  # Pause for a brief moment to update the plot

if __name__ == "__main__":
    # Create an instance of the controller
    controller = Controller("Test Controller", debug_mode=True, k_p=1, k_i=0.1, k_d=0.1)

    # Simulate a process with a fixed setpoint and measurements
    setpoint = 10
    measurement = 5
    for i in range(50):  # Run for 50 time steps
        measurement += (controller.calculate(setpoint, measurement) - measurement) * 0.1  # Simulate system dynamics
        time.sleep(0.1)  # Simulate delay

    # Keep the plot open at the end
    plt.ioff()
    plt.show()
