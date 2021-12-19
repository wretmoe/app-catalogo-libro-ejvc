from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from werkzeug.utils import redirect

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://zpfddoncwinjgp:735374770cda71c6280417cf91c0ff84597b5f219d6a0b698da2edcd410c227d@ec2-54-197-43-39.compute-1.amazonaws.com:5432/daqcmgrfv7tk2b"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Usuarios(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80))
    password = db.Column(db.String(255))

    def __init__(self, email, password):
        self.email = email
        self.password = password

class Editorial(db.Model):
    __tablename__ = "editorial"
    id_editorial = db.Column(db.Integer, primary_key=True)
    nombre_editorial = db.Column(db.String(80))

    def __init__(self, nombre_editorial):
        self.nombre_editorial = nombre_editorial

class Libro(db.Model):
    __tablename__ = "libro"
    id_libro = db.Column(db.Integer, primary_key=True)
    titulo_libro = db.Column(db.String(80))
    fecha_publicacion = db.Column(db.Date)
    numero_paginas = db.Column(db.Integer)
    formato = db.Column(db.String(30))
    volumen = db.Column(db.Integer)

    #Relacion
    id_editorial = db.Column(db.Integer, db.ForeignKey("editorial.id_editorial"))
    id_autor = db.Column(db.Integer, db.ForeignKey("autor.id_autor"))
    id_genero = db.Column(db.Integer, db.ForeignKey("genero.id_genero"))

    def __init__(self, titulo_libro, fecha_publicacion, numero_paginas, formato, volumen, id_editorial, id_autor, id_genero):
        self.titulo_libro = titulo_libro
        self.fecha_publicacion = fecha_publicacion
        self.numero_paginas = numero_paginas = numero_paginas
        self.formato = formato
        self.volumen = volumen
        self.id_editorial = id_editorial
        self.id_autor = id_autor
        self.id_genero = id_genero

class Autor(db.Model):
    __tablename__ = "autor"
    id_autor = db.Column(db.Integer, primary_key=True)
    nombre_autor = db.Column(db.String(80))
    fecha_nacimiento = db.Column(db.Date)
    nacionalidad = db.Column(db.String(80))

    def __init__(self, nombre_autor, fecha_nacimiento, nacionalidad):
        self.nombre_autor = nombre_autor
        self.fecha_nacimiento = fecha_nacimiento
        self.nacionalidad = nacionalidad

class Genero(db.Model):
    __tablename__ = "genero"
    id_genero = db.Column(db.Integer, primary_key=True)
    nombre_genero = db.Column(db.String(80))

    def __init__(self, nombre_genero):
        self.nombre_genero = nombre_genero

class Misfavoritos(db.Model):
    __tablename__ = "misfavoritos"
    id_favoritos = db.Column(db.Integer, primary_key=True)

    #Relacion
    id_libro = db.Column(db.Integer, db.ForeignKey("libro.id_libro"))
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"))

    def __init__(self, id_libro, id_usuario):
        self.id_libro = id_libro
        self.id_usuario = id_usuario

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/iniciologin", methods=['POST'])
def iniciologin():
    email = request.form["E-mail"]
    password = request.form["password"]
    #password_cifrado = bcrypt.generate_password_hash(password)
    consulta_usuario = Usuarios.query.filter_by(email=email).first()
    print(consulta_usuario.email)
    bcrypt.check_password_hash(consulta_usuario.password,password)
    return redirect("/leerlibro")

@app.route("/registrar")
def registrar():
    return render_template("registro.html")

@app.route("/registrar_usuario",  methods=['POST'])
def registrar_usuario():
    email = request.form["E-mail"]
    password = request.form["password"]
    password_cifrado = bcrypt.generate_password_hash(password).decode('utf-8')
    print(password_cifrado)

    usuario = Usuarios(email = email, password = password_cifrado)
    db.session.add(usuario)
    db.session.commit()
    return redirect("/")

#----------libro----------
@app.route("/leerlibro")
def leerlibro():
    consulta_libro = Libro.query.join(Genero, Libro.id_genero == Genero.id_genero).join(Autor, Libro.id_autor == Autor.id_autor).join(Editorial, Libro.id_editorial == Editorial.id_editorial).add_columns(Libro.id_libro, Libro.titulo_libro, Libro.fecha_publicacion, Libro.numero_paginas, Libro.formato, Libro.volumen, Editorial.nombre_editorial, Genero.nombre_genero, Autor.nombre_autor)
    
    return render_template("catalogoLibro.html", consulta_libro = consulta_libro)

@app.route("/favoritos/<id>")
def favoritos(id):
    consulta_favoritos = Libro.query.filter_by(id_libro=int(id)).first()
    return render_template("favoritos.html", consulta_favoritos = consulta_favoritos)

@app.route("/eliminarlibro/<id>")
def eliminarlibro(id):
    Libro.query.filter_by(id_libro=int(id)).delete()
    db.session.commit()
    return redirect("/leerlibro")

@app.route("/editarlibro/<id>")
def editarlibro(id):
    libro = Libro.query.filter_by(id_libro=int(id)).first()
    return render_template("modificarLibro.html", libro = libro)

@app.route("/modificarlibro", methods=['POST'])
def modificarlibro():
    id_nuevo = request.form["id_libro"]
    titulo_nuevo = request.form["titulo_libro"]
    fecha_nueva = request.form["fecha_publicacion"]
    paginas_nuevas = request.form["numero_paginas"]
    formato_nuevo = request.form["formato"]
    volumen_nuevo = request.form["volumen"]
    editorial_nuevo = request.form["editorial"]
    genero_nuevo = request.form["genero"]
    autor_nuevo = request.form["autor"]
    libro = Libro.query.filter_by(id_libro=int(id_nuevo)).first()
    libro.titulo_libro = titulo_nuevo
    libro.fecha_publicacion = fecha_nueva
    libro.numero_paginas = paginas_nuevas
    libro.formato = formato_nuevo
    libro.volumen = volumen_nuevo
    libro.editorial = editorial_nuevo
    libro.genero = genero_nuevo
    libro.autor = autor_nuevo
    db.session.commit()
    return redirect("/leerlibro")

@app.route("/libro")
def libro():
    consulta_editorial = Editorial.query.all()
    consulta_genero = Genero.query.all()
    consulta_autor = Autor.query.all()
    return render_template("libro.html", consulta_editorial = consulta_editorial, consulta_genero = consulta_genero, consulta_autor = consulta_autor)

@app.route("/registrarlibro", methods=['POST'])
def registrarlibro():
    titulo_libro = request.form["titulo_libro"]
    fecha_publicacion = request.form["fecha_publicacion"]
    numero_paginas = request.form["numero_paginas"]
    formato = request.form["formato"]
    volumen = request.form["volumen"]
    id_editorial = request.form["editorial"]
    id_genero = request.form["genero"]
    id_autor = request.form["autor"]
    volumen_int = int(volumen)
    numero_paginas_int = int(numero_paginas)
    libro_nuevo = Libro(titulo_libro = titulo_libro, fecha_publicacion=fecha_publicacion, numero_paginas=numero_paginas_int, formato=formato, volumen=volumen_int, id_editorial=id_editorial, id_genero=id_genero, id_autor=id_autor)
    db.session.add(libro_nuevo)
    db.session.commit()
    return redirect("/leerlibro")

#----------editorial----------
@app.route("/leereditorial")
def leereditorial():
    consulta_editorial = Editorial.query.all()
    for editorial in consulta_editorial:
        editorial.nombre_editorial
    return render_template("catalogoEditorial.html", consulta_editorial = consulta_editorial)

@app.route("/eliminareditorial/<id>")
def eliminareditorial(id):
    Editorial.query.filter_by(id_editorial=int(id)).delete()
    db.session.commit()
    return redirect("/leereditorial")

@app.route("/editareditorial/<id>")
def editareditorial(id):
    editorial = Editorial.query.filter_by(id_editorial=int(id)).first()
    return render_template("modificarEditorial.html", editorial = editorial)

@app.route("/modificareditorial", methods=['POST'])
def modificareditorial():
    id_nuevo = request.form["id_editorial"]
    nombre_nuevo = request.form["nombre_editorial"]
    
    editorial = Editorial.query.filter_by(id_editorial=int(id_nuevo)).first()
    editorial.nombre_editorial = nombre_nuevo
    db.session.commit()
    return redirect("/leereditorial")

@app.route("/registrareditorial", methods=["POST"])
def registrareditorial():
    nombre_editorial = request.form["nombre_editorial"]
    nueva_editorial = Editorial(nombre_editorial = nombre_editorial)
    db.session.add(nueva_editorial)
    db.session.commit()
    return redirect("/leereditorial")

#----------autor----------
@app.route("/leerautor")
def leerautor():
    consulta_autor = Autor.query.all()
    for autor in consulta_autor:
        autor.nombre_autor
        autor.fecha_nacimiento
        autor.nacionalidad
    return render_template("catalogoAutor.html", consulta_autor = consulta_autor)

@app.route("/eliminarautor/<id>")
def eliminarautor(id):
    Autor.query.filter_by(id_autor=int(id)).delete()
    db.session.commit()
    return redirect("/leerautor")

@app.route("/editarautor/<id>")
def editarautor(id):
    autor = Autor.query.filter_by(id_autor=int(id)).first()
    return render_template("modificarAutor.html", autor = autor)

@app.route("/modificarautor", methods=['POST'])
def modificarautor():
    id_nuevo = request.form["id_autor"]
    nombre_nuevo = request.form["nombre_autor"]
    nacimiento_nuevo = request.form["fecha_nacimiento"]
    nacionalidad_nueva = request.form["nacionalidad"]
    
    autor = Autor.query.filter_by(id_autor=int(id_nuevo)).first()
    autor.nombre_autor = nombre_nuevo
    autor.fecha_nacimiento = nacimiento_nuevo
    autor.nacionalidad = nacionalidad_nueva
    db.session.commit()
    return redirect("/leerautor")

@app.route("/registrarautor", methods=["POST"])
def registrarautor():
    nombre_autor = request.form["nombre_autor"]
    fecha_nacimiento = request.form["fecha_nacimiento"]
    nacionalidad = request.form["nacionalidad"]
    nuevo_autor = Autor(nombre_autor = nombre_autor, fecha_nacimiento = fecha_nacimiento, nacionalidad = nacionalidad)
    db.session.add(nuevo_autor)
    db.session.commit()
    return redirect("/leerautor")

#----------genero----------
@app.route("/leergenero")
def leergenero():
    consulta_genero = Genero.query.all()
    for genero in consulta_genero:
        genero.nombre_genero
    return render_template("catalogoGenero.html", consulta_genero = consulta_genero)

@app.route("/eliminargenero/<id>")
def eliminargenero(id):
    Genero.query.filter_by(id_genero=int(id)).delete()
    db.session.commit()
    return redirect("/leergenero")

@app.route("/editargenero/<id>")
def editargenero(id):
    genero = Genero.query.filter_by(id_genero=int(id)).first()
    return render_template("modificarGenero.html", genero = genero)

@app.route("/modificargenero", methods=['POST'])
def modificargenero():
    id_nuevo = request.form["id_genero"]
    nombre_nuevo = request.form["nombre_genero"]
    genero = Genero.query.filter_by(id_genero=int(id_nuevo)).first()
    genero.nombre_genero = nombre_nuevo
    db.session.commit()
    return redirect("/leergenero")

@app.route("/registrargenero", methods=["POST"])
def registrargenero():
    nombre_genero = request.form["nombre_genero"]
    nuevo_genero = Genero(nombre_genero = nombre_genero)
    db.session.add(nuevo_genero)
    db.session.commit()
    return redirect("/leergenero")



@app.route("/iniciar_sesion")
def iniciar_sesion():
    return redirect("/")

@app.route("/autor")
def autor():
    return render_template("autor.html")

@app.route("/genero")
def genero():
    return render_template("genero.html")

@app.route("/editorial")
def editorial():
    return render_template("editorial.html")


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)