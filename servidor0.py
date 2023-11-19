import socket
import threading
import json

# Cargar el objeto JSON desde el archivo
with open("artefactos.json", "r", encoding="utf-8") as file:
    artefactos_dict = json.load(file)

# Crear un socket del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("127.0.0.1", 12345))
server_socket.listen(3)

# Lista para mantener un registro de todos los clientes conectados
clientes = []
nombres_clientes = {}
artefactos_clientes = {}


def enviar_mensaje_servidor(mensaje, cliente):
    mensaje_servidor = f"{mensaje}"
    try:
        cliente.send(mensaje_servidor.encode("utf-8"))
    except Exception as e:
        print(f"No se pudo enviar mensaje al cliente: {e}")
#cuando un nuevo cliente pone su nombre
def notificar_conexion_cliente(cliente):
    for otro_cliente in clientes:
        if otro_cliente != cliente:
            enviar_mensaje_servidor(f"[SERVER] {nombres_clientes[cliente]} se ha unido al chat.", otro_cliente)
#:p o mata la terminal
def notificar_desconexion_cliente(cliente_desconectado):
    for cliente in clientes:
        if cliente != cliente_desconectado:
            enviar_mensaje_servidor(f"[SERVER] {nombres_clientes[cliente_desconectado]} se ha desconectado.", cliente)
#comando u
def mostrar_clientes_conectados(cliente_emisor):
    lista_clientes = ", ".join([nombres_clientes[c] for c in clientes if c != cliente_emisor])
    mensaje_mostrar_clientes = f"[SERVER] Clientes conectados: {lista_clientes}"
    enviar_mensaje_servidor(mensaje_mostrar_clientes, cliente_emisor)
#comando artefactos
def mostrar_artefactos(cliente_emisor):
    if cliente_emisor in artefactos_clientes:
        artefactos_usuario = artefactos_clientes[cliente_emisor]
        descripcion_artefactos = [artefactos_dict.get(num, f"Artefacto Desconocido {num}") for num in artefactos_usuario]
        mensaje_artefactos = f"[SERVER] Tus artefactos son: {', '.join(descripcion_artefactos)}"
        enviar_mensaje_servidor(mensaje_artefactos, cliente_emisor)
    else:
        enviar_mensaje_servidor("[SERVER] No tienes artefactos registrados.", cliente_emisor)

#commandos
def manejar_comando(comando, cliente_emisor):
    mensaje_comando = None

    if comando == "smile":
        mensaje_comando = " :)"
    elif comando == "angry":
        mensaje_comando = " >:("    
    elif comando == "combito":
        mensaje_comando = " Q(’- ’Q)"
    elif comando == "larva":
        mensaje_comando = " (:o)OOOooo"   
    elif comando == "u":
        mostrar_clientes_conectados(cliente_emisor)
        return
    elif comando.startswith("p "):
        enviar_mensaje_privado(comando, cliente_emisor)
        return
    elif comando == "artefactos":
        mostrar_artefactos(cliente_emisor)
        return
    elif comando == "q":
        desconectar_cliente(cliente_emisor)
        return
    elif comando.startswith("artefacto "):
        obtener_nombre_artefacto(comando, cliente_emisor)
        return
    elif comando.startswith("offer "):
        manejar_oferta(comando, cliente_emisor)
        return
    elif comando == "accept":
        manejar_aceptar(cliente_emisor)
        return
    elif comando == "reject":
        manejar_rechazar(cliente_emisor)
        return
    if mensaje_comando:
        mensaje_a_enviar = f"{nombres_clientes[cliente_emisor]}:{mensaje_comando}"
        for cliente_destino in clientes:
            if cliente_destino != cliente_emisor:
                enviar_mensaje_servidor(mensaje_a_enviar, cliente_destino)

    else:
        enviar_mensaje_servidor(f"[SERVER] Comando desconocido: {comando}", cliente_emisor)

def manejar_oferta(comando, cliente_emisor):
    parametros = comando.split()[1:]

    if len(parametros) == 3:
        identificador_destino, mi_artefacto_id, su_artefacto_id = parametros

        # Validar que los artefactos son numeros validos y que el destino existe
        if mi_artefacto_id.isdigit() and su_artefacto_id.isdigit() and cliente_emisor in nombres_clientes:
            cliente_destino = obtener_cliente_por_nombre(identificador_destino)

            if cliente_destino:
                # Validar que los artefactos existen
                if mi_artefacto_id in artefactos_dict and su_artefacto_id in artefactos_dict:
                    # Validar que los clientes tengan los artefactos que estan intercambiando
                    if su_artefacto_id in artefactos_clientes[cliente_destino] and mi_artefacto_id in artefactos_clientes[cliente_emisor]:
                        # Realizar la oferta
                        mensaje_oferta = f"[SERVER] {nombres_clientes[cliente_emisor]} te ha ofrecido intercambiar {artefactos_dict[mi_artefacto_id]} por {artefactos_dict[su_artefacto_id]}. ¿Aceptar? (Si/No)"
                        enviar_mensaje_servidor(mensaje_oferta, cliente_destino)

                        # Esperar la respuesta del destino
                        respuesta_destino = cliente_destino.recv(1024).decode().strip().lower()

                        if respuesta_destino == 'si':
                            # Realizar el intercambio de artefactos
                            artefactos_clientes[cliente_emisor].remove(mi_artefacto_id)
                            artefactos_clientes[cliente_emisor].append(su_artefacto_id)

                            artefactos_clientes[cliente_destino].remove(su_artefacto_id)
                            artefactos_clientes[cliente_destino].append(mi_artefacto_id)

                            # Informar a ambos clientes sobre el intercambio
                            mensaje_aceptar = "[SERVER] ¡Intercambio realizado!"
                            enviar_mensaje_servidor(mensaje_aceptar, cliente_emisor)
                            enviar_mensaje_servidor(mensaje_aceptar, cliente_destino)
                        else:
                            # Informar al emisor que la oferta fue rechazada
                            mensaje_rechazar = "[SERVER] Intercambio rechazado."
                            enviar_mensaje_servidor(mensaje_rechazar, cliente_emisor)

                        return

    # Si hay algún problema en los parametros, informar al emisor
    enviar_mensaje_servidor("[SERVER] Uso incorrecto del comando. Ejemplo: :offer Gus 32 12", cliente_emisor)
#no terminado
def manejar_aceptar(cliente_emisor):
    mensaje_aceptar = "[SERVER] ¡Intercambio realizado!"
    enviar_mensaje_servidor(mensaje_aceptar, cliente_emisor)
#no terminado
def manejar_rechazar(cliente_emisor):
    mensaje_rechazar = "[SERVER] Intercambio rechazado."
    enviar_mensaje_servidor(mensaje_rechazar, cliente_emisor)

def obtener_cliente_por_nombre(nombre):
    # Función para obtener el socket del cliente por su nombre
    for cliente, nombre_cliente in nombres_clientes.items():
        if nombre_cliente.lower() == nombre.lower():
            return cliente
    return None

def enviar_mensaje_privado(comando, cliente_emisor):
    parametros = comando.split()[1:]
    
    if len(parametros) >= 2:
        identificador_destino = parametros[0]
        mensaje = " ".join(parametros[1:])
        
        for cliente_destino, nombre_destino in nombres_clientes.items():
            if nombre_destino.lower() == identificador_destino.lower() and cliente_destino != cliente_emisor:
                mensaje_privado = f"{nombres_clientes[cliente_emisor]} te ha enviado un susurro: {mensaje}"
                enviar_mensaje_servidor(mensaje_privado, cliente_destino)
                enviar_mensaje_servidor(f"[SERVER] susurro enviado a {nombre_destino}.", cliente_emisor)
                return

    # Si no se encuentra el destinatario, informar al emisor
    enviar_mensaje_servidor("[SERVER] No se encontró el usuario especificado o no puedes enviarte un mensaje privado a ti mismo.", cliente_emisor)
#commando q el que lo usa no alcanza a ver el mensaje mejorable
def desconectar_cliente(cliente):
    if cliente in clientes:
        clientes.remove(cliente)
        enviar_mensaje_servidor("[SERVER] Te has desconectado del chat.", cliente)
        cliente.close()
#busca el artefacto por id
def obtener_nombre_artefacto(comando, cliente_emisor):
    parametros = comando.split()[1:]

    if len(parametros) == 1 and parametros[0].isdigit():
        artefactoid = int(parametros[0])
        nombre_artefacto = artefactos_dict.get(str(artefactoid), f"Artefacto Desconocido {artefactoid}")
        mensaje_servidor = f"[SERVER] El artefacto {artefactoid} es: {nombre_artefacto}."
        enviar_mensaje_servidor(mensaje_servidor, cliente_emisor)
    else:
        enviar_mensaje_servidor("[SERVER] Uso incorrecto del comando. Ejemplo: :artefacto 22", cliente_emisor)


def manejar_cliente(client_socket, addr):
    with client_socket:
        try:
            # Establecer el nombre del cliente
            client_socket.send(b"[SERVER] Bienvenid@ al chat de Granjerxs! Por favor, introduce tu nombre:")
            client_name = client_socket.recv(1024).decode().strip()
            #busca duplicado
            if client_name in nombres_clientes:
                enviar_mensaje_servidor("[SERVER] Nombre ya en uso. Desconectando...", client_socket)
                return
            #lista de clientes activos
            nombres_clientes[client_socket] = client_name
            notificar_conexion_cliente(client_socket)
            enviar_mensaje_servidor(f"[SERVER] Cliente {client_name} conectado.", client_socket)
            print(f"[SERVER] {client_name} se ha conectado desde {addr[0]}:{addr[1]}")

            clientes.append(client_socket)

            while True:
                # Preguntar por artefactos al unirse al chat
                mensaje_arte = "[SERVER] Cuéntame, ¿qué artefactos tienes? (Ingresa los números separados por comas, maximo 6)"
                enviar_mensaje_servidor(mensaje_arte, client_socket)

                artefactos_usuario = client_socket.recv(1024).decode().strip().split(',')

                # Verificar si los artefactos son válidos

                if all(num in artefactos_dict for num in artefactos_usuario) and len(artefactos_usuario) <= 6:
                    break
                else:
                    enviar_mensaje_servidor("[SERVER] Al menos un artefacto no es válido. Por favor, inténtalo de nuevo.", client_socket)
            #guarda que artefactos pertenecen al cliente
            artefactos_clientes[client_socket] = artefactos_usuario
            
            descripcion_artefactos = [artefactos_dict.get(num, f"Artefacto Desconocido {num}") for num in artefactos_usuario]

            # Mostrar las descripciones al usuario
            mensaje_servidor = f"[SERVER] Tus artefactos son: {', '.join(descripcion_artefactos)}.\n¿Está bien? (Si/No)"
            enviar_mensaje_servidor(mensaje_servidor, client_socket)

            respuesta_usuario = client_socket.recv(1024).decode().strip().lower()
            #mejoreable hacer un loop en vez de desconectar
            if respuesta_usuario == 'si':
                enviar_mensaje_servidor(f"[SERVER] ¡OK! {client_name}, estás en el chat.", client_socket)
            else:
                enviar_mensaje_servidor(f"[SERVER] {client_name} ha decidido no continuar.", client_socket)
                clientes.remove(client_socket)
            #permite que se pueda usar el chat
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                mensaje = data.decode()
                # Verificar si es un comando
                if mensaje.startswith(":"):
                    comando = mensaje[1:].lower()  # Eliminar el ":" y convertir a minúsculas
                    manejar_comando(comando, client_socket)
                else:
                    mensaje_reenviado = f"{client_name}: {mensaje}"
                    for otro_cliente in clientes:
                        if otro_cliente != client_socket:
                            otro_cliente.send(mensaje_reenviado.encode())
                    print(mensaje_reenviado)
        except Exception as e:
            # Manejar la excepción y eliminar el cliente de la lista
            enviar_mensaje_servidor(f"[SERVER] Cliente {client_name} desconectado.", client_socket)
            if client_socket in clientes:
                clientes.remove(client_socket)

        finally:
            # Cerrar el socket del cliente
            if client_socket in clientes:
                clientes.remove(client_socket)
                client_socket.close()
            print(f"[SERVER] Cliente {client_name} ({addr[0]}:{addr[1]}) desconectado.")
            enviar_mensaje_servidor(f"[SERVER] Cliente {client_name} desconectado.", client_socket)
            notificar_desconexion_cliente(client_socket)

# Escuchar y aceptar conexiones de clientes
while True:
    client_socket, client_addr = server_socket.accept()
    cliente_thread = threading.Thread(target=manejar_cliente, args=(client_socket, client_addr))
    cliente_thread.start()
