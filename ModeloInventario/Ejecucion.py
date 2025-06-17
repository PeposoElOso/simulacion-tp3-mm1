import ModeloInventario as modelo
import Graficar as grafico
import GuardarTabla as Tabla
import pandas as pd
import numpy as np


resultados = modelo.EjecutarVarios(120, [60], [100], 1)
limiteInferior, limiteSuperior = Tabla.GenerarIntervaloDeConfianza(resultados)
print("Intervalo mensual de confianza de un 90% para los costos mensuales del inventario: "f"{limiteInferior:.1f}" + " " + f"{limiteSuperior:.1f}")
Tabla.GuardarTabla(resultados)
grafico.GraficarBarras(resultados)



    

