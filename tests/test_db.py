"""Teste da camada relacional (SQLite temporário, tipos portáveis)."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base, Empresa


def test_empresa_persiste_e_le(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path/'t.db'}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)

    with Session() as s:
        s.add(
            Empresa(
                nome="Tractian",
                setor="Indústria",
                descricao="manutenção preditiva",
                dados={"nome": "Tractian", "tecnologias": ["IoT"]},
                fontes=["https://tractian.com"],
            )
        )
        s.commit()

    with Session() as s:
        e = s.query(Empresa).first()
        assert e.nome == "Tractian"
        assert e.dados["tecnologias"] == ["IoT"]   # JSON portável funciona
        assert e.fontes == ["https://tractian.com"]
        assert e.created_at is not None
