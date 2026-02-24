import serial
import time


def read_temperature(serial_port="COM3", baud_rate=115200, timeout=10):
    """
    Reads the current temperature from the INSTEC MK2000 temperature controller.

    Parameters:
        serial_port (str): The serial port to which the MK2000 is connected.
        baud_rate (int): The baud rate for the serial communication.
        timeout (int): Timeout for the serial communication in seconds.

    Returns:
        list: A list of temperatures read from the MK2000.
    """
    try:
        # Initialize serial connection
        mk2000 = serial.Serial(
            port=serial_port,
            baudrate=baud_rate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout,
            xonxoff=False,  # No flow control
            rtscts=False,  # No RTS/CTS flow control
            dsrdtr=True,  # Data Terminal Ready on
        )

        # Check connection status
        print(f"Serial Port Status: {'Open' if mk2000.is_open else 'Closed'}")

        temperatures = []

        for i in range(3):
            time.sleep(1)  # Pause for 1 second

            if not mk2000.is_open:
                mk2000.open()

            # Send the identification command
            mk2000.write(b"*IDN?\n")
            idn_response = mk2000.readline().decode().strip()
            print(f"Device ID: {idn_response}")

            # Send the command to read the current temperature
            mk2000.write(b"temp:ctemperature?\n")
            temp_response = mk2000.readline().decode().strip()

            try:
                temperature = float(temp_response)
                temperatures.append(temperature)
                print(f"Current Temperature (Attempt {i+1}): {temperature} °C")
            except ValueError as ve:
                print(f"Error converting response to float: {temp_response} - {ve}")

            mk2000.close()

        return temperatures

    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")


# Example usage
if __name__ == "__main__":
    # Adjust the COM port as needed
    read_temperature(serial_port="COM3")
