"""Geração de planos de execução com IA.

Usa a API compatível com OpenAI (padrão: Groq). Provedor, modelo e chave vêm
do .env. Se as chaves do Langfuse estiverem configuradas, cada chamada é
rastreada automaticamente.
"""
from __future__ import annotations

import json
import os
from datetime import date
from typing import Literal

import openai
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
MAX_TENTATIVAS = 2

LANGFUSE_ATIVO = bool(
    os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
)

if LANGFUSE_ATIVO:
    from langfuse.openai import OpenAI  # drop-in: rastreia entradas, saídas, tokens, latência
else:
    from openai import OpenAI


class ErroIA(Exception):
    """Falha ao gerar o plano, com mensagem própria para exibir ao usuário."""


class Etapa(BaseModel):
    titulo: str
    descricao: str
    tempo_estimado_min: int = Field(ge=5, description="Tempo da etapa em minutos")


class Plano(BaseModel):
    analise: str
    prioridade: Literal["Baixa", "Média", "Alta"]
    etapas: list[Etapa] = Field(min_length=2)
    recomendacoes: list[str]

    @property
    def tempo_total_min(self) -> int:
        # Calculado aqui, e não pelo modelo, para nunca divergir das etapas.
        return sum(e.tempo_estimado_min for e in self.etapas)


SYSTEM_PROMPT = """Você é um assistente de planejamento acadêmico. Receberá uma \
atividade de um estudante e deve produzir um plano de execução realista e prático.

Responda SOMENTE com um objeto JSON válido, sem texto fora dele, neste formato:
{
  "analise": "resumo do que a atividade exige e dos principais riscos",
  "prioridade": "Baixa" | "Média" | "Alta",
  "etapas": [
    {"titulo": "...", "descricao": "...", "tempo_estimado_min": 45}
  ],
  "recomendacoes": ["...", "..."]
}

Regras:
- Escreva em português do Brasil.
- Defina a prioridade combinando prazo restante e dificuldade.
- Use entre 3 e 8 etapas, em ordem de execução, cada uma concluível em uma sessão.
- Os tempos devem ser em minutos e coerentes com a dificuldade e o prazo.
- Se o prazo for curto, reduza o escopo das etapas em vez de ignorar o prazo.
- Dê de 2 a 4 recomendações objetivas."""


def _criar_cliente() -> OpenAI:
    return OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL, timeout=60)


def _montar_mensagens(atividade: dict) -> list[dict]:
    dias = (date.fromisoformat(atividade["prazo"]) - date.today()).days
    if dias < 0:
        situacao = f"vencido há {-dias} dia(s)"
    elif dias == 0:
        situacao = "vence hoje"
    else:
        situacao = f"faltam {dias} dia(s)"

    usuario = (
        f"Atividade: {atividade['nome']}\n"
        f"Descrição: {atividade['descricao']}\n"
        f"Prazo: {atividade['prazo']} ({situacao})\n"
        f"Dificuldade: {atividade['dificuldade']}"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": usuario},
    ]


def _chamar_modelo(client: OpenAI, mensagens: list[dict], atividade: dict) -> str:
    base = dict(
        model=LLM_MODEL,
        messages=mensagens,
        temperature=0.3,
        max_completion_tokens=4000,
    )
    if LANGFUSE_ATIVO:
        base["name"] = "studyflow-gerar-plano"
        base["metadata"] = {
            "atividade_id": atividade.get("id"),
            "dificuldade": atividade.get("dificuldade"),
        }

    try:
        # Preferência: saída estruturada com o esquema do Pydantic.
        resposta = client.chat.completions.create(
            **base,
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "plano", "schema": Plano.model_json_schema()},
            },
        )
    except openai.BadRequestError:
        # Modelo sem suporte a json_schema: recorre ao modo JSON simples.
        resposta = client.chat.completions.create(
            **base, response_format={"type": "json_object"}
        )
    return resposta.choices[0].message.content or ""


def _extrair_json(texto: str) -> str:
    texto = texto.strip()
    if texto.startswith("```"):
        texto = texto.strip("`")
        if texto.lower().startswith("json"):
            texto = texto[4:]
    return texto.strip()


def gerar_plano(atividade: dict) -> tuple[Plano, str]:
    """Gera e valida o plano. Retorna (plano, modelo_utilizado)."""
    if not LLM_API_KEY:
        raise ErroIA("Chave da API não configurada. Defina LLM_API_KEY no arquivo .env.")

    client = _criar_cliente()
    mensagens = _montar_mensagens(atividade)
    ultimo_erro = ""

    try:
        for _ in range(MAX_TENTATIVAS):
            texto = _chamar_modelo(client, mensagens, atividade)
            try:
                plano = Plano.model_validate(json.loads(_extrair_json(texto)))
                return plano, LLM_MODEL
            except (json.JSONDecodeError, ValidationError) as e:
                ultimo_erro = str(e)
                mensagens = mensagens + [
                    {"role": "assistant", "content": texto},
                    {
                        "role": "user",
                        "content": "A resposta anterior foi inválida. Responda novamente "
                        "apenas com o JSON no formato pedido.",
                    },
                ]
    except openai.AuthenticationError:
        raise ErroIA("Chave da API inválida ou sem permissão. Verifique o .env.")
    except openai.RateLimitError:
        raise ErroIA("Limite de requisições do provedor atingido. Aguarde um instante.")
    except openai.APIConnectionError:
        raise ErroIA("Não foi possível conectar ao provedor de IA. Verifique a internet.")
    except openai.APIError as e:
        raise ErroIA(f"Erro retornado pelo provedor de IA: {e}")
    finally:
        if LANGFUSE_ATIVO:
            try:
                from langfuse import get_client

                get_client().flush()
            except Exception:
                pass  # observabilidade nunca deve derrubar a aplicação

    raise ErroIA(
        f"O modelo não retornou um plano válido após {MAX_TENTATIVAS} tentativas."
        + (f" Detalhe: {ultimo_erro[:200]}" if ultimo_erro else "")
    )