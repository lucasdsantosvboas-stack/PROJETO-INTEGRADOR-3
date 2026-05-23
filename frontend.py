# Interface de usuário (Frontend)
from nicegui import ui
import httpx
from datetime import date

BASE = "http://localhost:8000/api/v1"

STATUS_BG = {
    "DISPONIVEL": "background:#dcfce7;color:#166534",
    "ALUGADO":    "background:#dbeafe;color:#1e40af",
    "VENDIDO":    "background:#fee2e2;color:#991b1b",
    "INATIVO":    "background:#f3f4f6;color:#6b7280",
}
TIPO_BG = {
    "FISICA":   "background:#ccfbf1;color:#0f766e",
    "JURIDICA": "background:#ede9fe;color:#6d28d9",
}
PAG_BG = {
    "PENDENTE":  "background:#fef9c3;color:#854d0e",
    "PAGO":      "background:#dcfce7;color:#166534",
    "ATRASADO":  "background:#fee2e2;color:#991b1b",
    "CANCELADO": "background:#f3f4f6;color:#6b7280",
}
TIPO_PARCELA_BG   = "background:#e0e7ff;color:#3730a3"
TIPO_CONTRATO_BG  = {
    "VENDA":   "background:#ede9fe;color:#6d28d9",
    "ALUGUEL": "background:#dbeafe;color:#1e40af",
}

CARD_STYLE = "border-radius:20px;overflow:hidden;min-width:440px;max-width:480px;width:100%"

def tag(text: str, style: str):
    ui.label(text).style(
        f"display:inline-block;padding:2px 10px;border-radius:999px;"
        f"font-size:11px;font-weight:600;letter-spacing:.4px;{style}"
    )

def dlg(title: str, color: str):
    """Retorna (dialog, card) com tamanho e centralização corretos."""
    d = ui.dialog().props("persistent")
    with d, ui.card().style(CARD_STYLE):
        with ui.element("div").style(
            f"background:{color};padding:16px 20px;border-radius:20px 20px 0 0"
        ):
            ui.label(title).style("color:white;font-size:17px;font-weight:700")
    return d

# ── FUNÇÕES AUXILIARES ────────────────────────────────────────────────────────

async def api_get(path):
    try:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{BASE}{path}")
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        ui.notify(f"Falha de conexão: {e}", type="negative"); return []

async def api_post(path, data):
    async with httpx.AsyncClient() as c:
        return await c.post(f"{BASE}{path}", json=data)

async def api_put(path, data):
    async with httpx.AsyncClient() as c:
        return await c.put(f"{BASE}{path}", json=data)

async def api_patch(path, data):
    async with httpx.AsyncClient() as c:
        return await c.patch(f"{BASE}{path}", json=data)

def ok(r, msg):
    if r.status_code in (200, 201):
        ui.notify(msg, type="positive", position="top-right", timeout=2500); return True
    ui.notify(f"Erro: {r.json().get('detail','Erro desconhecido')}", type="negative", position="top-right"); return False

def section_header(label, btn_label, btn_color, btn_action):
    with ui.row().classes("justify-between items-center w-full mb-5"):
        ui.label(label).classes("text-2xl font-bold text-gray-800")
        ui.button(btn_label, on_click=btn_action).props(f"color={btn_color} unelevated rounded").classes("px-5")

def modal_actions(dlg_ref, save_fn, btn_color):
    with ui.row().style("justify-content:flex-end;gap:8px;padding:8px 20px 20px"):
        ui.button("Cancelar", on_click=dlg_ref.close).props("flat color=grey")
        ui.button("Salvar", on_click=save_fn).props(f"color={btn_color} unelevated rounded")

# ── IMÓVEIS ───────────────────────────────────────────────────────────────────

def build_imoveis():
    h = {"id": None}

    async def refresh():
        lista.clear()
        items = await api_get("/imoveis/")
        with lista:
            if not items:
                ui.label("Nenhum imóvel cadastrado.").classes("text-gray-400 py-8 text-center w-full")
                return
            for im in items:
                with ui.card().style("flex:0 0 calc(33.333% - 11px);width:calc(33.333% - 11px);border-radius:16px;border:1px solid #f1f5f9;box-shadow:0 1px 4px rgba(0,0,0,.06)").classes("hover:shadow-md transition-shadow"):
                    with ui.card_section():
                        with ui.row().classes("w-full justify-between items-center gap-4"):
                            with ui.column().classes("gap-1 flex-1 min-w-0"):
                                ui.label(im["titulo"]).classes("font-semibold text-gray-800")
                                ui.label(im["endereco"]).classes("text-sm text-gray-500")
                                with ui.row().classes("gap-2 mt-1 items-center"):
                                    tag(im["status"], STATUS_BG.get(im["status"], "background:#f3f4f6;color:#6b7280"))
                                    ui.label(f"R$ {float(im['preco_atual']):,.2f}").style(
                                        "color:#059669;font-weight:700;font-size:13px;"
                                        "background:#ecfdf5;padding:2px 10px;border-radius:999px")
                            with ui.row().classes("gap-2 shrink-0"):
                                ui.button("Editar", on_click=lambda _, i=im: open_edit(i)).props("flat dense color=primary size=sm")
                                ui.button("Status", on_click=lambda _, i=im: open_status(i)).props("flat dense color=orange size=sm")

    def open_create():
        for f in [f_titulo, f_descricao, f_endereco]: f.value = ""
        f_preco.value = None
        dlg_c.open()

    def open_edit(im):
        h["id"] = im["id"]
        e_titulo.value    = im["titulo"]
        e_descricao.value = im.get("descricao") or ""
        e_preco.value     = float(im["preco_atual"])
        e_endereco.value  = im["endereco"]
        e_status.value    = im["status"]
        dlg_e.open()

    def open_status(im):
        h["id"] = im["id"]
        s_status.value = im["status"]
        dlg_s.open()

    async def do_create():
        if len(f_titulo.value or "") < 5: ui.notify("Título: mín. 5 caracteres", type="warning"); return
        if not f_preco.value or f_preco.value <= 0: ui.notify("Preço deve ser > 0", type="warning"); return
        if len(f_endereco.value or "") < 10: ui.notify("Endereço: mín. 10 caracteres", type="warning"); return
        r = await api_post("/imoveis/", {"titulo": f_titulo.value, "descricao": f_descricao.value,
                                          "preco_atual": f_preco.value, "endereco": f_endereco.value, "status": "DISPONIVEL"})
        if ok(r, "Imóvel criado!"): dlg_c.close(); await refresh()

    async def do_edit():
        if len(e_titulo.value or "") < 5: ui.notify("Título: mín. 5 caracteres", type="warning"); return
        if not e_preco.value or e_preco.value <= 0: ui.notify("Preço deve ser > 0", type="warning"); return
        if len(e_endereco.value or "") < 10: ui.notify("Endereço: mín. 10 caracteres", type="warning"); return
        r = await api_put(f"/imoveis/{h['id']}", {"titulo": e_titulo.value, "descricao": e_descricao.value,
                                                    "preco_atual": e_preco.value, "endereco": e_endereco.value, "status": e_status.value})
        if ok(r, "Imóvel atualizado!"): dlg_e.close(); await refresh()

    async def do_status():
        r = await api_patch(f"/imoveis/{h['id']}/status", {"status": s_status.value})
        if ok(r, "Status atualizado!"): dlg_s.close(); await refresh()

    section_header("Imóveis", "+ Novo Imóvel", "primary", open_create)
    lista = ui.element("div").style("display:flex;flex-wrap:wrap;gap:16px;width:100%")

    # modal criar
    with ui.dialog().props("persistent") as dlg_c, ui.card().style(CARD_STYLE):
        with ui.element("div").style("background:#2563eb;padding:16px 20px;border-radius:20px 20px 0 0"):
            ui.label("Novo Imóvel").style("color:white;font-size:17px;font-weight:700")
        with ui.column().style("padding:16px 20px;gap:12px;width:100%"):
            f_titulo    = ui.input("Título do anúncio").props("outlined dense").classes("w-full")
            f_descricao = ui.textarea("Descrição").props("outlined dense").classes("w-full")
            f_preco     = ui.number("Preço (R$)", format="%.2f").props("outlined dense prefix=R$").classes("w-full")
            f_endereco  = ui.input("Endereço completo").props("outlined dense").classes("w-full")
        modal_actions(dlg_c, do_create, "primary")

    # modal editar
    with ui.dialog().props("persistent") as dlg_e, ui.card().style(CARD_STYLE):
        with ui.element("div").style("background:#f97316;padding:16px 20px;border-radius:20px 20px 0 0"):
            ui.label("Editar Imóvel").style("color:white;font-size:17px;font-weight:700")
        with ui.column().style("padding:16px 20px;gap:12px;width:100%"):
            e_titulo    = ui.input("Título do anúncio").props("outlined dense").classes("w-full")
            e_descricao = ui.textarea("Descrição").props("outlined dense").classes("w-full")
            e_preco     = ui.number("Preço (R$)", format="%.2f").props("outlined dense prefix=R$").classes("w-full")
            e_endereco  = ui.input("Endereço completo").props("outlined dense").classes("w-full")
            e_status    = ui.select(["DISPONIVEL","ALUGADO","VENDIDO","INATIVO"], label="Status").props("outlined dense").classes("w-full")
        modal_actions(dlg_e, do_edit, "orange")

    # modal status
    with ui.dialog().props("persistent") as dlg_s, ui.card().style("border-radius:20px;overflow:hidden;min-width:340px;max-width:380px;width:100%"):
        with ui.element("div").style("background:#334155;padding:16px 20px;border-radius:20px 20px 0 0"):
            ui.label("Alterar Status").style("color:white;font-size:17px;font-weight:700")
        with ui.column().style("padding:16px 20px;gap:12px;width:100%"):
            s_status = ui.select(["DISPONIVEL","ALUGADO","VENDIDO","INATIVO"], label="Novo status").props("outlined dense").classes("w-full")
        modal_actions(dlg_s, do_status, "grey-8")

    ui.timer(0.1, refresh, once=True)

# ── CLIENTES ──────────────────────────────────────────────────────────────────

def build_clientes():
    async def refresh():
        lista.clear()
        items = await api_get("/clientes/")
        with lista:
            if not items:
                ui.label("Nenhum cliente cadastrado.").classes("text-gray-400 py-8 text-center w-full")
                return
            for cl in items:
                with ui.card().style("flex:0 0 calc(33.333% - 11px);width:calc(33.333% - 11px);border-radius:16px;border:1px solid #f1f5f9;box-shadow:0 1px 4px rgba(0,0,0,.06)").classes("hover:shadow-md transition-shadow"):
                    with ui.card_section():
                        with ui.row().classes("justify-between items-center w-full"):
                            with ui.column().classes("gap-0"):
                                ui.label(cl["nome"]).classes("font-semibold text-gray-800")
                                ui.label(cl["contato"]).classes("text-sm text-gray-500")
                            tag(cl["tipo"], TIPO_BG.get(cl["tipo"], "background:#f3f4f6;color:#6b7280"))

    async def do_create():
        if len(f_nome.value or "") < 3: ui.notify("Nome: mín. 3 caracteres", type="warning"); return
        if len(f_contato.value or "") < 8: ui.notify("Contato: mín. 8 caracteres", type="warning"); return
        r = await api_post("/clientes/", {"nome": f_nome.value, "contato": f_contato.value, "tipo": f_tipo.value})
        if ok(r, "Cliente criado!"): dlg_c.close(); await refresh()

    section_header("Clientes", "+ Novo Cliente", "teal", lambda: dlg_c.open())
    lista = ui.element("div").style("display:flex;flex-wrap:wrap;gap:16px;width:100%")

    with ui.dialog().props("persistent") as dlg_c, ui.card().style(CARD_STYLE):
        with ui.element("div").style("background:#0d9488;padding:16px 20px;border-radius:20px 20px 0 0"):
            ui.label("Novo Cliente").style("color:white;font-size:17px;font-weight:700")
        with ui.column().style("padding:16px 20px;gap:12px;width:100%"):
            f_nome    = ui.input("Nome completo / Razão Social").props("outlined dense").classes("w-full")
            f_contato = ui.input("Telefone ou E-mail").props("outlined dense").classes("w-full")
            f_tipo    = ui.select(["FISICA","JURIDICA"], label="Tipo de pessoa", value="FISICA").props("outlined dense").classes("w-full")
        modal_actions(dlg_c, do_create, "teal")

    ui.timer(0.1, refresh, once=True)

# ── TRANSAÇÕES ────────────────────────────────────────────────────────────────

def build_transacoes():
    # mapas id→nome carregados ao abrir o modal
    imoveis_map:  dict[int, str] = {}
    clientes_map: dict[int, str] = {}

    async def refresh():
        lista.clear()
        items = await api_get("/transacoes/")
        with lista:
            if not items:
                ui.label("Nenhuma transação registrada.").classes("text-gray-400 py-8 text-center w-full")
                return
            for tr in items:
                titulo_im  = imoveis_map.get(tr["imovel_id"],  f"Imóvel #{tr['imovel_id']}")
                nome_prop  = clientes_map.get(tr["proprietario_id"], f"Cliente #{tr['proprietario_id']}")
                nome_cli   = clientes_map.get(tr["cliente_id"],      f"Cliente #{tr['cliente_id']}")
                with ui.card().style("flex:0 0 calc(33.333% - 11px);width:calc(33.333% - 11px);border-radius:16px;border:1px solid #f1f5f9;box-shadow:0 1px 4px rgba(0,0,0,.06)").classes("hover:shadow-md transition-shadow"):
                    with ui.card_section():
                        with ui.row().classes("justify-between items-center w-full"):
                            with ui.column().classes("gap-1 flex-1"):
                                with ui.row().classes("gap-2 items-center"):
                                    tag(tr["tipo_contrato"], TIPO_CONTRATO_BG.get(tr["tipo_contrato"], "background:#f3f4f6;color:#6b7280"))
                                    ui.label(titulo_im).classes("font-semibold text-gray-800")
                                ui.label(f"{nome_prop}  →  {nome_cli}").classes("text-sm text-gray-500")
                            ui.label(f"R$ {float(tr['valor_total_contrato']):,.2f}").style(
                                "color:#059669;font-weight:700;background:#ecfdf5;"
                                "padding:4px 12px;border-radius:999px;font-size:13px;white-space:nowrap")

    async def open_modal():
        # carrega listas e popula os selects
        imoveis  = await api_get("/imoveis/")
        clientes = await api_get("/clientes/")
        imoveis_map.clear();  imoveis_map.update({i["id"]: i["titulo"]  for i in imoveis})
        clientes_map.clear(); clientes_map.update({c["id"]: c["nome"]   for c in clientes})
        f_imovel.options  = {i["id"]: i["titulo"] for i in imoveis}
        f_prop.options    = {c["id"]: c["nome"]   for c in clientes}
        f_cliente.options = {c["id"]: c["nome"]   for c in clientes}
        f_imovel.value = f_prop.value = f_cliente.value = None
        f_imovel.update(); f_prop.update(); f_cliente.update()
        dlg_c.open()

    async def do_create():
        try:
            dados = {
                "imovel_id":           int(f_imovel.value),
                "proprietario_id":     int(f_prop.value),
                "cliente_id":          int(f_cliente.value),
                "tipo_contrato":       f_tipo.value,
                "valor_total_contrato": float(f_valor.value),
                "comissao_percentual":  float(f_comissao.value) if f_comissao.value else None,
                "sinal_negocio":        float(f_sinal.value)    if f_sinal.value    else None,
                "reajuste_anual_percentual": float(f_reajuste.value) if f_reajuste.value else None,
            }
        except (ValueError, TypeError):
            ui.notify("Preencha todos os campos obrigatórios", type="warning"); return
        r = await api_post("/transacoes/", dados)
        if ok(r, "Transação criada!"): dlg_c.close(); await refresh()

    section_header("Transações", "+ Nova Transação", "deep-purple", open_modal)
    lista = ui.element("div").style("display:flex;flex-wrap:wrap;gap:16px;width:100%")

    with ui.dialog().props("persistent") as dlg_c, ui.card().style(CARD_STYLE):
        with ui.element("div").style("background:#7c3aed;padding:16px 20px;border-radius:20px 20px 0 0"):
            ui.label("Nova Transação").style("color:white;font-size:17px;font-weight:700")
        with ui.column().style("padding:16px 20px;gap:12px;width:100%"):
            f_imovel  = ui.select({}, label="Imóvel").props("outlined dense use-input input-debounce=0 clearable").classes("w-full")
            f_tipo    = ui.select(["VENDA","ALUGUEL"], label="Tipo de contrato", value="VENDA").props("outlined dense").classes("w-full")
            f_prop    = ui.select({}, label="Proprietário").props("outlined dense use-input input-debounce=0 clearable").classes("w-full")
            f_cliente = ui.select({}, label="Comprador / Locatário").props("outlined dense use-input input-debounce=0 clearable").classes("w-full")
            f_valor   = ui.number("Valor Total (R$)", format="%.2f").props("outlined dense prefix=R$").classes("w-full")
            with ui.expansion("Campos opcionais").classes("w-full border rounded-xl text-sm"):
                with ui.column().classes("gap-3 p-2"):
                    with ui.row().classes("w-full gap-3"):
                        f_comissao = ui.number("Comissão %", format="%.2f").props("outlined dense").classes("flex-1")
                        f_sinal    = ui.number("Sinal (R$)", format="%.2f").props("outlined dense").classes("flex-1")
                    f_reajuste = ui.number("Reajuste Anual %", format="%.2f").props("outlined dense").classes("w-full")
        modal_actions(dlg_c, do_create, "deep-purple")

    ui.timer(0.1, refresh, once=True)

# ── FINANCEIRO ────────────────────────────────────────────────────────────────

def build_financeiro():
    h = {"id": None}
    transacoes_map: dict[int, str] = {}

    async def refresh():
        # carrega mapa de transações para exibir label nos cards
        transacoes = await api_get("/transacoes/")
        transacoes_map.clear()
        transacoes_map.update({t["id"]: f"#{t['id']} — {t['tipo_contrato']} | Imóvel #{t['imovel_id']}" for t in transacoes})

        lista.clear()
        items = await api_get("/parcelas/")
        with lista:
            if not items:
                ui.label("Nenhuma parcela registrada.").classes("text-gray-400 py-8 text-center w-full")
                return
            for p in items:
                label_tr = transacoes_map.get(p["transacao_id"], f"Transação #{p['transacao_id']}")
                with ui.card().style("flex:0 0 calc(33.333% - 11px);width:calc(33.333% - 11px);border-radius:16px;border:1px solid #f1f5f9;box-shadow:0 1px 4px rgba(0,0,0,.06)").classes("hover:shadow-md transition-shadow"):
                    with ui.card_section():
                        with ui.row().classes("justify-between items-center w-full"):
                            with ui.column().classes("gap-1 flex-1"):
                                with ui.row().classes("gap-2 items-center"):
                                    tag(p["status_pagamento"], PAG_BG.get(p["status_pagamento"], "background:#f3f4f6;color:#6b7280"))
                                    tag(p["tipo_parcela"], TIPO_PARCELA_BG)
                                ui.label(label_tr).classes("text-sm text-gray-500")
                                ui.label(f"Venc. {p['data_vencimento']}").classes("text-xs text-gray-400")
                                ui.label(f"R$ {float(p['valor_parcela']):,.2f}").style(
                                    "color:#059669;font-weight:700;font-size:13px;margin-top:2px")
                            if p["status_pagamento"] != "PAGO":
                                def _open(pid=p["id"]):
                                    h["id"] = pid
                                    b_data.value = str(date.today())
                                    dlg_baixa.open()
                                ui.button("Dar Baixa", on_click=_open).props("color=positive unelevated rounded size=sm")

    async def open_modal():
        transacoes = await api_get("/transacoes/")
        transacoes_map.clear()
        transacoes_map.update({t["id"]: f"#{t['id']} — {t['tipo_contrato']} | Imóvel #{t['imovel_id']}" for t in transacoes})
        f_transacao.options = {t["id"]: f"#{t['id']} — {t['tipo_contrato']} | Imóvel #{t['imovel_id']}" for t in transacoes}
        f_transacao.value = None
        f_transacao.update()
        dlg_c.open()

    async def do_create():
        try:
            dados = {"transacao_id": int(f_transacao.value), "valor_parcela": float(f_valor.value),
                     "data_vencimento": f_venc.value, "tipo_parcela": f_tipo.value}
        except (ValueError, TypeError):
            ui.notify("Preencha todos os campos corretamente", type="warning"); return
        r = await api_post("/parcelas/", dados)
        if ok(r, "Parcela criada!"): dlg_c.close(); await refresh()

    async def do_baixa():
        r = await api_patch(f"/parcelas/{h['id']}/pagar", {"data_pagamento_efetivo": b_data.value})
        if ok(r, "Pagamento registrado!"): dlg_baixa.close(); await refresh()

    section_header("Financeiro", "+ Nova Parcela", "positive", open_modal)
    lista = ui.element("div").style("display:flex;flex-wrap:wrap;gap:16px;width:100%")

    with ui.dialog().props("persistent") as dlg_c, ui.card().style(CARD_STYLE):
        with ui.element("div").style("background:#16a34a;padding:16px 20px;border-radius:20px 20px 0 0"):
            ui.label("Nova Parcela").style("color:white;font-size:17px;font-weight:700")
        with ui.column().style("padding:16px 20px;gap:12px;width:100%"):
            f_transacao = ui.select({}, label="Transação").props("outlined dense use-input input-debounce=0 clearable").classes("w-full")
            f_valor     = ui.number("Valor (R$)", format="%.2f").props("outlined dense prefix=R$").classes("w-full")
            f_venc      = ui.input("Data de Vencimento", placeholder="AAAA-MM-DD").props("outlined dense").classes("w-full")
            f_tipo      = ui.select(["SINAL","COMISSAO","ALUGUEL","REAJUSTE","OUTRO"], label="Tipo", value="ALUGUEL").props("outlined dense").classes("w-full")
        modal_actions(dlg_c, do_create, "positive")

    with ui.dialog().props("persistent") as dlg_baixa, ui.card().style("border-radius:20px;overflow:hidden;min-width:360px;max-width:400px;width:100%"):
        with ui.element("div").style("background:#16a34a;padding:16px 20px;border-radius:20px 20px 0 0"):
            ui.label("Registrar Pagamento").style("color:white;font-size:17px;font-weight:700")
        with ui.column().style("padding:16px 20px;gap:12px;width:100%"):
            b_data = ui.input("Data do Pagamento", placeholder="AAAA-MM-DD").props("outlined dense").classes("w-full")
        with ui.row().style("justify-content:flex-end;gap:8px;padding:8px 20px 20px"):
            ui.button("Cancelar", on_click=dlg_baixa.close).props("flat color=grey")
            ui.button("Confirmar Pagamento", on_click=do_baixa).props("color=positive unelevated rounded")

    ui.timer(0.1, refresh, once=True)

# ── CORRETORES ────────────────────────────────────────────────────────────────

def build_corretores():
    async def refresh():
        lista.clear()
        items = await api_get("/corretores/")
        with lista:
            if not items:
                ui.label("Nenhum corretor cadastrado.").classes("text-gray-400 py-8 text-center w-full")
                return
            for cr in items:
                status_color = "background:#dcfce7;color:#166534" if cr.get("ativo") else "background:#fee2e2;color:#991b1b"
                status_text = "ATIVO" if cr.get("ativo") else "INATIVO"
                with ui.card().style("flex:0 0 calc(33.333% - 11px);width:calc(33.333% - 11px);border-radius:16px;border:1px solid #f1f5f9;box-shadow:0 1px 4px rgba(0,0,0,.06)").classes("hover:shadow-md transition-shadow"):
                    with ui.card_section():
                        with ui.row().classes("justify-between items-center w-full"):
                            with ui.column().classes("gap-0"):
                                ui.label(cr["nome"]).classes("font-semibold text-gray-800")
                                ui.label(cr["email"]).classes("text-sm text-gray-500")
                                ui.label(f"CRECI: {cr['registro_profissional']}").classes("text-xs text-gray-400 mt-1")
                            tag(status_text, status_color)

    async def do_create():
        if len(f_nome.value or "") < 3: ui.notify("Nome: mín. 3 caracteres", type="warning"); return
        if len(f_senha.value or "") < 8: ui.notify("Senha: mín. 8 caracteres", type="warning"); return
        r = await api_post("/corretores/", {"nome": f_nome.value, "email": f_email.value, "registro_profissional": f_creci.value, "senha": f_senha.value})
        if ok(r, "Corretor criado!"): dlg_c.close(); await refresh()

    section_header("Corretores", "+ Novo Corretor", "blue-grey", lambda: dlg_c.open())
    lista = ui.element("div").style("display:flex;flex-wrap:wrap;gap:16px;width:100%")

    with ui.dialog().props("persistent") as dlg_c, ui.card().style(CARD_STYLE):
        with ui.element("div").style("background:#64748b;padding:16px 20px;border-radius:20px 20px 0 0"):
            ui.label("Novo Corretor").style("color:white;font-size:17px;font-weight:700")
        with ui.column().style("padding:16px 20px;gap:12px;width:100%"):
            f_nome  = ui.input("Nome completo").props("outlined dense").classes("w-full")
            f_email = ui.input("E-mail").props("outlined dense").classes("w-full")
            f_creci = ui.input("Registro Profissional (CRECI)").props("outlined dense").classes("w-full")
            f_senha = ui.input("Senha de Acesso", password=True).props("outlined dense type=password").classes("w-full")
        modal_actions(dlg_c, do_create, "blue-grey")

    ui.timer(0.1, refresh, once=True)

# ── LEADS ─────────────────────────────────────────────────────────────────────

def build_leads():
    corretores_map: dict[int, str] = {}

    async def refresh():
        lista.clear()
        corretores = await api_get("/corretores/")
        corretores_map.clear()
        corretores_map.update({c["id"]: c["nome"] for c in corretores})
        
        items = await api_get("/leads/")
        with lista:
            if not items:
                ui.label("Nenhum lead registrado.").classes("text-gray-400 py-8 text-center w-full")
                return
            for ld in items:
                corretor_nome = corretores_map.get(ld["corretor_id"], f"Corretor #{ld['corretor_id']}")
                with ui.card().style("flex:0 0 calc(33.333% - 11px);width:calc(33.333% - 11px);border-radius:16px;border:1px solid #f1f5f9;box-shadow:0 1px 4px rgba(0,0,0,.06)").classes("hover:shadow-md transition-shadow"):
                    with ui.card_section():
                        with ui.row().classes("justify-between items-start w-full"):
                            with ui.column().classes("gap-0"):
                                ui.label(ld["nome"]).classes("font-semibold text-gray-800")
                                ui.label(ld["telefone"]).classes("text-sm text-gray-500")
                                ui.label(f"Interesse: {ld.get('interesse') or 'Não informado'}").classes("text-xs text-gray-400 mt-1")
                                ui.label(f"Corretor: {corretor_nome}").classes("text-xs text-blue-500 mt-1 font-medium")
                            tag(ld["status"], "background:#fef3c7;color:#b45309")

    async def open_modal():
        corretores = await api_get("/corretores/")
        f_corretor.options = {c["id"]: c["nome"] for c in corretores}
        f_corretor.value = None
        f_corretor.update()
        dlg_c.open()

    async def do_create():
        if len(f_nome.value or "") < 3: ui.notify("Nome: mín. 3 caracteres", type="warning"); return
        if len(f_telefone.value or "") < 8: ui.notify("Telefone: mín. 8 caracteres", type="warning"); return
        if not f_corretor.value: ui.notify("Selecione um corretor", type="warning"); return
        
        dados = {"nome": f_nome.value, "telefone": f_telefone.value, "interesse": f_interesse.value, "corretor_id": int(f_corretor.value)}
        r = await api_post("/leads/", dados)
        if ok(r, "Lead registrado!"): dlg_c.close(); await refresh()

    section_header("Leads", "+ Novo Lead", "amber-8", open_modal)
    lista = ui.element("div").style("display:flex;flex-wrap:wrap;gap:16px;width:100%")

    with ui.dialog().props("persistent") as dlg_c, ui.card().style(CARD_STYLE):
        with ui.element("div").style("background:#d97706;padding:16px 20px;border-radius:20px 20px 0 0"):
            ui.label("Novo Lead").style("color:white;font-size:17px;font-weight:700")
        with ui.column().style("padding:16px 20px;gap:12px;width:100%"):
            f_nome      = ui.input("Nome do Lead").props("outlined dense").classes("w-full")
            f_telefone  = ui.input("Telefone").props("outlined dense").classes("w-full")
            f_interesse = ui.input("Interesse (ex: Comprar casa)").props("outlined dense").classes("w-full")
            f_corretor  = ui.select({}, label="Atribuir ao Corretor").props("outlined dense use-input input-debounce=0 clearable").classes("w-full")
        modal_actions(dlg_c, do_create, "amber-8")

    ui.timer(0.1, refresh, once=True)

# ── VISITAS ───────────────────────────────────────────────────────────────────

def build_visitas():
    imoveis_map: dict[int, str] = {}
    corretores_map: dict[int, str] = {}
    leads_map: dict[int, str] = {}

    async def refresh():
        lista.clear()
        imoveis = await api_get("/imoveis/")
        corretores = await api_get("/corretores/")
        leads = await api_get("/leads/")
        
        imoveis_map.clear()
        imoveis_map.update({i["id"]: i["titulo"] for i in imoveis})
        corretores_map.clear()
        corretores_map.update({c["id"]: c["nome"] for c in corretores})
        leads_map.clear()
        leads_map.update({l["id"]: l["nome"] for l in leads})
        
        items = await api_get("/visitas/")
        with lista:
            if not items:
                ui.label("Nenhuma visita agendada.").classes("text-gray-400 py-8 text-center w-full")
                return
            for v in items:
                imovel_nome = imoveis_map.get(v["imovel_id"], f"Imóvel #{v['imovel_id']}")
                corretor_nome = corretores_map.get(v["corretor_id"], f"Corretor #{v['corretor_id']}")
                lead_nome = leads_map.get(v["lead_id"], f"Lead #{v['lead_id']}")
                
                status_bg = {
                    "AGENDADA": "background:#dbeafe;color:#1e40af",
                    "REALIZADA": "background:#dcfce7;color:#166534",
                    "CANCELADA": "background:#fee2e2;color:#991b1b"
                }.get(v["status"], "background:#f3f4f6;color:#6b7280")
                
                with ui.card().style("flex:0 0 calc(33.333% - 11px);width:calc(33.333% - 11px);border-radius:16px;border:1px solid #f1f5f9;box-shadow:0 1px 4px rgba(0,0,0,.06)").classes("hover:shadow-md transition-shadow"):
                    with ui.card_section():
                        with ui.row().classes("justify-between items-start w-full"):
                            with ui.column().classes("gap-1"):
                                ui.label(f"Data: {v['data_visita'].replace('T', ' ')[:16]}").classes("font-semibold text-gray-800")
                                ui.label(f"Imóvel: {imovel_nome}").classes("text-sm text-gray-600")
                                ui.label(f"Lead: {lead_nome}").classes("text-xs text-gray-500")
                                ui.label(f"Corretor: {corretor_nome}").classes("text-xs text-blue-500 font-medium")
                            tag(v["status"], status_bg)

    async def open_modal():
        imoveis = await api_get("/imoveis/")
        corretores = await api_get("/corretores/")
        leads = await api_get("/leads/")
        
        f_imovel.options = {i["id"]: i["titulo"] for i in imoveis}
        f_corretor.options = {c["id"]: c["nome"] for c in corretores}
        f_lead.options = {l["id"]: l["nome"] for l in leads}
        
        f_imovel.value = f_corretor.value = f_lead.value = None
        f_imovel.update(); f_corretor.update(); f_lead.update()
        
        f_data.value = ""
        dlg_c.open()

    async def do_create():
        if not f_data.value: ui.notify("Selecione a data/hora", type="warning"); return
        if not f_imovel.value: ui.notify("Selecione um imóvel", type="warning"); return
        if not f_corretor.value: ui.notify("Selecione um corretor", type="warning"); return
        if not f_lead.value: ui.notify("Selecione um lead", type="warning"); return
        
        dados = {
            "data_visita": f_data.value,
            "imovel_id": int(f_imovel.value),
            "corretor_id": int(f_corretor.value),
            "lead_id": int(f_lead.value)
        }
        r = await api_post("/visitas/", dados)
        if ok(r, "Visita agendada!"): dlg_c.close(); await refresh()

    section_header("Visitas", "+ Agendar Visita", "pink-6", open_modal)
    lista = ui.element("div").style("display:flex;flex-wrap:wrap;gap:16px;width:100%")

    with ui.dialog().props("persistent") as dlg_c, ui.card().style(CARD_STYLE):
        with ui.element("div").style("background:#db2777;padding:16px 20px;border-radius:20px 20px 0 0"):
            ui.label("Nova Visita").style("color:white;font-size:17px;font-weight:700")
        with ui.column().style("padding:16px 20px;gap:12px;width:100%"):
            f_data     = ui.input("Data e Hora").props("outlined dense type=datetime-local").classes("w-full")
            f_imovel   = ui.select({}, label="Imóvel").props("outlined dense use-input input-debounce=0 clearable").classes("w-full")
            f_corretor = ui.select({}, label="Corretor responsável").props("outlined dense use-input input-debounce=0 clearable").classes("w-full")
            f_lead     = ui.select({}, label="Lead interessado").props("outlined dense use-input input-debounce=0 clearable").classes("w-full")
        modal_actions(dlg_c, do_create, "pink-6")

    ui.timer(0.1, refresh, once=True)

# ── ESTRUTURA BASE DA PÁGINA ──────────────────────────────────────────────────

ui.add_head_html('''
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  * { font-family: "Inter", sans-serif !important; }
  body, .nicegui-content { background: #f1f5f9 !important; }
  .q-tab--active .q-tab__label { font-weight: 700; }
  .q-tab__indicator { height: 3px; border-radius: 3px; }
  .q-icon { display: none !important; }
  .q-dialog__inner { align-items: center !important; justify-content: center !important; }
  .q-dialog__inner > div { margin: auto !important; }
</style>
''', shared=True)

# token em memória para a sessão
session = {"token": None, "username": None}

def get_headers():
    return {"Authorization": f"Bearer {session['token']}"} if session["token"] else {}

# ── CATÁLOGO PÚBLICO ──────────────────────────────────────────────────────────

@ui.page("/catalogo")
def catalogo_page():
    """Página pública de catálogo de imóveis com filtros (sem autenticação necessária)."""
    
    imoveis_lista = []
    bairros_disponiveis = []
    tipos_transacao = ["VENDA", "ALUGUEL"]
    tipos_imovel_lista = ["APARTAMENTO", "CASA", "COMERCIAL", "TERRENO", "COBERTURA", "KITINETE"]
    
    async def carregar_bairros():
        """Carrega lista de bairros disponíveis."""
        nonlocal bairros_disponiveis
        try:
            async with httpx.AsyncClient() as c:
                r = await c.get(f"{BASE}/imoveis/bairros/")
            if r.status_code == 200:
                bairros_disponiveis = r.json()
                combo_bairro.options = ["Todos"] + bairros_disponiveis
                combo_bairro.value = "Todos"
                combo_bairro.update()
        except Exception as e:
            print(f"Erro ao carregar bairros: {e}")
    
    async def filtrar_imoveis():
        """Aplica filtros e carrega imóveis."""
        nonlocal imoveis_lista
        try:
            # Monta query params
            params = {}
            
            if combo_bairro.value and combo_bairro.value != "Todos":
                params["bairro"] = combo_bairro.value
            
            if combo_tipo.value and combo_tipo.value != "Ambos":
                params["tipo"] = combo_tipo.value
            
            if combo_imovel.value and combo_imovel.value != "Todos":
                params["tipo_imovel"] = combo_imovel.value
            
            if slider_valor.value and slider_valor.value[0] > 0:
                params["valor_min"] = slider_valor.value[0]
            
            if slider_valor.value and slider_valor.value[1] < 1000000:
                params["valor_max"] = slider_valor.value[1]
            
            # Faz requisição
            async with httpx.AsyncClient() as c:
                r = await c.get(f"{BASE}/imoveis/filtrado/", params=params)
            
            if r.status_code == 200:
                imoveis_lista = r.json()
                await exibir_imoveis()
            else:
                ui.notify("Erro ao buscar imóveis", type="negative")
        except Exception as e:
            ui.notify(f"Erro: {e}", type="negative")
    
    async def exibir_imoveis():
        """Exibe os imóveis em cards."""
        cards_container.clear()
        
        if not imoveis_lista:
            with cards_container:
                ui.label("Nenhum imóvel encontrado com os filtros selecionados.").classes("text-gray-500 py-12 text-center w-full text-lg")
            return
        
        with cards_container:
            for imovel in imoveis_lista:
                with ui.card().style(
                    "flex:0 0 calc(33.333% - 12px);width:calc(33.333% - 12px);"
                    "border-radius:16px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,.1);"
                    "transition:all .3s;cursor:pointer"
                ).classes("hover:shadow-xl hover:-translate-y-1").props("flat"):
                    
                    # Foto
                    with ui.image(source=imovel.get("foto_url") or "/api/v1/static/placeholder.png").style(
                        "width:100%;height:200px;object-fit:cover"
                    ):
                        pass
                    
                    # Conteúdo
                    with ui.card_section():
                        # Título e localização
                        ui.label(imovel["titulo"]).classes("font-bold text-lg text-gray-900")
                        ui.label(imovel.get("bairro", "Bairro não informado")).classes("text-sm text-gray-500 mb-3")
                        
                        # Tags
                        with ui.row().classes("gap-2 items-center flex-wrap mb-3"):
                            if imovel.get("tipo_transacao"):
                                tipo_color = "bg-purple-100 text-purple-800" if imovel["tipo_transacao"] == "VENDA" else "bg-blue-100 text-blue-800"
                                ui.label(imovel["tipo_transacao"]).classes(f"px-3 py-1 rounded-full text-xs font-semibold {tipo_color}")
                            
                            if imovel.get("tipo_imovel"):
                                ui.label(imovel["tipo_imovel"]).classes("px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-800")
                        
                        # Preço
                        ui.label(f"R$ {float(imovel['preco_atual']):,.2f}").style(
                            "color:#059669;font-weight:700;font-size:18px"
                        )
                        
                        # Descrição resumida
                        desc = imovel.get("descricao", "Sem descrição")
                        if len(desc) > 100:
                            desc = desc[:100] + "..."
                        ui.label(desc).classes("text-sm text-gray-600 mt-2")
                    
                    # Botão
                    with ui.card_section():
                        async def ver_detalhes(imovel_id=imovel["id"]):
                            await abrir_modal_detalhes(imovel_id)
                        
                        ui.button("Ver Detalhes", on_click=ver_detalhes).props(
                            "color=primary unelevated rounded"
                        ).classes("w-full")
    
    async def abrir_modal_detalhes(imovel_id: int):
        """Abre modal com detalhes do imóvel."""
        try:
            async with httpx.AsyncClient() as c:
                r = await c.get(f"{BASE}/imoveis/{imovel_id}")
            
            if r.status_code == 200:
                im = r.json()
                
                # Modal de detalhes
                with ui.dialog() as dlg_detalhes:
                    with ui.card().style("max-width:600px;border-radius:20px;overflow:hidden"):
                        # Foto grande
                        if im.get("foto_url"):
                            ui.image(source=im["foto_url"]).style("width:100%;height:300px;object-fit:cover")
                        
                        # Detalhes
                        with ui.card_section():
                            ui.label(im["titulo"]).classes("font-bold text-xl text-gray-900")
                            ui.label(im["endereco"]).classes("text-sm text-gray-600")
                            
                            with ui.row().classes("gap-2 my-3 flex-wrap"):
                                if im.get("bairro"):
                                    ui.label(f"Bairro: {im['bairro']}").classes("px-3 py-1 rounded text-sm bg-blue-50 text-blue-800")
                                if im.get("tipo_transacao"):
                                    ui.label(im["tipo_transacao"]).classes("px-3 py-1 rounded text-sm bg-purple-50 text-purple-800")
                                if im.get("tipo_imovel"):
                                    ui.label(im["tipo_imovel"]).classes("px-3 py-1 rounded text-sm bg-gray-100 text-gray-800")
                            
                            ui.label(f"R$ {float(im['preco_atual']):,.2f}").style(
                                "color:#059669;font-weight:700;font-size:22px;display:block;margin:12px 0"
                            )
                            
                            ui.label("Descrição:").classes("font-semibold text-gray-800 mt-4")
                            ui.label(im.get("descricao", "Sem descrição")).classes("text-sm text-gray-700 whitespace-pre-wrap")
                            
                            # Formulário de contato
                            ui.label("Entrar em Contato:").classes("font-semibold text-gray-800 mt-6")
                            
                            nome_contato = ui.input("Seu nome").props("outlined dense").classes("w-full mt-2")
                            email_contato = ui.input("Seu e-mail").props("outlined dense").classes("w-full")
                            telefone_contato = ui.input("Seu telefone").props("outlined dense").classes("w-full")
                            mensagem_contato = ui.textarea("Mensagem").props("outlined dense").classes("w-full")
                            
                            async def enviar_interesse():
                                if not nome_contato.value or not email_contato.value or not telefone_contato.value:
                                    ui.notify("Preencha nome, e-mail e telefone", type="warning")
                                    return
                                
                                # Cria um lead anônimo
                                try:
                                    # Primeiro, podemos tentar criar um cliente
                                    dados_cliente = {
                                        "nome": nome_contato.value,
                                        "contato": email_contato.value,
                                        "tipo": "FISICA"
                                    }
                                    
                                    async with httpx.AsyncClient() as c:
                                        r_cliente = await c.post(f"{BASE}/clientes/", json=dados_cliente)
                                    
                                    cliente_id = r_cliente.json().get("id") if r_cliente.status_code in (200, 201) else None
                                    
                                    # Depois, criar um lead para correlator (primeiro corretor disponível)
                                    # Nota: seria ideal selecionar um corretor. Por enquanto, assume-se que existe pelo menos um
                                    
                                    ui.notify("Obrigado pelo interesse! Em breve entraremos em contato.", type="positive")
                                    dlg_detalhes.close()
                                except Exception as e:
                                    ui.notify(f"Erro ao registrar interesse: {e}", type="negative")
                            
                            ui.button("Enviar Interesse", on_click=enviar_interesse).props(
                                "color=primary unelevated rounded"
                            ).classes("w-full mt-4")
                        
                        # Fechar
                        with ui.card_section():
                            ui.button("Fechar", on_click=dlg_detalhes.close).props("flat").classes("w-full")
                
                dlg_detalhes.open()
        except Exception as e:
            ui.notify(f"Erro ao buscar detalhes: {e}", type="negative")
    
    # ── Layout da Página ──
    
    with ui.header().style("background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);padding:0;box-shadow:0 4px 20px rgba(0,0,0,.2)"):
        with ui.row().classes("items-center justify-between w-full px-8").style("height:70px"):
            with ui.column().classes("gap-0 leading-none"):
                ui.label("🏠 Catálogo de Imóveis").style("color:white;font-weight:700;font-size:18px")
                ui.label("Encontre seu imóvel ideal").style("color:#e0e7ff;font-size:12px")
            ui.button("Entrar", on_click=lambda: ui.navigate.to("/login")).props("color=white flat").classes("px-6")
    
    with ui.column().classes("w-full max-w-7xl mx-auto px-6 py-8 gap-6"):
        # Filtros
        with ui.card().classes("w-full rounded-lg shadow-sm"):
            with ui.column().classes("gap-4"):
                ui.label("Filtrar Imóveis").classes("font-bold text-lg text-gray-800 mb-2")
                
                with ui.row().classes("gap-4 flex-wrap w-full"):
                    combo_bairro = ui.select([], label="Bairro").props("outlined dense clearable").classes("flex-1 min-w-48")
                    combo_tipo = ui.select(["Ambos"] + tipos_transacao, value="Ambos", label="Tipo").props("outlined dense").classes("flex-1 min-w-48")
                    combo_imovel = ui.select(["Todos"] + tipos_imovel_lista, value="Todos", label="Tipo de Imóvel").props("outlined dense").classes("flex-1 min-w-48")
                
                with ui.row().classes("gap-4 w-full items-end"):
                    ui.label("Faixa de Preço:").classes("font-semibold text-gray-700")
                    slider_valor = ui.slider(min=0, max=1000000, value=(0, 1000000)).props("range").classes("flex-1")
                    label_valor = ui.label("").classes("min-w-40 text-right")
                    
                    def atualizar_label():
                        label_valor.set_text(f"R$ {slider_valor.value[0]:,.0f} - R$ {slider_valor.value[1]:,.0f}")
                    
                    slider_valor.on_value_change(lambda: atualizar_label())
                    atualizar_label()
                
                with ui.row().classes("gap-2 justify-end w-full"):
                    ui.button("Buscar", on_click=filtrar_imoveis).props("color=primary unelevated rounded").classes("px-8")
                    ui.button("Limpar Filtros", on_click=lambda: combo_bairro.set_value("Todos") or combo_tipo.set_value("Ambos") or combo_imovel.set_value("Todos")).props("flat").classes("px-6")
        
        # Cards de imóveis
        cards_container = ui.element("div").style("display:flex;flex-wrap:wrap;gap:16px;width:100%")
        
        # Carrega dados iniciais
        async def init():
            await carregar_bairros()
            await filtrar_imoveis()
        
        ui.timer(0.1, init, once=True)

# ── TELA DE LOGIN ─────────────────────────────────────────────────────────────

@ui.page("/login")
def login_page():
    async def do_login():
        if not u_input.value or not p_input.value:
            ui.notify("Preencha usuário e senha", type="warning"); return
        try:
            async with httpx.AsyncClient() as c:
                r = await c.post(f"{BASE}/auth/login",
                                 json={"username": u_input.value, "password": p_input.value})
            if r.status_code == 200:
                data = r.json()
                session["token"]    = data["access_token"]
                session["username"] = u_input.value
                ui.navigate.to("/")
            else:
                ui.notify(r.json().get("detail", "Credenciais inválidas"), type="negative")
        except Exception as e:
            ui.notify(f"Falha de conexão: {e}", type="negative")

    with ui.column().style("min-height:100vh;display:flex;align-items:center;justify-content:center;background:#0f172a"):
        with ui.card().style("width:380px;border-radius:24px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.4)"):
            with ui.element("div").style("background:#1e293b;padding:32px 32px 24px;text-align:center"):
                ui.label("ERP Imobiliária").style("color:white;font-size:22px;font-weight:700;display:block")
                ui.label("Sistema de Gestão").style("color:#94a3b8;font-size:13px;display:block;margin-top:4px")
            with ui.column().style("padding:24px 32px 32px;gap:16px;background:white"):
                u_input = ui.input("Usuário").props("outlined dense").classes("w-full")
                p_input = ui.input("Senha", password=True, password_toggle_button=False).props("outlined dense type=password").classes("w-full")
                ui.button("Entrar", on_click=do_login).props("color=primary unelevated rounded").classes("w-full").style("height:44px;font-size:15px;font-weight:600")
                ui.label("Acesso restrito ao sistema").style("color:#94a3b8;font-size:11px;text-align:center")

# ── TELA PRINCIPAL ────────────────────────────────────────────────────────────

@ui.page("/")
def main_page():
    # redireciona para catálogo se não autenticado
    if not session["token"]:
        ui.navigate.to("/catalogo")
        return

    def do_logout():
        session["token"] = None
        session["username"] = None
        ui.navigate.to("/login")

    with ui.header().style("background:#0f172a;padding:0;box-shadow:0 2px 12px rgba(0,0,0,.4)"):
        with ui.row().classes("items-center justify-between w-full px-8").style("height:60px"):
            with ui.column().classes("gap-0 leading-none"):
                ui.label("ERP Imobiliária").style("color:white;font-weight:700;font-size:16px")
                ui.label("Sistema de Gestão").style("color:#94a3b8;font-size:11px")
            with ui.row().classes("items-center gap-4"):
                ui.label(f"● {session['username']}").style("color:#4ade80;font-size:13px")
                ui.button("Sair", on_click=do_logout).props("flat color=grey size=sm")

    with ui.column().classes("w-full max-w-5xl mx-auto px-6 py-6 gap-4"):
        with ui.card().classes("w-full rounded-2xl shadow-sm p-0 overflow-hidden"):
            with ui.tabs().props("dense indicator-color=primary align=left").classes("w-full px-2 bg-white") as tabs:
                t1 = ui.tab("Imóveis")
                t2 = ui.tab("Clientes")
                t3 = ui.tab("Transações")
                t4 = ui.tab("Financeiro")
                t5 = ui.tab("Corretores")
                t6 = ui.tab("Leads")
                t7 = ui.tab("Visitas")

        with ui.tab_panels(tabs, value=t1).classes("w-full bg-transparent"):
            with ui.tab_panel(t1).classes("p-0 pt-2"):
                build_imoveis()
            with ui.tab_panel(t2).classes("p-0 pt-2"):
                build_clientes()
            with ui.tab_panel(t3).classes("p-0 pt-2"):
                build_transacoes()
            with ui.tab_panel(t4).classes("p-0 pt-2"):
                build_financeiro()
            with ui.tab_panel(t5).classes("p-0 pt-2"):
                build_corretores()
            with ui.tab_panel(t6).classes("p-0 pt-2"):
                build_leads()
            with ui.tab_panel(t7).classes("p-0 pt-2"):
                build_visitas()

ui.run(title="ERP Imobiliária", dark=False, port=8080)
