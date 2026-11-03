import pytest

from mealie.services.openai.transcription import parse_subtitle_content

# Legenda completa, parecida com as que o yt-dlp baixa
subtitle = """WEBVTT

1
00:00:01.000 --> 00:00:03.000
<c>Mix</c> the flour

2
00:00:03.000 --> 00:00:05.000
with 2 eggs
"""


@pytest.mark.parametrize(
    "text, expected",
    [
        pytest.param("Mix the flour", "Mix the flour", id="C1: Fala normal"),
        pytest.param("WEBVTT\n\nMix", "Mix", id="C2: Cabecalho WEBVTT"),
        pytest.param("00:00:01.000 --> 00:00:03.000\nMix", "Mix", id="C3: Linha de tempo"),
        pytest.param("1\nMix", "Mix", id="C4: Numero do bloco"),
        pytest.param("Mix\n   \n\nstir", "Mix stir", id="C5: Linhas vazias"),
        pytest.param("<c>Mix</c> the <i>flour</i>", "Mix the flour", id="C6: Tags de formatacao"),
        pytest.param(subtitle, "Mix the flour with 2 eggs", id="C7: Legenda completa"),
        pytest.param("", "", id="C8: Legenda vazia"),
        pytest.param("WEBVTT\n\n1\n00:00:01.000 --> 00:00:03.000\n", "", id="C9: Legenda sem fala"),
    ],
)
def test_equivalence_partitioning(text, expected):
    """Um representante de cada classe de equivalencia valida."""
    assert parse_subtitle_content(text) == expected


def test_invalid_input():
    """C10 (classe invalida): a funcao espera texto, com None ela da erro."""
    with pytest.raises(AttributeError):
        parse_subtitle_content(None)


@pytest.mark.parametrize(
    "text, expected",
    [
        pytest.param(" ", "", id="VL1: Um espaco"),
        pytest.param("a", "a", id="VL2: Um caractere"),
        pytest.param("1", "", id="VL3: Um digito"),
        pytest.param("12", "", id="VL4: So digitos"),
        pytest.param("12 eggs", "12 eggs", id="VL5: Numero com texto"),
        pytest.param("WEBVTT", "", id="VL6: WEBVTT no comeco"),
        pytest.param("Text WEBVTT", "Text WEBVTT", id="VL7: WEBVTT no meio"),
        pytest.param("a --> b", "", id="VL8: Seta de tempo"),
        pytest.param("a -> b", "a -> b", id="VL9: Seta incompleta"),
    ],
)
def test_boundary_value_analysis(text, expected):
    """Casos no limite entre linha que sai e linha que fica."""
    assert parse_subtitle_content(text) == expected


# Bug encontrado: com quebra de linha do Windows (\r\n) o numero do bloco
# nao e removido. Marcado como xfail para documentar a falha.
@pytest.mark.xfail(strict=True, reason="numero do bloco nao e removido com \\r\\n")
def test_windows_line_break():
    """C12: legenda com \\r\\n, que o formato WebVTT tambem aceita."""
    text = "WEBVTT\r\n\r\n1\r\n00:00:01.000 --> 00:00:03.000\r\nMix the flour\r\n"
    assert parse_subtitle_content(text) == "Mix the flour"


# MC/DC do if: A and B and C and D
# A = linha nao vazia, B = nao e WEBVTT, C = nao tem "-->", D = nao e so numero
@pytest.mark.parametrize(
    "line, expected",
    [
        pytest.param("Mix the flour", "Mix the flour", id="T1: Todas verdadeiras"),
        pytest.param("   ", "", id="T2: A falsa"),
        pytest.param("WEBVTT", "", id="T3: B falsa"),
        pytest.param("00:00:01.000 --> 00:00:03.000", "", id="T4: C falsa"),
        pytest.param("12", "", id="T5: D falsa"),
    ],
)
def test_mcdc(line, expected):
    """T1 tem tudo verdadeiro; cada outro teste muda so uma condicao."""
    assert parse_subtitle_content(line) == expected
