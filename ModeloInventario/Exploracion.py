import ModeloInventario as modelo
import Graficar as grafico
import GuardarTabla as Tabla
import numpy as np

#Inicializo las variables
meses = 12
replicas = 1
reposicion = np.arange(0, 105, 5)
tamanios = np.arange(5, 105, 5)

#Ejecuto y obtengo datos
resultados = modelo.EjecutarVarios(meses, reposicion, tamanios, replicas)

#Cargo Datos
X, Y, Z = Tabla.CargarData(resultados)

#Grafico
Xi, Yi = np.meshgrid(X, Y)
grafico.GraficarContorno(Xi, Yi, Z)



