from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('buscar_fecha_lanzamiento', views.buscar_fecha_lanzamiento,
         name='buscar_fecha_lanzamiento'),
    path('buscar_videojuegos_plataformas', views.buscar_videojuegos_plataformas,
         name='buscar_videojuegos_plataformas'),
    path('buscar_desarrollador_o_descripcion', views.buscar_desarrollador_o_descripcion,
         name='buscar_desarrollador_o_descripcion'),
    path('buscar_genero_y_nombre', views.buscar_genero_y_nombre,
         name='buscar_genero_y_nombre'),
    path('registro', views.register, name='registro'),
    path('login', views.iniciar_sesion, name='login'),
    path('logout', views.cerrar_sesion, name='logout'),
    path('cargar', views.cargar, name='cargar'),
    path('recomendar_videojuegos', views.recomendar_videojuegos, name='recomendar_videojuegos'),
    path('videojuego/<int:id>', views.detalle_videojuego, name='detalle_videojuego'),
    path('plataforma/<int:plataforma_id>', views.detalle_plataforma, name='detalle_plataforma'),
]
