import pytest

@pytest.mark.asyncio
async def test_listar_estacoes(client):
    response = await client.get("/estacoes/", follow_redirects=False)
    assert response.status_code == 200
    estacoes = response.json()
    assert isinstance(estacoes, list)
