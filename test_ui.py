from nicegui import ui

@ui.page('/')
def index():
    ui.label('Teste OK - NiceGUI Funcionando!')

ui.run(title='Teste', port=8080)
