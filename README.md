# BLE Computer Control

This project enables interaction with a computer using three main interfaces: 

1. A **Flask web interface**, 
2. A **Flutter-based mobile application**, and 
3. **Touch-sensitive pins on an ESP32 microcontroller**. 

Each interface can trigger various predefined actions on the computer, providing a flexible and innovative approach to computer control.

## Features

### 1. **Mobile Application**
- Developed with Flutter.
- Includes BLE scanning to connect to the ESP32 device.
- Allows sending voice commands that are classified locally on the computer using a **Logistic Regression model** hosted on the Flask interface.

### 2. **ESP32 Microcontroller**
- Utilizes the touch-sensitive pins of the ESP32 for physical interactions.
- Sends signals via BLE to control the computer.

### 3. **Flask Web Interface**
- Hosts the backend for voice command classification.
- Provides a user-friendly web interface for managing interactions and monitoring actions.

### 4. **Predefined Actions**
The system supports the following actions:
- **Increase Brightness** (`parlaklik_ac`)
- **Decrease Brightness** (`parlaklik_kapat`)
- **Increase Volume** (`ses_ac`)
- **Decrease Volume** (`ses_kapat`)
- **Take a Screenshot** (`ekran_goruntusu`)

## Requirements

- **Hardware**:
  - A computer with Bluetooth capabilities.
  - An ESP32 microcontroller with touch-sensitive pins.
- **Software**:
  - Flutter mobile application ([Download Here](https://drive.google.com/file/d/1VfUPdJfNOAdrBGB1T-_16OfgXumDGQcu/view?usp=sharing)).
  - Python environment for Flask and the Logistic Regression model.

## Setup and Installation

### 1. **Setting Up the Mobile Application**
- Download the mobile app APK from the [provided link](https://drive.google.com/file/d/1VfUPdJfNOAdrBGB1T-_16OfgXumDGQcu/view?usp=sharing).
- Install it on your smartphone.
- Open the app and navigate to the BLE scanning screen to find and connect to the ESP32 device.  
**(Place Screenshot 1: BLE scanning screen here)**

### 2. **Configuring the ESP32**
- Upload the firmware to the ESP32, ensuring BLE and touch pin functionality are enabled.
- Set the ESP32 in discoverable mode.

### 3. **Flask Server Setup**
- Clone the repository from GitHub.
- Install the required Python libraries:
  ```bash
  pip install -r requirements.txt
  ```
- Run the Flask server:
  ```bash
  python app.py
  ```
- The server will classify voice commands sent from the mobile application using the Logistic Regression model.

### 4. **Interfacing**
- After BLE connection, use the mobile app to send voice commands or interact with the ESP32 touch pins to trigger actions.  
![image](https://github.com/user-attachments/assets/69a12ac4-4e5f-4199-8aa1-d44a4456d601)


- The Flask web interface will display and manage interactions as they occur.  
**(Place Screenshot 3: Flask web interface here)**

## Screenshots

1. **Mobile App - BLE Scanning Screen**: Shows available BLE devices before connecting.  
2. **Mobile App - Connected Interface**: Displays the interface after successfully connecting to the ESP32 device.  
3. **Flask Web Interface**: Displays the actions triggered and status updates.

## How It Works

1. The **mobile app** connects to the ESP32 device via BLE. Users can:
   - Send voice commands to the Flask server for classification.
   - Trigger actions defined by the system.

2. The **ESP32 touch pins** send signals to perform predefined actions.

3. The **Flask interface**:
   - Processes voice commands using a locally trained Logistic Regression model.
   - Displays actions and logs for user monitoring.

## Troubleshooting

- **BLE Connection Issues**:
  - Ensure the ESP32 is powered and in discoverable mode.
  - Check that Bluetooth is enabled on your smartphone.

- **Voice Command Errors**:
  - Ensure the Flask server is running and accessible.
  - Verify the Logistic Regression model is properly trained and loaded.

## License

This project is licensed under the MIT License. For more details, see the [LICENSE](https://github.com/tamerkanak/BLE-Computer-Control/blob/main/LICENSE).

## Acknowledgments

- Special thanks to the open-source community for tools like [flutter_blue](https://pub.dev/packages/flutter_blue) and Flask. 

For source code and further information, visit the [GitHub repository](https://github.com/tamerkanak/BLE-Computer-Control/tree/main).
