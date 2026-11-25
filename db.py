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


def _migrar(conn):
    """Adiciona colunas novas em bancos criados por versões anteriores."""
    colunas = {r["name"] for r in conn.execute("PRAGMA table_info(atividades)")}
    if "concluida_em" not in colunas:
        conn.execute("ALTER TABLE atividades ADD COLUMN concluida_em TEXT")


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
                criada_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                concluida_em TEXT
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
        _migrar(conn)


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
            "SELECT * FROM atividades "
            "ORDER BY concluida_em IS NOT NULL, prazo ASC, id DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def obter_atividade(atividade_id: int) -> dict | None:
    with conectar() as conn:
        row = conn.execute(
            "SELECT * FROM atividades WHERE id = ?", (atividade_id,)
        ).fetchone()
    return dict(row) if row else None


def excluir_atividade(atividade_id: int) -> bool:
    with conectar() as conn:
        cur = conn.execute(
            "DELETE FROM atividades WHERE id = ?",
            (atividade_id,)
        )

        return cur.rowcount > 0


def concluir_atividade(atividade_id: int) -> bool:
    with conectar() as conn:
        cur = conn.execute(
            "UPDATE atividades SET concluida_em = datetime('now', 'localtime') "
            "WHERE id = ? AND concluida_em IS NULL",
            (atividade_id,),
        )
        return cur.rowcount > 0


def reabrir_atividade(atividade_id: int) -> bool:
    with conectar() as conn:
        cur = conn.execute(
            "UPDATE atividades SET concluida_em = NULL "
            "WHERE id = ? AND concluida_em IS NOT NULL",
            (atividade_id,),
        )
        return cur.rowcount > 0


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


def atividade_tem_plano(atividade_id: int) -> bool:
    with conectar() as conn:
        resultado = conn.execute(
            """
            SELECT 1
            FROM planos
            WHERE atividade_id = ?
            LIMIT 1
            """,
            (atividade_id,)
        ).fetchone()

    return resultado is not None