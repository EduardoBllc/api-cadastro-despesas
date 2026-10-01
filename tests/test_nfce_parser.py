from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.services.nfce_parser import (
    ItemNota,
    NotaInvalidaError,
    parse,
    ratear_desconto,
    total_no_banco,
)

FIXTURE = Path(__file__).parent / "fixtures" / "nfce_rs.html"
LINHA_DESCONTO = (
    '<div id="linhaTotal"><label>Descontos R$:</label><span class="totalNumb">14,65</span></div>'
)


@pytest.fixture(scope="module")
def html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def test_parse_cabecalho(html: str) -> None:
    nota = parse(html)
    assert nota.chave == "43260801132478002343651080003191521164954990"
    assert nota.cnpj == "01132478002343"
    assert nota.razao_social == "Irmaos Andreazza Ltda"
    assert nota.endereco == "Rua Padre Angelo Tronca, 2150, Sao Luiz, Caxias Do Sul, RS"
    assert nota.data_emissao == date(2026, 8, 19)


def test_parse_totais(html: str) -> None:
    nota = parse(html)
    assert nota.valor_total == Decimal("146.50")
    assert nota.desconto == Decimal("14.65")
    assert nota.valor_pago == Decimal("131.85")


def test_parse_itens(html: str) -> None:
    nota = parse(html)
    assert len(nota.itens) == 14
    assert nota.itens[0] == ItemNota(
        "162558", "Cenoura Kg", Decimal("1.250"), "KG", Decimal("8.99"), Decimal("11.23")
    )
    assert nota.itens[-1] == ItemNota(
        "102881", "Milho Oderich200g", Decimal("3.000"), "UN", Decimal("3.69"), Decimal("11.07")
    )


def test_parse_nota_sem_linha_de_desconto(html: str) -> None:
    assert LINHA_DESCONTO in html
    nota = parse(html.replace(LINHA_DESCONTO, ""))
    assert nota.desconto == Decimal("0.00")


def test_parse_html_sem_estrutura_de_nota() -> None:
    with pytest.raises(NotaInvalidaError):
        parse("<html><body>Nota não encontrada</body></html>")


def test_rateio_fecha_com_o_valor_pago(html: str) -> None:
    nota = parse(html)
    descontos = ratear_desconto(nota.itens, nota.desconto, nota.valor_pago)
    assert descontos[0] == Decimal("0.90")
    total = sum(total_no_banco(i, d) for i, d in zip(nota.itens, descontos, strict=True))
    assert total == nota.valor_pago


def test_rateio_ajusta_centavos_no_primeiro_item_com_quantidade_1() -> None:
    pesado = ItemNota("1", "Banana", Decimal("0.865"), "KG", Decimal("8.99"), Decimal("7.77"))
    unitario = ItemNota("2", "Leite", Decimal("1.000"), "UN", Decimal("10.00"), Decimal("10.00"))
    descontos = ratear_desconto([pesado, unitario], Decimal("0.00"), Decimal("17.77"))
    assert descontos == [Decimal("0.00"), Decimal("0.01")]


def test_rateio_sem_item_com_quantidade_1_mantem_a_diferenca() -> None:
    pesado = ItemNota("1", "Banana", Decimal("0.865"), "KG", Decimal("8.99"), Decimal("7.77"))
    assert ratear_desconto([pesado], Decimal("0.00"), Decimal("7.77")) == [Decimal("0.00")]
