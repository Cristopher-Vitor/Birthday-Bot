from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///dados.db")
Base = declarative_base()
Sessao_base = sessionmaker(engine)

class Aniversariantes(Base):
  __tablename__ = "aniversariantes"

  id = Column(Integer, primary_key=True)
  nome = Column(String)
  data = Column(String)

Base.metadata.create_all(engine)

