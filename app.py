import sqlalchemy
from sqlalchemy import *
from flask import Flask, jsonify, request
from flask_pydantic_spec import FlaskPydanticSpec
from models import *
from datetime import datetime, timedelta
from functools import wraps
from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity, jwt_required

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "Am12081965$!"
jwt = JWTManager(app)
spec = FlaskPydanticSpec('flask', title='API + Biblioteca + Banco', version='1.0.0')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        db_session = local_session()
        try:
            sql = select(USER).where(USER.id == current_user)
            user = db_session.execute(sql).scalar()
            if user and user.admin:
                return f(*args, **kwargs)
            return jsonify({
                "msg": "Acesso negado, privilégio de administrador necessário."
            }), 401
        finally:
            db_session.close()
    return decorated_function
#  ADMIN

@app.route('/cadastrar/livro', methods=['POST'])
@jwt_required()
@admin_required
def cadastrar_livro():
    """
        API para cadastrar livro.

        ## Endpoint:
            /cadastrar/livro

        ## Respostas (JSON):
        ```json

        {
            "titulo":
            "autor",
            "isbn":,
            "resumo",
        }, 201

        ## Erros possíveis (JSON):
        "O livro já está cadastrado", rertorna erro ***400
        Bad Request***:
            ```json
        """
    db_session = local_session()
    try:
        dados = request.get_json()
        print(dados)
        if "titulo" not in dados or "autor" not in dados or "isbn" not in dados or "resumo" not in dados:
            return jsonify({"erro": "Campo obrigatorio"})
        if dados["titulo"] == '' or dados["autor"] == '' or dados["isbn"] == '' or dados['resumo'] == '':
            return jsonify({"erro": "Campo nao pode ser vazio"})

        titulo = dados["titulo"].strip()
        autor = dados['autor']
        isbn = dados['isbn'].strip()
        resumo = dados['resumo']

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

        livro_cadastrar = Livro(
            titulo=titulo,
            autor=autor,
            isbn=isbn,
            resumo=resumo
        )

        livro_cadastrar.save(db_session)
        # db_session.close()

        return jsonify({
            "titulo": livro_cadastrar.titulo,
            "autor": livro_cadastrar.autor,
            "isbn": livro_cadastrar.isbn,
            "resumo": livro_cadastrar.resumo
        }), 201

    # except sqlalchemy.exc.IntegrityError:
    #     return jsonify({
    #         "erro": "Esse livro já está cadastrado!"
    #     }), 400
    except Exception as e:
        return jsonify({
            "erro": str(e)
        }), 400
    finally:
        db_session.close()


# ADMIN
@app.route('/cadastrar/usuario', methods=['POST'])
@jwt_required()
@admin_required
def cadastrar_usuario():
    """
        API para cadastrar usuário.

        ## Endpoint:
            /cadastrar/usuario

        ## Respostas (JSON):
            ```json

            {
                "mensagem": usuario cadastrado com sucesso!,
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
    db_session = local_session()
    try:
        dados = request.get_json()
        print(dados)
        if "nome" not in dados or "cpf" not in dados or "endereco" not in dados:
            return jsonify({"erro": "Campo obrigatorio"})
        if dados["nome"] == '' or dados["cpf"] == '' or dados["endereco"] == '':
            return jsonify({"erro": "Campo nao pode ser vazio"})

        nome = dados['nome'].strip()
        cpf = dados['cpf'].strip()
        endereco = dados['endereco'].strip()

        cpf_existe = db_session.execute(select(Usuario).where(Usuario.cpf == cpf)).scalar()
        endereco_existe = db_session.execute(select(Usuario).where(Usuario.endereco == endereco)).scalar()

        if cpf_existe:
            return jsonify({
                "error": "Este cpf já existe!"
            })
        if endereco_existe:
            return jsonify({
                "error": "Este endereço já está cadastrado!"
            })

        usuario_cadastrar = Usuario(
            nome=nome,
            cpf=cpf,
            endereco=endereco,
        )

        usuario_cadastrar.save(db_session)

        return jsonify({
            "nome": usuario_cadastrar.nome,
            "cpf": usuario_cadastrar.cpf,
            "endereco": usuario_cadastrar.endereco,
            "status": usuario_cadastrar.status_user
        }), 201

    except Exception as e:
        return jsonify({
            "erro": str(e)
        }), 404
    finally:
        db_session.close()


# ADMIN
@app.route('/cadastrar/emprestimo', methods=['POST'])
@jwt_required()
@admin_required
def cadastrar_emprestimo():
    """
        API para cadastrar emprestimo.

        ## Endpoint:
            /cadastrar/emprestimo

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
    db_session = local_session()

    try:
        dados = request.get_json()
        campos_necessarios = ['id_livro', 'id_usuario']

        # Verifica se todos os campos obrigatórios foram enviados (sem as datas)
        if not all(campo in dados for campo in campos_necessarios):
            return jsonify({"erro": "Campo obrigatório não enviado"}), 400

        if any(dados[campo] == '' for campo in campos_necessarios):
            return jsonify({"erro": "Campo não pode ser vazio!"}), 400

        id_livro = int(dados['id_livro'])
        id_usuario = int(dados['id_usuario'])

        livro = db_session.execute(select(Livro).where(Livro.id == id_livro)).scalar()
        if not livro:
            return jsonify({"erro": "Livro não encontrado"}), 404
        if not livro.status_livro:
            return jsonify({"erro": "Livro indisponível"}), 400

        usuario = db_session.execute(select(Usuario).where(Usuario.id == id_usuario)).scalar()
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        if not usuario.status_user:
            return jsonify({"erro": "Usuário indisponível"}), 400

        emprestimo_ativo = db_session.execute(
            select(Emprestimo).where(
                Emprestimo.livro_id == id_livro,
                Emprestimo.status_emprestimo == True
            )
        ).scalar()



        if emprestimo_ativo:
            return jsonify({"erro": "Livro já emprestado, selecione outro exemplar!"}), 400

        # Gerar as datas automaticamente
        data_emprestimo = datetime.now().date()
        data_devolucao_prevista = data_emprestimo + timedelta(days=30)

        emprestimo_cadastrar = Emprestimo(
            data_emprestimo=data_emprestimo,
            data_devolucao_prevista=data_devolucao_prevista,
            livro_id=id_livro,
            usuario_id=id_usuario
        )
        emprestimo_cadastrar.save(db_session)

        return jsonify({
            "data_devolucao": emprestimo_cadastrar.data_devolucao_prevista.strftime("%d/%m/%Y"),
            "data_emprestimo": emprestimo_cadastrar.data_emprestimo.strftime("%d/%m/%Y"),
            "livro": emprestimo_cadastrar.livro_id,
            "usuario": emprestimo_cadastrar.usuario_id
        }), 201

    except sqlalchemy.exc.IntegrityError:
        return jsonify({"erro": "Empréstimo já cadastrado!"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        db_session.close()


# ADMIN
@app.route('/editar/livro/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def editar_livro(id):
    """
        API para editar informações do livro.

        ## Endpoint:
        /editar/livro/<int:id>

        ## Parâmetro:
        "id" **Id do livro**

        ## Respostas (JSON):
        ```json

        {
                "titulo":
                "autor":,
                "isbn":,
                "resumo":,
            }

        ## Erros possíveis (JSON):
            "O titulo deste livro já está cadastrado", rertorna erro ***400
            Bad Request***:
                ```json
        """
    db_session = local_session()
    try:
        livro_atualizado = db_session.execute(select(Livro).where(Livro.id == id)).scalar()

        if not livro_atualizado:
            return jsonify({
                "erro": "Livro não encontrado!"
            })

        data = request.get_json()
        if not data or not all(key in data for key in ['titulo', 'autor', 'isbn', 'resumo', 'status_livro']):
            return jsonify({"erro": "Preencha todos os campos!"}), 400  # Retorna 400 Bad Request
        isbn = data['isbn']
        status_livro = bool(data['status_livro'])
        isbn_existe = db_session.execute(select(Livro).where(Livro.isbn == isbn)).scalar()
        status_emprestimo = db_session.execute(select(Emprestimo).where(Emprestimo.livro_id == id)).scalar()
        if isbn_existe and livro_atualizado.isbn != isbn:
            return jsonify({
                "erro": "Este ISBN já existe!"
            })
        if status_emprestimo:
            return jsonify({
                "error": "Não é possivel editar o livro com emprestimo pendente!"
            })
        else:
            livro_atualizado.titulo = data['titulo']
            livro_atualizado.autor = data['autor']
            livro_atualizado.isbn = data['isbn']
            livro_atualizado.resumo = data['resumo']
            livro_atualizado.status_livro = status_livro

            livro_atualizado.save(db_session)
            # db_session.commit()

        return jsonify({
            "titulo": livro_atualizado.titulo,
            "autor": livro_atualizado.autor,
            "isbn": livro_atualizado.isbn,
            "resumo": livro_atualizado.resumo,
            "status_livro": livro_atualizado.status_livro
        })

    except sqlalchemy.exc.IntegrityError:
        return jsonify({
            "erro": "O título deste livro já está cadastrado!"
        })
    finally:
        db_session.close()


# ADMIN
@app.route('/editar/usuario/<int:id>', methods=['PUT'])
@jwt_required()
def editar_usuario(id):
    """
        API para editar dados do usuario.

        ## Endpoint:
            /editar/usuario/<int:id>

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
    db_session = local_session()
    try:
        usuario_atualizado = db_session.execute(select(Usuario).where(Usuario.id == id)).scalar()

        if not usuario_atualizado:
            return jsonify({
                "erro": "Usuário não encontrado!"
            })

        data = request.get_json()
        if not data or not all(key in data for key in ['nome', 'cpf', 'endereco', 'status_user']):
            return jsonify({"error": "Preencha todos os campos!"}), 400
        if data['nome'] == '' or data['cpf'] == '' or data['endereco'] == '' or data['status_user'] == '':
            return jsonify({
                "error": "Campo obrigatorio!"
            })
        cpf = data['cpf'].strip()
        status = data['status_user']
        cpf_existe = db_session.execute(select(Usuario).where(Usuario.cpf == cpf)).scalar()
        status_emprestimo = db_session.execute(select(Emprestimo).where(Emprestimo.usuario_id == id)).scalar()

        if cpf_existe and usuario_atualizado.cpf != cpf:
            return jsonify({
                "erro": "Este CPF já existe!"
            }), 400
        if status_emprestimo:
            return jsonify({
                "erro": "Não possivel atualizar o usuario com emprestimo pendente!"
            })
        else:
            usuario_atualizado.nome = data['nome']
            usuario_atualizado.cpf = cpf
            usuario_atualizado.endereco = data['endereco']
            usuario_atualizado.status_user = bool(status)

            usuario_atualizado.save(db_session)

            return jsonify({
                "nome": usuario_atualizado.nome,
                "cpf": usuario_atualizado.cpf,
                "endereco": usuario_atualizado.endereco,
                "status_user": usuario_atualizado.status_user
            })

    except sqlalchemy.exc.IntegrityError:
        return jsonify({
            "erro": "O CPF deste usuário já está cadastrado!"
        })
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return jsonify({"erro": "Erro interno do servidor"}), 500
    finally:
        db_session.close()


# ADMIN
# @app.route('/editar/emprestimo/<int:id>', methods=['PUT'])
# def editar_emprestimo(id):
#     """
#     API para editar dados do emprestimo.
#     ## Endpoint:
#     /editar/emprestimo/<int:id>
#
#     ##Parâmetros:
#     "id" **Id do emprestimo**
#
#     ## Respostas (JSON):
#     ```json
#     {
#         "id": ,
#         "id_usuario": ,
#         "id_livro": ,
#         "status": ,
#         }
#
#         ##Erros possíveis (JSON):
#         "Usuário não encontrado", rertorna erro ***400
#         Bad Request***:
#         ```json
#     """
#     try:
#         emprestimo = db_session.execute(select(Emprestimo).where(Emprestimo.id == id)).scalar()
#
#         if not emprestimo:
#             return jsonify({
#                 "erro": "Empréstimo inexistente!"
#             })
#         data = request.get_json()
#         if not data or not all(key in data for key in ['status']):
#             return jsonify({
#                 "error": "Preencha todos os campos!"
#             }), 400
#         if data['status']:
#             return jsonify({
#                 "error": "Campo obrigatorio!"
#             }), 400
#         else:
#             emprestimo.status = bool(emprestimo.status)
#             emprestimo.save()
#
#             livro_select = select(Livro).where(Livro.id == emprestimo.livro_id)
#             post = db_session.execute(livro_select).scalar()
#             post.status_emprestado = False
#             post.save()
#         return jsonify({
#             "status": bool(emprestimo.status)
#         })
#     except Exception as e:
#         print(f"Erro inesperado: {e}")
#         return jsonify({
#             "erro": "Erro interno do servidor"
#         }), 500
# ADMIN
@app.route('/get/usuario/<int:id>', methods=['GET'])
@jwt_required()
@admin_required
def get_usuario(id):
    """

        API para buscar um usuário.

        ## Endpoint:
            /get/usuario/<int:id>

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
    db_session = local_session()
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
    finally:
        db_session.close()


# ADMIN
@app.route('/usuarios', methods=['GET'])
@jwt_required()
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
    db_session = local_session()
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
    finally:
        db_session.close()


# QUALQUER UM
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
    db_session = local_session()
    try:
        sql_livros = select(Livro)
        resultado_livros = db_session.execute(sql_livros).scalars()
        lista_livros = []
        status_livro = db_session.execute(select(Livro).where(Livro.status_livro == False)).scalar()

        for livro in resultado_livros:
            lista_livros.append(livro.serialize_livro())
        return jsonify({
            "livros": lista_livros
        })
    except ValueError:
        return jsonify({
            "error": "Não foi possível listar os livros"
        })
    finally:
        db_session.close()


# QUALQUER UM
@app.route('/get/livro/<int:id>', methods=['GET'])
def get_livro(id):
    """
        API para verificar um livro.

        ## Endpoint:
            /get/livro/<int:id>

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
    db_session = local_session()
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
    finally:
        db_session.close()


@app.route('/emprestimos', methods=['GET'])
@jwt_required()
def emprestimos():
    """
    API para listar todos os emprestimo.
    :return: Listar todos os emprestimos
    ## Endpoint:
    /emprestimos
    ## Respostas (JSON):
    ```json
    {
        'lista_emprestimos': lista_emprestimos
        }
    ## Erros possiveis:
    Se inserir letras retornará uma mensagem inválida.
    """
    db_session = local_session()
    try:
        emprestimo = select(Emprestimo)
        resultado_emprestimo = db_session.execute(emprestimo).scalars()
        lista_emprestimos = []
        for e in resultado_emprestimo:
            lista_emprestimos.append(e.serialize_emprestimo())
            print(lista_emprestimos[-1])
        return jsonify({
            'lista_emprestimos': lista_emprestimos
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        })
    finally:
        db_session.close()


# ADMIN
@app.route('/emprestimos/usuario/<id>', methods=['GET'])
@jwt_required()
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
    db_session = local_session()
    try:
        id_usuario = int(id)
        emprestimos_user = db_session.execute(
            select(Emprestimo).where(Emprestimo.usuario_id == id_usuario)).scalars().all()

        if not emprestimos_user:
            return jsonify({
                "error": "Este usuário não fez emprestimo!"
            })
        status_livro = db_session.execute(select(Livro).where(Livro.status_livro == True)).scalar()
        status_usuario = db_session.execute(select(Usuario).where(Usuario.status_user == True)).scalar()
        if not status_usuario:
            return jsonify({
                "error": "Usuário desativado!"
            })
        if not status_livro:
            return jsonify({
                "error": "Livro desativado!"
            })
        else:
            emprestimos_livros = []
            for emprestimo in emprestimos_user:
                emprestimos_livros.append(emprestimo.serialize_emprestimo())
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
    finally:
        db_session.close()


# QUALQUER UM
@app.route('/status/livro/<id>', methods=['GET'])
def status_livro(id):
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
    db_session = local_session()
    try:
        livro_id = int(id)

        livro = db_session.execute(select(Livro).where(Emprestimo.livro_id == livro_id)).scalar()
        status_emprestimo = db_session.execute(select(Emprestimo).where(Emprestimo.status == True)).scalar()

        if livro:
            if status_emprestimo:
                print(status_emprestimo.status)
                return jsonify({
                    'resultado': 'Livro emprestado!'
                })
            else:
                return jsonify({
                    'resultado': 'Livro disponivel!'
                })
        else:
            return jsonify({
                'resultado': 'Livro disponivel!'
            })

        # id_livro_emprestado = db_session.execute(
        #     select(Livro.id).where(Livro.id == Emprestimo.livro_id).distinct(Livro.isbn)).scalars()

        # print("livro Emprestado", livro_emprestado)
        # livro = db_session.execute(select(Livro)).scalars()

        # print("Livros todos", livros)

        print('livro', livro.status)

        return jsonify({"resultado": [{livro.titulo: livro.status}]})
        # lista_emprestados = []
        # lista_disponiveis = []
        # for livro in livro_emprestado:
        #     lista_emprestados.append(livro.serialize_livro())
        #
        # for book in livros:
        #     if book.id not in id_livro_emprestado:
        #         lista_disponiveis.append(book.serialize_livro())
        #
        # print("resultados lista", lista_emprestados)
        # print("resultados disponibiliza", lista_disponiveis)

        # return jsonify({
        #     "livros emprestados": "lista_emprestados",
        #     "livros disponiveis": "lista_disponiveis"
        #
        # })

    except ValueError:
        return jsonify({
            "error": "Nao foi possível mostrar o status do livro"
        }), 400
    finally:
        db_session.close()


# QUALQUER UM
@app.route('/status/movimentacao/<id_emprestimo>', methods=['PUT'])
def status_emprestimo(id_emprestimo):
    """
    Edita o status de um empréstimo (ativo ou devolvido) e atualiza a disponibilidade do livro associado.

    ## Endpoint:
        PUT /status/movimentacao/<id_emprestimo>

    ## Parâmetros:
        - id_emprestimo (path): ID do empréstimo a ser atualizado.

    ## Corpo da Requisição (JSON):
        {
            "status": true  # ou false
        }

        - true: Empréstimo finalizado (livro será marcado como disponível)
        - false: Empréstimo ainda ativo (livro continua indisponível)

    ## Respostas:
        ✅ Sucesso - 200 OK
        ```json
        {
            "mensagem": "Empréstimo editado com sucesso!",
            "status": 200
        }
        ```

        ❌ Erro - 400 Bad Request (faltam informações ou dados inválidos)
        ```json
        {
            "erro": "Campo 'status' ausente!"
        }
        ```

        ❌ Erro - 404 Not Found
        ```json
        {
            "erro": "Empréstimo não encontrado"
        }
        ```

        ❌ Erro - 500 Internal Server Error
        ```json
        {
            "erro": "Erro interno no servidor"
        }
        ```
    """
    db_session = local_session()
    try:
        id_emprestimo = int(id_emprestimo)
        json_dados = request.get_json()

        if 'status_emprestimo' not in json_dados:
            raise TypeError("Campo 'status' ausente!")

        # Converte status para booleano
        status_valor = json_dados['status_emprestimo']
        if status_valor in ['True', True, '1', 1]:
            novo_status = True
        elif status_valor in ['False', False, '0', 0]:
            novo_status = False
        else:
            raise ValueError("Status inválido! Use true ou false.")

        # Consulta o empréstimo e o livro associado
        consulta = db_session.execute(
            select(Emprestimo, Livro)
            .join(Livro, Emprestimo.livro_id == Livro.id)
            .where(Emprestimo.id == id_emprestimo)
        ).first()

        if not consulta:
            return jsonify({'erro': 'Empréstimo não encontrado'}), 404

        emprestimo, livro = consulta  # desempacota

        # Atualiza status do empréstimo
        emprestimo.status_emprestimo = novo_status

        # Se devolveu o livro, torna-o disponível
        if novo_status:
            livro.disponibilidade = True

        db_session.commit()

        return jsonify({
            'mensagem': 'Empréstimo editado com sucesso!',
            'status_code': 200
        }), 200

    except TypeError as e:
        return jsonify({'erro': str(e)}), 400
    except ValueError as e:
        return jsonify({'erro': str(e)}), 400
    except Exception as e:
        print("Erro inesperado:", e)
        return jsonify({'erro': 'Erro interno no servidor'}), 500
    finally:
        db_session.close()


@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    cpf = dados['cpf']
    senha = dados['password']

    db_session = local_session()

    try:
        sql = select(USER).where(USER.cpf == cpf)
        user = db_session.execute(sql).scalar()

        if user and user.check_password(senha):
            acess_token = create_access_token(identity=user.id)  # corrigido aqui
            return jsonify({
                "access_token": acess_token  # corrigido aqui
            })
        else:
            return jsonify({
                "msg": "Credenciais inválidas."
            }), 401
    except Exception as e:
        print(e)
        return jsonify({"msg": "Erro interno no servidor."}), 500
    finally:
        db_session.close()

@app.route("/cadastro", methods=["POST"])
def cadastro():
    dados = request.get_json()
    nome = dados['name']
    cpf = dados['cpf']
    senha = dados['password']
    admin = dados['admin']
    db_session = local_session()

    if not nome or not cpf or not senha:
        return jsonify({"msg": "Nome de usuário e senha são obrigatórios"}), 400

    try:
        user_check = select(USER).where(USER.cpf == cpf)
        user_existente = db_session.execute(user_check).scalar()
        if user_existente:
            return jsonify({
                "msg": "Usuário já existe."
            }), 400
        new_user = USER(name=nome, cpf=cpf, admin=admin)
        new_user.set_password(senha)
        db_session.add(new_user)
        db_session.commit()

        user_id = new_user.id
        return jsonify({
            "msg": "Usuário cadastrado com sucesso.", "user_id": user_id,
        }), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({"msg": "Erro interno no servidor."}), 500
    finally:
        db_session.close()



spec.register(app)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
