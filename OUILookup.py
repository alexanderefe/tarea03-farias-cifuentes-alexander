import time
import sys
import requests
import subprocess
import re

#variable global
uri = "https://api.maclookup.app/v2/macs/"

#funciones

def obtener_direcciones_mac():
    try:
        resultado = subprocess.check_output(["arp", "-a"], universal_newlines=True)
        # Utilizamos una expresión regular para buscar direcciones MAC en el resultado
        direcciones_mac = re.findall(r"([0-9a-fA-F]{2}(?:[:-][0-9a-fA-F]{2}){5})", resultado)
        direcciones_mac = [mac.replace('-', ':') for mac in direcciones_mac]
        return direcciones_mac
    except subprocess.CalledProcessError as e:
        return f"Error al obtener la tabla ARP: {e}"

def obtener_direcciones_ip():
    try:
        resultado = subprocess.check_output(["arp", "-a"], universal_newlines=True)
        # Utilizamos una expresión regular para buscar direcciones IP en el resultado
        direcciones_ip = re.findall(r"\d+\.\d+\.\d+\.\d+", resultado)
        return direcciones_ip
    except subprocess.CalledProcessError as e:
        return f"Error al obtener las direcciones IP: {e}"

def obtener_fabricante(macs):
    fabricante = list()
    i = 0
    while i < len(macs):
        respuesta = consultarViaAPIrest(uri + macs[i]).json()
        fabricante.append(respuesta["company"])
        i = i + 1
    
    return fabricante

def consultarViaAPIrest(url): 
    return requests.get(url)

def mostrar_mac_fabricante(mac):
    url_consulta = uri + mac
    start_time = time.time()
    respuesta = consultarViaAPIrest(url_consulta)
    end_time = time.time()
    total_time = end_time-start_time
    if respuesta.status_code == 400 or respuesta.status_code == 429:
        fabricante = "not found"
    elif respuesta.status_code == 200:    
        respuesta = respuesta.json()
        fabricante = respuesta["company"]
        if fabricante == "":
                    fabricante = "not found"


    print("Direccion MAC: " + mac + "\nFabricante: " + fabricante)
    print("el tiempo de la consulta fue de: {} Segundos".format(total_time))


#main
direcciones_mac = obtener_direcciones_mac()
direcciones_ip = obtener_direcciones_ip()


if len(sys.argv) == 1 or sys.argv[1] == "--help":
    print("\npython OUILookup.py --ip <IP> | --mac <IP> | --arp | [--help]\n--ip : IP del host a consultar.\n--mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.\n--arp: muestra los fabricantes de los host disponibles en la tabla arp.\n--help: muestra este mensaje y termina.")

elif sys.argv[1] == "--ip":
    ip_ingresada = sys.argv[2]
    i = 0
    while i < len(direcciones_ip):
        if ip_ingresada != direcciones_ip[i]:
            i = i + 1
            encontrado = 0
        else:
            encontrado = 1
            mostrar_mac_fabricante(direcciones_mac[i])
            i = len(direcciones_ip)

    if encontrado == 0:
        print("Error: ip is outside the host network")
    

elif sys.argv[1] == "--mac":
    mac_ingresada = sys.argv[2]
    mostrar_mac_fabricante(mac_ingresada)


elif sys.argv[1] == "--arp":
    fabricantes = obtener_fabricante(direcciones_mac)
    i = 0
    while i < len(direcciones_mac):
        print(direcciones_ip[i] + " / " + direcciones_mac[i] + " / " + fabricantes[i])
        i = i + 1