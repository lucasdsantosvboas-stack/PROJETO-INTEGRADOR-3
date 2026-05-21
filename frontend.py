# frontend.py
from nicegui import ui
import httpx

API_URL = "http://localhost:8000/api/v1/imoveis"

# --- LÓGICA DE COMUNICAÇÃO (API) ---

async def carregar_imoveis():
    container_lista.clear()
    try:
        async with httpx.AsyncClient() as client:
            resposta = await client.get(API_URL)
            
        if resposta.status_code == 200:
            imoveis = resposta.json()
            with container_lista:
                if not imoveis:
                    ui.label("Nenhum imóvel cadastrado.").classes('text-gray-500')
                for imovel in imoveis:
                    with ui.card().classes('w-full mb-2'):
                        ui.label(imovel['titulo']).classes('font-bold')
                        ui.label(f"R$ {imovel['preco_atual']}")
        else:
            ui.notify('Erro ao buscar imóveis', type='negative')
    except Exception as e:
        ui.notify(f'Falha na conexão: {e}', type='negative')

async def salvar_imovel():
    # 1. Montamos o Payload (Dicionário com os dados)
    dados = {
        "titulo": input_titulo.value,
        "descricao": input_descricao.value,
        "preco_atual": input_preco.value,
        "endereco": input_endereco.value,
        "status": "DISPONIVEL" # Status inicial padrão
    }
    
    # 2. Enviamos via POST para a API
    try:
        async with httpx.AsyncClient() as client:
            resposta = await client.post(API_URL, json=dados)
            
        if resposta.status_code == 201: # 201 Created
            ui.notify('Imóvel cadastrado com sucesso!', type='positive')
            dialog_cadastro.close() # Fecha o modal
            await carregar_imoveis() # Atualiza a lista na tela
        else:
            # Pega o erro que o FastAPI/Pydantic enviou
            erro = resposta.json().get('detail', 'Erro desconhecido')
            ui.notify(f'Erro no backend: {erro}', type='negative')
            
    except Exception as e:
         ui.notify(f'Erro de conexão: {e}', type='negative')


# --- INTERFACE DO USUÁRIO (UI) ---

ui.label('Painel da Imobiliária').classes('text-3xl font-bold mb-6')

with ui.row().classes('mb-4 gap-4'):
    ui.button('Atualizar Lista', on_click=carregar_imoveis)
    ui.button('Novo Imóvel', on_click=lambda: dialog_cadastro.open()).classes('bg-green-600')

# Modal de Cadastro
with ui.dialog() as dialog_cadastro, ui.card().classes('w-96'):
    ui.label('Cadastrar Novo Imóvel').classes('text-xl font-bold mb-4')
    
    # O botão de salvar só vai funcionar se retornarem True
    # O botão de salvar só vai funcionar se retornarem True
    input_titulo = ui.input('Título do Anúncio', 
                            validation={'Mínimo 5 caracteres': lambda v: len(v or '') >= 5}).classes('w-full')
    
    input_descricao = ui.textarea('Descrição').classes('w-full')
    
    input_preco = ui.number('Preço (R$)', format='%.2f',
                            validation={'Preço deve ser maior que zero': lambda v: v is not None and v > 0}).classes('w-full')
    
    input_endereco = ui.input('Endereço Completo',
                              validation={'Mínimo 10 caracteres': lambda v: len(v or '') >= 10}).classes('w-full')
    
    with ui.row().classes('w-full justify-end mt-4'):
        ui.button('Cancelar', on_click=dialog_cadastro.close).classes('bg-gray-400')
        ui.button('Salvar', on_click=salvar_imovel).classes('bg-blue-600')

# Container onde os imóveis aparecem
container_lista = ui.column().classes('w-full max-w-2xl')

# Carrega a lista automaticamente ao abrir a página
ui.timer(0.1, carregar_imoveis, once=True)

ui.run(title="ERP Imobiliário")