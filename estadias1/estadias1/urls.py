"""estadias1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from accounts import views
from accounts.views import ticket_generator
#from django_select2 import views as select2_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('ticket-generator/', ticket_generator, name='ticket_generator'),#i'm proud of this shit
    
    #path('', LoginView.as_view(template_name='index.html'), name = 'login'),
    path('', views.index, name='login'),

    path('first_caja/',views.caja,name="caja"),

    path('open_caja/',views.open_caja,name="open_caja"),

    path('close_caja/',views.close_caja,name="close_caja"),

    path('registro_venta/',views.registro_ventas,name="ventas"),
    
    path('registrar_clientes/',views.registrar_cliente,name='cliente'),
    
    path('registro_compra/',views.registrar_compra,name='compra'),
    
    path('registrar_proveedor/',views.registrar_proveedor,name='proveedor'),
    
    path('registrar_inventario/',views.registrar_producto,name='producto'),

    path('producto/eliminar/<int:id_producto>/', views.eliminar_producto, name='eliminar_producto'),
    
    path('menu_principal/', views.menu_principal, name='menu_principal'),
    
    path('historico_compras/', views.historico_compras, name='historicoCompras'),
    
    path('historico_ventas/', views.historico_ventas, name='historicoVentas'),
    
    path('registro_categoria/', views.registrar_categoria, name='altaCategoria'),

    path('registro_usuario/',views.registro_usuario, name='usuario'),

    path('detalle_compra/',views.detalle_compra, name='detalle_compra'),
    
    path('detalle_venta/',views.detalle_venta, name='detalle_venta'),

    path('logout/', views.logout_view, name='logout'),

    path('historico_caja/', views.historico_caja, name='historico_caja'),

    path('historico_ganancias/', views.historico_ganancias, name='ganancias'),
    
    path('historico_rector/', views.historico_rector, name='rector'),

    path('registro_codes/', views.codes, name='codes'),
    
    path('verificar_codigo/', views.verificar_codigo, name='verificar_codigo'),

    path('calculate_total_venta/', views.calculate_total_venta, name='calculate_total_venta'),
    
    #prueba coneksion a la bd directo
    #path('test_db/',views.test_db_view, name='test_db'),

    #path('select2/', views.ProveedorSelect2View.as_view(), namespace='select2_proveedor'),

]

