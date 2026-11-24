"""Camada de persistência do StudyFlow (SQLite local)."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

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
    with conectar() as conn:
        cur = conn.execute(
            "INSERT INTO atividades (nome, descricao, prazo, dificuldade) "
            "VALUES (?, ?, ?, ?)",
            (nome.strip(), descricao.strip(), prazo, dificuldade),
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