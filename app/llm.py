"""Cliente LLM do projeto — apontado para a Groq (gpt-oss, grátis).

`ChatOpenAI` é só o cliente compatível com a API da OpenAI; com `base_url`/`api_key`
da Groq, ele fala com a Groq — não chama OpenAI. Este helper centraliza essa
construção para o código de nós não repetir a fiação nem expor o nome confuso.
"""

from langchain_openai import ChatOpenAI

from app.config import settings


def chat(temperature: float = 0.0) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.llm_model,
        temperature=temperature,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
    )
