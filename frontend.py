# frontend.py
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

# ── helpers ───────────────────────────────────────────────────────────────────

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

# ── SHELL ─────────────────────────────────────────────────────────────────────

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

# ── LOGIN PAGE ────────────────────────────────────────────────────────────────

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

# ── MAIN PAGE ─────────────────────────────────────────────────────────────────

@ui.page("/")
def main_page():
    # redireciona se não autenticado
    if not session["token"]:
        ui.navigate.to("/login")
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

        with ui.tab_panels(tabs, value=t1).classes("w-full bg-transparent"):
            with ui.tab_panel(t1).classes("p-0 pt-2"):
                build_imoveis()
            with ui.tab_panel(t2).classes("p-0 pt-2"):
                build_clientes()
            with ui.tab_panel(t3).classes("p-0 pt-2"):
                build_transacoes()
            with ui.tab_panel(t4).classes("p-0 pt-2"):
                build_financeiro()

ui.run(title="ERP Imobiliária", dark=False, port=8080)
