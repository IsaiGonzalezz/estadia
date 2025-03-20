from django.db import models
from django.contrib.auth.models import AbstractUser


#Commented bcs this isn't working
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    rol = models.BooleanField(default=False)
    password = models.CharField(max_length=512)

    class Meta:
        db_table = 'usuario'
        managed = False
    def __str__(self):
        return self.nombre


#class Usuario(models.Model):
#    db_table = 'USUARIO' 
#    id_usuario = models.AutoField(primary_key=True)
#    nombre = models.CharField(max_length=255)
#    privilegio = models.CharField(max_length=255)
#    password = models.CharField(max_length=255)
#    managed = False


#MÉTODOS DEL CLIENTE "-------------UWU------------------"
class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    rfc = models.CharField(max_length=13)
    razon_social = models.CharField(max_length=255)
    uso_factura = models.CharField(max_length=255)
    regimen_fiscal = models.CharField(max_length=255)
    codigo_postal = models.IntegerField()

    class Meta:
        db_table = "cliente"
        managed = False

    def __str__(self):
        return self.razon_social if self.razon_social else 'Cliente sin razón social'


class Proveedor(models.Model): 
    id_proveedor = models.AutoField(primary_key=True)
    razon_social = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=255)
    municipio = models.CharField(max_length=255)
    estado = models.CharField(max_length=255)
    cp = models.IntegerField()
    telefono = models.CharField(max_length=20)
    rfc = models.CharField(max_length=12)

    class Meta:
        db_table = 'proveedor'
        managed = False 
    def __str__(self):
        return self.razon_social


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=255)

    class Meta : 
        db_table = 'categoria_producto'
        managed = False
    def __str__(self):
        return self.descripcion
    

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    stock = models.IntegerField()
    nombre = models.CharField(max_length=255)
    id_categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL,db_column='id_categoria',null=True)
    costo_venta = models.DecimalField(decimal_places=2, max_digits=10)
    costo_compra = models.DecimalField(decimal_places=2, max_digits=10)
    porcentaje_utilidad = models.DecimalField(decimal_places=2, max_digits=5)
    punto_reorden = models.IntegerField()
    estado = models.BooleanField(default=False)

    class Meta :
        db_table = 'producto'
        managed = False
    def __str__(self):
        return self.nombre


class Compra(models.Model):
    id_compra = models.AutoField(primary_key=True)
    total = models.DecimalField(decimal_places=2, max_digits=10)
    fecha = models.DateField()
    id_proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL,db_column='id_proveedor',null=True)

    class Meta : 
        db_table = 'compra'
        managed = False



class Detalle_Compra(models.Model):
    id_detallecompra = models.AutoField(primary_key=True)
    id_compra = models.ForeignKey(Compra, on_delete=models.SET_NULL, db_column='id_compra',null=True)
    id_producto = models.ForeignKey(Producto,on_delete=models.SET_NULL, db_column='id_producto',null=True)
    cantidad = models.IntegerField()
    costo = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'detalle_compra'
        managed = False



class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    fecha = models.DateTimeField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, db_column='id_usuario',null=True)

    class Meta:
        db_table = 'venta'
        managed = False

        

class Detalle_Venta(models.Model):
    id_detalleventa = models.AutoField(primary_key=True)
    id_venta = models.ForeignKey(Venta, on_delete=models.SET_NULL, db_column='id_venta', null=True)
    id_producto = models.ForeignKey(Producto,on_delete=models.SET_NULL, db_column='id_producto',null=True)
    #id_cliente = models.ForeignKey(Cliente,on_delete=models.SET_NULL, db_column='id_cliente', null=True)
    cantidad = models.IntegerField()
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        db_table = 'detalle_venta'
        managed = False


        
class Caja(models.Model):
    id_caja = models.AutoField(primary_key=True)
    usuario_id = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='usuario_id')
    billetes_1000 = models.IntegerField()
    billetes_500 = models.IntegerField()
    billetes_200 = models.IntegerField()
    billetes_100 = models.IntegerField()
    billetes_50 = models.IntegerField()
    billetes_20 = models.IntegerField()
    monedas = models.DecimalField(max_digits=10, decimal_places=2)
    monto_asignado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_asignacion = models.DateTimeField()
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'caja'
        managed = False

    def __str__(self):
        return f"Caja: {self.id_caja}"



class Cierre_Caja(models.Model):
    id_cierre = models.AutoField(primary_key=True)
    id_caja = models.ForeignKey(Caja, on_delete=models.CASCADE, db_column='id_caja')
    billetes_1000 = models.IntegerField()
    billetes_500 = models.IntegerField()
    billetes_200 = models.IntegerField()
    billetes_100 = models.IntegerField()
    billetes_50 = models.IntegerField()
    billetes_20 = models.IntegerField()
    monedas = models.DecimalField(max_digits=10, decimal_places=2)
    monto_entregado = models.DecimalField(max_digits=10, decimal_places=2)
    monto_final = models.DecimalField(max_digits=10, decimal_places=2)
    diferencia =  models.DecimalField(max_digits=10, decimal_places=2)
    fecha_fin = models.DateTimeField()
    total_venta = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        db_table = 'cierre_caja'
        managed = False


class Codes(models.Model):
    id_code = models.AutoField(primary_key=True)
    code = models.IntegerField()
    class Meta:
        db_table = 'codes'
        managed = False
