
from flask import Flask, render_template, request, redirect, url_for, abort, flash
import os
from database import criar_tabelas, conectar

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "servicehub-chave-local-desenvolvimento"
)

criar_tabelas()


@app.route("/")
def inicio():

    conexao = conectar()

    # Quantidade real de clientes
    total_clientes = conexao.execute("""
        SELECT COUNT(*) FROM clientes
    """).fetchone()[0]

    # Quantidade real de equipamentos
    total_equipamentos = conexao.execute("""
        SELECT COUNT(*) FROM equipamentos
    """).fetchone()[0]

    # Ordens em andamento
    ordens_andamento = conexao.execute("""
    SELECT COUNT(*)
    FROM ordens_servico
    WHERE status <> ?
""", ("Concluída",)).fetchone()[0]

    # Ordens concluídas
    ordens_concluidas = conexao.execute("""
        SELECT COUNT(*) FROM ordens_servico
        WHERE status = 'Concluída'
    """).fetchone()[0]

    # Cinco ordens mais recentes
    ordens_recentes = conexao.execute("""
        SELECT
            ordens_servico.id,
            ordens_servico.status,
            clientes.nome AS nome_cliente,
            clientes.telefone AS telefone_cliente,
            equipamentos.tipo,
            equipamentos.marca,
            equipamentos.modelo
        FROM ordens_servico
        JOIN equipamentos
            ON ordens_servico.equipamento_id = equipamentos.id
        JOIN clientes
            ON equipamentos.cliente_id = clientes.id
        ORDER BY ordens_servico.id DESC
        LIMIT 5
    """).fetchall()

    conexao.close()

    return render_template(
        "index.html",
        total_clientes=total_clientes,
        total_equipamentos=total_equipamentos,
        ordens_andamento=ordens_andamento,
        ordens_concluidas=ordens_concluidas,
        ordens_recentes=ordens_recentes
    )


@app.route("/clientes", methods=["GET", "POST"])
def clientes():

    if request.method == "POST":
        nome = request.form["nome"]
        telefone = request.form["telefone"]
        email = request.form["email"]

        conexao = conectar()

        conexao.execute("""
            INSERT INTO clientes (nome, telefone, email)
            VALUES (?, ?, ?)
        """, (nome, telefone, email))

        conexao.commit()
        conexao.close()

        return redirect(url_for("clientes"))

    conexao = conectar()

    pesquisa = request.args.get("q", "").strip()

    if pesquisa:
        termo = f"%{pesquisa}%"

        lista_clientes = conexao.execute("""
            SELECT * FROM clientes
            WHERE nome LIKE ?
            OR telefone LIKE ?
            OR email LIKE ?
            ORDER BY id DESC
        """, (termo, termo, termo)).fetchall()

    else:
        lista_clientes = conexao.execute(
            "SELECT * FROM clientes ORDER BY id DESC"
        ).fetchall()

    conexao.close()

    return render_template(
        "clientes.html",
        clientes=lista_clientes
    )


@app.route("/clientes/editar/<int:cliente_id>", methods=["GET", "POST"])
def editar_cliente(cliente_id):

    conexao = conectar()

    cliente = conexao.execute(
        "SELECT * FROM clientes WHERE id = ?",
        (cliente_id,)
    ).fetchone()

    if cliente is None:
        conexao.close()
        abort(404)

    if request.method == "POST":

        nome = request.form["nome"]
        telefone = request.form["telefone"]
        email = request.form["email"]

        conexao.execute("""
            UPDATE clientes
            SET nome = ?, telefone = ?, email = ?
            WHERE id = ?
        """, (nome, telefone, email, cliente_id))

        conexao.commit()
        conexao.close()

        return redirect(url_for("clientes"))

    conexao.close()

    return render_template(
        "editar_cliente.html",
        cliente=cliente
    )

@app.route("/clientes/excluir/<int:cliente_id>", methods=["POST"])
def excluir_cliente(cliente_id):

    conexao = conectar()

    # Busca os dados do cliente antes da exclusão
    cliente = conexao.execute("""
        SELECT id, nome, telefone, email
        FROM clientes
        WHERE id = ?
    """, (cliente_id,)).fetchone()

    if cliente is None:
        conexao.close()
        abort(404)

    # Verifica se existem equipamentos vinculados
    equipamentos = conexao.execute("""
        SELECT COUNT(*)
        FROM equipamentos
        WHERE cliente_id = ?
    """, (cliente_id,)).fetchone()[0]

    if equipamentos > 0:
        conexao.close()

        flash(
            "Não é possível excluir este cliente porque existem "
            "equipamentos vinculados ao cadastro.",
            "erro"
        )

        return redirect(url_for("clientes"))

    try:
        # Registra a exclusão antes de apagar o cliente
        conexao.execute("""
            INSERT INTO historico_clientes (
                cliente_id_original,
                nome_cliente,
                telefone_cliente,
                email_cliente,
                evento
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            cliente["id"],
            cliente["nome"],
            cliente["telefone"],
            cliente["email"],
            "Cliente excluído do cadastro"
        ))

        # Exclui o cliente
        conexao.execute("""
            DELETE FROM clientes
            WHERE id = ?
        """, (cliente_id,))

        conexao.commit()

        flash("Cliente excluído com sucesso!", "sucesso")

    except Exception:
        conexao.rollback()
        flash(
            "Não foi possível excluir o cliente. "
            "Verifique se existem registros vinculados.",
            "erro"
        )

    finally:
        conexao.close()

    return redirect(url_for("clientes"))

@app.route("/equipamentos", methods=["GET", "POST"])
def equipamentos():

    conexao = conectar()

    # Busca os clientes cadastrados
    lista_clientes = conexao.execute(
        "SELECT * FROM clientes ORDER BY nome"
    ).fetchall()

    if request.method == "POST":

        cliente_id = request.form["cliente_id"]
        tipo = request.form["tipo"]
        marca = request.form["marca"]
        modelo = request.form["modelo"]
        numero_serie = request.form["numero_serie"]
        descricao = request.form["descricao"]

        conexao.execute("""
            INSERT INTO equipamentos
            (cliente_id, tipo, marca, modelo, numero_serie, descricao)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            cliente_id,
            tipo,
            marca,
            modelo,
            numero_serie,
            descricao
        ))

        conexao.commit()
        conexao.close()

        return redirect(url_for("equipamentos"))

    lista_equipamentos = conexao.execute("""
        SELECT
            equipamentos.*,
            clientes.nome AS nome_cliente
        FROM equipamentos
        JOIN clientes
        ON equipamentos.cliente_id = clientes.id
        ORDER BY equipamentos.id DESC
    """).fetchall()

    conexao.close()

    return render_template(
        "equipamentos.html",
        clientes=lista_clientes,
        equipamentos=lista_equipamentos
    )
@app.route("/ordens-servico", methods=["GET", "POST"])
def ordens_servico():
    conexao = conectar()

    if request.method == "POST":
        equipamento_id = request.form["equipamento_id"]
        problema = request.form["problema"]
        diagnostico = request.form["diagnostico"]
        valor = request.form["valor"]

        conexao.execute("""
            INSERT INTO ordens_servico
            (equipamento_id, problema, diagnostico, valor)
            VALUES (?, ?, ?, ?)
        """, (equipamento_id, problema, diagnostico, valor))

        conexao.commit()
        conexao.close()

        return redirect(url_for("ordens_servico"))

    lista_equipamentos = conexao.execute("""
    SELECT
        equipamentos.id,
        equipamentos.tipo,
        equipamentos.marca,
        equipamentos.modelo,
        equipamentos.numero_serie,
        clientes.nome AS nome_cliente,
        clientes.telefone AS telefone_cliente
    FROM equipamentos
    JOIN clientes ON equipamentos.cliente_id = clientes.id
    ORDER BY clientes.nome
""").fetchall()

    pesquisa = request.args.get("q", "").strip()

    if pesquisa:
        termo = f"%{pesquisa}%"

        lista_ordens = conexao.execute("""
            SELECT
                ordens_servico.*,
                equipamentos.tipo,
                equipamentos.marca,
                equipamentos.modelo,
                clientes.nome AS nome_cliente
            FROM ordens_servico
            JOIN equipamentos
                ON ordens_servico.equipamento_id = equipamentos.id
            JOIN clientes
                ON equipamentos.cliente_id = clientes.id
            WHERE
                CAST(ordens_servico.id AS TEXT) LIKE ?
                OR ('OS-' || printf('%06d', ordens_servico.id)) LIKE ?
                OR clientes.nome LIKE ?
                OR equipamentos.tipo LIKE ?
                OR equipamentos.marca LIKE ?
                OR equipamentos.modelo LIKE ?
            ORDER BY ordens_servico.id DESC
        """, (termo, termo, termo, termo, termo, termo)).fetchall()

    else:
        lista_ordens = conexao.execute("""
            SELECT
                ordens_servico.*,
                equipamentos.tipo,
                equipamentos.marca,
                equipamentos.modelo,
                clientes.nome AS nome_cliente
            FROM ordens_servico
            JOIN equipamentos
                ON ordens_servico.equipamento_id = equipamentos.id
            JOIN clientes
                ON equipamentos.cliente_id = clientes.id
            ORDER BY ordens_servico.id DESC
        """).fetchall()

    conexao.close()

    return render_template(
        "ordens_servico.html",
        equipamentos=lista_equipamentos,
        ordens=lista_ordens
    )



@app.route("/ordens-servico/atualizar-status/<int:ordem_id>", methods=["POST"])
def atualizar_status_os(ordem_id):
    novo_status = request.form.get("status")
    motivo = request.form.get("motivo", "").strip()

    status_permitidos = [
        "Aguardando",
        "Aguardando orçamento",
        "Em andamento",
        "Concluída"
    ]

    if novo_status not in status_permitidos:
        abort(400)

    if not motivo:
        abort(400, description="O motivo da alteração é obrigatório.")

    conexao = conectar()

    ordem = conexao.execute("""
        SELECT id, status
        FROM ordens_servico
        WHERE id = ?
    """, (ordem_id,)).fetchone()

    if ordem is None:
        conexao.close()
        abort(404)

    status_anterior = ordem["status"]

    # Só registra se realmente houve mudança
    if status_anterior != novo_status:

        conexao.execute("""
            INSERT INTO historico_alteracoes (
                ordem_id,
                campo_alterado,
                valor_anterior,
                novo_valor,
                motivo
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            ordem_id,
            "status",
            status_anterior,
            novo_status,
            motivo
        ))

        conexao.execute("""
            UPDATE ordens_servico
            SET status = ?
            WHERE id = ?
        """, (novo_status, ordem_id))

    conexao.commit()
    conexao.close()

    return redirect(url_for("ordens_servico"))


@app.route("/ordens-servico/editar/<int:ordem_id>", methods=["GET", "POST"])
def editar_ordem(ordem_id):

    conexao = conectar()

    ordem = conexao.execute("""
        SELECT
            ordens_servico.*,
            equipamentos.tipo,
            equipamentos.marca,
            equipamentos.modelo,
            equipamentos.numero_serie,
            clientes.nome AS nome_cliente
        FROM ordens_servico
        JOIN equipamentos
            ON ordens_servico.equipamento_id = equipamentos.id
        JOIN clientes
            ON equipamentos.cliente_id = clientes.id
        WHERE ordens_servico.id = ?
    """, (ordem_id,)).fetchone()

    if ordem is None:
        conexao.close()
        abort(404)

    if request.method == "POST":

        problema = request.form.get("problema", "").strip()
        diagnostico = request.form.get("diagnostico", "").strip()
        valor_texto = request.form.get("valor", "").strip()
        status = request.form.get("status", "").strip()
        motivo = request.form.get("motivo", "").strip()

        status_permitidos = [
            "Aguardando",
            "Aguardando orçamento",
            "Em andamento",
            "Concluída"
        ]

        if not problema or not motivo or status not in status_permitidos:
            conexao.close()
            return "Preencha o problema, o motivo e selecione um status válido.", 400

        try:
            valor = float(valor_texto.replace(",", "."))
            if valor < 0:
                raise ValueError
        except ValueError:
            conexao.close()
            return "Informe um valor válido e não negativo.", 400

        alteracoes = []

        campos = {
            "Problema": (ordem["problema"], problema),
            "Diagnóstico": (ordem["diagnostico"] or "", diagnostico),
            "Valor": (str(ordem["valor"]), str(valor)),
            "Status": (ordem["status"], status)
        }

        for campo, (anterior, novo) in campos.items():
            if anterior != novo:
                alteracoes.append((campo, anterior, novo))

        if alteracoes:
            for campo, anterior, novo in alteracoes:
                conexao.execute("""
                    INSERT INTO historico_alteracoes (
                        ordem_id,
                        campo_alterado,
                        valor_anterior,
                        novo_valor,
                        motivo
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (ordem_id, campo, anterior, novo, motivo))

            conexao.execute("""
                UPDATE ordens_servico
                SET problema = ?,
                    diagnostico = ?,
                    valor = ?,
                    status = ?
                WHERE id = ?
            """, (problema, diagnostico, valor, status, ordem_id))

            conexao.commit()

        conexao.close()
        return redirect(url_for("ordens_servico"))

    conexao.close()

    return render_template("editar_ordem.html", ordem=ordem)

@app.route("/historico")
def historico():

    conexao = conectar()

    registros = conexao.execute("""
        SELECT
            'ordem' AS tipo_registro,
            historico_alteracoes.id AS id_registro,
            ordens_servico.id AS numero_ordem,
            clientes.nome AS nome_cliente,
            historico_alteracoes.campo_alterado,
            historico_alteracoes.valor_anterior,
            historico_alteracoes.novo_valor,
            historico_alteracoes.motivo,
            historico_alteracoes.responsavel,
            historico_alteracoes.data_alteracao AS data_evento
        FROM historico_alteracoes
        JOIN ordens_servico
            ON historico_alteracoes.ordem_id = ordens_servico.id
        JOIN equipamentos
            ON ordens_servico.equipamento_id = equipamentos.id
        JOIN clientes
            ON equipamentos.cliente_id = clientes.id

        UNION ALL

        SELECT
            'cliente' AS tipo_registro,
            id AS id_registro,
            NULL AS numero_ordem,
            nome_cliente,
            evento AS campo_alterado,
            '-' AS valor_anterior,
            '-' AS novo_valor,
            'Exclusão de cadastro de cliente' AS motivo,
            responsavel,
            data_evento
        FROM historico_clientes

        ORDER BY data_evento DESC
    """).fetchall()

    conexao.close()

    return render_template(
        "historico.html",
        registros=registros
    )

if __name__ == "__main__":
    app.run(debug=True)
