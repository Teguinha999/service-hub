
import sqlite3


def conectar():
    conexao = sqlite3.connect("servicehub.db")
    conexao.row_factory = sqlite3.Row

    # Ativa a integridade das relações entre tabelas
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


def criar_tabelas():
    conexao = conectar()

    # Tabela de clientes
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            email TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabela de equipamentos
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            marca TEXT,
            modelo TEXT,
            numero_serie TEXT,
            descricao TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (cliente_id)
            REFERENCES clientes (id)
            ON DELETE RESTRICT
        )
    """)

    # Tabela de ordens de serviço
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipamento_id INTEGER NOT NULL,
            problema TEXT NOT NULL,
            diagnostico TEXT,
            valor REAL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Aguardando',
            data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (equipamento_id)
            REFERENCES equipamentos (id)
            ON DELETE RESTRICT
        )
    """)

        # Tabela de histórico de alterações das ordens de serviço
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS historico_alteracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ordem_id INTEGER NOT NULL,
            campo_alterado TEXT NOT NULL,
            valor_anterior TEXT,
            novo_valor TEXT,
            motivo TEXT NOT NULL,
            responsavel TEXT DEFAULT 'Não identificado',
            data_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (ordem_id)
            REFERENCES ordens_servico (id)
            ON DELETE RESTRICT
        )
    """)
        # Histórico de exclusões de clientes
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS historico_clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id_original INTEGER,
            nome_cliente TEXT NOT NULL,
            telefone_cliente TEXT,
            email_cliente TEXT,
            evento TEXT NOT NULL,
            responsavel TEXT DEFAULT 'Não identificado',
            data_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conexao.commit()
    conexao.close()
