from whoosh.query import Or, And
from django.shortcuts import render, redirect, get_object_or_404
from .scrapping import populateDB
from .models import VideoJuego, Genero, Plataforma, Desarrolladores, CompañiaPlataforma
from .populateWhoosh import create_schema_videojuego
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from .forms import FechaLanzamientoForm, PlataformasForm, DesarrolladorDescripcionForm, GeneroNombreForm, RegisterForm, LoginForm, VideoJuegoForm
import datetime
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

# Create your views here.


def index(request):
    return render(request, 'index.html', {'videojuegos': VideoJuego.objects.all(), 'generos': Genero.objects.all(), 'plataformas': Plataforma.objects.all(), 'desarrolladores': Desarrolladores.objects.all(), 'compañias': CompañiaPlataforma.objects.all()})


def buscar_fecha_lanzamiento(request):
    ix = open_dir("indice_videojuegos")
    form = FechaLanzamientoForm()
    if request.method == 'POST':
        form = FechaLanzamientoForm(request.POST)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            with ix.searcher() as searcher:
                query = QueryParser("fecha_lanzamiento", ix.schema).parse(
                    'fecha_lanzamiento:[{} TO {}]'.format(fecha, datetime.datetime.now().date().isoformat()))
                results = searcher.search(
                    query, limit=10, sortedby="fecha_lanzamiento")
                return render(request, 'buscar_videojuegos_fecha_lanzamiento.html', {'videojuegos': results, 'form': form})
        else:
            return render(request, 'buscar_videojuegos_fecha_lanzamiento.html', {'form': form})
    else:
        return render(request, 'buscar_videojuegos_fecha_lanzamiento.html', {'form': form})


def buscar_videojuegos_plataformas(request):
    ix = open_dir("indice_videojuegos")
    form = PlataformasForm()
    if request.method == 'POST':
        form = PlataformasForm(request.POST)
        if form.is_valid():
            nombre_plataforma = form.cleaned_data['plataforma'].nombre
            with ix.searcher() as searcher:
                query = QueryParser("plataformas", ix.schema).parse(
                    f'"{nombre_plataforma}"')
                results = searcher.search(
                    query, limit=5, sortedby="fecha_lanzamiento")
                return render(request, 'buscar_videojuegos_plataformas.html', {'videojuegos': results, 'form': form})
        else:
            return render(request, 'buscar_videojuegos_plataformas.html', {'form': form})
    else:
        return render(request, 'buscar_videojuegos_plataformas.html', {'form': form})


def buscar_desarrollador_o_descripcion(request):
    ix = open_dir("indice_videojuegos")
    form = DesarrolladorDescripcionForm()
    if request.method == 'POST':
        form = DesarrolladorDescripcionForm(request.POST)
        if form.is_valid():
            en = form.cleaned_data['busqueda']
            desarrollador = form.cleaned_data['desarrollador']
            sp = desarrollador.nombre if desarrollador else ''
            with ix.searcher() as searcher:
                query_desarrollador = QueryParser(
                    "desarrolladores", ix.schema).parse('"' + sp + '"') if sp else None
                query_descripcion = QueryParser(
                    "descripcion", ix.schema).parse('"' + en + '"') if en else None
                query = Or(
                    [q for q in [query_desarrollador, query_descripcion] if q is not None])
                results = searcher.search(query, limit=5)
                return render(request, 'buscar_desarrollador_o_descripcion.html', {'videojuegos': results, 'form': form})
    else:
        return render(request, 'buscar_desarrollador_o_descripcion.html', {'form': form})


def buscar_genero_y_nombre(request):
    ix = open_dir("indice_videojuegos")
    form = GeneroNombreForm()
    if request.method == 'POST':
        form = GeneroNombreForm(request.POST)
        if form.is_valid():
            en = form.cleaned_data['busqueda']
            sp = form.cleaned_data['generos'].nombre
            with ix.searcher() as searcher:
                nombre_query = QueryParser("nombre", ix.schema).parse(en)
                generos_query = QueryParser(
                    "genero", ix.schema).parse(f'"{sp}"')
                query = And([nombre_query, generos_query])
                results = searcher.search(query, limit=20)
                return render(request, 'buscar_genero_y_nombre.html', {'videojuegos': results, 'form': form})
        else:
            return render(request, 'buscar_genero_y_nombre.html', {'form': form})
    else:
        return render(request, 'buscar_genero_y_nombre.html', {'form': form})


@user_passes_test(lambda u: u.is_anonymous, login_url='index')
def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            firstname = form.cleaned_data['first_name']
            if User.objects.filter(username__iexact=username).exists():
                form.add_error(
                    'username', 'El nombre de usuario ya existe')
                return render(request, 'registro.html', {'form': form})
            if User.objects.filter(email__iexact=email).exists():
                form.add_error(
                    'email', 'El email ya existe')
                return render(request, 'registro.html', {'form': form})
            if User.objects.filter(first_name__iexact=firstname).exists():
                form.add_error(
                    'first_name', 'El nombre ya existe')
                return render(request, 'registro.html', {'form': form})
            user = User.objects.create_user(
                username=username, email=email, password=form.cleaned_data['password'])

            user.first_name = firstname
            user.last_name = form.cleaned_data['last_name']
            user.save()
            return redirect('login')
    return render(request, 'registro.html', {'form': form})


@user_passes_test(lambda u: u.is_anonymous, login_url='index')
def iniciar_sesion(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data["password"]
            if not User.objects.filter(username=username).exists():
                form.add_error(
                    'username', 'El nombre de usuario no existe')
                return render(request, 'login.html', {'form': form})
            if not check_password(password, User.objects.get(username=username).password):
                form.add_error(
                    'password', 'La contraseña no es correcta')
                return render(request, 'login.html', {'form': form})
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    return render(request, 'login.html', {'form': form})


@user_passes_test(lambda u: u.is_authenticated, login_url='index')
def cerrar_sesion(request):
    logout(request)
    return redirect('index')


@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def cargar(request):
    if request.method == 'POST':
        if request.POST['cargar'] == 'Si':
            populateDB()
            print('Cargando BD y creando esquema de videojuegos')
            create_schema_videojuego()
            print('BD cargada y esquema de videojuegos creado')
            return render(request, 'cargar_BD.html', {'videojuegos': VideoJuego.objects.all(), 'generos': Genero.objects.all(), 'plataformas': Plataforma.objects.all(), 'desarrolladores': Desarrolladores.objects.all(), 'compañias': CompañiaPlataforma.objects.all()})
        else:
            return redirect("index")
    return render(request, 'confirmar_carga_BD.html')

@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def recomendar_videojuegos(request):
    if request.method == 'POST':
        form = VideoJuegoForm(request.POST)
        if form.is_valid():
            nombre_videojuego = form.cleaned_data['nombre_videojuego']
            videojuegos_recomendados = obtener_recomendaciones(nombre_videojuego)
            return render(request, 'recomendar_videojuegos.html', {'form': form, 'videojuegos_recomendados': videojuegos_recomendados})
    else:
        form = VideoJuegoForm()
    return render(request, 'recomendar_videojuegos.html', {'form': form})

def calcular_similitud():
    videojuegos = VideoJuego.objects.all()
    descripciones = videojuegos.values_list(
        'plataformas__nombre', 'genero__nombre', 'temas', 'desarrolladores__nombre')
    descripciones = [' '.join(map(str, desc)) for desc in descripciones]

    # Crear un vector de características para cada videojuego
    vectorizer = TfidfVectorizer()
    matriz_tfidf = vectorizer.fit_transform(descripciones)

    # Calcular la similitud del coseno
    similitud_cos = linear_kernel(matriz_tfidf, matriz_tfidf)

    # Para cada videojuego, obtener las 10 videojuegos más similares
    indices = pd.Series(range(len(videojuegos)), index=[
                        videojuego.nombre.lower() for videojuego in videojuegos]).drop_duplicates()

    return similitud_cos, indices, videojuegos


def obtener_recomendaciones(nombre_videojuego):
    similitud_cos, indices, videojuegos = calcular_similitud()
    nombre_videojuego = nombre_videojuego.lower()
    if nombre_videojuego not in indices:
        return []
    idx = indices[nombre_videojuego]
    sim_scores = list(enumerate(similitud_cos[idx].flatten()))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores if i[0] < len(videojuegos)]
    return [videojuegos[i] for i in movie_indices]

def detalle_videojuego(request, id):
    videojuego = get_object_or_404(VideoJuego, pk=id)
    return render(request, 'detalle_videojuego.html', {'videojuego': videojuego})

def detalle_plataforma(request, plataforma_id):
    plataforma = get_object_or_404(Plataforma, pk=plataforma_id)
    return render(request, 'detalle_plataforma.html', {'plataforma': plataforma})