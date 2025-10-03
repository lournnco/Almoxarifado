import sys
import mysql.connector
from mysql.connector import Error
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QPushButton, QLineEdit, QListWidget,
    QMessageBox, QScrollArea, QFrame, QCheckBox,
    QSplitter, QSizePolicy, QDialog, QTabWidget
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
from datetime import datetime
from pytz import timezone
from Config import ConfigBanco

class ItemEmprestimo(QFrame):
    def __init__(self, id_emprestimo, componente, quantidade, data_emp, data_dev, status, parent=None):
        super().__init__(parent)
        self.id_emprestimo = id_emprestimo
        self.componente = componente
        self.quantidade = quantidade
        self.data_emp = data_emp
        self.data_dev = data_dev
        self.status = status
        self.configurar_interface()
       
    def configurar_interface(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedHeight(70)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)

        self.checkbox = QCheckBox()
        self.checkbox.setEnabled(self.status == "Emprestado")
        layout.addWidget(self.checkbox)

        layout_info = QVBoxLayout()
        layout_info.setSpacing(2)

        cabecalho = QHBoxLayout()
        label_nome = QLabel(f"<b>{self.componente}</b>")
        label_nome.setFont(QFont("Arial", 9))
        label_nome.setMinimumWidth(150)
        cabecalho.addWidget(label_nome)

        label_quantidade = QLabel(f"<b>Quantidade:</b> {self.quantidade}")
        label_quantidade.setFont(QFont("Arial", 9))
        cabecalho.addWidget(label_quantidade)
        cabecalho.addStretch()

        self.label_status = QLabel()
        if self.status == "Emprestado":
            self.label_status.setText("<b>EMPRESTADO</b>")
            self.label_status.setStyleSheet("color: red;")
        else:
            self.label_status.setText("<b>DEVOLVIDO</b>")
            self.label_status.setStyleSheet("color: green;")
        self.label_status.setFont(QFont("Arial", 9))
        cabecalho.addWidget(self.label_status)

        layout_info.addLayout(cabecalho)

        layout_datas = QHBoxLayout()
       
        layout_data_emp = QHBoxLayout()
        layout_data_emp.addWidget(QLabel("<b>Retirado:</b>"))
        self.label_data_emp = QLabel(self.data_emp)
        self.label_data_emp.setFont(QFont("Arial", 8))
        layout_data_emp.addWidget(self.label_data_emp)
        layout_datas.addLayout(layout_data_emp)

        layout_data_dev = QHBoxLayout()
        layout_data_dev.addWidget(QLabel("<b>Devolvido:</b>"))
        self.label_data_dev = QLabel(self.data_dev)
        self.label_data_dev.setFont(QFont("Arial", 8))
        layout_data_dev.addWidget(self.label_data_dev)
        layout_datas.addLayout(layout_data_dev)

        layout_info.addLayout(layout_datas)
        layout.addLayout(layout_info, 1)
        self.setLayout(layout)

        self.setStyleSheet("""
            QFrame {
                border: 1px solid #D6DBE0;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QLabel { color: #333333; }
            QCheckBox { color: #333333; }
            QFrame:hover { background-color: #F5F5F5; }
        """)

class AppAlmoxarifado(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Almoxarifado - Liberato")
        self.setGeometry(100, 100, 1200, 700)
       
        self.modo_escuro = False
        self.matricula_selecionada = None
        self.itens_emprestimo = []
       
        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)
       
        self.configurar_interface()
        self.aplicar_estilo()

    def configurar_interface(self):
        self.configurar_barra_ferramentas()
        self.configurar_paineis_principais()

    def configurar_barra_ferramentas(self):
        barra_ferramentas = QHBoxLayout()
       
        self.botao_modo_escuro = QPushButton("🌙 Modo Escuro")
        self.botao_modo_escuro.clicked.connect(self.alternar_modo_escuro)
        barra_ferramentas.addWidget(self.botao_modo_escuro)
       
        self.botao_turmas = QPushButton("Turmas")
        self.botao_turmas.clicked.connect(self.mostrar_turmas)
        barra_ferramentas.addWidget(self.botao_turmas)
       
        self.botao_banco = QPushButton(f"Banco: {ConfigBanco.banco_atual()}")
        self.botao_banco.clicked.connect(self.mostrar_seletor_banco)
        barra_ferramentas.addWidget(self.botao_banco)
       
        barra_ferramentas.addStretch()
        self.layout().addLayout(barra_ferramentas)

    def configurar_paineis_principais(self):
        divisor = QSplitter(Qt.Orientation.Horizontal)
       
        painel_esquerdo = QWidget()
        layout_esquerdo = QVBoxLayout(painel_esquerdo)
        self.criar_grupo_detalhes()
        self.criar_grupo_pesquisa_componente()
        layout_esquerdo.addWidget(self.grupo_detalhes)
        layout_esquerdo.addWidget(self.grupo_pesquisa_componente)
       
        painel_direito = QWidget()
        layout_direito = QVBoxLayout(painel_direito)
        self.criar_grupo_pesquisa()
        self.criar_grupo_emprestimos()
        layout_direito.addWidget(self.grupo_pesquisa)
        layout_direito.addWidget(self.grupo_emprestimos)
       
        divisor.addWidget(painel_esquerdo)
        divisor.addWidget(painel_direito)
        divisor.setSizes([400, 800])
       
        self.layout().addWidget(divisor)

    def criar_grupo_detalhes(self):
        self.grupo_detalhes = QGroupBox("Detalhes do Aluno")
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        layout_superior = QHBoxLayout()
       
        self.label_foto = QLabel()
        try:
            pixmap = QPixmap("default.png")
            if pixmap.isNull():
                raise FileNotFoundError
            self.label_foto.setPixmap(pixmap.scaled(80, 80))
        except Exception:
            self.label_foto.setText("Sem imagem")
        self.label_foto.setFixedSize(80, 80)
        self.label_foto.setStyleSheet("border: 1px solid #D6DBE0; border-radius: 3px;")
        layout_superior.addWidget(self.label_foto)

        layout_info = QVBoxLayout()
        layout_info.setSpacing(5)
       
        self.label_matricula = QLabel(" Matrícula: -")
        self.label_nome = QLabel(" Nome: -")
        self.label_email = QLabel(" E-mail: -")
        self.label_turma = QLabel(" Turma: -")
       
        for label in [self.label_matricula, self.label_nome, self.label_email, self.label_turma]:
            label.setFont(QFont("Arial", 9))
       
        layout_info.addWidget(self.label_matricula)
        layout_info.addWidget(self.label_nome)
        layout_info.addWidget(self.label_email)
        layout_info.addWidget(self.label_turma)

        layout_superior.addLayout(layout_info)
        layout.addLayout(layout_superior)
       
        layout_status = QHBoxLayout()
        layout_status.addWidget(QLabel("Status de Empréstimos:"))
        self.label_status_emprestimos = QLabel("Nenhum empréstimo")
        self.label_status_emprestimos.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        layout_status.addWidget(self.label_status_emprestimos)
        layout_status.addStretch()
        layout.addLayout(layout_status)
       
        self.grupo_detalhes.setLayout(layout)

    def criar_grupo_pesquisa(self):
        self.grupo_pesquisa = QGroupBox("Pesquisar Aluno")
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        layout_pesquisa = QHBoxLayout()
        self.campo_pesquisa = QLineEdit()
        self.campo_pesquisa.setPlaceholderText("Digite matrícula ou nome")
        self.campo_pesquisa.setClearButtonEnabled(True)
        self.campo_pesquisa.returnPressed.connect(self.pesquisar_aluno)
        layout_pesquisa.addWidget(self.campo_pesquisa)
       
        self.botao_pesquisa = QPushButton("Buscar")
        self.botao_pesquisa.setFixedWidth(80)
        self.botao_pesquisa.clicked.connect(self.pesquisar_aluno)
        layout_pesquisa.addWidget(self.botao_pesquisa)
       
        layout.addLayout(layout_pesquisa)
       
        self.lista_alunos = QListWidget()
        self.lista_alunos.setMinimumHeight(150)
        self.lista_alunos.itemClicked.connect(self.mostrar_detalhes_aluno)
        layout.addWidget(self.lista_alunos)
       
        self.grupo_pesquisa.setLayout(layout)

    def criar_grupo_pesquisa_componente(self):
        self.grupo_pesquisa_componente = QGroupBox("Pesquisar Componentes/Empréstimos")
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
       
        self.tabs_pesquisa = QTabWidget()
       
        # Tab Componentes
        tab_componentes = QWidget()
        layout_componentes = QVBoxLayout(tab_componentes)
       
        layout_pesquisa = QHBoxLayout()
        self.campo_pesquisa_componente = QLineEdit()
        self.campo_pesquisa_componente.setPlaceholderText("Digite nome ou código do componente")
        self.campo_pesquisa_componente.setClearButtonEnabled(True)
        self.campo_pesquisa_componente.returnPressed.connect(self.pesquisar_componente)
        layout_pesquisa.addWidget(self.campo_pesquisa_componente)
       
        self.botao_pesquisa_componente = QPushButton("Buscar")
        self.botao_pesquisa_componente.setFixedWidth(80)
        self.botao_pesquisa_componente.clicked.connect(self.pesquisar_componente)
        layout_pesquisa.addWidget(self.botao_pesquisa_componente)
       
        layout_componentes.addLayout(layout_pesquisa)
       
        self.lista_componentes = QListWidget()
        self.lista_componentes.setMinimumHeight(150)
        self.lista_componentes.itemDoubleClicked.connect(self.selecionar_componente)
        layout_componentes.addWidget(self.lista_componentes)
       
        self.tabs_pesquisa.addTab(tab_componentes, "Componentes")
       
        # Tab Empréstimos (mostra apenas empréstimos ativos)
        tab_emprestimos = QWidget()
        layout_emprestimos = QVBoxLayout(tab_emprestimos)
       
        layout_pesquisa_emp = QHBoxLayout()
        self.campo_pesquisa_emprestimo = QLineEdit()
        self.campo_pesquisa_emprestimo.setPlaceholderText("Digite nome do componente ou matrícula")
        self.campo_pesquisa_emprestimo.setClearButtonEnabled(True)
        self.campo_pesquisa_emprestimo.returnPressed.connect(lambda: self.pesquisar_emprestimos(apenas_emprestados=True))
        layout_pesquisa_emp.addWidget(self.campo_pesquisa_emprestimo)
       
        self.botao_pesquisa_emprestimo = QPushButton("Buscar")
        self.botao_pesquisa_emprestimo.setFixedWidth(80)
        self.botao_pesquisa_emprestimo.clicked.connect(lambda: self.pesquisar_emprestimos(apenas_emprestados=True))
        layout_pesquisa_emp.addWidget(self.botao_pesquisa_emprestimo)
       
        layout_emprestimos.addLayout(layout_pesquisa_emp)
       
        self.lista_emprestimos = QListWidget()
        self.lista_emprestimos.setMinimumHeight(150)
        layout_emprestimos.addWidget(self.lista_emprestimos)
       
        self.tabs_pesquisa.addTab(tab_emprestimos, "Empréstimos Ativos")
       
        layout.addWidget(self.tabs_pesquisa)
        self.grupo_pesquisa_componente.setLayout(layout)

    def criar_grupo_emprestimos(self):
        self.grupo_emprestimos = QGroupBox("Gerenciar Empréstimos")
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
       
        # Formulário para novos empréstimos
        layout_formulario = QGridLayout()
        layout_formulario.setColumnStretch(0, 1)
        layout_formulario.setColumnStretch(1, 1)
        layout_formulario.setColumnStretch(2, 0)
       
        layout_formulario.addWidget(QLabel("Componente:"), 0, 0)
        self.campo_componente = QLineEdit()
        self.campo_componente.setPlaceholderText("ID ou nome do componente")
        layout_formulario.addWidget(self.campo_componente, 0, 1)
       
        layout_formulario.addWidget(QLabel("Quantidade:"), 1, 0)
        self.campo_quantidade = QLineEdit()
        self.campo_quantidade.setPlaceholderText("Quantidade")
        layout_formulario.addWidget(self.campo_quantidade, 1, 1)
       
        self.botao_adicionar = QPushButton("Adicionar")
        self.botao_adicionar.setFixedWidth(100)
        self.botao_adicionar.clicked.connect(self.adicionar_emprestimo)
        layout_formulario.addWidget(self.botao_adicionar, 0, 2, 2, 1)
       
        layout.addLayout(layout_formulario)
       
        # Abas para empréstimos ativos e devolvidos
        self.tabs_emprestimos = QTabWidget()
       
        # Tab Empréstimos Ativos
        tab_emprestados = QWidget()
        layout_emprestados = QVBoxLayout(tab_emprestados)
       
        self.area_rolagem_emprestados = QScrollArea()
        self.area_rolagem_emprestados.setWidgetResizable(True)
        self.conteudo_emprestados = QWidget()
        self.layout_emprestados = QVBoxLayout(self.conteudo_emprestados)
        self.layout_emprestados.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_emprestados.setSpacing(8)
        self.area_rolagem_emprestados.setWidget(self.conteudo_emprestados)
       
        layout_emprestados.addWidget(self.area_rolagem_emprestados)
        self.tabs_emprestimos.addTab(tab_emprestados, "Empréstimos Ativos")
       
        # Tab Empréstimos Devolvidos
        tab_devolvidos = QWidget()
        layout_devolvidos = QVBoxLayout(tab_devolvidos)
       
        self.area_rolagem_devolvidos = QScrollArea()
        self.area_rolagem_devolvidos.setWidgetResizable(True)
        self.conteudo_devolvidos = QWidget()
        self.layout_devolvidos = QVBoxLayout(self.conteudo_devolvidos)
        self.layout_devolvidos.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_devolvidos.setSpacing(8)
        self.area_rolagem_devolvidos.setWidget(self.conteudo_devolvidos)
       
        layout_devolvidos.addWidget(self.area_rolagem_devolvidos)
        self.tabs_emprestimos.addTab(tab_devolvidos, "Empréstimos Devolvidos")
       
        layout.addWidget(self.tabs_emprestimos)
       
        # Botão de devolução
        layout_botoes = QHBoxLayout()
        layout_botoes.addStretch()
       
        self.botao_devolver = QPushButton("Registrar Devolução")
        self.botao_devolver.setFixedWidth(150)
        self.botao_devolver.clicked.connect(self.registrar_devolucao)
        layout_botoes.addWidget(self.botao_devolver)
       
        layout.addLayout(layout_botoes)
       
        self.grupo_emprestimos.setLayout(layout)

    def aplicar_estilo(self):
        if self.modo_escuro:
            estilo = """
                QWidget { background-color: #2D2D2D; color: #E0E0E0; }
                QGroupBox {
                    background-color: #3C3C3C; color: #FFFFFF;
                    border: 1px solid #555555; border-radius: 5px;
                    margin-top: 0.5em; padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin; left: 10px;
                    padding: 0 3px; background-color: #3C3C3C;
                    color: #FFFFFF;
                }
                QLineEdit {
                    background-color: #4A4A4A; color: #FFFFFF;
                    border: 1px solid #555555; border-radius: 3px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #228B22; color: #FFFFFF;
                    border: 1px solid #555555; border-radius: 3px;
                    padding: 5px;
                }
                QListWidget, QScrollArea {
                    background-color: #4A4A4A; color: #FFFFFF;
                    border: 1px solid #555555; border-radius: 3px;
                }
                QTabWidget::pane {
                    border: 1px solid #555555;
                    background: #3C3C3C;
                }
                QTabBar::tab {
                    background: #3C3C3C;
                    color: white;
                    padding: 8px;
                    border: 1px solid #555555;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background: #555555;
                }
            """
        else:
            estilo = """
                QWidget { background-color: #F5F7FA; color: #333333; }
                QGroupBox {
                    background-color: #FFFFFF; color: #2C3E50;
                    border: 1px solid #D6DBE0; border-radius: 5px;
                    margin-top: 0.5em; padding-top: 10px;
                    font-weight: bold;
                }
                QLineEdit {
                    background-color: #FFFFFF; color: #333333;
                    border: 1px solid #D6DBE0; border-radius: 3px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #228B22; color: #FFFFFF;
                    border: none; border-radius: 3px;
                    padding: 6px 12px;
                }
                QListWidget, QScrollArea {
                    background-color: #FFFFFF; color: #333333;
                    border: 1px solid #D6DBE0; border-radius: 3px;
                }
                QTabWidget::pane {
                    border: 1px solid #D6DBE0;
                    background: #FFFFFF;
                }
                QTabBar::tab {
                    background: #F5F7FA;
                    color: #333333;
                    padding: 8px;
                    border: 1px solid #D6DBE0;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background: #FFFFFF;
                    border-bottom: 1px solid #FFFFFF;
                }
            """
       
        self.setStyleSheet(estilo)

    def alternar_modo_escuro(self):
        self.modo_escuro = not self.modo_escuro
        self.aplicar_estilo()
        texto = "☀️ Modo Claro" if self.modo_escuro else "🌙 Modo Escuro"
        self.botao_modo_escuro.setText(texto)
       
        if self.matricula_selecionada:
            self.carregar_emprestimos(self.matricula_selecionada)

    def mostrar_seletor_banco(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Selecionar Banco de Dados")
        dialog.setFixedSize(300, 150)
       
        layout = QVBoxLayout()
        dialog.setLayout(layout)
       
        btn_producao = QPushButton("Banco de Produção")
        btn_producao.clicked.connect(lambda: self.selecionar_banco(dialog, "produção"))
       
        btn_teste = QPushButton("Banco de Teste")
        btn_teste.clicked.connect(lambda: self.selecionar_banco(dialog, "teste"))
       
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(dialog.reject)
       
        layout.addWidget(btn_producao)
        layout.addWidget(btn_teste)
        layout.addWidget(btn_cancelar)
       
        dialog.exec()

    def selecionar_banco(self, dialog, tipo_banco):
        if tipo_banco == "produção":
            ConfigBanco.usar_banco_producao()
            QMessageBox.information(self, "Banco Alterado", "Agora usando banco de PRODUÇÃO")
        else:
            ConfigBanco.usar_banco_teste()
            QMessageBox.information(self, "Banco Alterado", "Agora usando banco de TESTE")
       
        self.botao_banco.setText(f"Banco: {ConfigBanco.banco_atual()}")
        dialog.accept()
        self.recarregar_dados()

    def mostrar_turmas(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Selecionar Turma")
        dialog.setFixedSize(300, 400)
       
        layout = QVBoxLayout()
        dialog.setLayout(layout)
       
        lista_turmas = QListWidget()
        turmas = [
            "4111", "4211", "4311", "4411", "4511",
            "4112", "4212", "4312", "4412",
            "4123", "4223", "4323", "4423",
            "4124", "4224", "4324", "4424",
            "EX-Alunos"
        ]
       
        for turma in turmas:
            lista_turmas.addItem(turma)
       
        layout.addWidget(lista_turmas)
       
        btn_layout = QHBoxLayout()
        btn_selecionar = QPushButton("Selecionar")
        btn_cancelar = QPushButton("Cancelar")
       
        btn_selecionar.clicked.connect(dialog.accept)
        btn_cancelar.clicked.connect(dialog.reject)
       
        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(btn_selecionar)
        layout.addLayout(btn_layout)
       
        if dialog.exec() == QDialog.DialogCode.Accepted:
            items = lista_turmas.selectedItems()
            if items:
                self.pesquisar_por_turma(items[0].text())

    def pesquisar_aluno(self):
        termo = self.campo_pesquisa.text().strip()
        if not termo:
            QMessageBox.warning(self, "Campo Vazio", "Digite um termo para pesquisa")
            return
           
        self.lista_alunos.clear()

        try:
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Error("Não foi possível conectar ao banco de dados")
               
            cursor = conexao.cursor()

            cursor.execute(
                "SELECT matricula, nome FROM alunos "
                "WHERE matricula LIKE %s OR nome LIKE %s "
                "LIMIT 50",
                (f"%{termo}%", f"%{termo}%")
            )
            resultados = cursor.fetchall()

            if resultados:
                for matricula, nome in resultados:
                    self.lista_alunos.addItem(f"{matricula} - {nome}")
            else:
                self.lista_alunos.addItem("Nenhum aluno encontrado.")

            cursor.close()
            conexao.close()
        except Error as erro:
            QMessageBox.critical(self, "Erro", f"Erro na pesquisa: {str(erro)}")

    def mostrar_detalhes_aluno(self, item):
        texto = item.text()
        if " - " not in texto:
            return
           
        matricula = texto.split(" - ")[0]
        self.matricula_selecionada = matricula

        try:
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Error("Não foi possível conectar ao banco de dados")
               
            cursor = conexao.cursor()

            cursor.execute(
                "SELECT nome, email, turma, foto "
                "FROM alunos WHERE matricula = %s",
                (matricula,)
            )
            aluno = cursor.fetchone()

            if aluno:
                nome, email, turma, foto_bytes = aluno
                self.label_matricula.setText(f"Matrícula: {matricula}")
                self.label_nome.setText(f"Nome: {nome}")
                self.label_email.setText(f"E-mail: {email}")
                self.label_turma.setText(f"Turma: {turma}")

                if foto_bytes:
                    pixmap = QPixmap()
                    pixmap.loadFromData(foto_bytes)
                else:
                    pixmap = QPixmap("default.png")
                   
                self.label_foto.setPixmap(
                    pixmap.scaled(
                        self.label_foto.width(),
                        self.label_foto.height(),
                        Qt.AspectRatioMode.KeepAspectRatio
                    )
                )

                self.carregar_emprestimos(matricula)

            cursor.close()
            conexao.close()
        except Error as erro:
            QMessageBox.critical(self, "Erro", f"Erro ao buscar aluno: {str(erro)}")

    def carregar_emprestimos(self, matricula):
        # Limpar empréstimos anteriores
        for i in reversed(range(self.layout_emprestados.count())):
            widget = self.layout_emprestados.itemAt(i).widget()
            if widget:
                widget.deleteLater()
       
        for i in reversed(range(self.layout_devolvidos.count())):
            widget = self.layout_devolvidos.itemAt(i).widget()
            if widget:
                widget.deleteLater()
       
        total_emprestimos = 0
        self.itens_emprestimo = []

        try:
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Error("Não foi possível conectar ao banco de dados")
               
            cursor = conexao.cursor()

            cursor.execute(
                """SELECT e.id, e.quantidade, c.nome,
                   e.data_emp, e.data_dev, e.status
                   FROM emprestimos e
                   JOIN alunos a ON e.aluno_id = a.id
                   JOIN componentes c ON e.componente_id = c.id
                   WHERE a.matricula = %s
                   ORDER BY e.data_emp DESC""",
                (matricula,)
            )

            registros = cursor.fetchall()
            for (id_emprestimo, qtd, nome, data_emp, data_dev, status) in registros:
                data_emp_str = data_emp.strftime("%d/%m/%Y %H:%M") if data_emp else "---"
                data_dev_str = data_dev.strftime("%d/%m/%Y %H:%M") if data_dev else "---"
               
                item = ItemEmprestimo(
                    id_emprestimo, nome, qtd, data_emp_str, data_dev_str, status
                )
               
                if status == 'Emprestado':
                    self.layout_emprestados.addWidget(item)
                    total_emprestimos += int(qtd)
                else:
                    self.layout_devolvidos.addWidget(item)
               
                self.itens_emprestimo.append(item)

            self.atualizar_cor_fundo(total_emprestimos)
           
            if total_emprestimos == 0:
                self.label_status_emprestimos.setText("Nenhum empréstimo ativo")
            elif total_emprestimos < 10:
                self.label_status_emprestimos.setText("Empréstimos sob controle")
            elif total_emprestimos < 15:
                self.label_status_emprestimos.setText("Atenção: Muitos empréstimos")
            else:
                self.label_status_emprestimos.setText("ALERTA: Limite excedido!")
           
            cursor.close()
            conexao.close()
        except Error as erro:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar empréstimos: {str(erro)}")

    def atualizar_cor_fundo(self, total_emprestimos):
        if self.modo_escuro:
            if total_emprestimos == 0:
                cor = "#3C3C3C"
            elif total_emprestimos < 10:
                cor = "#006400"
            elif total_emprestimos < 15:
                cor = "#8B8000"
            else:
                cor = "#8B0000"
        else:
            if total_emprestimos == 0:
                cor = "#FFFFFF"
            elif total_emprestimos < 10:
                cor = "#015501"
            elif total_emprestimos < 15:
                cor = "#EEEE03"
            else:
                cor = "#FF0400"

        self.grupo_detalhes.setStyleSheet(f"""
            QGroupBox {{
                background-color: {cor};
                border: 1px solid #D6DBE0;
                border-radius: 5px;
            }}
        """)

    def pesquisar_componente(self):
        termo = self.campo_pesquisa_componente.text().strip()
        if not termo:
            QMessageBox.warning(self, "Campo Vazio", "Digite um termo para pesquisa")
            return
       
        self.lista_componentes.clear()

        try:
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Error("Não foi possível conectar ao banco de dados")
               
            cursor = conexao.cursor()

            query = """
            SELECT id, nome
            FROM componentes
            WHERE nome LIKE %s OR id = %s
            ORDER BY nome
            LIMIT 50
            """
           
            if termo.isdigit():
                cursor.execute(query, (f"%{termo}%", int(termo)))
            else:
                cursor.execute("""
                    SELECT id, nome
                    FROM componentes
                    WHERE nome LIKE %s
                    ORDER BY nome
                    LIMIT 50
                """, (f"%{termo}%",))

            resultados = cursor.fetchall()

            if resultados:
                for id_comp, nome in resultados:
                    self.lista_componentes.addItem(f"{id_comp} - {nome}")
            else:
                self.lista_componentes.addItem("Nenhum componente encontrado.")

            cursor.close()
            conexao.close()
        except Error as erro:
            QMessageBox.critical(self, "Erro", f"Erro na pesquisa: {str(erro)}")

    def pesquisar_emprestimos(self, apenas_emprestados=True):
        termo = self.campo_pesquisa_emprestimo.text().strip()
        if not termo:
            QMessageBox.warning(self, "Campo Vazio", "Digite um termo para pesquisa")
            return
       
        self.lista_emprestimos.clear()

        try:
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Error("Não foi possível conectar ao banco de dados")
               
            cursor = conexao.cursor()

            query = """
            SELECT e.id, c.nome, a.matricula, a.nome, e.quantidade,
                   e.data_emp, e.data_dev, e.status
            FROM emprestimos e
            JOIN componentes c ON e.componente_id = c.id
            JOIN alunos a ON e.aluno_id = a.id
            WHERE (c.nome LIKE %s OR a.matricula LIKE %s)
            """
           
            if apenas_emprestados:
                query += " AND e.status = 'Emprestado'"
           
            query += " ORDER BY e.data_emp DESC LIMIT 50"
           
            cursor.execute(query, (f"%{termo}%", f"%{termo}%"))
            resultados = cursor.fetchall()

            if resultados:
                for (id_emp, comp, matricula, aluno, qtd, data_emp, data_dev, status) in resultados:
                    data_emp_str = data_emp.strftime("%d/%m/%Y %H:%M") if data_emp else "---"
                    data_dev_str = data_dev.strftime("%d/%m/%Y %H:%M") if data_dev else "---"
                   
                    item_text = (f"{comp} | Matrícula: {matricula} | Aluno: {aluno} | "
                               f"Quantidade: {qtd} | Retirado: {data_emp_str} | "
                                )
                    self.lista_emprestimos.addItem(item_text)
            else:
                if apenas_emprestados:
                    self.lista_emprestimos.addItem("Nenhum empréstimo ativo encontrado.")
                else:
                    self.lista_emprestimos.addItem("Nenhum empréstimo encontrado.")

            cursor.close()
            conexao.close()
        except Error as erro:
            QMessageBox.critical(self, "Erro", f"Erro na pesquisa: {str(erro)}")

    def selecionar_componente(self, item):
        texto = item.text()
        if " - " not in texto:
            return
           
        id_componente = texto.split(" - ")[0]
        self.campo_componente.setText(id_componente)
        self.campo_quantidade.setFocus()

    def adicionar_emprestimo(self):
        if not self.matricula_selecionada:
            QMessageBox.warning(self, "Aluno Não Selecionado", "Selecione um aluno primeiro")
            return

        componente = self.campo_componente.text().strip()
        quantidade = self.campo_quantidade.text().strip()

        if not componente:
            QMessageBox.warning(self, "Componente Ausente", "Informe o componente")
            return
           
        if not quantidade.isdigit() or int(quantidade) <= 0:
            QMessageBox.warning(self, "Quantidade Inválida", "Digite um número positivo")
            return

        conexao = None
        cursor = None
        try:
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Error("Não foi possível conectar ao banco de dados")
               
            cursor = conexao.cursor()

            cursor.execute("SELECT id FROM alunos WHERE matricula = %s", (self.matricula_selecionada,))
            aluno = cursor.fetchone()
            if not aluno:
                QMessageBox.warning(self, "Aluno Não Encontrado", "Matrícula não existe")
                return
            aluno_id = aluno[0]
           
            if componente.isdigit():
                cursor.execute("SELECT id, nome FROM componentes WHERE id = %s", (int(componente),))
            else:
                cursor.execute("SELECT id, nome FROM componentes WHERE nome LIKE %s", (f"%{componente}%",))
           
            componente_info = cursor.fetchone()
            if not componente_info:
                QMessageBox.warning(self, "Componente Não Encontrado", "Nenhum componente encontrado")
                return
               
            componente_id, componente_nome = componente_info
               
            agora = datetime.now(timezone("America/Sao_Paulo"))
            cursor.execute(
                """INSERT INTO emprestimos
                   (aluno_id, componente_id, quantidade, data_emp, status)
                   VALUES (%s, %s, %s, %s, 'Emprestado')""",
                (aluno_id, componente_id, int(quantidade), agora)
            )
           
            conexao.commit()
            self.carregar_emprestimos(self.matricula_selecionada)
           
            self.campo_componente.clear()
            self.campo_quantidade.clear()

        except Error as erro:
            QMessageBox.critical(self, "Erro", f"Erro ao registrar empréstimo: {str(erro)}")
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

    def registrar_devolucao(self):
        if not self.matricula_selecionada:
            QMessageBox.warning(self, "Aluno Não Selecionado", "Selecione um aluno primeiro")
            return

        itens_selecionados = []
        for i in range(self.layout_emprestados.count()):
            widget = self.layout_emprestados.itemAt(i).widget()
            if isinstance(widget, ItemEmprestimo) and widget.checkbox.isChecked():
                itens_selecionados.append(widget)

        if not itens_selecionados:
            QMessageBox.warning(
                self,
                "Nenhum Item Selecionado",
                "Selecione pelo menos um empréstimo ativo"
            )
            return

        confirmacao = QMessageBox.question(
            self,
            "Confirmar Devolução",
            f"Deseja registrar a devolução de {len(itens_selecionados)} item(ns)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmacao != QMessageBox.StandardButton.Yes:
            return

        conexao = None
        cursor = None
        try:
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Error("Não foi possível conectar ao banco de dados")
               
            cursor = conexao.cursor()

            agora = datetime.now(timezone("America/Sao_Paulo"))
            for item in itens_selecionados:
                cursor.execute(
                    """UPDATE emprestimos SET data_dev = %s, status = 'Devolvido'
                       WHERE id = %s""",
                    (agora, item.id_emprestimo)
                )
           
            conexao.commit()
            self.carregar_emprestimos(self.matricula_selecionada)

        except Error as erro:
            QMessageBox.critical(self, "Erro", f"Erro ao registrar devolução: {str(erro)}")
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

    def pesquisar_por_turma(self, turma):
        self.lista_alunos.clear()
        self.campo_pesquisa.clear()
       
        try:
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Error("Não foi possível conectar ao banco de dados")
               
            cursor = conexao.cursor()

            if turma == "EX-Alunos":
                cursor.execute("SELECT matricula, nome FROM alunos")
            else:
                cursor.execute(
                    "SELECT matricula, nome FROM alunos WHERE turma = %s",
                    (turma,)
                )
           
            resultados = cursor.fetchall()

            if resultados:
                for matricula, nome in resultados:
                    self.lista_alunos.addItem(f"{matricula} - {nome}")
            else:
                self.lista_alunos.addItem("Nenhum aluno encontrado")

            cursor.close()
            conexao.close()
        except Error as erro:
            QMessageBox.critical(self, "Erro", f"Erro na pesquisa: {str(erro)}")

    def recarregar_dados(self):
        if self.matricula_selecionada:
            self.carregar_emprestimos(self.matricula_selecionada)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = AppAlmoxarifado()
    janela.show()
    sys.exit(app.exec())
