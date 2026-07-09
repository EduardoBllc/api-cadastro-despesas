from app.schemas.abastecimento import (
    AtualizarAbastecimento,
    CriarAbastecimento,
    RespostaAbastecimento,
    RespostaPaginadaAbastecimento,
)
from app.schemas.carro import AtualizarCarro, CriarCarro, RespostaCarro
from app.schemas.categoria_despesa import (
    AtualizarCategoriaDespesa,
    CriarCategoriaDespesa,
    RespostaCategoriaDespesa,
)
from app.schemas.categoria_item import (
    AtualizarCategoriaItem,
    CriarCategoriaItem,
    RespostaCategoriaItem,
)
from app.schemas.configuracao import AtualizarConfiguracao, RespostaConfiguracao
from app.schemas.despesa import (
    AtualizarDespesa,
    CriarDespesa,
    RespostaDespesaDetalhe,
    RespostaDespesaLista,
    RespostaPaginadaDespesa,
)
from app.schemas.estabelecimento import (
    AtualizarEstabelecimento,
    CriarEstabelecimento,
    RespostaEstabelecimento,
)
from app.schemas.historico_preco_item import RespostaHistoricoPrecoItem
from app.schemas.item import AtualizarItem, CriarItem, RespostaItem
from app.schemas.item_despesa import (
    AtualizarItemDespesa,
    CriarItemDespesa,
    ItemDespesaParaAtualizar,
    RespostaItemDespesa,
)
from app.schemas.tipo_estabelecimento import (
    AtualizarTipoEstabelecimento,
    CriarTipoEstabelecimento,
    RespostaTipoEstabelecimento,
)
from app.schemas.relatorio import (
    AbastecimentoEficiencia,
    AbastecimentoMensal,
    GastoCategoria,
    GastoMensal,
)
from app.schemas.unidade_medida import (
    AtualizarUnidadeMedida,
    CriarUnidadeMedida,
    RespostaUnidadeMedida,
)

__all__ = [
    "AbastecimentoEficiencia",
    "AbastecimentoMensal",
    "GastoCategoria",
    "GastoMensal",
    "AtualizarAbastecimento",
    "AtualizarCarro",
    "AtualizarCategoriaDespesa",
    "AtualizarCategoriaItem",
    "AtualizarConfiguracao",
    "AtualizarDespesa",
    "AtualizarEstabelecimento",
    "AtualizarItem",
    "AtualizarItemDespesa",
    "AtualizarTipoEstabelecimento",
    "AtualizarUnidadeMedida",
    "CriarAbastecimento",
    "CriarCarro",
    "CriarCategoriaDespesa",
    "CriarCategoriaItem",
    "CriarDespesa",
    "CriarEstabelecimento",
    "CriarItem",
    "CriarItemDespesa",
    "CriarTipoEstabelecimento",
    "CriarUnidadeMedida",
    "ItemDespesaParaAtualizar",
    "RespostaAbastecimento",
    "RespostaCarro",
    "RespostaCategoriaDespesa",
    "RespostaCategoriaItem",
    "RespostaConfiguracao",
    "RespostaDespesaDetalhe",
    "RespostaDespesaLista",
    "RespostaEstabelecimento",
    "RespostaHistoricoPrecoItem",
    "RespostaItem",
    "RespostaItemDespesa",
    "RespostaPaginadaAbastecimento",
    "RespostaPaginadaDespesa",
    "RespostaTipoEstabelecimento",
    "RespostaUnidadeMedida",
]
