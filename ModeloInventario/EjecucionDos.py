import ModeloInventario as modelo
import Graficar as grafico
import GuardarTabla as Tabla
import numpy as np

#Corro la primer configuracion
resultado = modelo.EjecutarVarios(120, [20], [60], 30)
configuracion1 = grafico.SepararEnArreglos(resultado)

#Corro la segunda configuracion
resultado = modelo.EjecutarVarios(120, [60], [80], 30) 
configuracion2 = grafico.SepararEnArreglos(resultado)

grafico.GraficarBarrasVarias([configuracion1, configuracion2])

promedioCfg1= np.mean(configuracion1['CostosTotales'])
promedioCfg2= np.mean(configuracion2['CostosTotales'])

print('Promedio de costo mensual para (20, 60): ', round(promedioCfg1, 2))
print('Promedio de costo mensual para (60, 80): ', round(promedioCfg2, 2))

grafico.GraficarCajas(configuracion1['CostosTotales'])

#Extraigo los datos para calcular
data = [m - n for m,n in zip(configuracion1['CostosTotales'], configuracion2['CostosTotales'])]

#Obtengo la media y la desviacion
media = np.mean(data)
std = np.std(data, ddof=1)

#Computo las estadisticas
tstat = Tabla.ComputarDatos(len(data))

#Computo el intervalo
limiteInferior, limiteSuperior = Tabla.ComputarIntervalo(tstat, media, std, len(data))

#Muestro resultado
print("Intervalo mensual de confianza de un 90% para los costos mensuales del inventario: "f"{limiteInferior:.1f}" + " " + f"{limiteSuperior:.1f}")
