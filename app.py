# -*- coding: utf-8 -*-
from flask import Flask, render_template,request,redirect,url_for,session,flash # For flask implementation
from bson import ObjectId # For ObjectId to work
from pymongo import MongoClient
import os



app = Flask(__name__)
#parametro 
app.secret_key='grupo4'
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
        id=request.values.get("ci_usuario")
        id=int(id)
        passw=request.values.get("contra_usuario")
        cliente=clientes.find({"_id":id})
        lista_cliente=list(cliente)
        #print(len(lista_cliente))
        if len(lista_cliente)!= 0:
            cliente=clientes.find({"_id":id})
            if(cliente[0]["_id"]==id and cliente[0]["contraCli"]==passw): #validaciones
                return redirect("/mostrarCats/"+format(id))
            else:
                return redirect("/") #que vuelva a pedir que se registre pero con una advertencia de que el usuario o contrasenia que ingreso no existen
        else:
            return redirect("/")
    return render_template("IniciarSesion.html")

@app.route("/mostrarCats/<id>/", methods=['GET','POST'])
def mostrarCats(id):
    id=int(id)
    cliente_l=clientes.find({"_id":id})
    #print("Id: ",cliente_l[0]["_id"]," pass:",cliente_l[0]["contraCli"])
    return render_template("Categorias.html",cliente=cliente_l)

@app.route("/datosCliente/<id>/", methods=['GET','POST'])
def datosCliente(id):
    id=int(id)
    cliente_l=clientes.find({"_id":id})
    print("Id: ",cliente_l[0]["_id"]," pass:",cliente_l[0]["contraCli"])
    return render_template("DatosCliente.html",cliente=cliente_l)

@app.route("/mostrarNegs/<id>/",methods=['GET','POST']) #get para mandar 
@app.route("/mostrarNegs/<id>/<categoria>/",methods=['GET','POST']) #get para mandar 
def mostrarNegs(id,categoria=None):
    DicProductos.clear()
    #print("Id: ",id)
    id=int(id)
    cliente_l=clientes.find({"_id":id})
    if(categoria != None):
        negocios_l=negocios.find({"Categoria":categoria})
    else:
        negocios_l=negocios.find()
    #print("Id: ",cliente_l[0]["_id"]," pass:",cliente_l[0]["contraCli"])
    return render_template("negocios.html",cliente=cliente_l,negocios=negocios_l,categoria=categoria)

@app.route("/buscar/<id>/",methods=['GET','POST'])
#@app.route("/buscar/<id>/<categoria>/",methods=['GET','POST'])
def buscar (id):    
    id=int(id)
    criterio=request.values.get("search")
    categoria=request.values.get("categoria")
    cliente=clientes.find({"_id":id})
    if(categoria != None):
        negocios_l=negocios.find({"Nombre":criterio,"Categoria":categoria})
    else:
        negocios_l=negocios.find({"Nombre":criterio})
    return render_template("negocios.html",cliente=cliente,negocios=negocios_l,categoria=categoria)

############################# PARTE MIA JUAN PABLO ############################


@app.route("/mostrarProds/<idCli>/<float:idNeg>/",methods=['GET','POST'])
def mostrarProds (idCli,idNeg):  

    idCli=int(idCli)
    idNeg = float(idNeg)
    cliente_p=clientes.find({"_id":idCli})
    negocio_p=negocios.find({"_id":idNeg})
    pipeline = [{"$match":{"_id":idNeg}},{"$unwind":'$Productos'},{"$match":{"Productos.Estado":"Disponible"}},{"$project":{"_id":0,"Productos":1}}]  
    productos_p=list(negocios.aggregate(pipeline))
    return render_template("Productos.html",cliente=cliente_p,negocio=negocio_p,productos=productos_p)

def validarProducto(estado):
    if (estado == "No Disponible"):
        return False
    else:
        return True
                      
@app.route("/AgregarProd/<idCli>/<float:idNeg>/<float:idProd>/<cantidad>/<estado>",methods=['GET','POST'])   
def leerProducto(idCli,idNeg,idProd,cantidad,estado):
    cantidad=int(cantidad)
    if(cantidad==1):
        if (validarProducto(estado) == True):
            if idProd in DicProductos:
                ar = DicProductos[idProd]
                ar[0]+=cantidad
                DicProductos[idProd]=ar
            else:
                idCli=int(idCli)
                idNeg=float(idNeg)
                negocio_p=negocios.find({"_id":idNeg})
                prodNom=negocio_p[0]["Nombre"]
                idProd = float(idProd)
                cantidad = int(cantidad)
                pipeline = [{"$match":{"_id":idNeg}},{"$unwind":'$Productos'},{"$match":{"Productos.codProd":idProd}},{"$project":{"_id":0,"NombreProd":"$Productos.Nombre","Precio":"$Productos.Precio","Productos":1}}]  
                #producto=negocios.aggregate(pipeline)
                producto=list(negocios.aggregate(pipeline))
                for produ in producto:
                    #print(produ["NombreProd"])
                    prodNom=produ["NombreProd"]
                    precioProd=produ["Precio"]
                print(prodNom,precioProd)
                arry=[cantidad,precioProd,prodNom]
                DicProductos[idProd] = arry
    elif(cantidad==-1):
        if(len(DicProductos)>0):
            if idProd in DicProductos:
                if(DicProductos[idProd][0]>1):
                    DicProductos[idProd][0]+=cantidad
                else:
                    DicProductos.pop(idProd)
    print(DicProductos) 
    return redirect(request.referrer)

# @app.route("/buscarProducto/<idNeg>/",methods=['GET','POST'])
# def buscarProd (id):    
#     id=int(id)
#     criterio=request.values.get("search")
#     categoria=request.values.get("categoria")
#     negocios=negocios.find({"_id":id})
#     if(categoria != None):
#         negocios_l=negocios.find({"Nombre":criterio,"Categoria":categoria})
#     else:
#         negocios_l=negocios.find({"Nombre":criterio})
#     return render_template("Productos.html",cliente=cliente,negocios=negocios_l)

###################################################################################


################################## PARTE ADRIAN ##################################

@app.route("/mostrarPedido/<idCli>/<float:idNeg>/",methods=['GET'])
def mostrarPedido (idCli,idNeg):    
    idCli=int(idCli)
    idNeg=float(idNeg)
    cliente=clientes.find({"_id":idCli})
    negocio=negocios.find({"_id":idNeg})
    total=calcularTotal()
    if (len(DicProductos)) == 0:
        return redirect(request.referrer)
    else:
        return render_template("MisPedidos.html",cliente=cliente, negocio=negocio, productos=DicProductos,total=total)

def calcularTotal ():    
    total = 0
    for producto in DicProductos:
        total = total + (DicProductos[producto][0] * DicProductos[producto][1])
    return total
 
@app.route("/insertarPedido/<idCli>/<float:idNeg>/",methods=['GET'])
def insertarPedido (idCli,idNeg):    
    idCli=int(idCli)
    idNeg=float(idNeg)
    total=calcularTotal()
    cliente=clientes.find({"_id":idCli})
    negocio=negocios.find({"_id":idNeg})

    repartidor=repartidores.find({"estado":"D"})
    if len(list(repartidor))!= 0:
        repartidor=repartidores.find({"estado":"D"})
        idRep=repartidor[0]["_id"]
        
        cont=contador.find({"_id":1})
        valor=cont[0]["contador"]
        pedidos.insert_one({"_id":valor,"estadoPed":"pendiente","montoTotal":total,"cliente":idCli,"negocioId":idNeg,"repartidorId":idRep,"productos":[]})
        for producto in DicProductos:
            #produ="productos":['codProd':producto,'Nombre':DicProductos[producto][2],'Precio':DicProductos[producto][1],'Cantidad':DicProductos[producto][0]]
            pedidos.update_one({"_id":valor},{"$push":{"productos":{'codProd':producto,'Nombre':DicProductos[producto][2],'Precio':DicProductos[producto][1],'Cantidad':DicProductos[producto][0]}}})
        contador.update_one({"_id":1},{"$inc":{"contador":1}})
        return render_template("recibo.html",cliente=cliente, negocio=negocio, productos=DicProductos, total=total, repartidor=repartidor)
    return redirect(request.referrer)
###################################################################################

@app.route("/logout")
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
        print("Registrado con exito")
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
    print("Update con exito")
    return redirect("/datosCliente/"+format(ci))

################################# VISTA NEGOCIO ############################################
@app.route("/loginNeg",methods=['GET','POST']) #get para mandar 
def loginNegocio ():
    if request.method =='POST':
        nombreNeg=request.values.get("nombre_neg")
        passw=request.values.get("contra_neg")
        negocio=negocios.find({"Nombre":nombreNeg})
        lista_negocio=list(negocio)
        #print(len(lista_cliente))
        if len(lista_negocio)!= 0:
            negocio=negocios.find({"Nombre":nombreNeg})
            if(negocio[0]["Nombre"]==nombreNeg and negocio[0]["contraNeg"]==passw): #validaciones
                return redirect("/mostrarProdsNeg/"+format(nombreNeg)) #implementar
            else:
                #mensaje="Usuario o contraseña incorrectos, vuelva a ingresar sus datos o registrese!"
                #flash(mensaje,"ERROR")
                return redirect("/loginNeg") #que vuelva a pedir que se registre pero con una advertencia de que el usuario o contrasenia que ingreso no existen
        else:
            return redirect("/loginNeg")
    return render_template("IniciarSesionNegocio.html")

@app.route("/registrarNeg",methods=['GET'])
def registrarNegocio ():
    return render_template("RegistrarNegocio.html")

@app.route("/insertarNeg",methods=['POST']) #post para recibir 
def insertarNegocio ():
    nombreNeg=request.values.get("nombre_neg")
    negocio=negocios.find({"Nombre":nombreNeg})
    lista_negocio=list(negocio)
    if len(lista_negocio) == 0:
        categ=request.values.get("categoria")
        contra=request.values.get("contra_neg")
        #id tiene que ser igual autonumerico como pedido
        cont=contador.find({"_id":1})
        valor=cont[0]["contador2"]
        negocios.insert_one({"_id":valor,"Nombre":nombreNeg,"Categoria":categ,"contraNeg":contra,"Productos":[]})
        print("Registrado con exito")
        return redirect("/loginNeg")
    else:
        return redirect("/registrarNeg")
    
@app.route("/mostrarProdsNeg/<nombreNeg>/",methods=['GET','POST'])
def mostrarProductosNegocio (nombreNeg):  
    negocio_p=negocios.find({"Nombre":nombreNeg})
    pipeline = [{"$match":{"Nombre":nombreNeg}},{"$unwind":'$Productos'},{"$project":{"_id":0,"Productos":1}}]  
    productos_p=list(negocios.aggregate(pipeline))
    return render_template("ProductosNegocio.html",negocio=negocio_p,productos=productos_p)
  
def validarEstadoProd(estado):
    if estado=="Disponible":
        return "No Disponible"
    else:
        return "Disponible"
    
@app.route("/actualizarEst/<nombreNeg>/<float:codProd>/<estado>/",methods=['GET','POST'])
def actualizarEstadoProd (nombreNeg,codProd,estado):  
    codProd=float(codProd)
    estado=validarEstadoProd(estado)
    negocios.update_one({"Nombre":nombreNeg,"Productos.codProd":codProd},{"$set":{"Productos.$.Estado":estado}})
    return redirect("/mostrarProdsNeg/"+format(nombreNeg))

@app.route("/borrarProd/<nombreNeg>/<float:codProd>/",methods=['GET','POST'])
def borrarProductos (nombreNeg,codProd):  
    codProd=float(codProd)
    negocios.update_one({"Nombre":nombreNeg},{"$pull":{"Productos":{"codProd":codProd}}})
    return redirect("/mostrarProdsNeg/"+format(nombreNeg))
    
@app.route("/datosNegocio/<nombreNeg>/", methods=['GET','POST'])
def datosNegocio(nombreNeg):
    negocio_p=negocios.find({"Nombre":nombreNeg})
    return render_template("DatosNegocio.html",negocio=negocio_p)

@app.route("/actualizarNeg", methods=['POST'])
def updateNegocio():
    idNeg=request.values.get("IdNeg")
    idNeg=float(idNeg)
    nombre=request.values.get("nombreNeg")
    categoria=request.values.get("Categoria")
    contra=request.values.get("contra")
    negocios.update_one({"_id":idNeg},{"$set":{"Nombre":nombre,"Categoria":categoria,"contraNeg":contra}})
    #clientes.update({"_id":ci},{"$set":{"nombreCli":nombre,"apellidoCli":apellido,"celular":celular,"contraCli":contra}})
    print("Update con exito")
    return redirect("/datosNegocio/"+format(nombre))

@app.route("/insertarProducto/<nombreNeg>/",methods=['POST']) #post para recibir 
def insertarProducto (nombreNeg):
    codProd=request.values.get("IdProd")
    codProd=float(codProd)
    nombreProd=request.values.get("NomProd")
    desc=request.values.get("descProd")
    categoria=request.values.get("CateProd")
    estado=request.values.get("Estado")
    precio=request.values.get("Precio")
    precio=int(precio)
    negocios.update_one({"Nombre":nombreNeg},{"$push":{"Productos":{"codProd":codProd,"Nombre":nombreProd,"Precio":precio,"Descripcion":desc,"Estado":estado,"Categoria":categoria}}})
    print("Insertado con exito")
    return redirect("/mostrarProdsNeg/"+format(nombreNeg))

@app.route("/pedidosNeg/<float:idNeg>/",methods=['GET'])
def pedidosNeg (idNeg):    
    idNeg=float(idNeg)
    listapedido=list(pedidos.find({"negocioId":idNeg}))
    #cliente=listapedido.cliente
    negocio=negocios.find({"_id":idNeg})
   # total=calcularTotal()
    return render_template("PedidosNegocio.html",pedidos=listapedido,negocio=negocio)


@app.route("/detallePedido/<float:idNeg>/<float:idPedido>",methods=['GET'])
def detallePedido (idNeg,idPedido):    
    idPedido=float(idPedido)
    idNeg=float(idNeg)
    pedido=list(pedidos.find({"_id":idPedido}))
    productos=pedido[0]["productos"]
    print(pedido[0]["productos"])
    productos=list(productos)
    #cliente=listapedido.cliente
    negocio=negocios.find({"_id":idNeg})
   # total=calcularTotal()
    return render_template("DetallePedido.html",negocio=negocio,productos=productos)
##############################################################################################

################################# VISTA REPARTIDOR ############################################
@app.route("/mostrarPedidosDisp/<idRep>/",methods=['GET','POST'])
def mostrarPedidosDisp (idRep):  
    idRep=int(idRep)
    repartidor=repartidores.find({"_id":idRep})
    pedidos_rep=pedidos.find({"repartidorId":idRep,"$or":[{"estadoPed":"pendiente"},{"estadoPed":"en camino"}]})
    return render_template("PedidosDisponibles.html",repartidor=repartidor,pedidos=pedidos_rep)

def validarEstadoRep(estado):
    if estado=="O":
        return "D"
    else:
        return "O"
    
def validarEstadoPed(estado):
    if estado=="pendiente":
        return "en camino"
    else:
        return "entregado"
    
@app.route("/actualizarEstRep/<float:idPedido>/<idRep>/<estadoPed>/<estadoRep>/",methods=['GET','POST'])
def actualizarEstadoRepartidor(idPedido,idRep,estadoPed,estadoRep):  
    idPedido=float(idPedido)
    idRep=int(idRep)
    estadoRep=validarEstadoRep(estadoRep)
    estadoPed=validarEstadoPed(estadoPed)
    repartidores.update_one({"_id":idRep},{"$set":{"estado":estadoRep}})
    pedidos.update_one({"_id":idPedido},{"$set":{"estadoPed":estadoPed}})
    return redirect("/mostrarPedidosDisp/"+format(idRep))

@app.route("/finalizarPedido/<float:idPedido>/<idRep>/<estadoPed>/<estadoRep>/",methods=['GET','POST'])
def finalizarPedido(idPedido,idRep,estadoPed,estadoRep):  
    idPedido=float(idPedido)
    idRep=int(idRep)
    estadoRep=validarEstadoRep(estadoRep)
    estadoPed=validarEstadoPed(estadoPed)
    repartidores.update_one({"_id":idRep},{"$set":{"estado":estadoRep}})
    pedidos.update_one({"_id":idPedido},{"$set":{"estadoPed":estadoPed}})
    return redirect("/mostrarPedidosDisp/"+format(idRep))


@app.route("/loginRep",methods=['GET','POST']) #get para mandar 
def loginRepartidor():
    if request.method =='POST':
        id=request.values.get("ci_rep")
        id=int(id)
        passw=request.values.get("contra_rep")
        repartidor=repartidores.find({"_id":id})
        lista_repartidores=list(repartidor)
        #print(len(lista_cliente))
        if len(lista_repartidores)!= 0:
            repartidor=repartidores.find({"_id":id})
            if(repartidor[0]["_id"]==id and repartidor[0]["contra"]==passw):#validaciones
                #print("Id: ",cliente[0]["_id"]," pass:",cliente[0]["contraCli"])
                return redirect("/mostrarPedidosDisp/"+format(id))
            else:
                #mensaje="Usuario o contraseña incorrectos, vuelva a ingresar sus datos o registrese!"
                #flash(mensaje,"ERROR")
                return redirect("/loginRep") #que vuelva a pedir que se registre pero con una advertencia de que el usuario o contrasenia que ingreso no existen
        else:
            return redirect("/")
    return render_template("IniciarSesionRepartidor.html")

@app.route("/registrarRep",methods=['GET'])
def registrarRepartidor ():
    return render_template("RegistrarRepartidor.html")

@app.route("/insertarRep",methods=['POST']) #post para recibir 
def insertarRepartidor ():
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
        print("Registrado con exito")
        return redirect("/loginRep")
    else:
        return redirect("/registrarRep")
    
@app.route("/datosRepartidor/<id>/", methods=['GET','POST'])
def datosRepartidor(id):
    id=int(id)
    repartidor_l=repartidores.find({"_id":id})
    print("Id: ",repartidor_l[0]["_id"]," pass:",repartidor_l[0]["contra"])
    return render_template("DatosRepartidor.html",repartidor=repartidor_l)

@app.route("/updateRep", methods=['POST'])
def updateRep():
    ci=request.values.get("ci_repartidor")
    ci=int(ci)
    nombre=request.values.get("nombre_repartidor")
    apellido=request.values.get("apellido_repartidor")
    celular=request.values.get("celular_repartidor")
    celular=int(celular)
    contra=request.values.get("contra_repartidor")
    print(ci,nombre,apellido,celular,contra)
    repartidores.update_one({"_id":ci},{"$set":{"Nombre":nombre,"Apellido":apellido,"celular":celular,"contra":contra}})
    print("Update con exito")
    return redirect("/datosRepartidor/"+format(ci))


@app.route("/pedidosRep/<idRep>/",methods=['GET'])
def pedidosRep(idRep):
    idRep=int(idRep)
    listapedido=list(pedidos.find({"repartidorId":idRep}))
    repartidor=repartidores.find({"_id":idRep})
    return render_template("PedidosRepartidor.html",pedidos=listapedido, repartidor=repartidor)

if __name__ == "__main__":
    app.run()
