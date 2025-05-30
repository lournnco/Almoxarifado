import sys
import mysql.connector
from mysql.connector import Error
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QLineEdit, QListWidget
)
from PyQt6.QtGui import QPixmap
from datetime import datetime
from pytz import timezone


DB_NAME = "almox"
DB_USER = "root"
DB_PASSWORD = "manulauro5308"
DB_HOST = "localhost"
DB_PORT = 3306  # padrão MySQL


def get_data_hora_brasilia():
    fuso = timezone("America/Sao_Paulo")
    agora = datetime.now(fuso)
    return agora.strftime("%d/%m/%Y %H:%M:%S")


class AlmoxarifadoApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistema de Almoxarifado")
        self.setGeometry(100, 100, 700, 750)

        self.matricula_selecionada = None

        main_layout = QVBoxLayout()

        self.criar_grupo_pesquisa(main_layout)
        self.criar_grupo_detalhes(main_layout)
        self.criar_grupo_emprestimos(main_layout)

        self.setLayout(main_layout)

        self.set_cor_fundo_verde()

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
        self.lista_alunos.itemClicked.connect(self.mostrar_detalhes_aluno)
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
            [
                "Quantidade",
                "Código",
                "Nome",
                "Retirada",
                "Devolução",
            ]
        )

        col_widths = [90, 90, 200, 140, 140]
        for i, w in enumerate(col_widths):
            self.tabela_emprestimos.setColumnWidth(i, w)

        emprestimos_layout.addWidget(self.tabela_emprestimos)

        self.botao_devolver = QPushButton("Registrar Devolução")
        self.botao_devolver.clicked.connect(self.registrar_devolucao)
        emprestimos_layout.addWidget(self.botao_devolver)

        self.input_componente = QLineEdit()
        self.input_componente.setPlaceholderText("ID do componente")

        self.input_quantidade = QLineEdit()
        self.input_quantidade.setPlaceholderText("Quantidade")

        self.botao_adicionar = QPushButton("Adicionar Empréstimo")
        self.botao_adicionar.clicked.connect(self.adicionar_emprestimo)

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
            self.lista_alunos.addItem("Digite algo para pesquisar...")
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
                    self.lista_alunos.addItem(f"{matricula} - {nome}")
            else:
                self.lista_alunos.addItem("Nenhum aluno encontrado.")

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

                self.label_matricula.setText(f"Matrícula: {matricula}")
                self.label_nome.setText(f"Nome: {nome}")
                self.label_email.setText(f"E-mail: {email}")

                if foto:
                    pixmap = QPixmap()
                    if pixmap.loadFromData(foto):
                        self.foto_label.setPixmap(pixmap.scaled(100, 100))
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

            # Query para pegar a soma dos empréstimos ativos
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

            # Aplicando a cor
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
            # Cor padrão em caso de erro
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
                    f"{data_ret} {hora_ret}" if data_ret and hora_ret else ""
                )
                devolucao = (
                    f"{data_dev} {hora_dev}" if data_dev and hora_dev else ""
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
            return

        componente_id = self.input_componente.text().strip()
        quantidade = self.input_quantidade.text().strip()

        if not componente_id or not quantidade.isdigit():
            return

        quantidade = int(quantidade)

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
            data_emprestimo = agora.date()
            hora_emprestimo = agora.time().replace(microsecond=0)

            query = (
                "INSERT INTO emprestimos "
                "(aluno_id, componente_id, "
                "quantidade, data_emprestimo, hora_emprestimo) "
                "VALUES (%s, %s, %s, %s, %s)"
            )
            cur.execute(
                query,
                (
                    aluno_id,
                    componente_id,
                    quantidade,
                    data_emprestimo,
                    hora_emprestimo,
                ),
            )
            conn.commit()
            cur.close()
            conn.close()

            self.carregar_emprestimos(self.matricula_selecionada)
            self.atualizar_cor_fundo_por_quantidade(self.matricula_selecionada)
            self.input_componente.clear()
            self.input_quantidade.clear()

        except Error as e:
            print(f"Erro ao adicionar empréstimo: {e}")

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
            cur.close()
            conn.close()

            self.carregar_emprestimos(self.matricula_selecionada)
            self.atualizar_cor_fundo_por_quantidade(self.matricula_selecionada)

        except Error as e:
            print(f"Erro ao registrar devolução: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AlmoxarifadoApp()
    window.show()
    sys.exit(app.exec())
