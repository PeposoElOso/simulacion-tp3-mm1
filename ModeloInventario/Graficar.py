import matplotlib.pyplot as plt
import statistics as stats
import os

def SepararEnArreglos(resultados):
    salidas = dict()
    
    for key in resultados[0].keys():
        if key != 'Pedido' and key != 'Tamanio':
            salidas[key] =  salidas.get(key, [])
        
    for key in salidas.keys():
        for i in range(0, len(resultados)):
            salidas[key].append(resultados[i].get(key))
            
    return salidas

def GenerarTitulo(concatena):
    palabra = []
    titulo = ''
    concatena += 'Z'
    for letra in concatena:
        if letra >= 'A' and letra <= 'Z':
            palabra.append(' ')
            titulo = titulo + "".join(palabra)
            palabra.clear()
        palabra.append(letra.upper())
    return titulo 

def GraficarBarrasYGuardar(salidas, version):    
    for key in salidas.keys():
        plt.bar(range(1, len(salidas.get(key))+1), salidas.get(key))
        media = stats.mean(salidas.get(key))
        plt.axhline(y=media, color='r', linestyle='-', label='Media')
        plt.ylabel(GenerarTitulo(key))
        plt.xlabel('NUMERO DE CORRIDA')
        plt.title('COMPARACION DE ' + GenerarTitulo(key))
        plt.savefig('GraficosDeBarras/' + key + str(version) + '.png')
        plt.close()

def GraficarBarras(resultados):
    for file in os.listdir('GraficosDeBarras'): 
        if file.endswith('.png') : os.remove(os.path.join('GraficosDeBarras', file))   

    salidas = SepararEnArreglos(resultados)
    
    GraficarBarrasYGuardar(salidas, '')


def GraficarBarrasVarias(resultados):
    for file in os.listdir('GraficosDeBarras'): 
        if file.endswith('.png') : os.remove(os.path.join('GraficosDeBarras', file))
        
    i = 1
    for resultado in resultados:
        GraficarBarrasYGuardar(resultado, i)
        i += 1

def GraficarCajas(datos):
    for file in os.listdir('GraficosDeCajas'): 
        if file.endswith('.png') : os.remove(os.path.join('GraficosDeCajas', file))
        
    #Crear area
    fig, ax = plt.subplots(dpi = 100)
    ax.set_xticklabels([ '(20, 60)'])
    ax.set_title('Costos promedio de inventario por configuracion')
    ax.set_xlabel('Configuracion (reposicion, tamaño)')
    ax.set_ylabel('Costo promedio mensual')
    
    #Cargar grafico y guardar
    ax.boxplot(datos)
    plt.savefig('GraficosDeCajas/CostosTotales.png')
    plt.close()
    
def GraficarContorno(Xi, Yi, Z):
    plt.figure(dpi=125)
    plt.title('Grafica de contorno')
    plt.xlabel('Punto de reposicion')
    plt.ylabel('Tamaño de pedido')
    
    contornos = plt.contour(Yi, Xi, Z, 10)
    plt.clabel(contornos, inline=True, fmt='%1.0f', fontsize=8)
    plt.grid(color='gray', linestyle='-', linewidth=.15)
    
    plt.savefig('Contorno.png')
    plt.close()