import sys
from time import sleep
from PyQt5.QtCore import QThread
from serial import Serial, SerialException
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QLineEdit, QPlainTextEdit, QPushButton


class InputThread(QThread):
    def __init__(self, current_com_port, input_label):
        QThread.__init__(self)
        self.flag = True
        self.current_com_port = current_com_port
        self.input_label = input_label

    def run(self) -> None:
        self.auto_read()

    def auto_read(self) -> None:
        while self.flag:
            try:
                start_byte = self.current_com_port.read(1).hex()
                if start_byte and start_byte[0] == 'a':
                    input_data = self.current_com_port.read(int(start_byte[1], 16) - 1).hex()
                    input_command = list()
                    input_command.append(start_byte.upper() + ' ')
                    for i, symbol in enumerate(input_data):
                        input_command.append(symbol.upper())
                        if i % 2 != 0 and i < len(input_data) - 1:
                            input_command.append(' ')
                    self.input_label.insertPlainText(f'{"".join(input_command)}\n')
                sleep(0.1)
            except (OSError, SerialException):
                pass

    def stop(self):
        self.flag = False
        self.current_com_port.close()


class COMPortTransmission(QMainWindow):
    def __init__(self):
        super(COMPortTransmission, self).__init__()
        self.input_thread = None
        self.current_com_port = None
        self.addresses = ['1', '2']

        self.setWindowTitle('COM port')
        self.setFixedSize(325, 450)

        self.com_port_label = QLabel(self)
        self.com_port_label.move(10, 10)
        self.com_port_label.setText('COM-порт:')
        self.com_port_label.adjustSize()

        self.com_port_choice = QComboBox(self)
        self.com_port_choice.setGeometry(130, 5, 80, 30)
        self.com_port_choice.setEnabled(False)

        self.output_label_title = QLabel(self)
        self.output_label_title.move(10, 140)
        self.output_label_title.setText('Введите команду (в hex, через пробел):')
        self.output_label_title.adjustSize()

        self.output_label = QLineEdit(self)
        self.output_label.setGeometry(10, 170, 305, 30)
        self.output_label.setReadOnly(True)

        self.input_label_title = QLabel(self)
        self.input_label_title.move(100, 255)
        self.input_label_title.setText('Ответ контроллера:')
        self.input_label_title.adjustSize()

        self.input_label = QPlainTextEdit(self)
        self.input_label.setGeometry(10, 280, 305, 160)
        self.input_label.setReadOnly(True)

        self.get_com_ports_button = QPushButton(self)
        self.get_com_ports_button.setText('Получить\nдоступные\nCOM-порты')
        self.get_com_ports_button.setGeometry(225, 5, 90, 70)
        self.get_com_ports_button.clicked.connect(self.get_com_ports)

        self.speed_title_label = QLabel(self)
        self.speed_title_label.setText('Адрес:')
        self.speed_title_label.move(10, 50)
        self.speed_title_label.adjustSize()

        self.address_choice = QComboBox(self)
        self.address_choice.setGeometry(130, 45, 80, 30)
        self.address_choice.setEnabled(False)

        self.com_port_connection_button = QPushButton(self)
        self.com_port_connection_button.setText('Образовать соединение')
        self.com_port_connection_button.setGeometry(10, 90, 155, 30)
        self.com_port_connection_button.setEnabled(False)
        self.com_port_connection_button.clicked.connect(self.com_port_connection)

        self.com_port_close_connection_button = QPushButton(self)
        self.com_port_close_connection_button.setText('Прервать соединение')
        self.com_port_close_connection_button.setGeometry(175, 90, 140, 30)
        self.com_port_close_connection_button.setEnabled(False)
        self.com_port_close_connection_button.clicked.connect(self.com_port_close_connection)

        self.clear_button = QPushButton(self)
        self.clear_button.setText('Послать запрос')
        self.clear_button.setGeometry(10, 210, 150, 30)
        self.clear_button.setEnabled(False)
        self.clear_button.clicked.connect(self.send_request)

        self.send_button = QPushButton(self)
        self.send_button.setText('Послать команду')
        self.send_button.setGeometry(170, 210, 145, 30)
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(self.send_command)

    def get_com_ports(self) -> None:
        self.address_choice.clear()
        self.com_port_choice.clear()
        com_ports = ['COM%s' % i for i in range(1, 257)]
        connection_flag = False
        for com_port_number in com_ports:
            try:
                com_port = Serial(com_port_number)
                com_port.close()
                connection_flag = True
                self.com_port_choice.addItem(com_port_number)
            except (OSError, SerialException):
                pass
        if connection_flag:
            for address in self.addresses:
                self.address_choice.addItem(address)

            self.address_choice.setEnabled(True)
            self.com_port_choice.setEnabled(True)
            self.com_port_connection_button.setEnabled(True)

    def com_port_connection(self) -> None:
        try:
            self.current_com_port = Serial(
                port=self.com_port_choice.currentText(),
                baudrate=10416,
                bytesize=8,
                parity='M',
                stopbits=1,
                timeout=1)
            self.input_thread = InputThread(self.current_com_port, self.input_label)
            self.input_thread.start()

            self.send_button.setEnabled(True)
            self.clear_button.setEnabled(True)
            self.com_port_close_connection_button.setEnabled(True)

            self.output_label.setReadOnly(False)
            self.com_port_choice.setEnabled(False)
            self.get_com_ports_button.setEnabled(False)
            self.com_port_connection_button.setEnabled(False)
        except (OSError, SerialException):
            pass

    def com_port_close_connection(self) -> None:
        self.output_label.clear()
        self.input_thread.stop()
        self.input_thread = None
        self.current_com_port = None

        self.output_label.setReadOnly(True)
        self.com_port_choice.setEnabled(True)
        self.get_com_ports_button.setEnabled(True)
        self.com_port_connection_button.setEnabled(True)

        self.send_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.com_port_close_connection_button.setEnabled(False)

    def send_request(self) -> None:
        self.current_com_port.parity = 'M'
        request_start_byte = 'A4'
        self.current_com_port.write(bytearray.fromhex(request_start_byte))
        self.current_com_port.parity = 'S'
        output_request = '0' + self.address_choice.currentText() + '02'
        output_request = output_request + self.crc_calculation(request_start_byte, output_request)
        print(request_start_byte + output_request)
        output_request = bytearray.fromhex(output_request)
        self.current_com_port.write(output_request)

    def send_command(self) -> None:
        output_command = self.output_label.text()
        if output_command:
            self.current_com_port.parity = 'M'
            command_size = output_command.rstrip().count(' ') + 4
            command_start_byte = 'A' + hex(command_size)[2:]
            self.current_com_port.write(bytearray.fromhex(command_start_byte))
            self.current_com_port.parity = 'S'
            output_command = '0' + self.address_choice.currentText() + output_command.replace(' ', '')
            output_command = output_command + self.crc_calculation(command_start_byte, output_command)
            output_command = bytearray.fromhex(output_command)
            self.current_com_port.write(output_command)

    @staticmethod
    def crc_calculation(start_byte: str, output: str) -> hex:
        output = [output[i - 1:i + 1] for i in range(int(start_byte[1], 16)) if i % 2 != 0]
        acc = int(start_byte, 16)
        for i in range(len(output)):
            if acc & int('80', 16) != 0:
                carry = 1
            else:
                carry = 0
            acc = (acc << 1) & 0xFF
            acc = ((acc + int(output[i], 16) & 0xFF) + carry) & 0xFF
        return hex(acc)[2:]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = COMPortTransmission()
    main_window.show()
    sys.exit(app.exec_())

# pyinstaller -w -F --onefile --upx-dir=D:\UPX main.py
