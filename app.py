import sys
import mysql.connector
from mysql.connector import Error
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QPushButton, QLineEdit, QListWidget, 
    QRadioButton, QMessageBox, QScrollArea, QFrame, QCheckBox,
    QSplitter, QSizePolicy, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMenu, QMenuBar, QToolBar
)
from PyQt6.QtGui import QPixmap, QFont, QIcon, QAction
from PyQt6.QtCore import Qt, QSize
from datetime import datetime
from pytz import timezone


DB_NAME = "almox"
DB_USER = "root"
DB_PASSWORD = "manulauro5308"
DB_HOST = "localhost"
DB_PORT = 3306


class EmprestimoItem(QFrame):
    def __init__(
        self, emprestimo_id, componente, quantidade,
        data_emp, data_dev, status, parent=None
    ):
        super().__init__(parent)
        self.emprestimo_id = emprestimo_id
        self.status = status
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedHeight(70)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)

        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setEnabled(status == "Emprestado")
        layout.addWidget(self.checkbox)

        # Info empréstimo
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        # Header: Nome e Qtd
        header = QHBoxLayout()

        nome_label = QLabel(f"<b>{componente}</b>")
        nome_label.setFont(QFont("Arial", 9))
        nome_label.setMinimumWidth(150)
        header.addWidget(nome_label)

        qtd_label = QLabel(f"<b>Quantidade:</b> {quantidade}")
        qtd_label.setFont(QFont("Arial", 9))
        header.addWidget(qtd_label)

        header.addStretch()

        self.status_label = QLabel()
        if status == "Emprestado":
            self.status_label.setText("<b>EMPRESTADO</b>")
        else:
            self.status_label.setText("<b>DEVOLVIDO</b>")
            self.checkbox.setChecked(False)
            
        if status == "Emprestado":
            self.status_label.setText("<b>EMPRESTADO</b>")
            self.status_label.setStyleSheet("color: red;")
        else:
            self.status_label.setText("<b>DEVOLVIDO</b>")
            self.status_label.setStyleSheet("color: green;")


        self.status_label.setFont(QFont("Arial", 9))
        header.addWidget(self.status_label)

        info_layout.addLayout(header)

        # Datas
        datas_layout = QHBoxLayout()

        emp_layout = QHBoxLayout()
        emp_layout.addWidget(QLabel("<b>Retirado:</b>"))
        self.data_emp_label = QLabel(data_emp)
        self.data_emp_label.setFont(QFont("Arial", 8))
        emp_layout.addWidget(self.data_emp_label)
        datas_layout.addLayout(emp_layout)

        dev_layout = QHBoxLayout()
        dev_layout.addWidget(QLabel("<b>Devolvido:</b>"))
        self.data_dev_label = QLabel(data_dev)
        self.data_dev_label.setFont(QFont("Arial", 8))
        dev_layout.addWidget(self.data_dev_label)
        datas_layout.addLayout(dev_layout)

        info_layout.addLayout(datas_layout)

        layout.addLayout(info_layout, 1)
        self.setLayout(layout)

        # 🔥 Definindo a cor dos textos igual do modo claro
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #D6DBE0;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QLabel {
                color: #333333;
            }
            QCheckBox {
                color: #333333;
            }
            QFrame:hover {
                background-color: #F5F5F5;
            }
        """)


class TurmasDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selecionar Turma")
        self.setFixedSize(300, 400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Lista de turmas
        self.lista_turmas = QListWidget()
        turmas = [
            "4111", "4211", "4311", "4411", "4511",
            "4112", "4212", "4312", "4412",
            "4123", "4223", "4323", "4423",
            "4124", "4224", "4324", "4424",
            "EX-Alunos"
        ]
        
        for turma in turmas:
            self.lista_turmas.addItem(turma)
            
        layout.addWidget(self.lista_turmas)
        
        # Botão de seleção
        self.botao_selecionar = QPushButton("Selecionar")
        self.botao_selecionar.clicked.connect(self.accept)
        layout.addWidget(self.botao_selecionar)
        
    def turma_selecionada(self):
        items = self.lista_turmas.selectedItems()
        if items:
            return items[0].text()
        return None


class ExAlunosDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EX-Alunos")
        self.setGeometry(200, 200, 800, 500)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        
        # Botão de fechar
        self.botao_fechar = QPushButton("Fechar")
        self.botao_fechar.clicked.connect(self.accept)
        layout.addWidget(self.botao_fechar)
        
        # Carregar dados
        


class AlmoxarifadoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Almoxarifado - Liberato")
        self.setGeometry(100, 100, 1200, 700)
        
        # Variável para controlar o tema
        self.dark_mode = False
        self.matricula_selecionada = None
        self.emprestimo_items = []
        
        # Layout principal
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Barra de menu
        menubar = QMenuBar()
        menu_turmas = menubar.addMenu("Turmas")
        
        # Ação para abrir turmas
        acao_turmas = QAction("Ver Turmas", self)
        acao_turmas.triggered.connect(self.mostrar_turmas)
        menu_turmas.addAction(acao_turmas)
        
        # Barra de ferramentas
        toolbar = QToolBar("Ferramentas")
        self.botao_dark_mode = QPushButton("🌙 Dark Mode")
        self.botao_dark_mode.setFixedSize(120, 30)
        self.botao_dark_mode.clicked.connect(self.alternar_dark_mode)
        toolbar.addWidget(self.botao_dark_mode)
        
        botao_turmas = QPushButton("Turmas")
        botao_turmas.setFixedSize(100, 30)
        botao_turmas.clicked.connect(self.mostrar_turmas)
        toolbar.addWidget(botao_turmas)
        
        main_layout.addWidget(toolbar)
        
        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter, 1)
        
        # Painel esquerdo (detalhes do aluno)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # Criar grupos
        self.criar_grupo_detalhes()
        self.criar_grupo_pesquisa_componente()
        
        left_layout.addWidget(self.group_detalhes)
        left_layout.addWidget(self.group_pesquisa_componente)
        left_layout.setStretch(0, 1)
        left_layout.setStretch(1, 1)
        
        # Painel direito (pesquisa e empréstimos)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        self.criar_grupo_pesquisa()
        self.criar_grupo_emprestimos()
        
        right_layout.addWidget(self.group_pesquisa)
        right_layout.addWidget(self.group_emprestimos)
        right_layout.setStretch(0, 1)
        right_layout.setStretch(1, 2)
        
        # Adicionar painéis ao splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        
        # Aplicar estilo inicial
        self.aplicar_estilo()

    def alternar_dark_mode(self):
        """Alterna entre os temas claro e escuro"""
        self.dark_mode = not self.dark_mode
        self.aplicar_estilo()
        self.botao_dark_mode.setText("☀️ Light Mode" if self.dark_mode else "🌙 Dark Mode")
        
        # Recarregar empréstimos para atualizar cores
        if self.matricula_selecionada:
            self.carregar_emprestimos(self.matricula_selecionada)

    def mostrar_turmas(self):
        dialog = TurmasDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            turma = dialog.turma_selecionada()
            if turma:
                self.pesquisar_por_turma(turma)

    def pesquisar_por_turma(self, turma):
        self.lista_alunos.clear()
        self.pesquisa_input.clear()
        
        try:
            conn = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, port=DB_PORT
            )
            cursor = conn.cursor()

            # Pesquisa especial para EX-Alunos
            if turma == "EX-Alunos":
                cursor.execute(
                    "SELECT matricula, nome FROM alunos"
                )
            else:
                cursor.execute(
                    "SELECT matricula, nome FROM alunos WHERE turma = %s",
                    (turma,)
                )
            
            resultados = cursor.fetchall()

            if resultados:
                for mat, nome in resultados:
                    self.lista_alunos.addItem(f"{mat} - {nome}")
            else:
                self.lista_alunos.addItem("Nenhum aluno encontrado nesta turma.")

            cursor.close()
            conn.close()
        except Error as e:
            QMessageBox.critical(self, "Erro", f"Erro na pesquisa: {str(e)}")

    def aplicar_estilo(self):
        """Aplica o estilo visual baseado no tema selecionado"""
        if self.dark_mode:
            estilo = """
                QWidget {
                    background-color: #2D2D2D;
                    color: #E0E0E0;
                }
                QGroupBox {
                    background-color: #3C3C3C;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    margin-top: 0.5em;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                    background-color: #3C3C3C;
                    color: #FFFFFF;
                }
                QLabel {
                    color: #E0E0E0;
                }
                QLineEdit {
                    background-color: #4A4A4A;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #228B22;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 5px;
                    }
                QPushButton:hover {
                        background-color: #1E7A1E;
                    }
                QPushButton:disabled {
                        background-color: #3A3A3A;
                        color: #7F7F7F;
                    }

                QListWidget {
                    background-color: #4A4A4A;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    border-radius: 3px;
                }
                QScrollArea {
                    background-color: #4A4A4A;
                    border: 1px solid #555555;
                    border-radius: 3px;
                }
                QRadioButton {
                    color: #E0E0E0;
                }
                QCheckBox {
                    color: #E0E0E0;
                }
                QMenuBar {
                    background-color: #3C3C3C;
                    color: #FFFFFF;
                }
                QMenuBar::item {
                    background-color: #3C3C3C;
                    color: #FFFFFF;
                }
                QMenuBar::item:selected {
                    background-color: #5A5A5A;
                }
                QMenu {
                    background-color: #3C3C3C;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                }
                QMenu::item:selected {
                    background-color: #5A5A5A;
                }
                QToolBar {
                    background-color: #3C3C3C;
                    border: 1px solid #555555;
                }
                QTableWidget {
                    background-color: #4A4A4A;
                    color: #FFFFFF;
                    gridline-color: #555555;
                    alternate-background-color: #3C3C3C;
                }
                QHeaderView::section {
                    background-color: #5A5A5A;
                    color: #FFFFFF;
                    padding: 4px;
                    border: 1px solid #555555;
                }
            """
        else:
            estilo = """
                QWidget {
                    background-color: #F5F7FA;
                    color: #333333;
                }
                QGroupBox {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    border: 1px solid #D6DBE0;
                    border-radius: 5px;
                    margin-top: 0.5em;
                    padding-top: 10px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                    background-color: #FFFFFF;
                    color: #2C3E50;
                }
                QLabel {
                    color: #333333;
                }
                QLineEdit {
                    background-color: #FFFFFF;
                    color: #333333;
                    border: 1px solid #D6DBE0;
                    border-radius: 3px;
                    padding: 5px;
                }
                QLineEdit:focus {
                    border: 1px solid #3498DB;
                }
                QPushButton {
                    background-color: #228B22;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 3px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #1E7A1E;
                }
                QPushButton:disabled {
                    background-color: #BDC3C7;
                    color: #7F8C8D;
                }

                QListWidget {
                    background-color: #FFFFFF;
                    color: #333333;
                    border: 1px solid #D6DBE0;
                    border-radius: 3px;
                }
                QScrollArea {
                    background-color: #FFFFFF;
                    border: 1px solid #D6DBE0;
                    border-radius: 3px;
                }
                QRadioButton {
                    color: #333333;
                }
                QCheckBox {
                    color: #333333;
                }
                QMenuBar {
                    background-color: #F0F0F0;
                    color: #333333;
                }
                QMenuBar::item {
                    background-color: #F0F0F0;
                    color: #333333;
                }
                QMenuBar::item:selected {
                    background-color: #E0E0E0;
                }
                QMenu {
                    background-color: #FFFFFF;
                    color: #333333;
                    border: 1px solid #D6DBE0;
                }
                QMenu::item:selected {
                    background-color: #3498DB;
                    color: #FFFFFF;
                }
                QToolBar {
                    background-color: #F0F0F0;
                    border: 1px solid #D6DBE0;
                }
                QTableWidget {
                    background-color: #FFFFFF;
                    color: #333333;
                    gridline-color: #D6DBE0;
                    alternate-background-color: #F5F7FA;
                }
                QHeaderView::section {
                    background-color: #3498DB;
                    color: #FFFFFF;
                    padding: 4px;
                    border: 1px solid #D6DBE0;
                }
            """
        
        self.setStyleSheet(estilo)

    def criar_grupo_detalhes(self):
        self.group_detalhes = QGroupBox("Detalhes do Aluno")
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Foto e informações básicas
        top_layout = QHBoxLayout()
        
        self.foto_label = QLabel()
        self.foto_label.setPixmap(QPixmap("default.png").scaled(80, 80))
        self.foto_label.setFixedSize(80, 80)
        self.foto_label.setStyleSheet("border: 1px solid #D6DBE0; border-radius: 3px;")
        top_layout.addWidget(self.foto_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        self.label_matricula = QLabel("Matrícula: -")
        self.label_nome = QLabel("Nome: -")
        self.label_email = QLabel("E-mail: -")
        self.label_turma = QLabel("Turma: -")
        
        for label in [self.label_matricula, self.label_nome, self.label_email, self.label_turma]:
            label.setFont(QFont("Arial", 9))
        
        info_layout.addWidget(self.label_matricula)
        info_layout.addWidget(self.label_nome)
        info_layout.addWidget(self.label_email)
        info_layout.addWidget(self.label_turma)

        top_layout.addLayout(info_layout)
        layout.addLayout(top_layout)
        
        # Status de empréstimos
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status de Empréstimos:"))
        self.status_label = QLabel("Nenhum empréstimo")
        self.status_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        self.group_detalhes.setLayout(layout)

    def criar_grupo_pesquisa(self):
        self.group_pesquisa = QGroupBox("Pesquisar Aluno")
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Campo de pesquisa
        search_layout = QHBoxLayout()
        self.pesquisa_input = QLineEdit()
        self.pesquisa_input.setPlaceholderText("Digite matrícula ou nome")
        self.pesquisa_input.setClearButtonEnabled(True)
        self.pesquisa_input.returnPressed.connect(self.pesquisar_aluno)
        search_layout.addWidget(self.pesquisa_input)
        
        self.botao_pesquisa = QPushButton("Buscar")
        self.botao_pesquisa.setFixedWidth(80)
        self.botao_pesquisa.clicked.connect(self.pesquisar_aluno)
        search_layout.addWidget(self.botao_pesquisa)
        
        layout.addLayout(search_layout)
        
        # Lista de alunos
        self.lista_alunos = QListWidget()
        self.lista_alunos.setMinimumHeight(150)
        self.lista_alunos.itemClicked.connect(self.mostrar_detalhes_aluno)
        layout.addWidget(self.lista_alunos)
        
        self.group_pesquisa.setLayout(layout)

    def criar_grupo_pesquisa_componente(self):
        self.group_pesquisa_componente = QGroupBox("Pesquisar Componente")
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Campo de pesquisa
        search_layout = QHBoxLayout()
        self.pesquisa_componente_input = QLineEdit()
        self.pesquisa_componente_input.setPlaceholderText("Digite nome ou código do componente")
        self.pesquisa_componente_input.setClearButtonEnabled(True)
        self.pesquisa_componente_input.returnPressed.connect(self.pesquisar_componente)
        search_layout.addWidget(self.pesquisa_componente_input)
        
        self.botao_pesquisa_componente = QPushButton("Buscar")
        self.botao_pesquisa_componente.setFixedWidth(80)
        self.botao_pesquisa_componente.clicked.connect(self.pesquisar_componente)
        search_layout.addWidget(self.botao_pesquisa_componente)
        
        layout.addLayout(search_layout)
        
        # Opções de pesquisa
        tipo_layout = QHBoxLayout()
        self.radio_nome = QRadioButton("Por Nome")
        self.radio_nome.setChecked(True)
        self.radio_codigo = QRadioButton("Por Código")
        tipo_layout.addWidget(self.radio_nome)
        tipo_layout.addWidget(self.radio_codigo)
        tipo_layout.addStretch()
        layout.addLayout(tipo_layout)
        
        # Lista de componentes
        self.lista_componentes = QListWidget()
        self.lista_componentes.setMinimumHeight(150)
        self.lista_componentes.itemDoubleClicked.connect(self.selecionar_componente)
        layout.addWidget(self.lista_componentes)
        
        self.group_pesquisa_componente.setLayout(layout)

    def criar_grupo_emprestimos(self):
        self.group_emprestimos = QGroupBox("Gerenciar Empréstimos")
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Formulário para adicionar empréstimos
        form_layout = QGridLayout()
        form_layout.setColumnStretch(0, 1)
        form_layout.setColumnStretch(1, 1)
        form_layout.setColumnStretch(2, 0)
        
        form_layout.addWidget(QLabel("Componente:"), 0, 0)
        self.input_componente = QLineEdit()
        self.input_componente.setPlaceholderText("ID ou nome do componente")
        form_layout.addWidget(self.input_componente, 0, 1)
        
        form_layout.addWidget(QLabel("Quantidade:"), 1, 0)
        self.input_quantidade = QLineEdit()
        self.input_quantidade.setPlaceholderText("Quantidade")
        form_layout.addWidget(self.input_quantidade, 1, 1)
        
        self.botao_adicionar = QPushButton("Adicionar")
        self.botao_adicionar.setFixedWidth(100)
        self.botao_adicionar.clicked.connect(self.adicionar_emprestimo)
        form_layout.addWidget(self.botao_adicionar, 0, 2, 2, 1)
        
        layout.addLayout(form_layout)
        
        # Área de empréstimos
        layout.addWidget(QLabel("Empréstimos Ativos:"))
        
        # Área de scroll para os empréstimos
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(8)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setMinimumHeight(250)
        
        layout.addWidget(self.scroll_area)
        
        # Botão para registrar devoluções
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.botao_devolver = QPushButton("Registrar Devolução")
        self.botao_devolver.setFixedWidth(150)
        self.botao_devolver.clicked.connect(self.registrar_devolucao)
        button_layout.addWidget(self.botao_devolver)
        
        layout.addLayout(button_layout)
        
        self.group_emprestimos.setLayout(layout)

    def pesquisar_aluno(self):
        termo = self.pesquisa_input.text().strip()
        if not termo:
            QMessageBox.warning(self, "Campo Vazio", "Digite um termo para pesquisa")
            return
            
        self.lista_alunos.clear()

        try:
            conn = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, port=DB_PORT
            )
            cursor = conn.cursor()

            cursor.execute(
                "SELECT matricula, nome FROM alunos "
                "WHERE matricula LIKE %s OR nome LIKE %s "
                "LIMIT 50",
                (f"%{termo}%", f"%{termo}%")
            )
            resultados = cursor.fetchall()

            if resultados:
                for mat, nome in resultados:
                    self.lista_alunos.addItem(f"{mat} - {nome}")
            else:
                self.lista_alunos.addItem("Nenhum aluno encontrado.")

            cursor.close()
            conn.close()
        except Error as e:
            QMessageBox.critical(self, "Erro", f"Erro na pesquisa: {str(e)}")

    def mostrar_detalhes_aluno(self, item):
        text = item.text()
        if " - " not in text:
            return
            
        matricula = text.split(" - ")[0]
        self.matricula_selecionada = matricula

        try:
            conn = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, port=DB_PORT
            )
            cursor = conn.cursor()

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

                # Carregar foto se existir
                if foto_bytes:
                    pixmap = QPixmap()
                    pixmap.loadFromData(foto_bytes)
                else:
                    pixmap = QPixmap("default.png")
                    
                self.foto_label.setPixmap(
                    pixmap.scaled(
                        self.foto_label.width(), 
                        self.foto_label.height(),
                        Qt.AspectRatioMode.KeepAspectRatio
                    )
                )

                # Carregar empréstimos do aluno
                self.carregar_emprestimos(matricula)

            cursor.close()
            conn.close()
        except Error as e:
            QMessageBox.critical(self, "Erro", f"Erro ao buscar aluno: {str(e)}")

    def pesquisar_componente(self):
        termo = self.pesquisa_componente_input.text().strip()
        if not termo:
            QMessageBox.warning(self, "Campo Vazio", "Digite um termo para pesquisa")
            return
            
        self.lista_componentes.clear()

        try:
            conn = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, port=DB_PORT
            )
            cursor = conn.cursor()

            if self.radio_nome.isChecked():
                cursor.execute(
                    "SELECT id, nome FROM componentes WHERE nome LIKE %s LIMIT 50",
                    (f"%{termo}%",)
                )
            else:
                if not termo.isdigit():
                    QMessageBox.warning(self, "Código Inválido", "O código deve ser um número")
                    return
                cursor.execute(
                    "SELECT id, nome FROM componentes WHERE id = %s",
                    (int(termo),)
                )

            resultados = cursor.fetchall()

            if resultados:
                for cid, nome in resultados:
                    self.lista_componentes.addItem(f"{cid} - {nome}")
            else:
                self.lista_componentes.addItem("Nenhum componente encontrado.")

            cursor.close()
            conn.close()
        except Error as e:
            QMessageBox.critical(self, "Erro", f"Erro na pesquisa: {str(e)}")

    def selecionar_componente(self, item):
        texto = item.text()
        if " - " not in texto:
            return
            
        id_comp = texto.split(" - ")[0]
        self.input_componente.setText(id_comp)
        self.input_quantidade.setFocus()

    def carregar_emprestimos(self, matricula):
        # Limpa os empréstimos anteriores
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        total_emprestimos = 0
        self.emprestimo_items = []

        try:
            conn = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, port=DB_PORT
            )
            cursor = conn.cursor()

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
                # Formata datas
                data_emp_str = data_emp.strftime("%d/%m/%Y %H:%M") if data_emp else "---"
                data_dev_str = data_dev.strftime("%d/%m/%Y %H:%M") if data_dev else "---"
                
                # Cria item visual para o empréstimo
                item = EmprestimoItem(
                    id_emprestimo, nome, qtd, data_emp_str, data_dev_str, status
                )
                self.scroll_layout.addWidget(item)
                self.emprestimo_items.append(item)
                
                # Soma apenas empréstimos ativos
                if status == 'Emprestado':
                    total_emprestimos += int(qtd)

            # Atualiza a cor de fundo baseado no total de empréstimos
            self.atualizar_cor_fundo(total_emprestimos)
            
            # Atualiza o status de empréstimos
            if total_emprestimos == 0:
                self.status_label.setText("Nenhum empréstimo ativo")
            elif total_emprestimos < 10:
                self.status_label.setText("Empréstimos sob controle")
            elif total_emprestimos < 15:
                self.status_label.setText("Atenção: Muitos empréstimos")
            else:
                self.status_label.setText("ALERTA: Limite excedido!")
            
            cursor.close()
            conn.close()
        except Error as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar empréstimos: {str(e)}")

    def atualizar_cor_fundo(self, total_emprestimos):
        """Atualiza a cor de fundo baseado no número de empréstimos"""
        if self.dark_mode:
            # Cores para dark mode
            if total_emprestimos == 0:
                cor = "#3C3C3C"
            elif total_emprestimos < 10:
                cor = "#006400"  # Verde escuro
            elif total_emprestimos < 15:
                cor = "#8B8000"  # Amarelo escuro
            else:
                cor = "#8B0000"  # Vermelho escuro
        else:
            # Cores para light mode
            if total_emprestimos == 0:
                cor = "#FFFFFF"
            elif total_emprestimos < 10:
                cor = "#90EE90"  # Verde claro
            elif total_emprestimos < 15:
                cor = "#FFFFE0"  # Amarelo claro
            else:
                cor = "#FFCCCB"  # Vermelho claro

        self.group_detalhes.setStyleSheet(f"""
            QGroupBox {{
                background-color: {cor};
                border: 1px solid #D6DBE0;
                border-radius: 5px;
            }}
        """)

    def adicionar_emprestimo(self):
        if not self.matricula_selecionada:
            QMessageBox.warning(self, "Aluno Não Selecionado", "Selecione um aluno antes de adicionar empréstimos.")
            return

        comp = self.input_componente.text().strip()
        qtd = self.input_quantidade.text().strip()

        if not comp:
            QMessageBox.warning(self, "Componente Ausente", "Informe o componente.")
            return
            
        if not qtd.isdigit() or int(qtd) <= 0:
            QMessageBox.warning(self, "Quantidade Inválida", "Digite um número positivo para quantidade.")
            return

        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, port=DB_PORT
            )
            cursor = conn.cursor()

            # Buscar ID do aluno
            cursor.execute("SELECT id FROM alunos WHERE matricula = %s", (self.matricula_selecionada,))
            aluno_result = cursor.fetchone()
            if not aluno_result:
                QMessageBox.warning(self, "Aluno Não Encontrado", "Matrícula não existe no banco de dados.")
                return
            aluno_id = aluno_result[0]
            
            # Buscar componente
            if comp.isdigit():
                cursor.execute("SELECT id, nome FROM componentes WHERE id = %s", (int(comp),))
            else:
                cursor.execute("SELECT id, nome FROM componentes WHERE nome LIKE %s", (f"%{comp}%",))
            
            comp_data = cursor.fetchone()
            if not comp_data:
                QMessageBox.warning(self, "Componente Não Encontrado", "Nenhum componente corresponde à pesquisa.")
                return
                
            comp_id, comp_nome = comp_data
                
            # Registrar empréstimo
            agora = datetime.now(timezone("America/Sao_Paulo"))
            cursor.execute(
                """INSERT INTO emprestimos 
                   (aluno_id, componente_id, quantidade, data_emp, status)
                   VALUES (%s, %s, %s, %s, 'Emprestado')""",
                (aluno_id, comp_id, int(qtd), agora)
            )
            
            conn.commit()
            self.carregar_emprestimos(self.matricula_selecionada)
            
            # Limpar campos e mostrar confirmação
            self.input_componente.clear()
            self.input_quantidade.clear()

        except Error as e:
            QMessageBox.critical(self, "Erro no Banco de Dados", f"Erro ao registrar empréstimo: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def registrar_devolucao(self):
        if not self.matricula_selecionada:
            QMessageBox.warning(self, "Aluno Não Selecionado", "Selecione um aluno antes de registrar devoluções.")
            return

        # Encontra os itens selecionados
        emprestimos_selecionados = []
        for item in self.emprestimo_items:
            if item.checkbox.isChecked() and item.status == 'Emprestado':
                emprestimos_selecionados.append(item)

        if not emprestimos_selecionados:
            QMessageBox.warning(
                self, 
                "Nenhum Item Selecionado", 
                "Selecione pelo menos um empréstimo ativo para devolução."
            )
            return

        # Confirmação antes de devolver
        confirm = QMessageBox.question(
            self,
            "Confirmar Devolução",
            f"Deseja registrar a devolução de {len(emprestimos_selecionados)} item(ns)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, port=DB_PORT
            )
            cursor = conn.cursor()

            agora = datetime.now(timezone("America/Sao_Paulo"))
            for item in emprestimos_selecionados:
                cursor.execute(
                    """UPDATE emprestimos SET data_dev = %s, status = 'Devolvido'
                       WHERE id = %s""",
                    (agora, item.emprestimo_id)
                )
            
            conn.commit()
            self.carregar_emprestimos(self.matricula_selecionada)

        except Error as e:
            QMessageBox.critical(self, "Erro no Banco de Dados", f"Erro ao registrar devolução: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AlmoxarifadoApp()
    window.show()
    sys.exit(app.exec())
