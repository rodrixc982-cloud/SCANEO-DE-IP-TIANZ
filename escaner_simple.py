#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IPTianz Scanner - Escáner de red profesional
Creado por Rodrixc Tianz
Versión 3.0 - Interfaz moderna con efectos visuales
"""

import os
import sys
import socket
import subprocess
import ipaddress
import threading
import time
import platform
import re
from datetime import datetime
import random

# Importar tkinter y extensiones
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    from tkinter.font import Font
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    print("Error: tkinter no está disponible.")

# Intentar importar PIL para imágenes (opcional)
try:
    from PIL import Image, ImageTk, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ------------------------- CONFIGURACIÓN -------------------------
# Puertos según tipo de dispositivo
PUERTOS_PUNTO_RED = [80, 443, 8080, 8000, 8443]
PUERTOS_SWITCH = [22, 23, 80, 443, 161, 162]
PUERTOS_CAMARA = [80, 443, 554, 8000, 8080, 37777, 8554]
PUERTOS_GATEWAY = [53, 67, 68, 80, 443, 1900]
PUERTOS_WIFI = [80, 443, 8080, 22, 23]
PUERTOS_OTROS = [21, 22, 23, 25, 80, 443, 445, 3389]

# Base de datos OUI (fabricantes)
OUI_DATABASE = {
    "00:1C:42": "Hikvision", "00:1F:54": "Dahua", "00:12:3F": "Bosch",
    "00:0C:43": "Samsung", "00:0F:5B": "LG", "00:14:22": "Sony",
    "00:17:61": "Panasonic", "00:1E:4C": "Axis", "00:40:8C": "Honeywell",
    "00:50:C2": "Mobotix", "00:60:9F": "Arecont", "00:90:2B": "Vivotek",
    "00:A0:3E": "Pelco", "00:B0:D0": "Cisco", "00:14:BF": "TP-Link",
    "00:1A:2B": "D-Link", "00:1C:F0": "Netgear", "00:1D:7E": "Ubiquiti",
    "00:24:A5": "MikroTik", "00:26:5E": "Intel", "00:50:56": "VMware",
    "00:0C:29": "VMware", "00:05:69": "HP", "00:21:5A": "Dell",
    "00:23:AE": "Apple", "00:1E:52": "Apple", "F4:5C:89": "TP-Link",
    "CC:2D:E0": "Cisco", "3C:2E:FF": "Ubiquiti", "18:68:CB": "MikroTik",
    "E0:63:DA": "Hikvision", "44:19:B6": "Dahua",
}

# Colores modernos
COLOR_FONDO = "#1e1e2e"        # Azul oscuro grisáceo
COLOR_FONDO2 = "#2d2d3f"       # Un tono más claro
COLOR_TEXTO = "#ffffff"
COLOR_HEADER = "#0a0a14"       # Casi negro
COLOR_BOTON = "#3b3b5c"
COLOR_BOTON_HOVER = "#5a5a7a"
COLOR_ENTRY = "#2d2d3f"
COLOR_TABLA_PAR = "#2a2a3c"
COLOR_TABLA_IMPAR = "#1f1f2e"
COLOR_SELECCION = "#4a4a6a"
COLOR_PROGRESO = "#6d6d8a"
COLOR_ACENTO = "#a6e3a1"       # Verde suave

# ------------------------------------------------------------------

class SplashScreen:
    """Pantalla de bienvenida con animación."""
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)  # Sin bordes
        self.window.attributes('-alpha', 0.0)  # Inicialmente transparente
        
        # Tamaño y posición
        ancho, alto = 600, 400
        x = (self.window.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.window.winfo_screenheight() // 2) - (alto // 2)
        self.window.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        # Canvas para fondo degradado
        self.canvas = tk.Canvas(self.window, width=ancho, height=alto, highlightthickness=0)
        self.canvas.pack()
        
        # Crear gradiente
        self.dibujar_gradiente(ancho, alto, "#0f0f1f", "#2a2a4a")
        
        # Texto principal animado
        self.texto_id = self.canvas.create_text(ancho//2, alto//2 - 40, text="IPTianz", 
                                                fill="white", font=("Helvetica", 48, "bold"))
        # Subtítulo
        self.canvas.create_text(ancho//2, alto//2 + 20, text="Escáner de Red Profesional",
                                fill="#a6e3a1", font=("Helvetica", 18))
        # Créditos
        self.canvas.create_text(ancho//2, alto - 60, text="Creado por Rodrixc Tianz",
                                fill="#cccccc", font=("Helvetica", 12, "italic"))
        
        # Animación de aparición
        self.fade_in()
        
        # Desaparecer después de 3 segundos
        self.window.after(3000, self.fade_out)
    
    def dibujar_gradiente(self, ancho, alto, color1, color2):
        """Dibuja un degradado vertical."""
        rgb1 = self.hex_to_rgb(color1)
        rgb2 = self.hex_to_rgb(color2)
        for i in range(alto):
            r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * i / alto)
            g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * i / alto)
            b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * i / alto)
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, ancho, i, fill=color, width=1)
    
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def fade_in(self):
        alpha = self.window.attributes('-alpha')
        if alpha < 1.0:
            alpha += 0.05
            self.window.attributes('-alpha', alpha)
            self.window.after(30, self.fade_in)
    
    def fade_out(self):
        alpha = self.window.attributes('-alpha')
        if alpha > 0:
            alpha -= 0.05
            self.window.attributes('-alpha', alpha)
            self.window.after(30, self.fade_out)
        else:
            self.window.destroy()
            if self.callback:
                self.callback()


class ModernButton(tk.Canvas):
    """Botón moderno con efecto hover y relieve plano."""
    def __init__(self, master, text, command=None, width=150, height=40, 
                 bg=COLOR_BOTON, fg=COLOR_TEXTO, font=("Arial", 11, "bold")):
        super().__init__(master, width=width, height=height, highlightthickness=0, bg=COLOR_FONDO)
        self.command = command
        self.text = text
        self.bg = bg
        self.fg = fg
        self.font = font
        self.width = width
        self.height = height
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
        self.draw_button(bg)
    
    def draw_button(self, color):
        self.delete("all")
        # Sombra
        self.create_rectangle(2, 2, self.width, self.height, fill="#000000", outline="", tags="sombra")
        # Fondo
        self.create_rectangle(0, 0, self.width-2, self.height-2, fill=color, outline="", tags="fondo")
        # Texto
        self.create_text(self.width//2 - 2, self.height//2 - 2, text=self.text, fill=self.fg, 
                         font=self.font, tags="texto")
    
    def on_enter(self, event):
        self.draw_button(COLOR_BOTON_HOVER)
    
    def on_leave(self, event):
        self.draw_button(self.bg)
    
    def on_click(self, event):
        if self.command:
            self.command()


class IPTianzScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("IPTianz Scanner")
        self.root.geometry("1300x750")
        self.root.configure(bg=COLOR_FONDO)
        
        # Centrar ventana
        self.centrar_ventana()
        
        # Variables
        self.escanenado = False
        self.red_objetivo = tk.StringVar(value="Detectando...")
        self.tipo_escaneo = tk.StringVar(value="cámara")  # por defecto
        self.puertos_seleccionados = PUERTOS_CAMARA
        
        # Configurar estilos
        self.configurar_estilos()
        
        # Mostrar splash screen primero
        self.splash = SplashScreen(self.root, self.iniciar_interfaz)
        
        # La interfaz se construirá después del splash, pero podemos dejarla oculta
        self.frame_contenido = ttk.Frame(self.root)
        # No empaquetamos aún, lo haremos en iniciar_interfaz
    
    def centrar_ventana(self):
        self.root.update_idletasks()
        ancho = self.root.winfo_width()
        alto = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores para ttk widgets
        style.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO, font=("Arial", 10))
        style.configure("TFrame", background=COLOR_FONDO)
        style.configure("TEntry", fieldbackground=COLOR_ENTRY, foreground=COLOR_TEXTO, 
                        borderwidth=0, relief="flat")
        style.map("TEntry", fieldbackground=[("focus", COLOR_ENTRY)])
        
        # Treeview
        style.configure("Treeview", background=COLOR_TABLA_PAR, foreground=COLOR_TEXTO, 
                        fieldbackground=COLOR_TABLA_PAR, borderwidth=0, rowheight=25)
        style.map("Treeview", background=[("selected", COLOR_SELECCION)])
        style.configure("Treeview.Heading", background=COLOR_HEADER, foreground=COLOR_TEXTO, 
                        font=("Arial", 10, "bold"), borderwidth=0)
        style.map("Treeview.Heading", background=[("active", COLOR_BOTON_HOVER)])
        
        # Scrollbar
        style.configure("TScrollbar", background=COLOR_BOTON, troughcolor=COLOR_FONDO, 
                        arrowcolor=COLOR_TEXTO, borderwidth=0)
    
    def iniciar_interfaz(self):
        """Construye la interfaz principal después del splash."""
        self.frame_contenido = ttk.Frame(self.root)
        self.frame_contenido.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cabecera con título y créditos
        self.crear_cabecera()
        
        # Panel de control superior
        self.crear_panel_control()
        
        # Área de resultados
        self.crear_tabla_resultados()
        
        # Barra de estado
        self.crear_barra_estado()
    
    def crear_cabecera(self):
        frame_cab = ttk.Frame(self.frame_contenido)
        frame_cab.pack(fill=tk.X, pady=(0, 10))
        
        # Título grande
        lbl_titulo = ttk.Label(frame_cab, text="IPTianz Scanner", font=("Helvetica", 24, "bold"))
        lbl_titulo.pack(side=tk.LEFT)
        
        # Créditos
        lbl_creditos = ttk.Label(frame_cab, text="Creado por Rodrixc Tianz", 
                                  font=("Arial", 10, "italic"), foreground="#a6e3a1")
        lbl_creditos.pack(side=tk.RIGHT, padx=10)
    
    def crear_panel_control(self):
        frame_control = ttk.Frame(self.frame_contenido)
        frame_control.pack(fill=tk.X, pady=5)
        
        # Red objetivo
        ttk.Label(frame_control, text="Red a escanear:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_red = ttk.Entry(frame_control, textvariable=self.red_objetivo, width=20)
        self.entry_red.grid(row=0, column=1, padx=5, pady=5)
        
        # Botón detectar red
        btn_detectar = ModernButton(frame_control, text="🔄 Detectar", command=self.detectar_red_auto,
                                     width=100, height=30, bg=COLOR_BOTON, fg=COLOR_TEXTO)
        btn_detectar.grid(row=0, column=2, padx=5, pady=5)
        
        # Menú de tipo de escaneo
        ttk.Label(frame_control, text="Tipo de dispositivo:").grid(row=0, column=3, padx=20, pady=5, sticky=tk.W)
        
        # Frame para botones de tipo
        frame_tipos = ttk.Frame(frame_control)
        frame_tipos.grid(row=0, column=4, columnspan=6, padx=5, pady=5)
        
        tipos = [
            ("📡 Punto red", "punto_red", PUERTOS_PUNTO_RED),
            ("🔄 Switch", "switch", PUERTOS_SWITCH),
            ("📷 Cámara", "camara", PUERTOS_CAMARA),
            ("🌐 Gateway", "gateway", PUERTOS_GATEWAY),
            ("📶 WiFi", "wifi", PUERTOS_WIFI),
            ("⚙️ Otros", "otros", PUERTOS_OTROS),
        ]
        
        for i, (text, key, puertos) in enumerate(tipos):
            btn = ModernButton(frame_tipos, text=text, 
                               command=lambda k=key, p=puertos: self.seleccionar_tipo(k, p),
                               width=100, height=30, bg=COLOR_BOTON, fg=COLOR_TEXTO)
            btn.grid(row=0, column=i, padx=3)
        
        # Botón escanear
        self.btn_escanear = ModernButton(frame_control, text="🔍 ESCANEAR", 
                                          command=self.iniciar_escaneo,
                                          width=150, height=40, bg=COLOR_ACENTO, fg="#000000")
        self.btn_escanear.grid(row=0, column=10, padx=20, pady=5)
    
    def seleccionar_tipo(self, key, puertos):
        self.tipo_escaneo.set(key)
        self.puertos_seleccionados = puertos
        # Opcional: cambiar color del botón seleccionado (no implementado por simplicidad)
    
    def crear_tabla_resultados(self):
        frame_tabla = ttk.Frame(self.frame_contenido)
        frame_tabla.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview
        self.tree = ttk.Treeview(frame_tabla, columns=("IP", "MAC", "Fabricante", "Puertos", "Tipo"), 
                                  show="headings", height=20)
        self.tree.heading("IP", text="Dirección IP")
        self.tree.heading("MAC", text="Dirección MAC")
        self.tree.heading("Fabricante", text="Fabricante")
        self.tree.heading("Puertos", text="Puertos abiertos")
        self.tree.heading("Tipo", text="Tipo dispositivo")
        
        self.tree.column("IP", width=140, anchor=tk.W)
        self.tree.column("MAC", width=150, anchor=tk.W)
        self.tree.column("Fabricante", width=200, anchor=tk.W)
        self.tree.column("Puertos", width=150, anchor=tk.CENTER)
        self.tree.column("Tipo", width=200, anchor=tk.W)
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frame_tabla, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)
        
        # Alternar colores de filas
        self.tree.tag_configure('par', background=COLOR_TABLA_PAR)
        self.tree.tag_configure('impar', background=COLOR_TABLA_IMPAR)
    
    def crear_barra_estado(self):
        frame_estado = ttk.Frame(self.frame_contenido)
        frame_estado.pack(fill=tk.X, pady=(5,0))
        
        self.lbl_estado = ttk.Label(frame_estado, text="Listo", foreground=COLOR_ACENTO)
        self.lbl_estado.pack(side=tk.LEFT)
        
        # Barra de progreso (inicialmente invisible)
        self.progreso = ttk.Progressbar(frame_estado, mode='indeterminate', length=200)
        self.progreso.pack(side=tk.RIGHT, padx=10)
        self.progreso.pack_forget()  # ocultar
    
    # ---------- Funciones de escaneo (similar a versiones anteriores) ----------
    def detectar_red_auto(self):
        """Detecta la red local y actualiza entry."""
        self.lbl_estado.config(text="Detectando red...")
        self.root.update()
        red = self.obtener_red_local()
        self.red_objetivo.set(red)
        self.lbl_estado.config(text="Red detectada")
    
    def obtener_red_local(self):
        """Detecta la red local."""
        sistema = platform.system()
        try:
            if sistema == "Windows":
                output = subprocess.check_output("ipconfig", shell=True, text=True, stderr=subprocess.DEVNULL)
                lines = output.splitlines()
                ip = None
                mascara = None
                for i, line in enumerate(lines):
                    lower = line.lower()
                    if any(x in lower for x in ['ipv4', 'dirección ipv4', 'ipv4 address']):
                        partes = line.split(':')
                        if len(partes) >= 2:
                            ip = partes[1].strip()
                    if any(x in lower for x in ['máscara de subred', 'subred', 'subnet mask']):
                        partes = line.split(':')
                        if len(partes) >= 2:
                            mascara = partes[1].strip()
                    if ip and mascara:
                        break
                if ip and mascara:
                    red = ipaddress.IPv4Network(f"{ip}/{mascara}", strict=False)
                    return str(red)
                else:
                    # Fallback
                    hostname = socket.gethostname()
                    ip_local = socket.gethostbyname(hostname)
                    if ip_local.startswith('127.'):
                        output = subprocess.check_output("ipconfig", shell=True, text=True)
                        for line in output.splitlines():
                            if "IPv4" in line or "Dirección IPv4" in line:
                                partes = line.split(':')
                                if len(partes) >= 2:
                                    ip_local = partes[1].strip()
                                    if not ip_local.startswith('127.'):
                                        break
                    partes = ip_local.split('.')
                    return f"{partes[0]}.{partes[1]}.{partes[2]}.0/24"
            else:
                # Linux/macOS
                output = subprocess.check_output("ip -4 addr show", shell=True, text=True, stderr=subprocess.DEVNULL)
                for line in output.splitlines():
                    if "inet" in line and not "127.0.0.1" in line:
                        partes = line.strip().split()
                        for p in partes:
                            if '/' in p:
                                return p
                # Fallback
                output = subprocess.check_output("ifconfig", shell=True, text=True, stderr=subprocess.DEVNULL)
                for line in output.splitlines():
                    if 'inet ' in line and 'broadcast' in line:
                        match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', line)
                        if match:
                            ip = match.group(1)
                            partes = ip.split('.')
                            return f"{partes[0]}.{partes[1]}.{partes[2]}.0/24"
        except:
            pass
        return "192.168.1.0/24"
    
    def iniciar_escaneo(self):
        if self.escanenado:
            messagebox.showwarning("Atención", "Ya hay un escaneo en progreso")
            return
        red = self.red_objetivo.get().strip()
        if not red:
            messagebox.showerror("Error", "Debes especificar una red")
            return
        try:
            ipaddress.IPv4Network(red, strict=False)
        except:
            messagebox.showerror("Error", "Formato de red inválido. Ej: 192.168.1.0/24")
            return
        
        # Limpiar tabla
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        self.escanenado = True
        self.btn_escanear.config(state=tk.DISABLED)
        self.lbl_estado.config(text="Escaneando...")
        self.progreso.pack(side=tk.RIGHT, padx=10)
        self.progreso.start(10)
        
        # Ejecutar escaneo en hilo
        thread = threading.Thread(target=self.ejecutar_escaneo, args=(red,))
        thread.daemon = True
        thread.start()
    
    def ejecutar_escaneo(self, red):
        try:
            ips_activas = self.escanear_ips(red)
            if not ips_activas:
                self.root.after(0, lambda: self.lbl_estado.config(text="No se encontraron dispositivos"))
                return
            
            time.sleep(1)  # espera ARP
            for ip in ips_activas:
                mac = self.obtener_mac(ip)
                fabricante = self.obtener_fabricante(mac) if mac else "Desconocido"
                puertos = self.escanear_puertos(ip, self.puertos_seleccionados)
                tipo = self.detectar_tipo(ip, puertos)
                self.root.after(0, lambda ip=ip, mac=mac, fab=fabricante, pts=puertos, tip=tipo:
                               self.insertar_fila(ip, mac, fab, pts, tip))
            self.root.after(0, lambda: self.lbl_estado.config(text="Escaneo completado"))
        except Exception as e:
            self.root.after(0, lambda: self.lbl_estado.config(text=f"Error: {str(e)}"))
        finally:
            self.root.after(0, self.finalizar_escaneo)
    
    def finalizar_escaneo(self):
        self.progreso.stop()
        self.progreso.pack_forget()
        self.btn_escanear.config(state=tk.NORMAL)
        self.escanenado = False
    
    def insertar_fila(self, ip, mac, fabricante, puertos, tipo):
        puertos_str = ', '.join(str(p) for p in puertos) if puertos else "Ninguno"
        # Alternar colores
        items = self.tree.get_children()
        tag = 'par' if len(items) % 2 == 0 else 'impar'
        self.tree.insert("", tk.END, values=(ip, mac or "No disponible", fabricante, puertos_str, tipo), tags=(tag,))
    
    # Funciones de escaneo (ping, ARP, puertos) similares a versiones anteriores
    def escanear_ips(self, red):
        # (mismo código que antes)
        red_obj = ipaddress.IPv4Network(red, strict=False)
        ips_activas = []
        hilos = []
        lock = threading.Lock()
        def ping_ip(ip):
            sistema = platform.system()
            params = "-n 1 -w 1000" if sistema == "Windows" else "-c 1 -W 1"
            cmd = f"ping {params} {ip}"
            try:
                res = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if res.returncode == 0:
                    with lock:
                        ips_activas.append(ip)
            except:
                pass
        for ip in red_obj.hosts():
            h = threading.Thread(target=ping_ip, args=(str(ip),))
            h.start()
            hilos.append(h)
            if len(hilos) >= 100:
                for hh in hilos:
                    hh.join()
                hilos = []
        for h in hilos:
            h.join()
        return ips_activas
    
    def obtener_mac(self, ip):
        sistema = platform.system()
        try:
            if sistema == "Windows":
                out = subprocess.check_output(f"arp -a {ip}", shell=True, text=True, stderr=subprocess.DEVNULL)
                for line in out.splitlines():
                    if ip in line:
                        parts = line.split()
                        for p in parts:
                            if '-' in p and len(p) == 17:
                                return p.replace('-', ':').upper()
            else:
                if os.path.exists('/proc/net/arp'):
                    with open('/proc/net/arp', 'r') as f:
                        for line in f:
                            if ip in line:
                                parts = line.split()
                                if len(parts) >= 4:
                                    mac = parts[3]
                                    if mac != "00:00:00:00:00:00":
                                        return mac.upper()
                else:
                    out = subprocess.check_output(f"arp -n {ip}", shell=True, text=True, stderr=subprocess.DEVNULL)
                    for line in out.splitlines():
                        if ip in line:
                            parts = line.split()
                            for p in parts:
                                if ':' in p and len(p) == 17:
                                    return p.upper()
        except:
            pass
        return None
    
    def obtener_fabricante(self, mac):
        if not mac or len(mac) < 8:
            return "Desconocido"
        oui = mac.replace(':', '')[:6].upper()
        oui_form = ':'.join(oui[i:i+2] for i in range(0,6,2))
        for key, val in OUI_DATABASE.items():
            if key.replace(':', '').upper() == oui or key.upper() == oui_form:
                return val
        return f"{oui_form} (OUI desconocido)"
    
    def escanear_puertos(self, ip, puertos):
        abiertos = []
        lock = threading.Lock()
        hilos = []
        def revisar(p):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                if sock.connect_ex((ip, p)) == 0:
                    with lock:
                        abiertos.append(p)
            except:
                pass
            finally:
                sock.close()
        for p in puertos:
            h = threading.Thread(target=revisar, args=(p,))
            h.start()
            hilos.append(h)
        for h in hilos:
            h.join()
        return abiertos
    
    def detectar_tipo(self, ip, puertos):
        if 80 in puertos or 443 in puertos:
            return "Servidor Web / Cámara"
        if 554 in puertos:
            return "Cámara RTSP"
        if 37777 in puertos:
            return "DVR Dahua/Hikvision"
        if 8080 in puertos:
            return "Posible cámara/web"
        if 22 in puertos:
            return "SSH (switch/router)"
        if 23 in puertos:
            return "Telnet (switch/router)"
        return "Dispositivo genérico"


def main():
    if not TKINTER_AVAILABLE:
        print("tkinter no está disponible.")
        sys.exit(1)
    
    # Verificar permisos
    if platform.system() == "Windows":
        try:
            subprocess.run("arp -a", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            print("ADVERTENCIA: No se tienen permisos de administrador. Algunas funciones pueden fallar.")
    else:
        if os.geteuid() != 0:
            print("ADVERTENCIA: No se ejecuta como root.")
    
    root = tk.Tk()
    root.configure(bg=COLOR_FONDO)
    app = IPTianzScanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()