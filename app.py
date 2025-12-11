import sys
import os
import mysql.connector
import urllib.request
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
from senha import LoginAdmin
from processar_alunos import processar_alunos
from emprestimos import importar_emprestimos



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
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #555555;
                background-color: #FFFFFF; /* fundo branco sempre */
            }
            QCheckBox::indicator:checked {
                background-color: #FFFFFF;
                image: url(check-mark.png); /* usa o PNG baixado */
            }
        """)
     

        self.campo_devolucao = QLineEdit()
        self.campo_devolucao.setPlaceholderText("Qtd")
        self.campo_devolucao.setFixedWidth(50)
        self.campo_devolucao.setEnabled(self.status == "Emprestado")
        self.campo_devolucao.setStyleSheet("background-color: #FFFFFF; color: #333333;")
        layout.addWidget(self.campo_devolucao)


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

        # Botão Administrativo na barra de ferramentas
        self.botao_admin = QPushButton("Abrir Administrativo")
        self.botao_admin.clicked.connect(self.abrir_administrativo)
        barra_ferramentas.addWidget(self.botao_admin)


        barra_ferramentas.addStretch()
        self.layout().addLayout(barra_ferramentas)
    
    def abrir_administrativo(self):
        self.login_dialog = LoginAdmin(self)
        self.login_dialog.show()

    def abrir_administrativo_real(self):
        self.janela_admin = QWidget()
        self.janela_admin.setWindowTitle("Administrativo")
        self.janela_admin.resize(500, 400)

        layout_admin = QVBoxLayout()

        # --- Título ---
        titulo = QLabel("Painel Administrativo")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setStyleSheet("color: #2c3e50; margin: 10px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_admin.addWidget(titulo)

        # --- Separador ---
        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.HLine)
        separador.setFrameShadow(QFrame.Shadow.Sunken)
        layout_admin.addWidget(separador)

        # --- Botões em linha ---
        botoes_layout = QHBoxLayout()
    
        botao_ranking = QPushButton("📊 Gerar Ranking")
        botao_ranking.setStyleSheet("padding: 10px; background-color: #3498db; color: white; border-radius: 5px;")
        botao_ranking.clicked.connect(self.mostrar_ranking)
        botoes_layout.addWidget(botao_ranking)

        botao_emails = QPushButton("📧 Gerar Emails Emprestados")
        botao_emails.setStyleSheet("padding: 10px; background-color: #2ecc71; color: white; border-radius: 5px;")
        botao_emails.clicked.connect(self.gerar_emails_pendentes)
        botoes_layout.addWidget(botao_emails)

        # Campo + botão para adicionar componente
        layout_add_cmp = QHBoxLayout()

        self.campo_novo_componente = QLineEdit()
        self.campo_novo_componente.setPlaceholderText("Nome do componente")
        self.campo_novo_componente.setFixedWidth(200)
        layout_add_cmp.addWidget(self.campo_novo_componente)

        botao_adicionar_cmp = QPushButton("Adicionar Componente")
        botao_adicionar_cmp.setStyleSheet("padding: 10px; background-color: #3498db; color: white; border-radius: 5px;")
        botao_adicionar_cmp.clicked.connect(self.adicionar_componente)
        layout_add_cmp.addWidget(botao_adicionar_cmp)

        botoes_layout.addLayout(layout_add_cmp)

        layout_admin.addLayout(botoes_layout)

        botao_processar = QPushButton("👨‍🎓 Processar Alunos")
        botao_processar.setStyleSheet("padding: 10px; background-color: #9b59b6; color: white; border-radius: 5px;")
        botao_processar.clicked.connect(self.executar_processar_alunos)
        botoes_layout.addWidget(botao_processar)

        botao_importar = QPushButton("📥 Importar Empréstimos")
        botao_importar.setStyleSheet("padding: 10px; background-color: #8e44ad; color: white; border-radius: 5px;")
        botao_importar.clicked.connect(self.executar_importar_emprestimos)
        botoes_layout.addWidget(botao_importar)



        # --- Botão Banco ---
        botao_banco_admin = QPushButton(f"🏦 Banco: {ConfigBanco.banco_atual()}")
        botao_banco_admin.setStyleSheet("padding: 10px; background-color: #e67e22; color: white; border-radius: 5px;")
        botao_banco_admin.clicked.connect(self.mostrar_seletor_banco)
        layout_admin.addWidget(botao_banco_admin)

        self.janela_admin.setLayout(layout_admin)
        self.janela_admin.show()

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
        layout_direito.addWidget(self.grupo_pesquisa, 1)
        layout_direito.addWidget(self.grupo_emprestimos, 4)
        
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
        self.lista_alunos.setMinimumHeight(100)
        self.lista_alunos.itemClicked.connect(self.mostrar_detalhes_aluno)
        layout.addWidget(self.lista_alunos)
        
        self.grupo_pesquisa.setLayout(layout)

    def criar_grupo_pesquisa_componente(self):
        self.grupo_pesquisa_componente = QGroupBox("Pesquisar Componentes / Empréstimos")
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        self.tabs_pesquisa = QTabWidget()

        # ---------------- TAB 1: Componentes ----------------
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

        # ---------------- TAB 2: Empréstimos Ativos ----------------
        tab_emprestimos = QWidget()
        layout_emprestimos = QVBoxLayout(tab_emprestimos)

        layout_pesquisa_emp = QHBoxLayout()
        self.campo_pesquisa_emprestimo = QLineEdit()
        self.campo_pesquisa_emprestimo.setPlaceholderText("Digite nome do componente ou matrícula")
        self.campo_pesquisa_emprestimo.setClearButtonEnabled(True)
        self.campo_pesquisa_emprestimo.returnPressed.connect(
            lambda: self.pesquisar_emprestimos(apenas_emprestados=True)
        )
        layout_pesquisa_emp.addWidget(self.campo_pesquisa_emprestimo)

        self.botao_pesquisa_emprestimo = QPushButton("Buscar")
        self.botao_pesquisa_emprestimo.setFixedWidth(80)
        self.botao_pesquisa_emprestimo.clicked.connect(
            lambda: self.pesquisar_emprestimos(apenas_emprestados=True)
        )
        layout_pesquisa_emp.addWidget(self.botao_pesquisa_emprestimo)

        layout_emprestimos.addLayout(layout_pesquisa_emp)

        self.lista_emprestimos = QListWidget()
        self.lista_emprestimos.itemClicked.connect(self.mostrar_detalhes_aluno)
        self.lista_emprestimos.itemClicked.connect(self.abrir_emprestimo_da_lista)
        self.lista_emprestimos.setMinimumHeight(150)
        layout_emprestimos.addWidget(self.lista_emprestimos)

        self.tabs_pesquisa.addTab(tab_emprestimos, "Empréstimos Ativos")

        # Carregar empréstimos do dia ao abrir a aba
        self.carregar_emprestimos_do_dia()

        # ---------------- Finalização ----------------
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
            "4111", "4112", "4123", "4124",
            "4211", "4212", "4223", "4224",
            "4311", "4312", "4323", "4324",
            "4411", "4412", "4422", "4423",
            "4511", "4512", "4523", "4524",
            "28131", "28231", "28331", "28431",
            "29531", "28631", "8131", "8231",
            "8331", "8431", "8531", "8631",
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

        if not termo or termo in [".", ".*", "^", "$"]:
            self.lista_alunos.clear()
            self.mostrar_emprestimos_do_dia_na_lista()
            return

        self.lista_alunos.clear()

        try:
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Error("Não foi possível conectar ao banco de dados")

            cursor = conexao.cursor(buffered=True)

            cursor.execute("""
                SELECT matricula, nome FROM alunos
                WHERE matricula LIKE %s OR nome LIKE %s
                LIMIT 50
            """, (f"%{termo}%", f"%{termo}%"))

            resultados = cursor.fetchall()

            if resultados:
                for matricula, nome in resultados:
                    self.lista_alunos.addItem(f"{matricula} - {nome}")
            else:
                self.lista_alunos.clear()
                self.mostrar_emprestimos_do_dia_na_lista()
                return

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
            
            cursor = conexao.cursor(buffered=True)

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

                # --- Ajuste da foto ---
                if foto_bytes:
                    pixmap = QPixmap()
                    pixmap.loadFromData(foto_bytes)
                else:
                    try:
                        url = f"https://intranet.liberato.com.br/tro/data/fotos/C{matricula}.jpeg"
                        resposta = urllib.request.urlopen(url)
                        dados_imagem = resposta.read()
                        pixmap = QPixmap()
                        pixmap.loadFromData(dados_imagem)

                        if pixmap.isNull():
                            raise ValueError("Imagem da URL inválida")
                    except Exception:
                        pixmap = QPixmap("default.png")

                # 👉 Redimensiona mantendo proporção e qualidade
                max_size = 150  # ajuste aqui o tamanho desejado (ex.: 150x150)
                pixmap = pixmap.scaled(
                    max_size,
                    max_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                # Aplica no QLabel
                self.label_foto.setPixmap(pixmap)
                self.label_foto.setFixedSize(pixmap.size())
                self.label_foto.setScaledContents(False)

                # Carregar empréstimos do aluno
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
                
            cursor = conexao.cursor(buffered=True)

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
                self.label_status_emprestimos.setText(f"{total_emprestimos}")
            elif total_emprestimos < 10:
                self.label_status_emprestimos.setText(f"{total_emprestimos}")
            elif total_emprestimos < 15:
                self.label_status_emprestimos.setText(f"{total_emprestimos}")
            else:
                self.label_status_emprestimos.setText(f"{total_emprestimos}")
            
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
                
            cursor = conexao.cursor(buffered=True)

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
            self.carregar_emprestimos_do_dia()
            return
        
        self.lista_emprestimos.clear()

        try:
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Error("Não foi possível conectar ao banco de dados")
                
            cursor = conexao.cursor(buffered=True)

            query = """
            SELECT e.id, a.matricula, a.nome, c.nome, e.quantidade, 
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
                for (id_emp, matricula, aluno, comp,  qtd, data_emp, data_dev, status) in resultados:
                    data_emp_str = data_emp.strftime("%d/%m/%Y %H:%M") if data_emp else "---"
                    data_dev_str = data_dev.strftime("%d/%m/%Y %H:%M") if data_dev else "---"
                    
                    item_text = (f"{matricula} | {aluno} |  {comp} | "
                               f" {qtd} |  {data_emp_str} | "
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
    
    def adicionar_componente(self):
        # Lê o texto do campo da aba "Adicionar Componente"
        nome = self.campo_novo_componente.text().strip()

        # Validação: não deixa cadastrar vazio
        if not nome:
            QMessageBox.warning(self, "Campo vazio", "Digite o nome do componente.")
            return

        conexao = None
        cursor = None
        try:
            # Conecta ao banco
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Error("Não foi possível conectar ao banco de dados.")

            cursor = conexao.cursor(buffered=True)

            # Insere o novo componente
            cursor.execute("SELECT nome FROM componentes WHERE nome = %s", (nome,))
            existentes = cursor.fetchall()
            if existentes:
                QMessageBox.warning(self, "Duplicado", f"O componente '{nome}' já existe")
                return       
            cursor.execute("INSERT INTO componentes (nome) VALUES (%s)", (nome,))   
            conexao.commit()

            # Mensagem de sucesso
            QMessageBox.information(self, "Sucesso", f"Componente '{nome}' adicionado com sucesso.")

            # Limpa o campo
            self.campo_novo_componente.clear()

            # Atualiza a lista da aba de pesquisa
            self.pesquisar_componente()

        except Error as erro:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar componente: {erro}")
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()


    def adicionar_emprestimo(self):
        if not self.matricula_selecionada:
            QMessageBox.warning(self, "Aluno Não Selecionado", "Selecione um aluno primeiro")
            return

        componente = self.campo_componente.text().strip()
        quantidade_texto = self.campo_quantidade.text().strip()
        try:
            quantidade = int(quantidade_texto)
            if quantidade <= 0:
                quantidade = 1
        except ValueError:
            quantidade = 1

        if not componente:
            QMessageBox.warning(self, "Componente Ausente", "Informe o componente")
            return

        conexao = None
        cursor = None
        try:
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Error("Não foi possível conectar ao banco de dados")
                
            cursor = conexao.cursor(buffered=True)

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

        conexao = None
        cursor = None
        try:
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Error("Não foi possível conectar ao banco de dados")
                
            cursor = conexao.cursor(buffered=True)
            agora = datetime.now(timezone("America/Sao_Paulo"))

            for item in itens_selecionados:
                texto_qtd = item.campo_devolucao.text().strip()

                if texto_qtd == "":
                    qtd_devolver = item.quantidade
                else:
                    try:
                        qtd_devolver = int(texto_qtd)
                    except ValueError:
                        QMessageBox.warning(self, "Valor inválido", f"Quantidade inválida para {item.componente}")
                        continue  # ✅ AGORA ESTÁ DENTRO DO LOOP

                    if qtd_devolver <= 0 or qtd_devolver > item.quantidade:
                        QMessageBox.warning(self, "Quantidade inválida", f"Quantidade fora do limite para {item.componente}")
                        continue


                restante = item.quantidade - qtd_devolver

                if restante > 0:
                    # Atualiza o registro original com o restante
                    cursor.execute(
                        "UPDATE emprestimos SET quantidade = %s WHERE id = %s",
                        (restante, item.id_emprestimo)
                    )


                    try:
                        data_emp_dt = datetime.strptime(item.data_emp, "%d/%m/%Y %H:%M")
                        data_emp_formatada = data_emp_dt.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        QMessageBox.warning(self, "Data inválida", f"Formato de data inválido para {item.componente}")
                        continue
                    

                    # Cria novo registro apenas da parte devolvida
                    cursor.execute(
                        """INSERT INTO emprestimos (aluno_id, componente_id, quantidade, data_emp, data_dev, status)
                           SELECT a.id, c.id, %s, %s, %s, 'Devolvido'
                           FROM alunos a
                           JOIN componentes c ON c.nome = %s
                           WHERE a.matricula = %s
                        """,
                        (qtd_devolver, data_emp_formatada, agora, item.componente, self.matricula_selecionada)
                    )
                else:
                    # Se devolveu tudo, só marca como devolvido
                    cursor.execute(
                        "UPDATE emprestimos SET data_dev = %s, status = 'Devolvido' WHERE id = %s",
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

    def mostrar_emprestimos_do_dia_na_lista(self):
        try:
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Error("Não foi possível conectar ao banco de dados")

            cursor = conexao.cursor()

            cursor.execute("""
                SELECT a.matricula, a.nome, c.nome, e.quantidade, e.data_emp, e.status
                FROM emprestimos e
                JOIN alunos a ON e.aluno_id = a.id
                JOIN componentes c ON e.componente_id = c.id
                WHERE DATE(e.data_emp) = CURDATE()
                ORDER BY e.data_emp DESC
            """)

            resultados = cursor.fetchall()
            cursor.close()
            conexao.close()

        except Error as erro:
            QMessageBox.critical(self, "Erro", f"Erro ao buscar empréstimos do dia: {str(erro)}")



    def pesquisar_por_turma(self, turma):
        self.lista_alunos.clear()
        self.campo_pesquisa.clear()
        
        try:
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Error("Não foi possível conectar ao banco de dados")
                
            cursor = conexao.cursor(buffered=True)

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
    
    def mostrar_ranking(self):
        try:
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Exception("Não foi possível conectar ao banco de dados")

            cursor = conexao.cursor(buffered=True)

            # Consulta principal: total saiu, emprestado e devolvido no ano
            cursor.execute("""
                SELECT 
                    c.nome,
                    SUM(e.quantidade) AS total_saiu,
                    SUM(CASE WHEN e.status = 'Emprestado' THEN e.quantidade ELSE 0 END) AS total_emprestado,
                    SUM(CASE WHEN e.status = 'Devolvido' THEN e.quantidade ELSE 0 END) AS total_devolvido
                    FROM emprestimos e
                    JOIN componentes c ON e.componente_id = c.id
                    WHERE e.data_emp >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
                    GROUP BY c.nome
                    ORDER BY total_saiu DESC
            """)
            dados_principais = cursor.fetchall()

            # Consulta extra: devolvidos no ano que também foram emprestados no ano
            cursor.execute("""
                SELECT 
                    c.nome,
                    SUM(e.quantidade) AS devolvido_no_ano
                FROM emprestimos e
                JOIN componentes c ON e.componente_id = c.id
                WHERE e.status = 'Devolvido'
                  AND e.data_emp >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
                  AND e.data_dev >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
                GROUP BY c.nome
            """)
            devolvidos_no_ano = dict(cursor.fetchall())

            texto = ""
            texto += f"{'Componente':<35} {'Saiu':<10} {'Emprestado':<12} {'Devolvido':<12} {'Saiu e Voltou':<15}\n"
            texto += "-" * 90 + "\n"

            for nome, saiu, emprestado, devolvido in dados_principais:
                saiu = saiu or 0
                emprestado = emprestado or 0
                devolvido = devolvido or 0
                saiu_e_voltou = devolvidos_no_ano.get(nome, 0)

                texto += f"{nome:<35} {saiu:<10} {emprestado:<12} {devolvido:<12} {saiu_e_voltou:<15}\n"

            # Caminho para área de trabalho
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            caminho_arquivo = os.path.join(desktop, "ranking_materiais.txt")

            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                f.write(texto)

            QMessageBox.information(self, "Ranking", f"Arquivo salvo em:\n{caminho_arquivo}")

        except Exception as erro:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar ranking: {erro}")




    def executar_processar_alunos(self):
        try:
            sucesso = processar_alunos()  # função importada
            if sucesso:
                QMessageBox.information(self, "Processar Alunos", "✅ Alunos processados com sucesso!")
            else:
                QMessageBox.warning(self, "Processar Alunos", "⚠️ Nenhum aluno foi processado ou ocorreu um erro.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"❌ Erro ao processar alunos: {e}")

    def executar_importar_emprestimos(self):
        try:
            # Aqui você pode fixar o arquivo ou abrir um seletor
            caminho_csv = "emficha.csv"  # ou usar QFileDialog para escolher
            importar_emprestimos(caminho_csv)
            QMessageBox.information(self, "Importar Empréstimos", "✅ Importação concluída com sucesso!")
        except FileNotFoundError:
            QMessageBox.critical(self, "Erro", "❌ Arquivo CSV não encontrado.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"❌ Erro ao importar empréstimos: {e}")

    def abrir_emprestimo_da_lista(self, item):
        texto = item.text()

        # Ignorar linhas de título
        if "📋" in texto or "Nenhum empréstimo" in texto:
            return

        # Extrair matrícula antes do " - "
        if " - " not in texto:
            return

        matricula = texto.split(" - ")[0].strip()

        # Salvar matrícula selecionada
        self.matricula_selecionada = matricula

        # Carregar empréstimos do aluno
        self.carregar_emprestimos(matricula)

        # Atualizar painel de detalhes do aluno
        self.carregar_emprestimos(matricula)


    def gerar_emails_pendentes(self):
        try:
            conexao = ConfigBanco.obter_conexao()
            if conexao is None:
                raise Exception("Não foi possível conectar ao banco de dados")

            cursor = conexao.cursor(buffered=True)

            cursor.execute("""
                SELECT DISTINCT a.email
                FROM emprestimos e
                JOIN alunos a ON e.aluno_id = a.id
                WHERE e.status = 'Emprestado'
                  AND e.data_emp >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
            """)

            resultados = cursor.fetchall()

            if not resultados:
                QMessageBox.information(self, "Emails", "Nenhum empréstimo com status 'Emprestado' encontrado no último ano.")
                return

            # Monta o texto
            texto = "Emails com empréstimos em aberto (status 'Emprestado') no último ano:\n\n"
            for (email,) in resultados:
                texto += f"{email}\n"

            # Caminho para área de trabalho
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            caminho_arquivo = os.path.join(desktop, "emails_emprestados.txt")

            # Salva o arquivo
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                f.write(texto)

        except Exception as erro:
            QMessageBox.critical(self, "Erro", f"Falha ao consultar banco: {erro}")

    def carregar_emprestimos_do_dia(self):
        self.lista_emprestimos.clear()

        try:
            conexao = ConfigBanco.obter_conexao()
            cursor = conexao.cursor()

            cursor.execute("""
                SELECT a.matricula, a.nome, c.nome, e.quantidade, e.data_emp, e.status
                FROM emprestimos e
                JOIN alunos a ON a.id = e.aluno_id
                JOIN componentes c ON c.id = e.componente_id
                WHERE DATE(e.data_emp) = CURDATE()
                ORDER BY e.data_emp DESC
            """)

            resultados = cursor.fetchall()

            if not resultados:
                self.lista_emprestimos.addItem("Nenhum empréstimo registrado hoje.")
                return

            self.lista_emprestimos.addItem("📋 Empréstimos registrados hoje:")

            self.lista_emprestimos.clear()

            ativos = [r for r in resultados if r[5] == "Emprestado"]

            if not ativos:
                self.lista_emprestimos.addItem("Nenhum empréstimo registrado hoje.")
                return

            self.lista_emprestimos.addItem("📋 Empréstimos registrados hoje:")

            for matricula, nome_aluno, nome_comp, qtd, data, status in ativos:
                hora = data.strftime("%H:%M") if isinstance(data, datetime) else str(data)
                texto = f"{matricula} - {nome_aluno} ({qtd}x {nome_comp} às {hora}, {status})"
                self.lista_emprestimos.addItem(texto)
        
            
        except Error as erro:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar empréstimos do dia: {erro}")

        finally:
            if cursor: cursor.close()
            if conexao: conexao.close()

    def recarregar_dados(self):
        if self.matricula_selecionada:
            self.carregar_emprestimos(self.matricula_selecionada)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = AppAlmoxarifado()
    janela.show()
    sys.exit(app.exec())
