import numpy as np
import simpy
import itertools

#! Variables de la simulacion
indiceDemanda = .1 #Tiempo promedio de la demanda de los clientes en meses
tamanioDemanda = [1, 2, 3, 4] #Posibles tamaños de la demanda de clientes en meses
probabilidadDemanda  = [1/6, 1/3, 1/3, 1/6] #Probabilidad de que se solicite dicha demanda
inventarioInicial = 60
costoOrdenSetup = 32
costoItemSetup = 3
costoBacklogItemSetup = 5
costoReservaItemSetup = 1 

class Inventario:

    def __init__(self, env, puntoDePedido, tamanioDePedido):
        self.puntoDePedido = puntoDePedido
        self.tamanioDePedido = tamanioDePedido
        self.inventario = inventarioInicial
        self.ultimoCambio = 0
        self.costoDeOrden = 0
        self.costoDeEscasez = 0
        self.deudas = 0
        self.mant = 0
        self.pasadas=0
        self.costoDeReserva = 0
        
        #! Iniciar los procesos
        env.process(self.RevisionInventario(env))
        env.process(self.Demandas(env))
        
    def CrearOrden(self, env, unidades):
        #Actualiza los costos de orden
        self.costoDeOrden += (costoOrdenSetup + unidades * costoItemSetup)
        
        #Determina cuando sera recibido el pedido 
        tiempoLider = np.random.uniform(.5, 1.0)
        yield env.timeout(tiempoLider)
        
        #Actualiza el inventario y los costos 
        #self.ActualizarCosto(env)
        self.inventario += unidades
        self.ultimoCambio = env.now
        
    def RevisionInventario(self, env):
        while True:
            self.pasadas+=1
            self.ActualizarCosto(env)
            #Crea orden si lo requiere
            if self.inventario <= self.puntoDePedido:
                unidades = (self.tamanioDePedido - self.inventario)
                env.process(self.CrearOrden(env, unidades))

            #Espera al siguiente chequeo
            yield env.timeout(1.0)
            
    def ActualizarCosto(self, env):
        
        #Actualizar costo por escasez
        if self.inventario <= 0:
            costoEscazo = (abs(self.inventario) * costoBacklogItemSetup )
            self.costoDeEscasez += costoEscazo
            self.deudas+=1
        else :
            #Actualizar costo de reserva
            costoReserva = (self.inventario * costoReservaItemSetup )
            self.mant+=1
            self.costoDeReserva += costoReserva
            
    def Demandas(self, env):
        while True:
            #Genera el tamaño y tiempo de la siguiente demanda 
            tiempo = np.random.exponential(indiceDemanda)
            tamanio = np.random.choice(tamanioDemanda, 1, p=probabilidadDemanda)
            yield env.timeout(tiempo)
            #Actualiza el nivel de inventario y costos en funcion de la demanda recibida
            #self.ActualizarCosto(env)
            self.inventario -= tamanio[0]
            self.ultimoCambio = env.now
            

def Ejecutar(largo, puntoDePedido, tamanioDePedido):
    #! Ejecuta el modelo de inventario para un largo dado y retorna los resultados en un diccionario
    
    #Validar ingresos de usuarios
    if largo <= 0:
        raise ValueError("El largo de la simulacion debe ser mayo que cero")
    if tamanioDePedido <= 0:
        raise ValueError("El tamaño del pedido debe ser mayo que cero")
    
    #Configurar la simulacion
    env = simpy.Environment()
    inv = Inventario(env, puntoDePedido, tamanioDePedido)
    env.run(largo)
    print(inv.deudas)
    print(inv.mant)
    #Computa y retorna los resultados
    promedioCostosTotales = (inv.costoDeOrden + inv.costoDeReserva + inv.costoDeEscasez) / largo
    promedioCostosOrden = inv.costoDeOrden / largo
    promedioCostosReserva = inv.costoDeReserva / largo
    promedioCostosEscasez = inv.costoDeEscasez / largo
    resultados = {'Pedido' : puntoDePedido,
                'Tamanio' : tamanioDePedido,
                'CostosTotales' : round(promedioCostosTotales, 1),
                'CostosOrden' : round(promedioCostosOrden, 1),
                'CostosReserva' : round(promedioCostosReserva, 1),
                'CostosEscasez' : round(promedioCostosEscasez, 1)}
    return resultados

def EjecutarVarios(largo, puntosDePedido, tamaniosDePedido, repeticiones):
    #! Ejecuta el modelo para cada combinacion de puntos de pedidos y tamaños de ordenes, y guarda los resultados en un arreglo de diccionarios
    
    #Validar ingresos del usuario
    if repeticiones <= 0:
        raise ValueError("El numero de repeticiones debe ser mayo que cero")
    
    #Inicializa las variables
    largo1 = len(puntosDePedido)
    largo2 = len(tamaniosDePedido)
    contador = 0
    resultados = []
    
    #Itera sobre todos los puntos
    for i,j in itertools.product(puntosDePedido, tamaniosDePedido):
        for k in range(repeticiones):
            contador += 1
            
            #Muestra mensaje a usuario cada 100 repeticiones
            if contador % 100 == 0:
                print('Iteracion ', contador, ' de ', largo1 * largo2 * repeticiones)
            
            #Guarda los resultados
            resultados.append(Ejecutar(largo, i, j))
            print(resultados)
    return resultados



