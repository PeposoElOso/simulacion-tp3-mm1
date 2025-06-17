import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
from scipy import stats


def ComputarDatos(cantDatos):
    alpha = 1 - .9
    tstat = stats.t.ppf(1-alpha/2, cantDatos - 1)
    return tstat

def ComputarIntervalo(tstat, media, desviacion, cantDatos):
    margenDeError = tstat * desviacion / np.sqrt(cantDatos)
    limiteInferior = media - margenDeError
    limiteSuperior = media + margenDeError
    return limiteInferior, limiteSuperior

def GenerarIntervaloDeConfianza(resultados):
    df = pd.DataFrame(resultados)
    media = df['CostosTotales'].mean()
    desviacionEstandar = df['CostosTotales'].std()
    
    tstat = ComputarDatos(len(resultados))
    limiteInferior, limiteSuperior = ComputarIntervalo(tstat, media, desviacionEstandar, len(resultados))
    
    return limiteInferior, limiteSuperior

def GuardarTabla(resultados):  
    archivo = open('TablaDe' + str(len(resultados)) + 'Corridas.txt', 'w')
    df = pd.DataFrame(resultados)
    latexTable = df.style.to_latex()
    texto = latexTable.split('\n')
    for linea in texto:
        archivo.write(linea)
        archivo.write('\n')
    archivo.close()
    
def CargarData(resultados):
    df = pd.DataFrame(resultados)
    
    #Selecciono las columnas relevantes
    data = df[['Tamanio', 'Pedido', 'CostosTotales']]

    #Para cada combinacion de tamaño y reposicion, computamos el costo correspondiente
    data = data.groupby(['Pedido', 'Tamanio']).mean()

    #Reseteamos los datos y renombramos las columnas
    data.reset_index(inplace = True)
    data.columns = ['Pedido', 'Tamanio', 'CostosTotales']
    data = data.pivot(index='Pedido', columns='Tamanio', values='CostosTotales')
   
    #Mapeamos
    #X = data.columns.nlevels[1].values #Tamaños de orden
    X = data.columns.values #Tamaños de orden
    Y = data.index.values #Puntos de reposicion
    Z = data.values #Promedios de costos
    return X, Y, Z