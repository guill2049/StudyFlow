"""Camada de persistência do StudyFlow (SQLite local)."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import date, datetime

DB_PATH = Path(__file__).parent / "studyflow.db"
DIFICULDADES = ("Fácil", "Média", "Difícil")


@contextmanager
def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def inicializar():
    """Cria as tabelas caso ainda não existam."""
    with conectar() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS atividades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT NOT NULL,
                prazo TEXT NOT NULL,
                dificuldade TEXT NOT NULL
                    CHECK (dificuldade IN ('Fácil', 'Média', 'Difícil')),
                criada_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS planos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                atividade_id INTEGER NOT NULL
                    REFERENCES atividades(id) ON DELETE CASCADE,
                conteudo TEXT NOT NULL,
                modelo TEXT,
                criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );
            """
        )


# ---------- Atividades (RF01, RF02) ----------

def criar_atividade(nome: str, descricao: str, prazo: str, dificuldade: str) -> int:
    # ---------- Validação dos campos ----------

    nome = nome.strip()
    descricao = descricao.strip()

    if not nome and not descricao:
        raise ValueError("Preencha os campos de nome e descrição.")

    if not nome:
        raise ValueError("O nome da atividade é obrigatório.")

    if not descricao:
        raise ValueError("A descrição da atividade é obrigatória.")

    if len(nome) < 3:
        raise ValueError("O nome deve possuir pelo menos 3 caracteres.")

    if len(nome) > 80:
        raise ValueError("O nome não pode ultrapassar 80 caracteres.")

    if len(descricao) < 10:
        raise ValueError("A descrição deve possuir pelo menos 10 caracteres.")

    if len(descricao) > 1000:
        raise ValueError("A descrição não pode ultrapassar 1000 caracteres.")

    # ---------- Validação do prazo ----------

    try:
        prazo_validade = date.fromisoformat(prazo)
    except (ValueError, TypeError):
        raise ValueError("O prazo informado é inválido.")

    if prazo_validade < date.today():
        raise ValueError("O prazo não pode ser anterior à data atual.")

    # ---------- Validação da dificuldade ----------

    if dificuldade not in DIFICULDADES:
        raise ValueError("A dificuldade informada é inválida.")

    # ---------- Inserção no banco ----------

    with conectar() as conn:
        cur = conn.execute(
            "INSERT INTO atividades (nome, descricao, prazo, dificuldade) "
            "VALUES (?, ?, ?, ?)",
            (nome, descricao, prazo, dificuldade),
        )

        return cur.lastrowid


def listar_atividades() -> list[dict]:
    with conectar() as conn:
        rows = conn.execute(
            "SELECT * FROM atividades ORDER BY prazo ASC, id DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def obter_atividade(atividade_id: int) -> dict | None:
    with conectar() as conn:
        row = conn.execute(
            "SELECT * FROM atividades WHERE id = ?", (atividade_id,)
        ).fetchone()
    return dict(row) if row else None


# ---------- Planos (RF05, RF06) ----------

def salvar_plano(atividade_id: int, conteudo_json: str, modelo: str | None = None) -> int:
    with conectar() as conn:
        cur = conn.execute(
            "INSERT INTO planos (atividade_id, conteudo, modelo) VALUES (?, ?, ?)",
            (atividade_id, conteudo_json, modelo),
        )
        return cur.lastrowid


def listar_planos() -> list[dict]:
    with conectar() as conn:
        rows = conn.execute(
            """
            SELECT p.id, p.atividade_id, a.nome AS atividade, p.conteudo,
                   p.modelo, p.criado_em
            FROM planos p
            JOIN atividades a ON a.id = p.atividade_id
            ORDER BY p.id DESC
            """
        ).fetchall()
    return [dict(r) for r in rows]