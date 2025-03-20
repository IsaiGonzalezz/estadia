from django.shortcuts import render, redirect, get_object_or_404
import requests
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.http import HttpResponse
import datetime
from django.utils.dateparse import parse_date, parse_datetime
from reportlab.pdfgen import canvas
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.forms import AuthenticationForm
from .models import Cliente, Proveedor, Categoria, Producto, Detalle_Compra, Detalle_Venta, Compra, Venta, Usuario, Caja, Cierre_Caja
from .forms import ProductoForm, ClienteForm, ProveedorForm, CompraForm, VentaForm, UsuarioForm, CajaForm, CierreForm, CodesForm
from django.http import HttpResponse, JsonResponse
from django_select2.views import AutoResponseView
from .db_connection import Database #conexión directa
import json
from decimal import Decimal
import bcrypt


#from .forms import ProductoForm
from django.contrib import messages

#shit for test, do not fokin delit

import os
import django
import escpos
import hashlib
import PIL.Image
from django.utils import timezone
from accounts.models import Detalle_Venta, Venta

#validacion de adminnn o kajero
from .decorators import admin_required, login_required


@admin_required
def menu_principal(request):
    
    return render(request, 'menu_principal.html')



def index(request): #INICIO DE SESIÓN 
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        password = request.POST.get('password')
        # Buscar usuario en la base de datos
        try:
            usuario = Usuario.objects.get(nombre=nombre)
            # Usar check_password para verificar la contraseña
            if check_password(password, usuario.password):
                request.session['usuario_id'] = usuario.id_usuario
                request.session['privilegio'] = usuario.rol

                # Verificar privilegio como booleano usando el valor de TINYINT
                if usuario.rol:
                    return redirect('menu_principal')
                else:  # 0 representa False (usuario regular)
                    return redirect('ventas')
            else:
                messages.error(request, 'Nombre o contraseña incorrectos')
        except Usuario.DoesNotExist:
            messages.error(request, 'Nombre o contraseña incorrectos')

    return render(request, 'index.html')


def logout_view(request):
    request.session.flush()  # Elimina todos los datos de la sesión
    messages.success(request, 'Has cerrado sesión correctamente.')  # Opción: Mostrar un mensaje de éxito
    return redirect('login') 


@admin_required
def registro_usuario(request):
    usuarios = Usuario.objects.all()
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.password = make_password(form.cleaned_data['password'])
            usuario.save()
            return redirect('usuario')
        else:
            messages.error(request, "Hubo un error al registrar el usuario.")
    else:
        form = UsuarioForm()
    return render(request, 'usuario.html', {'form':form, 'usuarios':usuarios})


@admin_required
def codes(request):
    if request.method == 'POST':
        form = CodesForm(request.POST)
        if form.is_valid():
            code = form.save(commit=False)
            code.save()
            messages.success(request, 'Código guardado exitosamente.')
            return redirect('codes')
        else:
            messages.error(request, 'Error al guardar el código. Verifique los datos ingresados.')
    else:
        form = CodesForm()

    return render(request, 'registro_codes.html', {'form': form})
@admin_required
def registrar_cliente(request):
    if request.method == 'POST' :
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('menu_principal')
        else:
            messages.error(request, "Hubo un error al registrar el cliente.")
    else:
        form = ClienteForm()
    
    return render(request, 'registro_cliente.html', {'form':form})
    

@admin_required
def registrar_proveedor(request):
    if request.method == 'POST' :
        form = ProveedorForm(request.POST)
        if form.is_valid():
            
            form.save()
            return redirect('proveedor')
        else:
            messages.error(request, "Hubo un error al registrar el proveedor.")
    else:
        form = ProveedorForm()
    proveedores = Proveedor.objects.all()
    return render(request, 'registro_proveedor.html', {'form':form, 'proveedores':proveedores})


@admin_required
def registrar_producto(request):
    query = request.GET.get('q', '')
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id', None)
        if producto_id:  # Si hay un ID, estamos actualizando un producto existente
            producto = get_object_or_404(Producto, id_producto=producto_id)
            form = ProductoForm(request.POST, instance=producto)
        else:  # Si no hay ID, estamos creando un nuevo producto
            form = ProductoForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Producto registrado exitosamente.")
            return redirect('producto')
        else:
            messages.error(request, "Hubo un error al registrar el producto.")
    else:
        form = ProductoForm()
    
    productos = Producto.objects.all()
    if query:
        productos_filtrados = productos.filter(id_producto=query)
    else:
        productos_filtrados = productos
    
    return render(request, 'registro_inventario.html', {
        'form': form,
        'productos': productos,
        'productos_filtrados': productos_filtrados,
        'query': query
    })


@admin_required
def eliminar_producto(request, id_producto):
    producto = get_object_or_404(Producto, id_producto=id_producto)
    producto.delete()
    messages.success(request, "Producto eliminado exitosamente.")
    return redirect('producto')


@admin_required
def registrar_categoria(request):
    if request.method == 'POST':
        nueva_categoria = Categoria()
        nueva_categoria.descripcion = request.POST.get('descripcion')
        nueva_categoria.save()
        return redirect('producto')
        
    return render(request, 'registro_categoria.html')


@admin_required
def registrar_compra(request):
    productos = Producto.objects.all()
    if request.method == 'POST': 
        form = CompraForm(request.POST)
        if form.is_valid() or not form.has_changed():
            try:
                fecha_compra = request.POST.get('fecha_compra')
                total_compra = Decimal(request.POST.get('total_compra'))
                proveedor_id = request.POST.get('proveedor_id')
                resumen_data = json.loads(request.POST.get('resumen_data', '[]'))

                proveedor = Proveedor.objects.get(id_proveedor=proveedor_id)

                # Crear nueva compra
                nueva_compra = Compra(fecha=fecha_compra, total=total_compra, id_proveedor=proveedor)
                nueva_compra.save()
                

                #insertar detalles de la compra
                for item in resumen_data:
                    producto = Producto.objects.get(id_producto=item['producto_id'])
                    cantidad = int(item['cantidad'])
                    costo = Decimal(item['costo'])

                    #calculazion de utilidad
                    porcentaje_utilidad = Decimal(producto.porcentaje_utilidad)
                    utilidad = costo * (porcentaje_utilidad/100)
                    precio_venta = costo + utilidad

                    #actualizar producto
                    #actualizar el precio de venta
                    producto.costo_venta = precio_venta
                    
                    #actualizar el costo de venta del producto
                    producto.costo_compra = costo

                    if isinstance(producto.stock,int) :
                        producto.stock += int(cantidad)
                    else :
                        producto.stock = int(cantidad)
                    producto.save()

                    detalle_compra = Detalle_Compra(
                        id_compra=nueva_compra,
                        id_producto=producto,
                        cantidad=cantidad,
                        costo=costo 
                    )
                    detalle_compra.save()
                    #actualización del stock
                return redirect('compra')
            except Exception as e:
                print(f"Error al guardar la compra: {e}")

        else:
            print("El formulario no es válido")
    else:
        form=CompraForm()
    context = {
        'form': form,
        'productos': productos
    }
    return render(request, 'registro_compra.html', context)  


@login_required
def registro_ventas(request):
    usuario_id = request.session.get('usuario_id')
    productos = Producto.objects.all()
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid() or not form.has_changed():
            try:

                fecha_venta = request.POST.get('fecha_venta')       
                total_venta = request.POST.get('total_venta')
                #cliente_id = request.POST.get('cliente_id')
                resumen_data = json.loads(request.POST.get('resumen_data', '[]'))

                usuario = Usuario.objects.get(id_usuario=usuario_id)
                    
                nueva_venta = Venta(fecha=fecha_venta, total=total_venta, id_usuario=usuario)
                nueva_venta.save()

                #cliente = Cliente.objects.get(id_cliente=cliente_id)

                for item in resumen_data:
                    #id_cliente = Cliente.objects.get(id_cliente=item['id_cliente'])
                    cantidad = int(item.get('cantidad'))
                    producto_id = Producto.objects.get(id_producto=item['producto_id'])
                    precio_total = float(item.get('precio_total'))
                    precio_base = precio_total
                    iva = precio_total - precio_base

                    #descontar stock
                    producto_id.stock -= int(cantidad)
                    producto_id.save()

                    detalle_venta = Detalle_Venta(
                        id_venta=nueva_venta,  # Aquí el campo en la tabla es 'id_venta'
                        id_producto=producto_id,  # Obtener instancia del producto
                        cantidad=cantidad,
                        precio_total=precio_base,
                        # id_cliente=cliente,  # Obtener instancia del cliente
                    )
                    detalle_venta.save()

                return redirect('ventas')
            except Exception as e:
                print(f"Error sabrá Dios dónde: {e}")
        else:
            print("El formulario no es válido")
    else:
        form = VentaForm()
    context = {
        'form': form,
        'productos': productos
    }
    return render(request, 'registro_venta.html', context)


def ticket_generator(request):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '../estadias1/settings')
    django.setup()
    printer = escpos.printer.SerialPrinter(port='/dev/ttyUSB0', baudrate=9600)
    #The fokin config of the printer MUST be defined in the previous line.
    #test's haven't been, you know, tested xd
    printer.write('**Electronic Store UTSJR or something**')
    now = timezone.now()
    printer.write(f'Fecha: {now.strftime("%Y-%m-%d")}')
    printer.write(f'Hora: {now.strftime("%H:%M:%S")}')
    detalles = Detalle_Venta.objects.all()
    

    #get the last Detalle_Venta
    ultimo_detalle = Detalle_Venta.objects.latest('id_detalleventa')

    #get the last detalle_venta1 to use it as a reference
    id_venta = ultimo_detalle.id_venta_id 

    #Get the things inside detalle_ventas, not VENTAS, DETALLE you filthy fucker
    detalles = Detalle_Venta.objects.filter(id_venta=id_venta).order_by('-id_detalleventa')

    #get the VENTA, not de DETALLE,the VENTA, based on the asociated VENTA1 id in detalle
    #kinda confusing but not so bad my dude
    venta = Venta.objects.get(id_venta=id_venta)

    #header of tha shi
    printer.write('**Electronic Store UTSJR or whatever**\n')
    now = timezone.now()
    printer.write(f'Date: {now.strftime("%Y-%m-%d")}\n')
    printer.write(f'Time: {now.strftime("%H:%M:%S")}\n')

    #Sell data
    printer.write(f"Sell number: {ultimo_detalle.id_detalleventa}\n")
    #printer.write(f"Cliente: {ultimo_detalle.id_cliente}")
    #printer.write(f"Fecha de Venta: {venta.fecha}")
    #printer.write("Products:")
    printer.write("Cantidad     |Costo         |Total\n")

    #pradacts
    for detalle in detalles:
        cantidad = detalle.cantidad
        individualPrice = detalle.precio_total
        total_articulo = cantidad * precio_total
        printer.write(f"{detalle.id_producto}\n")
        printer.write(f"{detalle.cantidad}    ")
        printer.write(f"{detalle.precio_total}    ")
        printer.write(f"{individualPrice}\n")        
        #printer.write(f"IVA: {detalle.iva}")
        printer.write('---------------------\n')
    #Total
    printer.write(f"Total de la Venta: {venta.total}")


    printer.cut()
# Further tests haven't been applied because, you know, we need a printer
# if this doesn't work you have below this message the original generator
# it generates ugly tickets in PDF but at least that fucking works
# That's it for today, i have an urgent call to buy an hamburguer cs i'm hungry as fuck
# -fakeCirc3



'''
def ticket_generator(request):
    # Generar la respuesta HTTP con el contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="detalle_venta.pdf"'

    # Crear un objeto canvas de ReportLab
    p = canvas.Canvas(response)

    # Obtener el último detalle de venta según id_detalleventa
    ultimo_detalle = Detalle_Venta.objects.latest('id_detalleventa')

    # Obtener el id_venta1 del último detalle de venta
    id_venta1 = ultimo_detalle.id_venta1_id  # Acceder al id de la venta

    # Obtener todos los detalles de venta para el id_venta1 obtenido, manteniendo el último id_detalleventa
    detalles = Detalle_Venta.objects.filter(id_venta1=id_venta1).order_by('-id_detalleventa')

    # Obtener la venta asociada al id_venta1
    venta = Venta.objects.get(id_venta=id_venta1)

    # Inicializar posición de escritura
    y = 800

    # Escribir los datos del último detalle de venta y productos asociados en el PDF
    p.drawString(100, y, f"ID Venta: {ultimo_detalle.id_detalleventa}")
    p.drawString(100, y - 20, f"Cliente: {ultimo_detalle.id_cliente}")
    p.drawString(100, y - 40, f"Fecha de Venta: {venta.fecha}")
    p.drawString(100, y - 60, "Productos:")

    # Listar todos los productos asociados al id_venta1 y último id_detalleventa
    for detalle in detalles:
        p.drawString(120, y - 80, f"Producto: {detalle.id_producto}, Cantidad: {detalle.cantidad}, Costo: {detalle.precio_total}, IVA: {detalle.iva}")
        y -= 40  # Mover hacia abajo para el siguiente detalle

    # Mostrar el total de la venta
    p.drawString(100, y - 100, f"Total de la Venta: {venta.total}")

    # Finalizar el PDF
    p.showPage()
    p.save()

    return response
'''


@admin_required
def historico_compras(request):
    db = Database()
    try:
        #datos del filtro
        proveedor_id = request.GET.get('proveedor')
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')

        #consulta con filtros
        query = """
        SELECT c.id_compra, c.fecha, pr.razon_social, c.total
        FROM compra c
        JOIN detalle_compra dc ON c.id_compra = dc.id_compra 
        JOIN proveedor pr ON pr.id_proveedor = c.id_proveedor
        WHERE 1=1
        
        """

        #añadir filtros a la consulta
        params = []
        if proveedor_id:
            query += " AND pr.id_proveedor = %s"
            params.append(proveedor_id)
        if fecha_inicio:
            query += " AND c.fecha >= %s"
            params.append(fecha_inicio)
        if fecha_fin:
            query += " AND c.fecha <= %s"
            params.append(fecha_fin)

        query += """
        group by c.id_compra,pr.razon_social
        order by c.id_compra desc
        """

        #obttener la lista de proveedores segun el filtro
        proveedores_query = "SELECT id_proveedor, razon_social FROM proveedor"
        proveedores = db.fetch_all(proveedores_query,[])
        proveedor_dict = [{'id_proveedor':proveedor[0],'razon_social': proveedor[1]} for proveedor in proveedores]

        historial_compras = db.fetch_all(query, params)
        total = sum(compra[3] for compra in historial_compras)

        context = {
            'historial_compras': historial_compras,
            'total' : total,
            'proveedores' : proveedor_dict
        }
    finally:
        db.close()
    return render(request, 'historico_compras.html', context)


@admin_required
def detalle_compra(request): #EXTENSION DEL HISTORICO DE COMPRA PARA VER EL DETALLE DE LA COMPRA SJSJ
    compra_id = request.GET.get('compra_id')
    db = Database()
    try:
        query = """
        SELECT dc.id_detallecompra, p.nombre, dc.cantidad, dc.costo, (dc.cantidad * dc.costo) as total
        FROM detalle_compra dc
        JOIN producto p ON p.id_producto = dc.id_producto
        WHERE dc.id_compra = %s
        """
        detalles_compra = db.fetch_all(query, [compra_id])

        total = sum(detalle[4] for detalle in detalles_compra)

        context = {
            'detalles_compra':detalles_compra,
            'total':total
        }
    finally:
        db.close()

    return render(request, 'detalle_compra.html', context)


@admin_required
def detalle_venta(request):
    venta_id = request.GET.get('venta_id')
    db = Database()
    try:
        query = """
        SELECT dv.id_detalleventa, p.nombre, dv.cantidad, dv.precio_total, (p.costo_venta * dv.cantidad ) as subtotal, ( dv.precio_total) as subtotalIva, p.costo_venta
        FROM detalle_venta dv
        JOIN producto p ON p.id_producto = dv.id_producto
        WHERE dv.id_venta = %s
        """
        detalles_venta = db.fetch_all(query, [venta_id])

        total = sum(detalle[5] for detalle in detalles_venta)  # Suma de subtotales
        

        context = {
            'detalles_venta': detalles_venta,
            'total': total
        }
    finally:
        db.close()

    return render(request, 'detalle_venta.html', context)






@admin_required
def historico_ventas(request):
    db = Database()
    try:
        # Datos del filtro
        #cliente_id = request.GET.get('cliente')
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')

        # Consulta con filtros
        query = """
        SELECT v.id_venta, v.fecha, SUM(dv.precio_total)
        FROM venta v
        JOIN detalle_venta dv ON v.id_venta = dv.id_venta
        
        WHERE 1=1
        """
#JOIN cliente cl ON cl.id_cliente = dv.id_cliente
        # Añadir filtros a la consulta
        params = []
        #if cliente_id:
        #    query += " AND cl.id_cliente = %s"
        #    params.append(cliente_id)
        if fecha_inicio:
            query += " AND v.fecha >= %s"
            params.append(fecha_inicio)
        if fecha_fin:
            query += " AND v.fecha <= %s"
            params.append(fecha_fin)

        query += """
        GROUP BY v.id_venta, v.fecha
        ORDER BY v.id_venta DESC
        """

        # Obtener la lista de clientes para el filtro
        #clientes_query = "SELECT id_cliente, razon_social FROM cliente"
        #clientes = db.fetch_all(clientes_query, [])
        #clientes_dict = [{'id_cliente': cliente[0], 'razon_social': cliente[1]} for cliente in clientes]


        historial_ventas = db.fetch_all(query, params)
        total = sum(venta[2] for venta in historial_ventas)

        context = {
            'historial_ventas': historial_ventas,
            'total': total
            #'clientes': clientes_dict
        }
    finally:
        db.close()
    return render(request, 'historico_ventas.html', context)



@admin_required
def open_caja(request):
    usuarios = Usuario.objects.all()
    if request.method == 'POST':
        form = CajaForm(request.POST)
        if form.is_valid():
            # Obtener el usuario_id desde el formulario
            usuario_id = form.cleaned_data['usuario_id'].id_usuario

            # Obtener el objeto Usuario correspondiente (ya no es necesario si solo necesitas el ID)
            # usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

            # Guardar el formulario y crear una nueva instancia de Caja
            form.save()

            # Redirigir a una página de éxito o lista de cajas
            return redirect('caja')
    else:
        form = CajaForm()

    return render(request, 'open_caja.html', {'form': form, 'usuarios': usuarios})


@admin_required
def caja(request):
    
    return render(request, 'first_caja.html')


@admin_required
def close_caja(request):
    cajas = Caja.objects.filter(activo=True)

    if request.method == 'POST':
        form = CierreForm(request.POST)
        if form.is_valid():
            caja_id=request.POST.get('id_caja')
            caja = Caja.objects.get(id_caja=caja_id)
            caja.activo = False
            caja.save()
            form.save()

            # Redirigir a una página de éxito o lista de cierres de caja
            return redirect('close_caja')
    else:
        form = CierreForm()
    return render(request, 'close_caja.html', {'form': form, 'cajas': cajas })



@admin_required
def calculate_total_venta(request):
    if request.method == 'GET':
        caja_id = request.GET.get('caja_id')
        fecha_fin = request.GET.get('fecha_fin')
        
        if caja_id and fecha_fin:
            try:
                caja = Caja.objects.get(id_caja=caja_id)
                total_venta = Venta.objects.filter(
                    fecha__gte=caja.fecha_asignacion, 
                    fecha__lte=fecha_fin,
                    id_usuario=caja.usuario_id.id_usuario
                ).aggregate(Sum('total'))['total__sum'] or 0
                return JsonResponse({'total_venta': total_venta})
            except Caja.DoesNotExist:
                return JsonResponse({'error': 'Caja no encontrada'}, status=404)
        
    return JsonResponse({'error': 'Solicitud inválida'}, status=400)

''' 
@admin_required
def historico_caja(request):
   
    # Obtener las fechas de inicio y fin del formulario
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # Convertir las fechas a objetos datetime
    if fecha_inicio:
        fecha_inicio = parse_datetime(fecha_inicio)
    if fecha_fin:
        fecha_fin = parse_datetime(fecha_fin)

    # Filtrar aperturas y cierres basados en las fechas si están definidas
    aperturas = Caja.objects.all().order_by('fecha_asignacion')
    cierres = Cierre_Caja.objects.all().order_by('fecha_fin')

    if fecha_inicio and fecha_fin:
        aperturas = aperturas.filter(fecha_asignacion__range=[fecha_inicio, fecha_fin])
        cierres = cierres.filter(fecha_fin__range=[fecha_inicio, fecha_fin])
    elif fecha_inicio:
        aperturas = aperturas.filter(fecha_asignacion__gte=fecha_inicio)
        cierres = cierres.filter(fecha_fin__gte=fecha_inicio)
    elif fecha_fin:
        aperturas = aperturas.filter(fecha_asignacion__lte=fecha_fin)
        cierres = cierres.filter(fecha_fin__lte=fecha_fin)

    # Armar la respuesta con los datos filtrados
    data = []
    for apertura in aperturas:
        data.append({
            'tipo': 'Apertura',
            'id_caja': apertura.id_caja,
            'monto_asignado': apertura.monto_asignado,
            'fecha_asignacion': apertura.fecha_asignacion,
            'usuario': apertura.usuario_id.nombre
        })

    for cierre in cierres:
        data.append({
            'tipo': 'Cierre',
            'id_caja': cierre.id_caja,
            'total_diferencia': cierre.diferencia,
            'monto_entregado': cierre.monto_entregado,
            'monto_final': cierre.monto_final,
            'fecha_cierre': cierre.fecha_fin,
            'total_venta': cierre.total_venta
        })

    data.sort(key=lambda x: x.get('fecha_asignacion', x.get('fecha_cierre')))

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(data, safe=False)

    return render(request, 'historico_caja.html', {'data': data, 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin})

''' 

from django.utils.dateparse import parse_datetime

@admin_required
def historico_caja(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    aperturas = Caja.objects.all().order_by('fecha_asignacion')
    cierres = Cierre_Caja.objects.all().order_by('fecha_fin')

    if fecha_inicio and fecha_fin:
        fecha_inicio_dt = parse_datetime(fecha_inicio)
        fecha_fin_dt = parse_datetime(fecha_fin)
        if fecha_inicio_dt and fecha_fin_dt:
            aperturas = aperturas.filter(fecha_asignacion__gte=fecha_inicio_dt, fecha_asignacion__lte=fecha_fin_dt)
            cierres = cierres.filter(fecha_fin__gte=fecha_inicio_dt, fecha_fin__lte=fecha_fin_dt)

    data = {}

    # Procesar aperturas
    for apertura in aperturas:
        data[apertura.id_caja] = {
            'tipo': 'Apertura',
            'id_caja': apertura.id_caja,
            'usuario': apertura.usuario_id.nombre,
            'fecha_asignacion': apertura.fecha_asignacion,
            'monto_asignado': apertura.monto_asignado,
            'tipo_cierre': '',
            'fecha_cierre': '',
            'monto_cierre': '',
            'total_diferencia': '',
            'total_ventas': ''
        }

    # Procesar cierres y actualizar las aperturas existentes en data
    for cierre in cierres:
        if cierre.id_caja.id_caja in data:
            data[cierre.id_caja.id_caja].update({
                'tipo_cierre': 'Cierre',
                'fecha_cierre': cierre.fecha_fin,
                'monto_cierre': cierre.monto_entregado,
                'total_diferencia': cierre.diferencia,
                'total_ventas': cierre.total_venta
            })

    # Convertir el diccionario en una lista ordenada por fecha de asignación
    data_list = list(data.values())
    data_list.sort(key=lambda x: x['fecha_asignacion'])

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(data_list, safe=False)

    return render(request, 'historico_caja.html', { 'data': data_list, 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin })


@admin_required
def historico_ganancias(request):
    today = datetime.date.today()

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio:
        fecha_inicio = parse_date(fecha_inicio)
    else:
        fecha_inicio = today

    if fecha_fin:
        fecha_fin = parse_date(fecha_fin)
    else:
        fecha_fin = today

    ventas = Detalle_Venta.objects.all()
    if fecha_inicio and fecha_fin:
        ventas = ventas.filter(id_venta__fecha__range=[fecha_inicio, fecha_fin])
    elif fecha_inicio:
        ventas = ventas.filter(id_venta__fecha__gte=fecha_inicio)
    elif fecha_fin:
        ventas = ventas.filter(id_venta__fecha__lte=fecha_fin)

    ventas = ventas.annotate(
        costo_total_compra=F('cantidad') * F('id_producto__costo_compra')
    ).values(
        'id_producto__nombre',
        'cantidad',
        'precio_total',
        'id_producto__costo_compra',
        'costo_total_compra'
    )

    ventas_con_ganancia = []
    for venta in ventas:
        ganancia = venta['precio_total'] - venta['costo_total_compra']
        ventas_con_ganancia.append({
            **venta,
            'ganancia': ganancia
        })

    total_ganancias = sum(venta['ganancia'] for venta in ventas_con_ganancia)

    context = {
        'ventas': ventas_con_ganancia,
        'total_ganancias': total_ganancias,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    }

    return render(request, 'historico_ganancias.html', context)

@admin_required
def historico_rector(request):
    # Obtener la fecha actual
    today = datetime.date.today()

    # Obtener las fechas del formulario de filtro, si están presentes
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # Si las fechas son cadenas, convertirlas a objetos date, de lo contrario usar today
    if fecha_inicio:
        fecha_inicio = parse_date(fecha_inicio)
    else:
        fecha_inicio = today

    if fecha_fin:
        fecha_fin = parse_date(fecha_fin)
    else:
        fecha_fin = today

    # Filtrar las ventas por rango de fechas si se proporcionan
    ventas = Detalle_Venta.objects.all()
    if fecha_inicio and fecha_fin:
        ventas = ventas.filter(id_venta__fecha__range=[fecha_inicio, fecha_fin])
    elif fecha_inicio:
        ventas = ventas.filter(id_venta__fecha__gte=fecha_inicio)
    elif fecha_fin:
        ventas = ventas.filter(id_venta__fecha__lte=fecha_fin)

    # Seleccionar solo los datos necesarios: precio_total, costo_compra, y calcular la ganancia
    ventas = ventas.values(
        'precio_total',
        'id_producto__costo_compra',
        'cantidad'
    )

    ventas_con_ganancia = []
    for venta in ventas:
        # Calcular el costo total multiplicando el costo individual por la cantidad
        costo_total = venta['cantidad'] * venta['id_producto__costo_compra']
        # Calcular la ganancia restando el costo total del precio total
        ganancia = venta['precio_total'] - costo_total
        ventas_con_ganancia.append({
            'precio_total': venta['precio_total'],  # Precio de venta
            'costo_total': costo_total,             # Precio de compra (multiplicado por la cantidad)
            'ganancia': ganancia                    # Total de la ganancia
        })

    total_ganancias = sum(venta['ganancia'] for venta in ventas_con_ganancia)

    context = {
        'ventas': ventas_con_ganancia,
        'total_ganancias': total_ganancias,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    }

    return render(request, 'historico_rector.html', context)


def verificar_codigo(request):
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo')
        try:
            codigo = Codes.objects.get(code=codigo_ingresado)
            return JsonResponse({'valid': True})
        except Codes.DoesNotExist:
            return JsonResponse({'valid': False})
    return JsonResponse({'valid': False}, status=400)


#TEST PARA LA CONEXION DIRECTA A LA BD !!--11--1--121-01|0|020|920|93UR84U2RY2U3
'''
def test_db_view(request):
    db = Database()
    try:
        #probando para insertar --se insertara un cliente 
        insert_query = "INSERT INTO cliente (RFC, razon_social, USO_FACTURA, REGIMEN_FISCAL, CODIGO_POSTAL) VALUES (%s, %s, %s, %s, %s)"
        db.execute_query(insert_query,('GGGGGGGGGGGGG','CALAMARDO','SEPA','noce',76800))

        #verificando la inserciónn
        select_query = "SELECT * FROM cliente WHERE RFC= %s"
        resultados = db.fetch_all(select_query,('GGGGGGGGGGGGG'))

        resultado_str = "<br>".join([str(fila) for fila in resultados])
        return HttpResponse(f"Inserción exitosa.<br>Resultados obtenidos:<br>{resultado_str}")
    except Exception as e:
        return HttpResponse(f"Error: {e}")
    
    finally:
        db.close()'''