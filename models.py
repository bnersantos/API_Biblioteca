
from sqlalchemy import create_engine, Integer, Column, String, ForeignKey, Float, Column, Boolean, Date
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash



engine = create_engine('sqlite:///banco_api_biblioteca.sqlite3')
local_session = sessionmaker(bind=engine)

Base = declarative_base()
#Base.query = db_session.query_property()

class Livro(Base):
    __tablename__ = 'TAB_BOOK'
    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False, index=True, unique=True)
    autor = Column(String, nullable=False, index=True)
    isbn = Column(String, nullable=False, index=True, unique=True)
    resumo = Column(String, nullable=False, index=True)
    status_livro = Column(Boolean, index=True, default=True)


    def __repr__(self):
        return '<Livro {}>'.format(self.titulo)

    def save(self, db_session):
        db_session.add(self)
        db_session.commit()

    def delete(self, db_session):
        db_session.delete(self)
        db_session.commit()

    def serialize_livro(self):
        dados_livro = {
            'id': self.id,
            'titulo': self.titulo,
            'autor': self.autor,
            'isbn': self.isbn,
            'resumo': self.resumo,
            'status_livro': self.status_livro,

        }
        return dados_livro

class Usuario(Base):
    __tablename__ = 'TAB_USER'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False, index=True)
    cpf = Column(String, nullable=False, index=True, unique=True)
    endereco = Column(String, nullable=False, index=True)
    status_user = Column(Boolean, index=True, default=True)

    def __repr__(self):
        return '<Usuario {}>'.format(self.nome)

    def save(self, db_session):
        db_session.add(self)
        db_session.commit()

    def delete_user(self, db_session):
        db_session.delete(self)
        db_session.commit()

    def serialize_user(self):
        dados_usuario = {
            'id': self.id,
            'nome': self.nome,
            'cpf': self.cpf,
            'endereco': self.endereco,
            'status': self.status_user,
        }
        return dados_usuario

class Emprestimo(Base):
    __tablename__ = 'TAB_EMPRESTIMO'
    id = Column(Integer, primary_key=True)
    data_emprestimo = Column(Date, nullable=False, index=True)
    data_devolucao_prevista = Column(Date, nullable=False, index=True)
    status_emprestimo = Column(Boolean, index=True, default=True)

    livro_id = Column(Integer, ForeignKey('TAB_BOOK.id'))
    livros = relationship(Livro)

    usuario_id = Column(Integer, ForeignKey('TAB_USER.id'))
    usuarios = relationship(Usuario)

    def __repr__(self):
        return '<Emprestimo {}>'.format(self.data_emprestimo)

    def save(self, db_session):
        db_session.add(self)
        db_session.commit()

    def delete(self, db_session):
        db_session.delete(self)
        db_session.commit()

    def serialize_emprestimo(self):
        dados_emprestimo = {
            'id': self.id,
            'data_emprestimo': self.data_emprestimo,
            'data_devolucao': self.data_devolucao_prevista,
            'livro_id': self.livro_id,
            'usuario_id': self.usuario_id,
            'status_emprestimo': self.status_emprestimo,
        }

        return dados_emprestimo

class USER(Base):
    __tablename__ = 'TAB_IS_ADMIN'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    cpf = Column(String(11), nullable=False, unique=True)
    password = Column(String, nullable=False)
    admin = Column(Boolean, default=True)


    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<Usuario(id={self.id}, nome={self.name}, cpf={self.cpf}, é admin={self.admin})>'

    def serialize(self):
        return {
            "id": self.id,
            "nome": self.name,
            "cpf": self.cpf,
            "papel": "admin" if self.admin else "usuario",
        }

    def save(self, db_session):
        db_session.add(self)
        db_session.commit()

    def delete(self, db_session):
        db_session.delete(self)
        db_session.commit()

def init_db():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    init_db()

