#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para limpiar emojis de todos los archivos Python"""

import os
import re

# Mapeo de emojis a reemplazos en ASCII
REEMPLAZOS = {
    '🚀': '[INIT]',
    '🧠': '[MANAGER]',
    '🖥️': '[UI]',
    '✅': '[OK]',
    '👨‍🌾': '[CAPATAZ]',
    '🔗': '[CONEXION]',
    '🤖': '[AGENTES]',
    '📋': '[INFO]',
    '📦': '[TRABAJO]',
    '⏳': '[ESPERA]',
    '🎬': '[SIMULACION]',
    '🌾': '[CULTIVO]',
    '📊': '[DATOS]',
    '💡': '[TIP]',
    '⚠️': '[ADVERTENCIA]',
    '❌': '[ERROR]',
    '🧪': '[PRUEBA]',
    '🌱': '[PEQUENO]',
    '🌳': '[GRANDE]',
    '🛑': '[DETENER]',
    '⸻': '[LINEA]',
    '👋': '[ADIOS]',
    '📡': '[COMUNICACION]',
    '⭐': '[PRIORIDAD]',
    '🔔': '[CAMPANA]',
    '🚨': '[EMERGENCIA]',
    '📍': '[POSICION]',
    '👥': '[EQUIPO]',
    '📢': '[ANUNCIO]',
    '🔍': '[BUSQUEDA]',
    '🍅': '[FRUTOS]',
    '⏱️': '[TIEMPO]',
    '✖️': '[X]',
    '📈': '[GRAFICO]',
    '🌡️': '[TEMPERATURA]',
    '💧': '[HUMEDAD]',
    '🐛': '[PLAGAS]',
    '🟢': '[VERDE]',
    '🟡': '[AMARILLO]',
    '🔴': '[ROJO]',
    '🟣': '[PURPURA]',
    '🟦': '[AZUL]',
    '⏸️': '[PAUSA]',
    '✔️': '[CHECK]',
    '🎯': '[OBJETIVO]',
    '║': '|',
    '╔': '+',
    '╗': '+',
    '╚': '+',
    '═': '=',
    '─': '-',
    '├': '|',
    '┤': '|',
    '┬': '+',
    '┴': '+',
}

def limpiar_archivo(filepath):
    """Limpia emojis de un archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        contenido_original = contenido
        
        # Reemplazar emojis
        for emoji, reemplazo in REEMPLAZOS.items():
            contenido = contenido.replace(emoji, reemplazo)
        
        # Reemplazar caracteres acentuados problemáticos
        acentos = {
            'ó': 'o',
            'á': 'a',
            'é': 'e',
            'í': 'i',
            'ü': 'u',
            'ñ': 'n',
            'Ó': 'O',
            'Á': 'A',
            'É': 'E',
            'Í': 'I',
            'Ü': 'U',
            'Ñ': 'N',
        }
        
        for original, reemplazo in acentos.items():
            contenido = contenido.replace(original, reemplazo)
        
        # Si hay cambios, guardar
        if contenido != contenido_original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(contenido)
            print(f"[OK] {filepath}")
            return True
        else:
            print(f"[SIN CAMBIOS] {filepath}")
            return False
    
    except Exception as e:
        print(f"[ERROR] {filepath}: {e}")
        return False

# Archivos a limpiar
archivos = [
    'main.py',
    'manager.py',
    'capataz.py',
    'fisico.py',
    'ui.py'
]

print("\n[INICIO] Limpiando emojis y acentos de archivos Python...\n")

cambios = 0
for archivo in archivos:
    if os.path.exists(archivo):
        if limpiar_archivo(archivo):
            cambios += 1

print(f"\n[FIN] Se modificaron {cambios} archivo(s)\n")
