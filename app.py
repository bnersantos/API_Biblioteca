import sqlalchemy
from sqlalchemy import *
from flask import Flask, jsonify, request
from flask_pydantic_spec import FlaskPydanticSpec
from models import *

app = Flask(__name__)
spec = FlaskPydanticSpec(app)


@app.route('/cadastrar_livro', methods=['GET', 'POST'])
def cadastrar_livro():
    """
       API para cadastrar livro.

       ## Endpoint:
        /cadastrar_livro

       ## Respostas (JSON):
       ```json

       {
            "titulo":
            "autor",
            "isbn":,
            "resumo",
        }

       ## Erros possíveis (JSON):
        "O livro já está cadastrado", rertorna erro ***400
        Bad Request***:
            ```json
       """

    try:
        if request.method == 'POST':
            if (not request.form['form_titulo'] or not request.form['form_autor']
                    or not request.form['form_isbn'] or not request.form['form_resumo']):
                return jsonify({
                    "erro": "Preencher os campos em branco!!"
                })
            else:
                titulo = request.form['form_titulo'].strip()
                autor = request.form['form_autor']
                isbn = request.form['form_isbn'].strip()
                resumo = request.form['form_resumo']

                titulo_existe = db_session.execute(select(Livro).where(Livro.titulo == titulo)).scalar()
                isbn_existe = db_session.execute(select(Livro).where(Livro.isbn == isbn)).scalar()

                if titulo_existe:
                    return jsonify({
                        "erro": "Já existe um livro com esse titulo!"
                    })

                if isbn_existe:
                    return jsonify({
                        "erro": "Já existe um livro com esse ISBN!"
                    })

                form_criar = Livro(
                    titulo=titulo,
                    autor=autor,
                    isbn=isbn,
                    resumo=resumo
                )

                form_criar.save()
                # db_session.close()

                return jsonify({
                    "titulo": form_criar.titulo,
                    "autor": form_criar.autor,
                    "isbn": form_criar.isbn,
                    "resumo": form_criar.resumo
                })

    except sqlalchemy.exc.IntegrityError:
        return jsonify({
            "erro": "Esse livro já está cadastrado!"
        })


@app.route('/cadastrar_usuario', methods=['POST', 'GET'])
def cadastrar_usuario():
    """
           API para cadastrar usuário.

           ## Endpoint:
            /cadastrar_usuario

           ## Respostas (JSON):
           ```json

           {
                "id":
                "nome",
                "cpf":,
                "endereco",
            }

           ## Erros possíveis (JSON):
            "O usuário já está cadastrado", rertorna erro ***400
            Bad Request***:
                ```json
           """

    try:
        if request.method == 'POST':
            if (not request.form['form_nome'] or not request.form['form_cpf']
                    or not request.form['form_endereco']):
                return jsonify({
                    "erro": "Preencher os campos em branco!!"
                })

            else:
                nome = request.form['form_nome']
                cpf = request.form['form_cpf'].strip()
                endereco = request.form['form_endereco']

                cpf_existe = db_session.execute(select(Usuario).where(Usuario.cpf == cpf)).scalar()

                if cpf_existe:
                    return jsonify({
                        "erro": "Este CPF já existe!"
                    })

                form_criar = Usuario(
                    nome=nome,
                    cpf=cpf,
                    endereco=endereco
                )

                form_criar.save()
                # db_session.close()

                return jsonify({
                    "id": form_criar.id,
                    "nome": form_criar.nome,
                    "cpf": form_criar.cpf,
                    "endereco": form_criar.endereco
                }), 201

    except sqlalchemy.exc.IntegrityError:
        return jsonify({
            "erro": "Este usuário já está cadastrado!"
        }), 404


@app.route('/cadastrar_emprestimo', methods=['POST', 'GET'])
def cadastrar_emprestimo():
    """
           API para cadastrar emprestimo.

           ## Endpoint:
            /cadastrar_emprestimo

           ## Respostas (JSON):
           ```json

           {
                "data_devolucao":
                "data_emprestimo",
                "livro":,
                "usuario":,
            }

           ## Erros possíveis (JSON):
            "Emprestimo já cadastrado", rertorna erro ***400
            Bad Request***:
                ```json
           """

    try:
        if request.method == 'POST':
            if (not request.form['form_data_emprestimo'] or not request.form['form_data_devolucao']
                    or not request.form['form_livro'] or not request.form['form_usuario']):
                return jsonify({
                    "erro": "Preencher os campos em branco!!"
                })

            else:
                data_devolucao = request.form['form_data_devolucao']
                data_emprestimo = request.form['form_data_emprestimo']
                livro = request.form['form_livro']
                usuario = request.form['form_usuario']

                form_criar = Emprestimo(
                    data_emprestimo=data_emprestimo,
                    data_devolucao_prevista=data_devolucao,
                    livro_id=int(livro),
                    usuario_id=int(usuario)
                )

                form_criar.save()
                # db_session.close()

                return jsonify({
                    "data_devolucao": form_criar.data_devolucao_prevista,
                    "data_emprestimo": form_criar.data_emprestimo,
                    "livro": form_criar.livro_id,
                    "usuario": form_criar.usuario_id
                })

    except sqlalchemy.exc.IntegrityError:
        return jsonify({
            "erro": "Empréstimo já cadastrado!"
        })


@app.route('/editar_livro/<int:id>', methods=['POST'])
def editar_livro(id):
    """
           API para editar informações do livro.

           ## Endpoint:
            /editar_livro/<int:id>

            ## Parâmetro:
            "id" **Id do livro**

           ## Respostas (JSON):
           ```json

           {
                "titulo":
                "autor",
                "isbn":,
                "resumo",
            }

           ## Erros possíveis (JSON):
            "O titulo deste livro já está cadastrado", rertorna erro ***400
            Bad Request***:
                ```json
           """

    try:
        livro_atualizado = db_session.execute(select(Livro).where(Livro.id == id)).scalar()

        if not livro_atualizado:
            return jsonify({
                "erro": "Livro não encontrado!"
            })

        if request.method == 'POST':
            if (not request.form['form_titulo'] and not request.form['form_autor']
                    and not request.form['form_isbn'] and not request.form['form_resumo']):
                return jsonify({
                    "erro": "Preencher os campos em branco!!"
                })

            else:
                livro_atualizado.titulo = request.form['form_titulo']
                livro_atualizado.autor = request.form['form_autor']
                livro_atualizado.isbn = request.form['form_isbn']
                livro_atualizado.resumo = request.form['form_resumo']

                livro_atualizado.save()
                # db_session.commit()

                return jsonify({
                    "titulo": livro_atualizado.titulo,
                    "autor": livro_atualizado.autor,
                    "isbn": livro_atualizado.isbn,
                    "resumo": livro_atualizado.resumo
                })

    except sqlalchemy.exc.IntegrityError:
        return jsonify({
            "erro": "O título deste livro já está cadastrado!"
        })


@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    """
           API para editar dados do usuario.

           ## Endpoint:
            /editar_usuario/<int:id>

            ##Parâmetros:
            "id" **Id do usuario**

           ## Respostas (JSON):
           ```json

           {
                "nome":
                "cpf",
                "endereco":,
            }

           ## Erros possíveis (JSON):
            "O CPF deste usuário já está cadastrado", rertorna erro ***400
            Bad Request***:
                ```json
           """

    try:
        usuario_atualizado = db_session.execute(select(Usuario).where(Usuario.id == id)).scalar()

        if not usuario_atualizado:
            return jsonify({
                "erro": "Usuário não encontrado!"
            })

        if request.method == 'POST':
            if (not request.form['form_nome'] and not request.form['form_cpf']
                    and not request.form['form_endereco']):
                return jsonify({
                    "erro": "Preencher os campos em branco!!"
                })

            else:
                cpf = request.form['form_cpf'].strip()
                if usuario_atualizado.cpf != cpf:
                    cpf_existe = db_session.execute(select(Usuario).where(Usuario.cpf == cpf)).scalar()

                    if cpf_existe:
                        return jsonify({
                            "erro": "Este CPF já existe!"
                        })

                usuario_atualizado.nome = request.form['form_nome']
                usuario_atualizado.cpf = request.form['form_cpf'].strip()
                usuario_atualizado.endereco = request.form['form_endereco']

                usuario_atualizado.save()
                # db_session.commit()

                return jsonify({
                    "nome": usuario_atualizado.nome,
                    "cpf": usuario_atualizado.cpf,
                    "endereco": usuario_atualizado.endereco,
                })

    except sqlalchemy.exc.IntegrityError:
        return jsonify({
            "erro": "O CPF deste usuário já está cadastrado!"
        })


@app.route('/get_usuario/<int:id>', methods=['GET'])
def get_usuario(id):
    """
           API para buscar um usuário.

           ## Endpoint:
            /get_usuario/<int:id>

            ##Parâmetros:
            "id" **Id do usuario**

           ## Respostas (JSON):
           ```json

           {
                "id":
                "nome",
                "cpf":,
                "endereco",
            }

           ## Erros possíveis (JSON):
            "Usuário não encontrado ***400
            Bad Request***:
                ```json
           """
    try:
        usuario = db_session.execute(select(Usuario).where(Usuario.id == id)).scalar()

        if not usuario:
            return jsonify({
                "erro": "Usuário não encontrado!"
            })

        else:
            return jsonify({
                "id": usuario.id,
                "nome": usuario.nome,
                "cpf": usuario.cpf,
                "endereco": usuario.endereco
            })
    except ValueError:
        return jsonify({
            "error": "Não foi possível listar os dados!"
        })


@app.route('/usuarios', methods=['GET'])
def usuarios():
    """
           API para listar usuários.

           ## Endpoint:
            /usuarios

           ## Respostas (JSON):
           ```json

           {
                "usuarios": lista_usuarios
            }

    """

    try:
        sql_usuarios = select(Usuario)
        resultado_usuarios = db_session.execute(sql_usuarios).scalars()
        lista_usuarios = []
        for usuario in resultado_usuarios:
            lista_usuarios.append(usuario.serialize_user())
        return jsonify({
            "usuarios": lista_usuarios
        })
    except ValueError:
        return jsonify({
            "error": "Não foi possível listar os usuários"
        })


@app.route('/livros', methods=['GET'])
def livros():
    """
           API listar livros.

           ## Endpoint:
            /livros

           ## Respostas (JSON):
           ```json

        {
            "livros": lista_livros"
        }

        ## Erros possíveis (JSON):
        "Não foi possível listar os livros ***400
        Bad Request***:
            ```json
           """

    try:
        sql_livros = select(Livro)
        resultado_livros = db_session.execute(sql_livros).scalars()
        lista_livros = []
        for livro in resultado_livros:
            lista_livros.append(livro.serialize_user())
        return jsonify({
            "livros": lista_livros
        })
    except ValueError:
        return jsonify({
            "error": "Não foi possível listar os livros"
        })

@app.route('/get_livro/<int:id>', methods=['GET'])
def get_livro(id):
    """
           API para verificar um livro.

           ## Endpoint:
            /get_livro/<int:id>

            ##Parâmetros:
            "id" **Id do livro**

           ## Respostas (JSON):
           ```json

        {
            "id":,
            "titulo":
            "autor",
            "isbn":,
            "resumo",
        }

        ## Erros possíveis (JSON):
            "Não foi possível listar os dados do livro ***400
            Bad Request***:
                ```json
           """


    try:
        livro = db_session.execute(select(Livro).where(Livro.id == id)).scalar()

        if not livro:
            return jsonify({
                "error": "Livro não encontrado!"
            })

        else:
            return jsonify({
                "id": livro.id,
                "titulo": livro.titulo,
                "autor": livro.autor,
                "isbn": livro.isbn,
                "resumo": livro.resumo
            })

    except ValueError:
        return jsonify({
            "error": "Não foi possívl listar os dados do livro"
        })
@app.route('/emprestimos_usuario/<id>', methods=['GET'])
def emprestimos_usuario(id):
    """
           API para listar emprestimos por usuários.

           ## Endpoint:
            /emprestimos_usuario/<int:id>

            ##Parâmetros:
            "id" **Id do usuário**

           ## Respostas (JSON):
           ```json

            {
                "usuario":
                "emprestimo",

            }

            ## Erros possíveis (JSON):
            "Não foi possível listar os dados deste emprestimo ***400
            Bad Request***:
                ```json
           """

    try:
        id_usuario = int(id)
        emprestimos_user = db_session.execute(select(Emprestimo).where(Emprestimo.usuario_id == id_usuario)).scalars().all()

        if not emprestimos_user:
            return jsonify({
                "error": "Este usuário não fez emprestimo!"
            })

        else:
            emprestimos_livros = []
            for emprestimo in emprestimos_user:
                emprestimos_livros.append(emprestimo.serialize_user())
            #     livro = db_session.execute(select(Livro).where(Livro.id == emprestimo.livro_id)).scalars().all()
            #     emprestimos_livros.append(livro)
            return jsonify({
                'usuario': int(id_usuario),
                'emprestimos': emprestimos_livros,
            })
    except ValueError:
        return jsonify({
            "error": "Não foi possível listar os dados do emprestimo"
        })
@app.route('/status_livro', methods=['GET'])
def status_livro():
    """
           API para mostrar status de livro.

           ## Endpoint:
            /status_livro

           ## Respostas (JSON):
           ```json

           {
                "livros emprestados":
                "livros disponiveis",
            }

            ## Erros possíveis (JSON):
            "Não foi possível mostrar o status dos livros ***400
            Bad Request***:
                ```json
            """


    try:
        livro_emprestado = db_session.execute(
            select(Livro).where(Livro.id == Emprestimo.livro_id).distinct(Livro.isbn)).scalars()
        id_livro_emprestado = db_session.execute(
            select(Livro.id).where(Livro.id == Emprestimo.livro_id).distinct(Livro.isbn)).scalars()
        print("livro Emprestado",livro_emprestado)
        livros = db_session.execute(select(Livro)).scalars()

        print("Livros todos", livros)

        lista_emprestados = []
        lista_disponiveis = []
        for livro in livro_emprestado:
            lista_emprestados.append(livro.serialize_user())

        for book in livros:
            if book.id not in id_livro_emprestado:
                lista_disponiveis.append(book.serialize_user())

        print("resultados lista", lista_emprestados)
        print("resultados disponibiliza", lista_disponiveis)


        return jsonify({
            "livros emprestados": lista_emprestados,
            "livros disponiveis": lista_disponiveis

        })

    except ValueError:
        return jsonify({
            "error": "não foi possível mostrar o status do livro"
        })


spec.register(app)

if __name__ == '__main__':
    app.run(debug=True)
