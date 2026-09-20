# -*- coding: utf-8 -*-
from flask import Flask, render_template,request,redirect,url_for,session,flash # For flask implementation
from flask_wtf.csrf import CSRFProtect
from bson import ObjectId # For ObjectId to work
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

STAGE_MATCH = "$match"
STAGE_PROJECT = "$project"
STAGE_UNWIND = "$unwind"
FIELD_PRODUCTOS = '$Productos'

MSG_REGISTRO_EXITOSO = "Registrado con exito"
MSG_UPDATE_EXITOSO = "Update con exito"
RUTA_MOSTRAR_PRODUCTOS_NEG = "/mostrarProdsNeg/"
RUTA_LOGIN_NEG = "/loginNeg"
RUTA_MOSTRAR_PEDIDOS_DISP = "/mostrarPedidosDisp/"


app = Flask(__name__)
#parametro 
app.secret_key=os.environ['SECRET_KEY']
csrf = CSRFProtect()
csrf.init_app(app)
titulo = "PROYECTO"
encabezado = " Iniciar Sesion "

conex = MongoClient("mongodb://127.0.0.1:27017") #host uri
bd = conex.Prueba_Proyecto_Final   #Select the database
clientes = bd.clientes #Select the collection name
negocios=bd.negocios
repartidores=bd.repartidores
pedidos=bd.pedidos   
contador=bd.contador  
DicProductos = {}

@app.route("/",methods=['GET','POST']) #get para mandar 
def login ():

    if request.method =='POST':
        id_cliente=request.values.get("ci_usuario")
        id_cliente=int(id_cliente)
        passw=request.values.get("contra_usuario")
        cliente=clientes.find({"_id":id_cliente})
        lista_cliente=list(cliente)
        #print(len(lista_cliente))
        if len(lista_cliente)!= 0:
            cliente=clientes.find({"_id":id_cliente})
            if(cliente[0]["_id"]==id_cliente and cliente[0]["contraCli"]==passw): #validaciones
                return redirect("/mostrarCats/"+format(id_cliente))
            else:
                return redirect("/") #que vuelva a pedir que se registre pero con una advertencia de que el usuario o contrasenia que ingreso no existen
        else:
            return redirect("/")
    return render_template("IniciarSesion.html")

@app.route("/mostrarCats/<id_cliente>/", methods=['GET','POST'])
def mostrar_categorias(id_cliente):
    id_cliente=int(id_cliente)
    cliente_l=clientes.find({"_id":id_cliente})
    #print("Id: ",cliente_l[0]["_id"]," pass:",cliente_l[0]["contraCli"])
    return render_template("Categorias.html",cliente=cliente_l)

@app.route("/datosCliente/<id_cliente>/", methods=['GET','POST'])
def datos_cliente(id_cliente):
    id_cliente=int(id_cliente)
    cliente_l=clientes.find({"_id":id_cliente})
    print("Id: ",cliente_l[0]["_id"]," pass:",cliente_l[0]["contraCli"])
    return render_template("DatosCliente.html",cliente=cliente_l)

@app.route("/mostrarNegs/<id_cliente>/",methods=['GET','POST']) #get para mandar 
@app.route("/mostrarNegs/<id_cliente>/<categoria>/",methods=['GET','POST']) #get para mandar 
def mostrar_negocios(id_cliente,categoria=None):
    DicProductos.clear()
    #print("Id: ",id)
    id_cliente=int(id_cliente)
    cliente_l=clientes.find({"_id":id_cliente})
    if(categoria != None):
        negocios_l=negocios.find({"Categoria":categoria})
    else:
        negocios_l=negocios.find()
    #print("Id: ",cliente_l[0]["_id"]," pass:",cliente_l[0]["contraCli"])
    return render_template("negocios.html",cliente=cliente_l,negocios=negocios_l,categoria=categoria)

@app.route("/buscar/<id_cliente>/",methods=['GET','POST'])
#@app.route("/buscar/<id>/<categoria>/",methods=['GET','POST'])
def buscar (id_cliente):    
    id_cliente=int(id_cliente)
    criterio=request.values.get("search")
    categoria=request.values.get("categoria")
    cliente=clientes.find({"_id":id_cliente})
    if(categoria != None):
        negocios_l=negocios.find({"Nombre":criterio,"Categoria":categoria})
    else:
        negocios_l=negocios.find({"Nombre":criterio})
    return render_template("negocios.html",cliente=cliente,negocios=negocios_l,categoria=categoria)

############################# PARTE MIA JUAN PABLO ############################


@app.route("/mostrarProds/<id_cliente>/<float:id_negocio>/",methods=['GET','POST'])
def mostrar_productos (id_cliente,id_negocio):  

    id_cliente=int(id_cliente)
    id_negocio = float(id_negocio)
    cliente_p=clientes.find({"_id":id_cliente})
    negocio_p=negocios.find({"_id":id_negocio})
    pipeline = [{STAGE_MATCH:{"_id":id_negocio}},{STAGE_UNWIND:FIELD_PRODUCTOS},{STAGE_MATCH:{"Productos.Estado":"Disponible"}},{STAGE_PROJECT:{"_id":0,"Productos":1}}]  
    productos_p=list(negocios.aggregate(pipeline))
    return render_template("Productos.html",cliente=cliente_p,negocio=negocio_p,productos=productos_p)

def validar_producto(estado):
    if (estado == "No Disponible"):
        return False
    else:
        return True

                       
def sumar_cantidad(id_producto, cantidad):
    DicProductos[id_producto][0] += cantidad

def buscar_datos_producto(id_negocio, id_producto):
    pipeline = [
        {STAGE_MATCH: {"_id": id_negocio}},
        {STAGE_UNWIND: FIELD_PRODUCTOS},
        {STAGE_MATCH: {"Productos.codProd": id_producto}},
        {STAGE_PROJECT: {"_id": 0, "NombreProd": "$Productos.Nombre", "Precio": "$Productos.Precio"}},
    ]
    resultados = list(negocios.aggregate(pipeline))
    if not resultados:
        return None, None
    return resultados[0]["NombreProd"], resultados[0]["Precio"]

def registrar_producto_nuevo(id_negocio, id_producto, cantidad):
    nombre, precio = buscar_datos_producto(id_negocio, id_producto)
    DicProductos[id_producto] = [cantidad, precio, nombre]

def procesar_incremento(id_producto, id_negocio, cantidad, estado):
    if not validar_producto(estado):
        return
    if id_producto in DicProductos:
        sumar_cantidad(id_producto, cantidad)
        return
    registrar_producto_nuevo(id_negocio, id_producto, cantidad)

def procesar_decremento(id_producto, cantidad):
    if id_producto not in DicProductos:
        return
    if DicProductos[id_producto][0] > 1:
        sumar_cantidad(id_producto, cantidad)
    else:
        DicProductos.pop(id_producto)

@app.route("/AgregarProd/<id_cliente>/<float:id_negocio>/<float:id_producto>/<cantidad>/<estado>", methods=['GET','POST'])
def leer_producto(id_cliente, id_negocio, id_producto, cantidad, estado):
    cantidad = int(cantidad)
    id_negocio = float(id_negocio)
    if cantidad == 1:
        procesar_incremento(id_producto, id_negocio, cantidad, estado)
    elif cantidad == -1:
        procesar_decremento(id_producto, cantidad)
    print(DicProductos)
    return redirect(request.referrer)

###################################################################################


################################## PARTE ADRIAN ##################################

@app.route("/mostrarPedido/<id_cliente>/<float:id_negocio>/",methods=['GET'])
def mostrar_pedido (id_cliente,id_negocio):    
    id_cliente=int(id_cliente)
    id_negocio=float(id_negocio)
    cliente=clientes.find({"_id":id_cliente})
    negocio=negocios.find({"_id":id_negocio})
    total=calcular_total()
    if (len(DicProductos)) == 0:
        return redirect(request.referrer)
    else:
        return render_template("MisPedidos.html",cliente=cliente, negocio=negocio, productos=DicProductos,total=total)

def calcular_total ():    
    total = 0
    for producto in DicProductos:
        total = total + (DicProductos[producto][0] * DicProductos[producto][1])
    return total
 
@app.route("/insertarPedido/<id_cliente>/<float:id_negocio>/",methods=['GET'])
def insertar_pedido (id_cliente,id_negocio):    
    id_cliente=int(id_cliente)
    id_negocio=float(id_negocio)
    total=calcular_total()
    cliente=clientes.find({"_id":id_cliente})
    negocio=negocios.find({"_id":id_negocio})

    repartidor=repartidores.find({"estado":"D"})
    if len(list(repartidor))!= 0:
        repartidor=repartidores.find({"estado":"D"})
        id_repartidor=repartidor[0]["_id"]
        
        cont=contador.find({"_id":1})
        valor=cont[0]["contador"]
        pedidos.insert_one({"_id":valor,"estadoPed":"pendiente","montoTotal":total,"cliente":id_cliente,"negocioId":id_negocio,"repartidorId":id_repartidor,"productos":[]})
        for producto in DicProductos:
            #produ="productos":['codProd':producto,'Nombre':DicProductos[producto][2],'Precio':DicProductos[producto][1],'Cantidad':DicProductos[producto][0]]
            pedidos.update_one({"_id":valor},{"$push":{"productos":{'codProd':producto,'Nombre':DicProductos[producto][2],'Precio':DicProductos[producto][1],'Cantidad':DicProductos[producto][0]}}})
        contador.update_one({"_id":1},{"$inc":{"contador":1}})
        return render_template("recibo.html",cliente=cliente, negocio=negocio, productos=DicProductos, total=total, repartidor=repartidor)
    return redirect(request.referrer)
###################################################################################

@app.route("/logout", methods=['GET'])
def logout ():    
    return redirect("/")

@app.route("/registrar",methods=['GET'])
def registrar ():
    return render_template("RegistrarCliente.html")

@app.route("/insertar",methods=['POST']) #post para recibir 
def insertar ():
    ci=request.values.get("ci_usuario")
    ci=int(ci)
    #preguntar si el usuario ya existe
    cliente=clientes.find({"_id":ci})
    lista_cliente=list(cliente)
    if len(lista_cliente)==0:
        nombre=request.values.get("nombre_usuario")
        apellido=request.values.get("apellido_usuario")
        celular=request.values.get("celular_usuario")
        celular=int(celular)
        contra=request.values.get("contra_usuario")
        clientes.insert_one({"_id":ci,"nombreCli":nombre,"apellidoCli":apellido,"celular":celular,"contraCli":contra})
        print(MSG_REGISTRO_EXITOSO)
        return redirect("/")
    else:
        return redirect("/registrar")

@app.route("/update", methods=['POST'])
def update():
    ci=request.values.get("ci_usuario")
    ci=int(ci)
    nombre=request.values.get("nombre_usuario")
    apellido=request.values.get("apellido_usuario")
    celular=request.values.get("celular_usuario")
    celular=int(celular)
    contra=request.values.get("contra_usuario")
    print(ci,nombre,apellido,celular,contra)
    clientes.update_one({"_id":ci},{"$set":{"nombreCli":nombre,"apellidoCli":apellido,"celular":celular,"contraCli":contra}})
    #clientes.update({"_id":ci},{"$set":{"nombreCli":nombre,"apellidoCli":apellido,"celular":celular,"contraCli":contra}})
    print(MSG_UPDATE_EXITOSO)
    return redirect("/datosCliente/"+format(ci))

################################# VISTA NEGOCIO ############################################
@app.route(RUTA_LOGIN_NEG,methods=['GET','POST']) #get para mandar 
def login_negocio ():
    if request.method =='POST':
        nombre_negocio=request.values.get("nombre_neg")
        passw=request.values.get("contra_neg")
        negocio=negocios.find({"Nombre":nombre_negocio})
        lista_negocio=list(negocio)
        #print(len(lista_cliente))
        if len(lista_negocio)!= 0:
            negocio=negocios.find({"Nombre":nombre_negocio})
            if(negocio[0]["Nombre"]==nombre_negocio and negocio[0]["contraNeg"]==passw): #validaciones
                return redirect(RUTA_MOSTRAR_PRODUCTOS_NEG+format(nombre_negocio)) #implementar
            else:
                return redirect(RUTA_LOGIN_NEG) #que vuelva a pedir que se registre pero con una advertencia de que el usuario o contrasenia que ingreso no existen
        else:
            return redirect(RUTA_LOGIN_NEG)
    return render_template("IniciarSesionNegocio.html")

@app.route("/registrarNeg",methods=['GET'])
def registrar_negocio ():
    return render_template("RegistrarNegocio.html")

@app.route("/insertarNeg",methods=['POST']) #post para recibir 
def insertar_negocio ():
    nombre_negocio=request.values.get("nombre_neg")
    negocio=negocios.find({"Nombre":nombre_negocio})
    lista_negocio=list(negocio)
    if len(lista_negocio) == 0:
        categ=request.values.get("categoria")
        contra=request.values.get("contra_neg")
        #id tiene que ser igual autonumerico como pedido
        cont=contador.find({"_id":1})
        valor=cont[0]["contador2"]
        negocios.insert_one({"_id":valor,"Nombre":nombre_negocio,"Categoria":categ,"contraNeg":contra,"Productos":[]})
        print(MSG_REGISTRO_EXITOSO)
        return redirect(RUTA_LOGIN_NEG)
    else:
        return redirect("/registrarNeg")
    
@app.route(RUTA_MOSTRAR_PRODUCTOS_NEG+"<nombre_negocio>/",methods=['GET','POST'])
def mostrar_productos_negocio (nombre_negocio):  
    negocio_p=negocios.find({"Nombre":nombre_negocio})
    pipeline = [{STAGE_MATCH:{"Nombre":nombre_negocio}},{STAGE_UNWIND:FIELD_PRODUCTOS},{STAGE_PROJECT:{"_id":0,"Productos":1}}]  
    productos_p=list(negocios.aggregate(pipeline))
    return render_template("ProductosNegocio.html",negocio=negocio_p,productos=productos_p)
  
def validar_estado_producto(estado):
    if estado=="Disponible":
        return "No Disponible"
    else:
        return "Disponible"
    
@app.route("/actualizarEst/<nombre_negocio>/<float:cod_producto>/<estado>/",methods=['GET','POST'])
def actualizar_estado_producto (nombre_negocio,cod_producto,estado):  
    cod_producto=float(cod_producto)
    estado=validar_estado_producto(estado)
    negocios.update_one({"Nombre":nombre_negocio,"Productos.codProd":cod_producto},{"$set":{"Productos.$.Estado":estado}})
    return redirect(RUTA_MOSTRAR_PRODUCTOS_NEG+format(nombre_negocio))

@app.route("/borrarProd/<nombre_negocio>/<float:cod_producto>/",methods=['GET','POST'])
def borrar_productos (nombre_negocio,cod_producto):  
    cod_producto=float(cod_producto)
    negocios.update_one({"Nombre":nombre_negocio},{"$pull":{"Productos":{"codProd":cod_producto}}})
    return redirect(RUTA_MOSTRAR_PRODUCTOS_NEG+format(nombre_negocio))
    
@app.route("/datosNegocio/<nombre_negocio>/", methods=['GET','POST'])
def datos_negocio(nombre_negocio):
    negocio_p=negocios.find({"Nombre":nombre_negocio})
    return render_template("DatosNegocio.html",negocio=negocio_p)

@app.route("/actualizarNeg", methods=['POST'])
def update_negocio():
    id_negocio=request.values.get("IdNeg")
    id_negocio=float(id_negocio)
    nombre=request.values.get("nombreNeg")
    categoria=request.values.get("Categoria")
    contra=request.values.get("contra")
    negocios.update_one({"_id":id_negocio},{"$set":{"Nombre":nombre,"Categoria":categoria,"contraNeg":contra}})
    #clientes.update({"_id":ci},{"$set":{"nombreCli":nombre,"apellidoCli":apellido,"celular":celular,"contraCli":contra}})
    print(MSG_UPDATE_EXITOSO)
    return redirect("/datosNegocio/"+format(nombre))

@app.route("/insertarProducto/<nombre_negocio>/",methods=['POST']) #post para recibir 
def insertar_producto (nombre_negocio):
    cod_producto=request.values.get("IdProd")
    cod_producto=float(cod_producto)
    nombre_producto=request.values.get("NomProd")
    desc=request.values.get("descProd")
    categoria=request.values.get("CateProd")
    estado=request.values.get("Estado")
    precio=request.values.get("Precio")
    precio=int(precio)
    negocios.update_one({"Nombre":nombre_negocio},{"$push":{"Productos":{"codProd":cod_producto,"Nombre":nombre_producto,"Precio":precio,"Descripcion":desc,"Estado":estado,"Categoria":categoria}}})
    print("Insertado con exito")
    return redirect(RUTA_MOSTRAR_PRODUCTOS_NEG+format(nombre_negocio))

@app.route("/pedidosNeg/<float:id_negocio>/",methods=['GET'])
def pedidos_negocio (id_negocio):    
    id_negocio=float(id_negocio)
    listapedido=list(pedidos.find({"negocioId":id_negocio}))
    negocio=negocios.find({"_id":id_negocio})
    return render_template("PedidosNegocio.html",pedidos=listapedido,negocio=negocio)



@app.route("/detallePedido/<float:id_negocio>/<float:id_pedido>",methods=['GET'])
def detalle_pedido (id_negocio,id_pedido):    
    id_pedido=float(id_pedido)
    id_negocio=float(id_negocio)
    pedido=list(pedidos.find({"_id":id_pedido}))
    productos=pedido[0]["productos"]
    print(pedido[0]["productos"])
    productos=list(productos)
    negocio=negocios.find({"_id":id_negocio})
    return render_template("DetallePedido.html",negocio=negocio,productos=productos)
##############################################################################################

################################# VISTA REPARTIDOR ############################################
@app.route(RUTA_MOSTRAR_PEDIDOS_DISP+"<id_repartidor>/",methods=['GET','POST'])
def mostrar_pedidos_disponibles (id_repartidor):  
    id_repartidor=int(id_repartidor)
    repartidor=repartidores.find({"_id":id_repartidor})
    pedidos_rep=pedidos.find({"repartidorId":id_repartidor,"$or":[{"estadoPed":"pendiente"},{"estadoPed":"en camino"}]})
    return render_template("PedidosDisponibles.html",repartidor=repartidor,pedidos=pedidos_rep)

def validar_estado_repartidor(estado):
    if estado=="O":
        return "D"
    else:
        return "O"
    
def validar_estado_pedido(estado):
    if estado=="pendiente":
        return "en camino"
    else:
        return "entregado"
    
@app.route("/actualizarEstRep/<float:id_pedido>/<id_repartidor>/<estado_pedido>/<estado_repartidor>/",methods=['GET','POST'])
def actualizar_estado_repartidor(id_pedido,id_repartidor,estado_pedido,estado_repartidor):  
    id_pedido=float(id_pedido)
    id_repartidor=int(id_repartidor)
    estado_repartidor=validar_estado_repartidor(estado_repartidor)
    estado_pedido=validar_estado_pedido(estado_pedido)
    repartidores.update_one({"_id":id_repartidor},{"$set":{"estado":estado_repartidor}})
    pedidos.update_one({"_id":id_pedido},{"$set":{"estadoPed":estado_pedido}})
    return redirect(RUTA_MOSTRAR_PEDIDOS_DISP+format(id_repartidor))

@app.route("/finalizarPedido/<float:id_pedido>/<id_repartidor>/<estado_pedido>/<estado_repartidor>/",methods=['GET','POST'])
def finalizar_pedido(id_pedido,id_repartidor,estado_pedido,estado_repartidor):  
    id_pedido=float(id_pedido)
    id_repartidor=int(id_repartidor)
    estado_repartidor=validar_estado_repartidor(estado_repartidor)
    estado_pedido=validar_estado_pedido(estado_pedido)
    repartidores.update_one({"_id":id_repartidor},{"$set":{"estado":estado_repartidor}})
    pedidos.update_one({"_id":id_pedido},{"$set":{"estadoPed":estado_pedido}})
    return redirect(RUTA_MOSTRAR_PEDIDOS_DISP+format(id_repartidor))


@app.route("/loginRep",methods=['GET','POST']) #get para mandar 
def login_repartidor():
    if request.method =='POST':
        id_repartidor=request.values.get("ci_rep")
        id_repartidor=int(id_repartidor)
        passw=request.values.get("contra_rep")
        repartidor=repartidores.find({"_id":id_repartidor})
        lista_repartidores=list(repartidor)
        #print(len(lista_cliente))
        if len(lista_repartidores)!= 0:
            repartidor=repartidores.find({"_id":id_repartidor})
            if(repartidor[0]["_id"]==id_repartidor and repartidor[0]["contra"]==passw):#validaciones
                #print("Id: ",cliente[0]["_id"]," pass:",cliente[0]["contraCli"])
                return redirect(RUTA_MOSTRAR_PEDIDOS_DISP+format(id_repartidor))
            else:
                return redirect("/loginRep") #que vuelva a pedir que se registre pero con una advertencia de que el usuario o contrasenia que ingreso no existen
        else:
            return redirect("/")
    return render_template("IniciarSesionRepartidor.html")

@app.route("/registrarRep",methods=['GET'])
def registrar_repartidor ():
    return render_template("RegistrarRepartidor.html")

@app.route("/insertarRep",methods=['POST']) #post para recibir 
def insertar_repartidor ():
    ci=request.values.get("ci_usuario")
    ci=int(ci)
    #preguntar si el usuario ya existe
    repartidor=repartidores.find({"_id":ci})
    lista_repartidor=list(repartidor)
    if len(lista_repartidor)==0:
        nombre=request.values.get("nombre_usuario")
        apellido=request.values.get("apellido_usuario")
        celular=request.values.get("celular_usuario")
        celular=int(celular)
        contra=request.values.get("contra_usuario")
        repartidores.insert_one({"_id":ci,"Nombre":nombre,"Apellido":apellido,"celular":celular,"contra":contra,"estado":"D"})
        print(MSG_REGISTRO_EXITOSO)
        return redirect("/loginRep")
    else:
        return redirect("/registrarRep")
    
@app.route("/datosRepartidor/<id_repartidor>/", methods=['GET','POST'])
def datos_repartidor(id_repartidor):
    id_repartidor=int(id_repartidor)
    repartidor_l=repartidores.find({"_id":id_repartidor})
    print("Id: ",repartidor_l[0]["_id"]," pass:",repartidor_l[0]["contra"])
    return render_template("DatosRepartidor.html",repartidor=repartidor_l)

@app.route("/updateRep", methods=['POST'])
def update_repartidor():
    ci=request.values.get("ci_repartidor")
    ci=int(ci)
    nombre=request.values.get("nombre_repartidor")
    apellido=request.values.get("apellido_repartidor")
    celular=request.values.get("celular_repartidor")
    celular=int(celular)
    contra=request.values.get("contra_repartidor")
    print(ci,nombre,apellido,celular,contra)
    repartidores.update_one({"_id":ci},{"$set":{"Nombre":nombre,"Apellido":apellido,"celular":celular,"contra":contra}})
    print(MSG_UPDATE_EXITOSO)
    return redirect("/datosRepartidor/"+format(ci))



@app.route("/pedidosRep/<id_repartidor>/",methods=['GET'])
def pedidos_repartidor(id_repartidor):
    id_repartidor=int(id_repartidor)
    listapedido=list(pedidos.find({"repartidorId":id_repartidor}))
    repartidor=repartidores.find({"_id":id_repartidor})
    return render_template("PedidosRepartidor.html",pedidos=listapedido, repartidor=repartidor)

if __name__ == "__main__":
    app.run()