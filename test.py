import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QWidget
from PyQt5.QtGui import QTextCursor 
from PyQt5.QtCore import Qt , pyqtSignal
import socket
import threading
#ui explicita
class ChatClient(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chat Client")
        self.setGeometry(100, 100, 600, 400)

        # QTextEdit para recibir mensajes
        self.rec_textedit = QTextEdit(self)
        self.rec_textedit.setReadOnly(True)

        # QTextEdit para escribir mensajes
        self.mensaje_textedit = QTextEdit(self)
        self.mensaje_textedit.setMaximumHeight(100)

        # Botón para enviar mensajes
        self.enviar_button = QPushButton("Enviar", self)
        self.enviar_button.clicked.connect(self.enviar_mensaje)

        # Diseño de la interfaz
        layout = QVBoxLayout()
        layout.addWidget(self.rec_textedit)
        layout.addWidget(self.mensaje_textedit)
        layout.addWidget(self.enviar_button)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Configuración del socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("127.0.0.1", 12345))

        # Iniciar hilo para recibir mensajes
        recibir_thread = threading.Thread(target=self.recibir_mensajes)
        recibir_thread.start()

        # Mostrar mensaje "Escriba su nombre" en el cuadro de texto de recepción
        self.rec_textedit.append("")

    def enviar_mensaje(self):
        mensaje = self.mensaje_textedit.toPlainText()
        if mensaje:
            # Agregar el mensaje con "yo:" al inicio al cuadro de texto de recepción
            mensaje_formateado = f"Yo: {mensaje}"
            self.rec_textedit.append(mensaje_formateado)
            # Enviar el mensaje al servidor
            self.client_socket.send(mensaje.encode())
            self.mensaje_textedit.clear()

    def recibir_mensajes(self):
        while True:
            data = self.client_socket.recv(1024)
            mensaje = data.decode()

            # Usar QScrollBar para desplazarte al final del QTextEdit
            scroll_bar = self.rec_textedit.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())

            # Usar un método seguro para actualizar QTextEdit en el hilo principal
            self.rec_textedit.append(mensaje)
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = ChatClient()
    client.show()
    sys.exit(app.exec_())
