import sys
import mysql.connector
from mysql.connector import Error
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QLineEdit, QListWidget, QRadioButton, QButtonGroup, QMessageBox
)
from PyQt6.QtGui import QPixmap
from datetime import datetime
from pytz import timezone


DB_NAME = "almox"
DB_USER = "root"
DB_PASSWORD = "manulauro5308"
DB_HOST = "localhost"
DB_PORT = 3306


def get_data_hora_brasilia():
    fuso = timezone("America/Sao_Paulo")
    agora = datetime.now(fuso)
    return agora.strftime("%d/%m/%Y %H:%M:%S")


class AlmoxarifadoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Almoxarifado")
        self.setGeometry(100, 100, 800, 800)
        self.matricula_selecionada = None
        main_layout = QVBoxLayout()

        self.criar_grupo_pesquisa(main_layout)
        self.criar_grupo_pesquisa_componente(main_layout)
        self.criar_grupo_detalhes(main_layout)
        self.criar_grupo_emprestimos(main_layout)

        self.setLayout(main_layout)
        self.set_cor_fundo("#ffffff")

    def criar_grupo_pesquisa_componente(self, layout):
        """Cria o grupo de pesquisa de componentes"""
        group = QGroupBox("Pesquisar Componente")
        vbox = QVBoxLayout()

        self.pesquisa_componente_input = QLineEdit()
        self.pesquisa_componente_input.setPlaceholderText(
            "Digite nome ou código do componente"
        )
        vbox.addWidget(self.pesquisa_componente_input)

        self.pesquisa_tipo_group = QButtonGroup()
        hbox = QHBoxLayout()

        self.radio_nome = QRadioButton("Por Nome")
        self.radio_nome.setChecked(True)
        self.pesquisa_tipo_group.addButton(self.radio_nome)
        hbox.addWidget(self.radio_nome)

        self.radio_codigo = QRadioButton("Por Código")
        self.pesquisa_tipo_group.addButton(self.radio_codigo)
        hbox.addWidget(self.radio_codigo)

        vbox.addLayout(hbox)

        self.botao_pesquisa_componente = QPushButton("Buscar Componente")
        self.botao_pesquisa_componente.clicked.connect(
            self.pesquisar_componente
        )
        vbox.addWidget(self.botao_pesquisa_componente)

        self.lista_componentes = QListWidget()
        self.lista_componentes.itemDoubleClicked.connect(
            self.selecionar_componente
        )
        vbox.addWidget(self.lista_componentes)

        group.setLayout(vbox)
        layout.addWidget(group)

    def pesquisar_componente(self):
        termo = self.pesquisa_componente_input.text().strip()

        if not termo:
            self.lista_componentes.clear()
            self.lista_componentes.addItem(
                "Digite um termo para pesquisar"
            )
            return

        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = conn.cursor()

            if self.radio_nome.isChecked():
                query = """
                    SELECT id, nome, quantidade
                    FROM componentes
                    WHERE LOWER(nome) LIKE LOWER(%s)
                    ORDER BY nome
                """
                param = f"%{termo}%"
            else:
                if not termo.isdigit():
                    self.lista_componentes.clear()
                    self.lista_componentes.addItem(
                        "Código deve ser numérico"
                    )
                    return

                query = """
                    SELECT id, nome, quantidade
                    FROM componentes
                    WHERE id = %s
                """
                param = int(termo)

            cursor.execute(query, (param,))
            resultados = cursor.fetchall()
            self.lista_componentes.clear()

            if resultados:
                for id_comp, nome, qtd in resultados:
                    self.lista_componentes.addItem(
                        f"{id_comp} - {nome} (Estoque: {qtd})"
                    )
            else:
                self.lista_componentes.addItem(
                    "Nenhum componente encontrado"
                )

            cursor.close()
            conn.close()

        except Error as e:
            self.lista_componentes.clear()
            self.lista_componentes.addItem(
                f"Erro na pesquisa: {str(e)}"
            )

    def selecionar_componente(self, item):
        """Quando um componente é selecionado na lista"""
        texto = item.text()
        try:
            id_componente = texto.split(" - ")[0]
            self.input_componente.setText(id_componente)
            self.input_quantidade.setFocus()
        except (AttributeError, IndexError) as e:
            QMessageBox.warning(
                self,
                "Aviso",
                f"Erro ao selecionar componente: {str(e)}"
            )

    def criar_grupo_pesquisa(self, layout):
        self.group_pesquisa = QGroupBox("Pesquisar Aluno")
        pesquisa_layout = QVBoxLayout()

        self.pesquisa_input = QLineEdit()
        self.pesquisa_input.setPlaceholderText(
            "Digite a matrícula ou nome do aluno"
        )
        pesquisa_layout.addWidget(self.pesquisa_input)

        self.botao_pesquisa = QPushButton("Pesquisar")
        self.botao_pesquisa.clicked.connect(self.pesquisar_aluno)
        pesquisa_layout.addWidget(self.botao_pesquisa)

        self.lista_alunos = QListWidget()
        self.lista_alunos.itemClicked.connect(
            self.mostrar_detalhes_aluno
        )
        pesquisa_layout.addWidget(self.lista_alunos)

        self.group_pesquisa.setLayout(pesquisa_layout)
        layout.addWidget(self.group_pesquisa)

    def criar_grupo_detalhes(self, layout):
        self.group_detalhes = QGroupBox("Detalhes do Aluno")
        detalhes_layout = QHBoxLayout()

        self.foto_label = QLabel()
        self.foto_label.setPixmap(
            QPixmap("default.png").scaled(100, 100)
        )
        self.foto_label.setFixedSize(100, 100)
        detalhes_layout.addWidget(self.foto_label)

        self.info_layout = QVBoxLayout()

        self.label_matricula = QLabel("Matrícula: -")
        self.label_nome = QLabel("Nome: -")
        self.label_email = QLabel("E-mail: -")

        self.info_layout.addWidget(self.label_matricula)
        self.info_layout.addWidget(self.label_nome)
        self.info_layout.addWidget(self.label_email)

        detalhes_layout.addLayout(self.info_layout)
        self.group_detalhes.setLayout(detalhes_layout)
        layout.addWidget(self.group_detalhes)

    def criar_grupo_emprestimos(self, layout):
        self.group_emprestimos = QGroupBox("Empréstimos")
        emprestimos_layout = QVBoxLayout()

        self.tabela_emprestimos = QTableWidget()
        self.tabela_emprestimos.setColumnCount(5)
        self.tabela_emprestimos.setHorizontalHeaderLabels(
            ["Quantidade", "Código", "Nome", "Retirada", "Devolução"]
        )

        col_widths = [90, 90, 200, 140, 140]
        for i, w in enumerate(col_widths):
            self.tabela_emprestimos.setColumnWidth(i, w)

        emprestimos_layout.addWidget(self.tabela_emprestimos)

        self.botao_devolver = QPushButton("Registrar Devolução")
        self.botao_devolver.clicked.connect(
            self.registrar_devolucao
        )
        emprestimos_layout.addWidget(self.botao_devolver)

        self.input_componente = QLineEdit()
        self.input_componente.setPlaceholderText("Nome ou ID do componente")

        self.input_quantidade = QLineEdit()
        self.input_quantidade.setPlaceholderText("Quantidade")

        self.botao_adicionar = QPushButton("Adicionar Empréstimo")
        self.botao_adicionar.clicked.connect(
            self.adicionar_emprestimo
        )

        form_layout = QHBoxLayout()
        form_layout.addWidget(self.input_componente)
        form_layout.addWidget(self.input_quantidade)
        form_layout.addWidget(self.botao_adicionar)

        emprestimos_layout.addLayout(form_layout)
        self.group_emprestimos.setLayout(emprestimos_layout)
        layout.addWidget(self.group_emprestimos)

    def set_cor_fundo_verde(self):
        self.group_detalhes.setStyleSheet(
            "QGroupBox { background-color: #d0f0c0; }"
        )

    def set_cor_fundo(self, cor_hex):
        self.group_detalhes.setStyleSheet(
            f"QGroupBox {{ background-color: {cor_hex}; }}"
        )

    def pesquisar_aluno(self):
        termo = self.pesquisa_input.text().strip()
        if not termo:
            self.lista_alunos.clear()
            self.lista_alunos.addItem(
                "Digite algo para pesquisar..."
            )
            return

        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT,
            )
            cur = conn.cursor()

            termo_lower = termo.lower()
            query = (
                "SELECT matricula, nome FROM alunos "
                "WHERE LOWER(matricula) LIKE %s OR LOWER(nome) LIKE %s"
            )
            cur.execute(query, (f"%{termo_lower}%", f"%{termo_lower}%"))
            resultados = cur.fetchall()

            self.lista_alunos.clear()

            if resultados:
                for matricula, nome in resultados:
                    self.lista_alunos.addItem(
                        f"{matricula} - {nome}"
                    )
            else:
                self.lista_alunos.addItem(
                    "Nenhum aluno encontrado."
                )

            cur.close()
            conn.close()

        except Error as e:
            self.lista_alunos.clear()
            self.lista_alunos.addItem(f"Erro: {e}")

    def mostrar_detalhes_aluno(self, item):
        matricula = item.text().split(" - ")[0]
        self.matricula_selecionada = matricula

        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT,
            )
            cur = conn.cursor()

            cur.execute(
                "SELECT nome, email, foto FROM alunos WHERE matricula = %s",
                (matricula,),
            )
            aluno = cur.fetchone()

            if aluno:
                nome, email, foto = aluno

                self.label_matricula.setText(
                    f"Matrícula: {matricula}"
                )
                self.label_nome.setText(f"Nome: {nome}")
                self.label_email.setText(f"E-mail: {email}")

                if foto:
                    pixmap = QPixmap()
                    if pixmap.loadFromData(foto):
                        self.foto_label.setPixmap(
                            pixmap.scaled(100, 100)
                        )
                    else:
                        self.foto_label.setPixmap(
                            QPixmap("default.png").scaled(100, 100)
                        )
                else:
                    self.foto_label.setPixmap(
                        QPixmap("default.png").scaled(100, 100)
                    )

                self.atualizar_cor_fundo_por_quantidade(matricula)
                self.carregar_emprestimos(matricula)
            else:
                self.label_matricula.setText("Matrícula: -")
                self.label_nome.setText("Nome: -")
                self.label_email.setText("E-mail: -")

                self.foto_label.setPixmap(
                    QPixmap("default.png").scaled(100, 100)
                )
                self.set_cor_fundo_verde()

            cur.close()
            conn.close()

        except Error as e:
            self.label_matricula.setText(f"Erro: {e}")

    def atualizar_cor_fundo_por_quantidade(self, matricula):
        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT,
            )
            cur = conn.cursor()

            query = """
                SELECT COALESCE(SUM(e.quantidade), 0)
                FROM emprestimos e
                JOIN alunos a ON e.aluno_id = a.id
                WHERE a.matricula = %s AND e.data_devolucao IS NULL
            """
            cur.execute(query, (matricula,))
            total = cur.fetchone()[0]

            if total == 0:
                cor = "#ffffff"  # Branco - nenhum empréstimo
            elif 1 <= total <= 9:
                cor = "#d0f0c0"  # Verde claro - situação normal
            elif 10 <= total <= 14:
                cor = "#f0e68c"  # Amarelo claro - atenção
            else:
                cor = "#f08080"  # Vermelho claro - situação crítica

            stylesheet = (
                f"QGroupBox {{ "
                f"background-color: {cor}; "
                f"border: 2px solid {self.escurecer_cor(cor)}; "
                f"}}"
            )
            self.group_detalhes.setStyleSheet(stylesheet)

            cur.close()
            conn.close()

        except Error as e:
            print(f"Erro ao atualizar cor: {e}")
            self.group_detalhes.setStyleSheet(
                "QGroupBox { "
                "background-color: #d0f0c0; "
                "border: 2px solid #a0d0a0; "
                "}"
            )

    def escurecer_cor(self, cor_hex, fator=0.8):
        """Escurece uma cor HEX para usar na borda"""
        cor_hex = cor_hex.lstrip('#')
        rgb = tuple(int(cor_hex[i:i+2], 16) for i in (0, 2, 4))
        escuro = tuple(int(c * fator) for c in rgb)
        return '#%02x%02x%02x' % escuro

    def carregar_emprestimos(self, matricula):
        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT,
            )
            cur = conn.cursor()

            cur.execute(
                """
                SELECT e.quantidade,
                        c.id,
                        c.nome,
                        e.data_emprestimo,
                        e.hora_emprestimo,
                        e.data_devolucao,
                        e.hora_devolucao
                FROM emprestimos e
                JOIN alunos a ON e.aluno_id = a.id
                JOIN componentes c ON e.componente_id = c.id
                WHERE a.matricula = %s
                ORDER BY e.data_emprestimo DESC,
                         e.hora_emprestimo DESC
                """,
                (matricula,),
            )
            registros = cur.fetchall()

            self.tabela_emprestimos.setRowCount(len(registros))

            for row, (
                qtde,
                codigo,
                nome,
                data_ret,
                hora_ret,
                data_dev,
                hora_dev,
            ) in enumerate(registros):
                retirada = (
                    f"{data_ret} {hora_ret}"
                    if data_ret and hora_ret
                    else ""
                )
                devolucao = (
                    f"{data_dev} {hora_dev}"
                    if data_dev and hora_dev
                    else ""
                )

                self.tabela_emprestimos.setItem(
                    row, 0, QTableWidgetItem(str(qtde))
                )
                self.tabela_emprestimos.setItem(
                    row, 1, QTableWidgetItem(str(codigo))
                )
                self.tabela_emprestimos.setItem(
                    row, 2, QTableWidgetItem(nome)
                )
                self.tabela_emprestimos.setItem(
                    row, 3, QTableWidgetItem(retirada)
                )
                self.tabela_emprestimos.setItem(
                    row, 4, QTableWidgetItem(devolucao)
                )

            cur.close()
            conn.close()

        except Error as e:
            print(f"Erro ao carregar empréstimos: {e}")

    def adicionar_emprestimo(self):
        if not self.matricula_selecionada:
            QMessageBox.warning(
                self,
                "Aviso",
                "Selecione um aluno primeiro"
            )
            return

        componente = self.input_componente.text().strip()
        quantidade = self.input_quantidade.text().strip()

        if not componente:
            QMessageBox.warning(
                self,
                "Aviso",
                "Digite o código ou nome do componente"
            )
            return

        if not quantidade.isdigit() or int(quantidade) <= 0:
            QMessageBox.warning(
                self,
                "Aviso",
                "Quantidade deve ser um número positivo"
            )
            return

        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT,
            )
            cur = conn.cursor()

            # Verifica se é número (ID) ou texto (nome)
            if componente.isdigit():
                cur.execute(
                    "SELECT id, quantidade FROM componentes WHERE id = %s",
                    (componente,)
                )
            else:
                cur.execute(
                    """SELECT id, quantidade FROM componentes
                    WHERE nome LIKE %s LIMIT 1""",
                    (f"%{componente}%",)
                )

            resultado = cur.fetchone()
            if not resultado:
                QMessageBox.warning(
                    self,
                    "Aviso",
                    "Componente não encontrado"
                )
                return

            componente_id, qtd_disponivel = resultado

            if int(quantidade) > qtd_disponivel:
                QMessageBox.warning(
                    self,
                    "Aviso",
                    f"Quantidade indisponível (estoque: {qtd_disponivel})"
                )
                return

            # Obtém ID do aluno
            cur.execute(
                "SELECT id FROM alunos WHERE matricula = %s",
                (self.matricula_selecionada,),
            )
            aluno_id = cur.fetchone()[0]

            # Registra o empréstimo
            agora = datetime.now(timezone("America/Sao_Paulo"))
            data = agora.date()
            hora = agora.time().replace(microsecond=0)

            cur.execute(
                """INSERT INTO emprestimos
                (aluno_id, componente_id,
                quantidade, data_emprestimo, hora_emprestimo)
                VALUES (%s, %s, %s, %s, %s)""",
                (aluno_id, componente_id, quantidade, data, hora),
            )

            # Atualiza o estoque
            cur.execute(
                "UPDATE componentes SET quantidade = quantidade"
                "- %s WHERE id = %s",
                (quantidade, componente_id)
            )

            conn.commit()
            cur.close()
            conn.close()

            # Atualiza a interface
            self.carregar_emprestimos(self.matricula_selecionada)
            self.atualizar_cor_fundo_por_quantidade(
                self.matricula_selecionada
            )
            self.input_componente.clear()
            self.input_quantidade.clear()

            QMessageBox.information(
                self,
                "Sucesso",
                "Empréstimo registrado!"
            )

        except Error as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao adicionar empréstimo: {e}"
            )

    def registrar_devolucao(self):
        if not self.matricula_selecionada:
            return

        linha = self.tabela_emprestimos.currentRow()
        if linha < 0:
            return

        codigo = self.tabela_emprestimos.item(linha, 1).text()

        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT,
            )
            cur = conn.cursor()

            cur.execute(
                "SELECT id FROM alunos WHERE matricula = %s",
                (self.matricula_selecionada,),
            )
            aluno_id_row = cur.fetchone()
            if not aluno_id_row:
                return
            aluno_id = aluno_id_row[0]

            agora = datetime.now(timezone("America/Sao_Paulo"))
            data_devolucao = agora.date()
            hora_devolucao = agora.time().replace(microsecond=0)

            query = (
                "UPDATE emprestimos "
                "SET data_devolucao = %s, hora_devolucao = %s "
                "WHERE aluno_id = %s AND componente_id = %s "
                "AND data_devolucao IS NULL LIMIT 1"
            )
            cur.execute(
                query,
                (
                    data_devolucao,
                    hora_devolucao,
                    aluno_id,
                    codigo,
                ),
            )
            conn.commit()

            # Atualiza a quantidade disponível do componente
            cur.execute(
                "SELECT quantidade FROM emprestimos "
                "WHERE aluno_id = %s AND componente_id = %s "
                "AND data_devolucao = %s LIMIT 1",
                (aluno_id, codigo, data_devolucao)
            )
            quantidade = cur.fetchone()[0]

            cur.execute(
                "UPDATE componentes SET quantidade = quantidade + %s "
                "WHERE id = %s",
                (quantidade, codigo)
            )
            conn.commit()

            cur.close()
            conn.close()

            self.carregar_emprestimos(self.matricula_selecionada)
            self.atualizar_cor_fundo_por_quantidade(
                self.matricula_selecionada
            )

        except Error as e:
            print(f"Erro ao registrar devolução: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AlmoxarifadoApp()
    window.show()
    sys.exit(app.exec())
