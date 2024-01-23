import http.client
from bs4 import BeautifulSoup

from .models import Plataforma, Genero, Desarrolladores, VideoJuego, CompañiaPlataforma
from datetime import datetime

import os
import urllib.request
import ssl
import re
import urllib.error


if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def permiso(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        'Accept-Language': 'es'
    }
    request = urllib.request.Request(
        "https://www.giantbomb.com" + url, headers=headers)
    try:
        f = urllib.request.urlopen(request)
        return BeautifulSoup(f, 'lxml')
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("Error 403: Forbidden. The server denied the access.")


def populateCompañiaPlataforma(datos_plataformas):
    if datos_plataformas[6].find('span') is None:
        nombre_compañia = "Sin Compañia"
    else:
        nombre_compañia = datos_plataformas[6].find('span').text.strip()

    # Populate CompañiaPlataforma
    compañia, created = CompañiaPlataforma.objects.get_or_create(
        nombre=nombre_compañia)
    return compañia


def populatePlataforma(s):
    plataformas = []
    try:
        site_main = s.find("div", id='site-main')
        if site_main is not None:
            plataformas = site_main.find(
                "section", id='river').ul.find_all("li")
        else:
            print("Could not find div with id 'site-main'")
    except AttributeError:
        print("An AttributeError occurred")
    pl = None
    for plataforma in plataformas:
        if plataforma.h3 is not None:
            nombre = plataforma.h3.text.strip()
        url_plataforma = plataforma.a['href']
        s2 = permiso(url_plataforma)

        try:
            site = s2.find("div", id='site')
            if site is not None:
                datos_plataformas = site.aside.find(
                    "div", class_='wiki-details').table.find_all('tr')
            else:
                print("Could not find div with id 'site'")
        except AttributeError:
            print("An AttributeError occurred")

        fecha_salida = None
        if datos_plataformas[2] is not None:
            fecha_salida = datos_plataformas[2].find('span').text.strip()
            if fecha_salida:  # Check if fecha_salida is not an empty string
                try:
                    fecha_salida = datetime.strptime(
                        fecha_salida, "%B %d, %Y").date()
                except ValueError:
                    try:
                        fecha_salida = datetime.strptime(
                            fecha_salida, "%B %Y").date()
                    except ValueError:
                        fecha_salida = datetime.strptime(
                            fecha_salida, "%Y").date()
            else:
                fecha_salida = None

        total_videojuegos = None
        if datos_plataformas[8].p is not None:
            total_videojuegos = datos_plataformas[8].p.text.strip().split(" ")[
                0]

        precio_original = None
        if datos_plataformas[5].span is not None:
            precio_original = float(datos_plataformas[5].span.text.strip().replace(
                "$", "").replace(",", "."))

        try:
            site = s2.find("div", class_='kubrick-strip')
            if site is not None:
                pic_url = site.div.img['src']
            else:
                print("Could not find div with id 'site'")
        except AttributeError:
            print("An AttributeError occurred")
        if pic_url is not None:
            picture_url = site.div.img['src']
        else:
            picture_url = "Sin imagen"

        # Populate CompañiaPlataforma
        compañia = populateCompañiaPlataforma(datos_plataformas)

        pl, created = Plataforma.objects.get_or_create(nombre=nombre, fecha_salida=fecha_salida, total_videojuegos=total_videojuegos,
                                                       compañia_plataforma=compañia, precio_original=precio_original, picture_url=picture_url)

    return pl


def populateVideoJuego(url):
    for i in range(1, 10):
        url_paginada = "https://www.giantbomb.com" + url + "?page=" + str(i)
        try:
            f = urllib.request.urlopen(url_paginada)
        except http.client.IncompleteRead:
            continue
        s2 = BeautifulSoup(f, 'lxml')
        datos = s2.find("div", id='site').find("ul").find_all("li")
        for dato in datos:
            if dato.h3 is not None:
                nombre = dato.h3.text.strip()
                url_videojuego = dato.a['href']
                s3 = permiso(url_videojuego)
                try:
                    site = s3.find("div", id='site-main')
                    if site is not None:
                        datos_videojuego = site.aside.find(
                            "div", class_='wiki-details').table.find_all('tr')
                    else:
                        print("Could not find div with id 'site-main'")

                except AttributeError:
                    print("An AttributeError occurred")
                fecha_lanzamiento = datos_videojuego[1].find(
                    'span').text.strip()
                if fecha_lanzamiento == "N/A":
                    fecha_lanzamiento = None
                else:
                    try:
                        fecha_lanzamiento = datetime.strptime(
                            fecha_lanzamiento, "%B %d, %Y").date()
                    except ValueError:
                        try:
                            fecha_lanzamiento = datetime.strptime(
                                fecha_lanzamiento, "%B %Y").date()
                        except ValueError:
                            try:
                                fecha_lanzamiento = datetime.strptime(
                                    fecha_lanzamiento, "%Y").date()
                            except ValueError:
                                if re.match(r'Q[1-4] \d{4}', fecha_lanzamiento):
                                    quarter, year = fecha_lanzamiento.split()
                                    month = (int(quarter[1]) - 1) * 3 + 1
                                    fecha_lanzamiento = datetime.strptime(
                                        f'{year}-{month}-01', "%Y-%m-%d").date()
                                else:
                                    print("Could not convert date: ",
                                          fecha_lanzamiento)
                try:
                    site = s3.find("div", id='site-main')
                    if site is not None:
                        etiqueta = site.find("div", class_='kubrick-cover')
                    else:
                        print("Could not find div with id 'site'")
                except AttributeError:
                    print("An AttributeError occurred")
                if etiqueta is not None:
                    descripcion = site.find(
                        "div", class_='kubrick-cover').find("div", class_='wiki-deck').h3.text.strip()
                else:
                    descripcion = "Sin descripción"

                temas = datos_videojuego[6].find('a')
                if temas is None:
                    temas = "Sin temas"
                else:
                    temas = temas.text.strip()
                picture_url = dato.a.img['src']

                # Populate VideoJuego
                videojuego, created = VideoJuego.objects.get_or_create(
                    nombre=nombre, fecha_lanzamiento=fecha_lanzamiento, descripcion=descripcion, temas=temas, picture_url=picture_url)

                # asociar las plataformas con el videojuego
                plataformas = datos_videojuego[2].find_all('a')
                for pl in plataformas:
                    nombre_plataforma = pl.text.strip()
                    plataforma = Plataforma.objects.get(
                        nombre=nombre_plataforma)
                    videojuego.plataformas.add(plataforma)

                # asociar los generos con el videojuego
                generos = datos_videojuego[5].find_all('a')
                for g in generos:
                    nombre_genero = g.text.strip()
                    genero, created = Genero.objects.get_or_create(
                        nombre=nombre_genero)
                    videojuego.genero.add(genero)

                # asociar los desarrolladores con el videojuego
                desarrolladores = datos_videojuego[3].find_all('a')
                for d in desarrolladores:
                    nombre_desarrollador = d.text.strip()
                    desarrollador, created = Desarrolladores.objects.get_or_create(
                        nombre=nombre_desarrollador)
                    videojuego.desarrolladores.add(desarrollador)


def populateDB():
    # Delete all data from DB
    Plataforma.objects.all().delete()
    CompañiaPlataforma.objects.all().delete()
    Genero.objects.all().delete()
    Desarrolladores.objects.all().delete()
    VideoJuego.objects.all().delete()

    s = permiso("")
    url_videojuegos = s.find("div", id='site-main').find("header", id='masthead').find(
        "div", class_='js-masthead-nav masthead-nav').find_all("li")[21].find("a")['href']
    url_plataformas = s.find("div", id='site-main').find("header", id='masthead').find(
        "div", class_='js-masthead-nav masthead-nav').find_all("li")[21].find_all("a")[5]['href']
    for i in range(1, 7):
        s3 = permiso(url_plataformas + "?page=" + str(i))

        # Populate Plataforma
        populatePlataforma(s3)

    # Populate VideoJuego
    populateVideoJuego(url_videojuegos)
