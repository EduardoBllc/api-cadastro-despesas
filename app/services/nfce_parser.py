"""Leitura do DANFE NFC-e (layout da SEFAZ RS) e rateio do desconto total."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from html.parser import HTMLParser

CENTAVO = Decimal("0.01")
MILESIMO = Decimal("0.001")
TAMANHO_CHAVE = 44
TAMANHO_CNPJ = 14
FORMATO_DATA_NOTA = "%d/%m/%Y"
_TAGS_VAZIAS = frozenset({"br", "img", "meta", "link", "input", "hr"})


class NotaInvalidaError(ValueError):
    pass


class ClasseDanfe(StrEnum):
    RAZAO_SOCIAL = "txtTopo"
    TEXTO_EMITENTE = "text"
    DESCRICAO = "txtTit"
    CODIGO = "RCod"
    QUANTIDADE = "Rqtd"
    UNIDADE = "RUN"
    VALOR_UNITARIO = "RvlUnit"
    VALOR_TOTAL_ITEM = "valor"
    TOTAL = "totalNumb"
    CHAVE = "chave"


class RotuloTotal(StrEnum):
    VALOR_TOTAL = "Valor total R$:"
    DESCONTOS = "Descontos R$:"
    VALOR_A_PAGAR = "Valor a pagar R$:"


_CAMPOS_ITEM = (
    ClasseDanfe.CODIGO,
    ClasseDanfe.QUANTIDADE,
    ClasseDanfe.UNIDADE,
    ClasseDanfe.VALOR_UNITARIO,
    ClasseDanfe.VALOR_TOTAL_ITEM,
)


@dataclass(frozen=True)
class ItemNota:
    codigo: str
    descricao: str
    quantidade: Decimal
    unidade: str
    valor_unitario: Decimal
    valor_total: Decimal


@dataclass(frozen=True)
class NotaNfce:
    chave: str
    data_emissao: date
    cnpj: str
    razao_social: str
    endereco: str
    itens: list[ItemNota]
    valor_total: Decimal
    desconto: Decimal
    valor_pago: Decimal


class _Coletor(HTMLParser):
    """Achata o HTML em (tag, classe, texto); classe = a do elemento com classe mais interno."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._pilha: list[tuple[str, str]] = []
        self.textos: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _TAGS_VAZIAS:
            return
        self._pilha.append((tag, dict(attrs).get("class") or ""))

    def handle_endtag(self, tag: str) -> None:
        if tag in _TAGS_VAZIAS:
            return
        for i in range(len(self._pilha) - 1, -1, -1):
            if self._pilha[i][0] == tag:
                del self._pilha[i:]
                return

    def handle_data(self, data: str) -> None:
        texto = " ".join(data.split())
        if not texto or not self._pilha:
            return
        tag = self._pilha[-1][0]
        classe = next((c for _, c in reversed(self._pilha) if c), "")
        self.textos.append((tag, classe, texto))


def _decimal_br(texto: str) -> Decimal:
    numero = re.search(r"\d[\d.]*(,\d+)?", texto)
    if numero is None:
        raise NotaInvalidaError(f"Valor numérico ausente em {texto!r}")
    return Decimal(numero.group(0).replace(".", "").replace(",", "."))


def _depois_do_rotulo(texto: str) -> str:
    return texto.split(":", 1)[-1].strip()


def parse(html: str) -> NotaNfce:
    coletor = _Coletor()
    coletor.feed(html)

    razao_social = ""
    textos_emitente: list[str] = []
    chave = ""
    totais: dict[str, str] = {}
    rotulo: str | None = None
    brutos: list[dict[str, str]] = []

    for tag, classe, texto in coletor.textos:
        if classe == ClasseDanfe.RAZAO_SOCIAL and not razao_social:
            razao_social = texto
        elif classe == ClasseDanfe.TEXTO_EMITENTE:
            textos_emitente.append(texto)
        elif classe == ClasseDanfe.DESCRICAO:
            brutos.append({ClasseDanfe.DESCRICAO: texto})
        elif brutos and classe in _CAMPOS_ITEM:
            atual = brutos[-1]
            atual[classe] = f"{atual.get(classe, '')} {texto}".strip()
        elif classe == ClasseDanfe.CHAVE:
            chave = re.sub(r"\D", "", texto)
        elif tag == "label":
            rotulo = texto
        elif ClasseDanfe.TOTAL in classe.split() and rotulo is not None:
            totais[rotulo] = texto
            rotulo = None

    texto_completo = " ".join(t for _, _, t in coletor.textos)
    emissao = re.search(r"Emissão:\s*(\d{2}/\d{2}/\d{4})", texto_completo)
    cnpj = next((re.sub(r"\D", "", t) for t in textos_emitente if "CNPJ" in t), "")

    if not (
        razao_social
        and brutos
        and emissao
        and len(chave) == TAMANHO_CHAVE
        and len(cnpj) == TAMANHO_CNPJ
    ):
        raise NotaInvalidaError("Estrutura da NFC-e não reconhecida")
    if RotuloTotal.VALOR_A_PAGAR not in totais or RotuloTotal.VALOR_TOTAL not in totais:
        raise NotaInvalidaError("Totais da NFC-e ausentes")

    try:
        itens = [
            ItemNota(
                codigo=re.sub(r"[^\w-]", "", _depois_do_rotulo(b[ClasseDanfe.CODIGO])),
                descricao=b[ClasseDanfe.DESCRICAO],
                # ponytail: quantidade com 4 casas é arredondada para as 3 que o banco guarda
                quantidade=_decimal_br(b[ClasseDanfe.QUANTIDADE]).quantize(MILESIMO, ROUND_HALF_UP),
                unidade=_depois_do_rotulo(b[ClasseDanfe.UNIDADE]),
                valor_unitario=_decimal_br(b[ClasseDanfe.VALOR_UNITARIO]),
                valor_total=_decimal_br(b[ClasseDanfe.VALOR_TOTAL_ITEM]),
            )
            for b in brutos
        ]
    except KeyError as exc:
        raise NotaInvalidaError(f"Campo de item ausente: {exc}") from exc

    # Endereço vem como "logradouro, número, complemento, bairro, município, UF" com vazios e "0"
    partes = [
        p.strip() for p in (textos_emitente[1] if len(textos_emitente) > 1 else "").split(",")
    ]
    endereco = ", ".join(p for p in partes if p and p != "0")

    return NotaNfce(
        chave=chave,
        data_emissao=datetime.strptime(emissao.group(1), FORMATO_DATA_NOTA).date(),
        cnpj=cnpj,
        razao_social=razao_social,
        endereco=endereco,
        itens=itens,
        valor_total=_decimal_br(totais[RotuloTotal.VALOR_TOTAL]),
        desconto=_decimal_br(totais.get(RotuloTotal.DESCONTOS, "0,00")),
        valor_pago=_decimal_br(totais[RotuloTotal.VALOR_A_PAGAR]),
    )


def total_no_banco(item: ItemNota, desconto_unitario: Decimal) -> Decimal:
    """Mesmo cálculo da coluna computada itens_despesa.valor_total (NUMERIC arredonda half-up)."""
    bruto = (item.valor_unitario - desconto_unitario) * item.quantidade
    return bruto.quantize(CENTAVO, ROUND_HALF_UP)


def ratear_desconto(itens: list[ItemNota], desconto: Decimal, valor_pago: Decimal) -> list[Decimal]:
    soma = sum((i.valor_total for i in itens), Decimal(0))
    descontos = [
        (desconto * i.valor_total / soma / i.quantidade).quantize(CENTAVO, ROUND_HALF_UP)
        if soma
        else Decimal(0).quantize(CENTAVO)
        for i in itens
    ]
    total = sum((total_no_banco(i, d) for i, d in zip(itens, descontos, strict=True)), Decimal(0))
    diferenca = total - valor_pago
    # ponytail: sobra de centavos vai para o 1º item com quantidade 1 (centavo exato); sem ele, fica
    idx = next((n for n, i in enumerate(itens) if i.quantidade == 1), None)
    if (
        diferenca
        and idx is not None
        and 0 <= descontos[idx] + diferenca < itens[idx].valor_unitario
    ):
        descontos[idx] += diferenca
    return descontos
