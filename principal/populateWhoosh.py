from whoosh.index import create_in
from whoosh.fields import *
from .models import VideoJuego
import os
import shutil
from datetime import datetime


def create_schema_videojuego():
    shema = Schema(id=ID(stored=True, unique=True), nombre=TEXT(stored=True, phrase=True), fecha_lanzamiento=DATETIME(stored=True),
                   descripcion=TEXT(stored=True), plataformas=KEYWORD(stored=True, commas=True), genero=KEYWORD(stored=True, commas=True), temas=TEXT(stored=True, phrase=True), desarrolladores=KEYWORD(stored=True, commas=True), picture_url=ID(stored=True, unique=True))

    if os.path.exists("indice_videojuegos"):
        shutil.rmtree("indice_videojuegos")
    os.mkdir("indice_videojuegos")

    ix = create_in("indice_videojuegos", shema)
    writer = ix.writer()

    lista_videojuegos = VideoJuego.objects.all()
    for videojuego in lista_videojuegos:
        plataformas = ','.join([str(plataforma.nombre)
                               for plataforma in videojuego.plataformas.all()])
        generos = ','.join([str(g.nombre)
                           for g in videojuego.genero.all()])
        desarrolladores = ','.join([str(d.nombre)
                                   for d in videojuego.desarrolladores.all()])
        if videojuego.fecha_lanzamiento is None:
            continue
        fecha_lanzamiento = datetime.combine(
            videojuego.fecha_lanzamiento, datetime.min.time())

        writer.add_document(id=str(videojuego.id), nombre=videojuego.nombre, fecha_lanzamiento=fecha_lanzamiento, descripcion=videojuego.descripcion,
                            plataformas=plataformas, genero=generos, temas=videojuego.temas, desarrolladores=desarrolladores, picture_url=videojuego.picture_url)
    writer.commit()
