import pytest

from mealie.services.openai.transcription import parse_subtitle_content

legenda = """WEBVTT

1
00:00:01.000 --> 00:00:03.000
<c>Misture</c> a farinha

2
00:00:03.000 --> 00:00:05.000
com 2 ovos
"""


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("Misture a farinha", "Misture a farinha"), 
        ("WEBVTT\n\nMisture", "Misture"), 
        ("00:00:01.000 --> 00:00:03.000\nMisture", "Misture"),  
        ("1\nMisture", "Misture"),  
        ("Misture\n   \n\nmexa", "Misture mexa"),  
        ("<c>Misture</c> a <i>farinha</i>", "Misture a farinha"), 
        ("", ""), 
        ("WEBVTT\n\n1\n00:00:01.000 --> 00:00:03.000\n", ""),  
    ],
    ids=["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"],
)
def test_classes(entrada, esperado):
    assert parse_subtitle_content(entrada) == esperado


def test_entrada_none():
    # C10 (invalida)
    with pytest.raises(AttributeError):
        parse_subtitle_content(None)


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        (" ", ""),  
        ("a", "a"),  
        ("1", ""),  
        ("12", ""),
        ("12 ovos", "12 ovos"), 
        ("WEBVTT", ""),
        ("Texto WEBVTT", "Texto WEBVTT"),  
        ("a --> b", ""),
        ("a -> b", "a -> b"), 
    ],
)
def test_valor_limite(entrada, esperado):
    assert parse_subtitle_content(entrada) == esperado


@pytest.mark.xfail(strict=True, reason="numero do bloco nao e removido com \\r\\n")
def test_quebra_de_linha_windows():
    entrada = "WEBVTT\r\n\r\n1\r\n00:00:01.000 --> 00:00:03.000\r\nMisture a farinha\r\n"
    assert parse_subtitle_content(entrada) == "Misture a farinha"


@pytest.mark.parametrize(
    "linha, esperado",
    [
        ("Misture a farinha", "Misture a farinha"),  
        ("   ", ""),  
        ("WEBVTT", ""),  
        ("00:00:01.000 --> 00:00:03.000", ""), 
        ("12", ""), 
    ],
    ids=["T1", "T2-A", "T3-B", "T4-C", "T5-D"],
)
def test_mcdc(linha, esperado):
    assert parse_subtitle_content(linha) == esperado
