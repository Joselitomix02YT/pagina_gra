import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import base64
from io import BytesIO
from flask import Flask, jsonify
import warnings
warnings.filterwarnings('ignore')
import time

app = Flask(__name__)
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False

def encode_image(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', dpi=80)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    return image_base64

def analizar_datos():
    try:
        df = pd.read_csv('grafica.csv')
    except FileNotFoundError:
        raise Exception("Error: No se encontró el archivo grafica.csv")
    except Exception as e:
        raise Exception(f"Error al leer grafica.csv: {str(e)}")
    
    resultado = {}
    
    # Frecuencias absolutas
    freq_abs = df['color'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    colores = {'Blanco': '#E0E0E0', 'Amarillo': '#FFD700', 'Verde': '#90EE90', 'NA': '#CCCCCC'}
    colors_list = [colores.get(x, '#808080') for x in freq_abs.index]
    freq_abs.plot(kind='bar', ax=ax, color=colors_list, edgecolor='black')
    ax.set_title('Frecuencias Absolutas', fontsize=12, fontweight='bold')
    ax.set_xlabel('Color', fontsize=11)
    ax.set_ylabel('Frecuencia', fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=45)
    resultado['grafica_barras'] = encode_image(fig)
    
    # Pastel
    fig, ax = plt.subplots(figsize=(10, 8))
    colors_pie = [colores.get(x, '#808080') for x in freq_abs.index]
    ax.pie(freq_abs, labels=freq_abs.index, autopct='%1.1f%%', colors=colors_pie, startangle=90)
    ax.set_title('Frecuencias Relativas - Pastel', fontsize=12, fontweight='bold')
    resultado['grafica_pastel'] = encode_image(fig)
    
    # Polar
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))
    theta = np.linspace(0, 2*np.pi, len(freq_abs), endpoint=False)
    ax.bar(theta, freq_abs.values, width=0.5, alpha=0.8, color=colors_pie, edgecolor='black')
    ax.set_xticks(theta)
    ax.set_xticklabels(freq_abs.index)
    ax.set_title('Frecuencias Relativas - Polar', fontsize=12, fontweight='bold', pad=20)
    resultado['grafica_polar'] = encode_image(fig)
    
    # Acumulada
    freq_acum = freq_abs.cumsum()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(range(len(freq_acum)), freq_acum.values, alpha=0.7, color='steelblue', edgecolor='black')
    ax.plot(range(len(freq_acum)), freq_acum.values, 'ro-', linewidth=2, markersize=8)
    ax.set_xticks(range(len(freq_acum)))
    ax.set_xticklabels(freq_acum.index, rotation=45)
    ax.set_title('Frecuencias Acumuladas', fontsize=12, fontweight='bold')
    ax.set_xlabel('Color', fontsize=11)
    ax.set_ylabel('Frecuencia Acumulada', fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    resultado['grafica_acumulada'] = encode_image(fig)
    
    # Polígono
    velocidad = df['velocidad'].dropna()
    n_bins = 8
    counts, bins = np.histogram(velocidad, bins=n_bins)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(bin_centers, counts, width=bins[1]-bins[0], alpha=0.6, color='skyblue', edgecolor='black')
    ax.plot(bin_centers, counts, 'ro-', linewidth=2, markersize=8)
    ax.set_title('Polígono de Frecuencias - Velocidad', fontsize=12, fontweight='bold')
    ax.set_xlabel('Velocidad (km/h)', fontsize=11)
    ax.set_ylabel('Frecuencia', fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    resultado['grafica_poligono'] = encode_image(fig)
    
    # Estadísticas
    moda_result = stats.mode(velocidad, keepdims=True)
    moda = moda_result.mode[0] if len(moda_result.mode) > 0 else None
    
    resultado['estadisticas'] = {
        'media': round(float(velocidad.mean()), 2),
        'mediana': round(float(velocidad.median()), 2),
        'moda': round(float(moda), 2) if moda is not None else 'N/A',
        'desv_std': round(float(velocidad.std()), 2),
        'varianza': round(float(velocidad.var()), 2),
        'minimo': round(float(velocidad.min()), 2),
        'maximo': round(float(velocidad.max()), 2),
        'rango': round(float(velocidad.max() - velocidad.min()), 2)
    }
    
    # Tabla
    freq_rel = (freq_abs / len(df) * 100).round(2)
    tabla = []
    for color in freq_abs.index:
        tabla.append({
            'color': color,
            'abs': int(freq_abs[color]),
            'rel': float(freq_rel[color]),
            'acum': int(freq_acum[color]),
            'pct': float((freq_abs[color] / len(df) * 100).round(2))
        })
    
    resultado['tabla'] = tabla
    resultado['total'] = len(df)
    resultado['velocidad_valida'] = len(velocidad)
    
    return resultado

@app.route('/')
def index():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "Error: No se encontró index.html", 404

@app.route('/api/analizar')
def api_analizar():
    try:
        resultado = analizar_datos()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n✅ Abriendo en http://localhost:5000\n")
    app.run(debug=False, port=5000)

    while True:
     time.sleep(3600)
