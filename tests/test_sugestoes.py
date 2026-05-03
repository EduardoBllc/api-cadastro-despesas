import pytest
from httpx import AsyncClient

PREFIX = "/sugestoes"

@pytest.mark.asyncio
async def test_sugerir_categoria_item(
    client: AsyncClient, 
    categoria_item_id: str,
    estabelecimento_id: str,
    categoria_despesa_id: str
):
    # Setup: criar despesa com itens para ter histórico
    # Precisamos criar uma categoria diferente para testar o ranking
    r_cat = await client.post("/categorias-item", json={"descricao": "Outra Categoria"})
    outra_cat_id = r_cat.json()["id"]

    # Cria despesa base
    payload_base = {
        "estabelecimento_id": estabelecimento_id,
        "categoria_despesa_id": categoria_despesa_id,
        "valor_total": "100.00",
    }
    
    # Adiciona 2 itens com categoria_item_id (66% de confiança)
    # Adiciona 1 item com outra_cat_id (33% de confiança)
    # Todos com a descrição similar "Chocolate Amargo"
    
    for _ in range(2):
        await client.post("/despesas", json={
            **payload_base,
            "itens": [{"descricao": "Chocolate Amargo", "categoria_item_id": categoria_item_id, "quantidade": 1, "valor_unitario": 5.0}]
        })
        
    await client.post("/despesas", json={
        **payload_base,
        "itens": [{"descricao": "Chocolate Amargo", "categoria_item_id": outra_cat_id, "quantidade": 1, "valor_unitario": 6.0}]
    })

    # Teste
    r = await client.get(f"{PREFIX}/categoria-item?termo=Chocolate")
    assert r.status_code == 200
    data = r.json()
    
    assert len(data["sugestoes"]) >= 2
    # O primeiro deve ser a categoria com 2 usos
    assert data["sugestoes"][0]["id"] == categoria_item_id
    assert data["sugestoes"][0]["confianca"] == 0.67 # 2/3 aproximado
    
    assert data["sugestoes"][1]["id"] == outra_cat_id
    assert data["sugestoes"][1]["confianca"] == 0.33 # 1/3 aproximado

@pytest.mark.asyncio
async def test_sugerir_categoria_despesa(
    client: AsyncClient,
    categoria_despesa_id: str,
    tipo_estabelecimento_id: str
):
    # Setup: Criar estabelecimentos similares
    # Est 1 -> Cat A
    # Est 2 -> Cat A
    # Est 3 -> Cat B
    
    r_cat_b = await client.post("/categorias-despesa", json={"descricao": "Cat B"})
    cat_b_id = r_cat_b.json()["id"]
    
    r_est_1 = await client.post("/estabelecimentos", json={"descricao": "Mercado Alpha", "tipo_id": tipo_estabelecimento_id})
    est_1_id = r_est_1.json()["id"]
    
    r_est_2 = await client.post("/estabelecimentos", json={"descricao": "Mercado Beta", "tipo_id": tipo_estabelecimento_id})
    est_2_id = r_est_2.json()["id"]
    
    # Despesas
    await client.post("/despesas", json={"estabelecimento_id": est_1_id, "categoria_despesa_id": categoria_despesa_id, "valor_total": 10})
    await client.post("/despesas", json={"estabelecimento_id": est_2_id, "categoria_despesa_id": categoria_despesa_id, "valor_total": 20})
    await client.post("/despesas", json={"estabelecimento_id": est_1_id, "categoria_despesa_id": cat_b_id, "valor_total": 30})

    # Busca por "Mercado"
    r = await client.get(f"{PREFIX}/categoria-despesa?termo=Mercado")
    assert r.status_code == 200
    data = r.json()
    
    # categoria_despesa_id apareceu 2 vezes, cat_b_id apareceu 1 vez
    assert data["sugestoes"][0]["id"] == categoria_despesa_id
    assert data["sugestoes"][0]["confianca"] == 0.67
