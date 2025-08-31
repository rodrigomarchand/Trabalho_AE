from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
import os
from functools import wraps
from flask import abort


app = Flask(__name__, template_folder="templates", static_folder="static")

# 🔑 DEFINIR A SECRET KEY
# Pode ser uma chave fixa:
# app.secret_key = "minha_chave_super_secreta_123"

# ou pode ser gerada aleatória a cada execução (não mantém sessão após restart):
app.secret_key = os.urandom(24)

DATABASE = "apple.db"

'''
    Para rodar, abrir o terminal e inserir: python app.py
    no navegador ficará disponível para receber novas requisições

'''

# Decorador para checar permissões
def requires_tipo(*tipos):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_tipo" not in session:
                return redirect(url_for("login_page"))
            if session["user_tipo"] not in tipos:
                return render_template("sem_permissao.html", permissoes=tipos), 403
            return f(*args, **kwargs)
        return decorated_function
    return wrapper


# --- Função para conectar ao banco ---
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Criação das tabelas ---
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        tipo TEXT CHECK(tipo IN ('aluno','professor','pai')) NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS livros (
        id_livro INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        ano INTEGER,
        disponivel INTEGER DEFAULT 1
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emprestimos (
        id_emprestimo INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER NOT NULL,
        id_livro INTEGER NOT NULL,
        data_retirada DATE DEFAULT CURRENT_DATE,
        data_devolucao DATE,
        status TEXT CHECK(status IN ('ativo','devolvido')) DEFAULT 'ativo',
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
        FOREIGN KEY (id_livro) REFERENCES livros(id_livro)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ranking (
        id_ranking INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER NOT NULL,
        pontos INTEGER DEFAULT 0,
        nivel INTEGER DEFAULT 1,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    );
    """)

    conn.commit()
    conn.close()

# -------------------------------
#           ENDPOINTS
# -------------------------------

# @app.route("/")
# def home():
#     return "🚀 AppLê funcionando com Flask + SQLite!"

# --- Usuários ---
@app.route("/usuarios", methods=["POST"])
def add_usuario():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nome,email,senha,tipo) VALUES (?,?,?,?)",
                   (data["nome"], data["email"], data["senha"], data["tipo"]))
    conn.commit()
    return jsonify({"msg": "Usuário cadastrado com sucesso!"})

@app.route("/usuarios", methods=["GET"])
def get_usuarios():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id_usuario, nome, email, tipo FROM usuarios")
    usuarios = [dict(row) for row in cursor.fetchall()]
    return jsonify(usuarios)

# --- Livros ---
@app.route("/livros", methods=["POST"])
def add_livro():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO livros (titulo,autor,ano) VALUES (?,?,?)",
                   (data["titulo"], data["autor"], data.get("ano")))
    conn.commit()
    return jsonify({"msg": "Livro cadastrado com sucesso!"})

@app.route("/livros", methods=["GET"])
def get_livros():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livros")
    livros = [dict(row) for row in cursor.fetchall()]
    return jsonify(livros)

# --- Empréstimos ---
@app.route("/emprestimos", methods=["POST"])
def add_emprestimo():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    # Verifica se o livro está disponível
    cursor.execute("SELECT disponivel FROM livros WHERE id_livro = ?", (data["id_livro"],))
    livro = cursor.fetchone()
    if livro and livro["disponivel"] == 0:
        return jsonify({"msg": "Livro indisponível!"}), 400

    # Registra empréstimo
    cursor.execute("INSERT INTO emprestimos (id_usuario,id_livro) VALUES (?,?)",
                   (data["id_usuario"], data["id_livro"]))
    # Atualiza status do livro
    cursor.execute("UPDATE livros SET disponivel = 0 WHERE id_livro = ?", (data["id_livro"],))
    conn.commit()
    return jsonify({"msg": "Empréstimo registrado com sucesso!"})

@app.route("/emprestimos", methods=["GET"])
def get_emprestimos():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id_emprestimo, u.nome AS usuario, l.titulo AS livro, e.data_retirada, e.status
        FROM emprestimos e
        JOIN usuarios u ON e.id_usuario = u.id_usuario
        JOIN livros l ON e.id_livro = l.id_livro
    """)
    emprestimos = [dict(row) for row in cursor.fetchall()]
    return jsonify(emprestimos)

# --- Devolução de livro ---
@app.route("/devolver/<int:id_emprestimo>", methods=["PUT"])
def devolver_livro(id_emprestimo):
    conn = get_db()
    cursor = conn.cursor()

    # Busca o empréstimo
    cursor.execute("SELECT id_usuario, id_livro, status FROM emprestimos WHERE id_emprestimo = ?", (id_emprestimo,))
    emprestimo = cursor.fetchone()

    if not emprestimo:
        return jsonify({"msg": "Empréstimo não encontrado!"}), 404
    if emprestimo["status"] == "devolvido":
        return jsonify({"msg": "Livro já devolvido!"}), 400

    id_usuario = emprestimo["id_usuario"]
    id_livro = emprestimo["id_livro"]

    # Atualiza status do empréstimo
    cursor.execute("UPDATE emprestimos SET status='devolvido', data_devolucao=CURRENT_DATE WHERE id_emprestimo = ?", (id_emprestimo,))
    # Atualiza livro como disponível
    cursor.execute("UPDATE livros SET disponivel=1 WHERE id_livro = ?", (id_livro,))

    # Atualiza ranking (10 pontos por devolução)
    cursor.execute("SELECT * FROM ranking WHERE id_usuario = ?", (id_usuario,))
    rank = cursor.fetchone()

    if rank:
        novos_pontos = rank["pontos"] + 10
        novo_nivel = (novos_pontos // 50) + 1  # sobe nível a cada 50 pontos
        cursor.execute("UPDATE ranking SET pontos=?, nivel=? WHERE id_usuario=?",
                       (novos_pontos, novo_nivel, id_usuario))
    else:
        cursor.execute("INSERT INTO ranking (id_usuario, pontos, nivel) VALUES (?,?,?)",
                       (id_usuario, 10, 1))

    conn.commit()
    conn.close()

    return jsonify({"msg": "Livro devolvido e pontos atualizados com sucesso!"})


# MOSTRA TOP 10
@app.route("/ranking", methods=["GET"])
def get_ranking():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id_usuario, u.nome AS nome, r.pontos, r.nivel
        FROM ranking r
        JOIN usuarios u ON r.id_usuario = u.id_usuario
        WHERE u.tipo = 'aluno'
        ORDER BY r.pontos DESC
        LIMIT 10
    """)
    ranking = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(ranking)


@app.route("/estatisticas", methods=["GET"])
def get_estatisticas():
    conn = get_db()
    cursor = conn.cursor()

    # Quantidade de alunos
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo='aluno'")
    total_alunos = cursor.fetchone()[0]

    # Quantidade de livros
    cursor.execute("SELECT COUNT(*) FROM livros")
    total_livros = cursor.fetchone()[0]

    # Quantidade de empréstimos
    cursor.execute("SELECT COUNT(*) FROM emprestimos")
    total_emprestimos = cursor.fetchone()[0]

    # Pontos totais acumulados
    cursor.execute("SELECT SUM(pontos) FROM ranking")
    total_pontos = cursor.fetchone()[0] or 0

    conn.close()

    return jsonify({
        "total_alunos": total_alunos,
        "total_livros": total_livros,
        "total_emprestimos": total_emprestimos,
        "total_pontos": total_pontos
    })

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Páginas ---
# @app.route("/")
# def home():
#     return redirect(url_for("login_page"))

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard_page"))  # Logado → Dashboard
    else:
        return redirect(url_for("login_page"))      # Não logado → Login

# @app.route("/login", methods=["GET", "POST"])
# def login_page():
#     if request.method == "POST":
#         email = request.form.get("email")
#         senha = request.form.get("senha")

#         conn = get_db()
#         c = conn.cursor()
#         c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
#         user = c.fetchone()
#         conn.close()

#         if user:
#             session["user_id"] = user["id_usuario"]
#             session["user_nome"] = user["nome"]
#             session["user_tipo"] = user["tipo"]
#             return redirect(url_for("ranking_page"))
#         else:
#             return render_template("login.html", erro="Credenciais inválidas")

#     return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id_usuario"]
            session["user_nome"] = user["nome"]
            session["user_tipo"] = user["tipo"]
            # Alterar para redirecionar para a dashboard em vez do ranking
            return redirect(url_for("dashboard_page"))  # ← MUDANÇA AQUI
        else:
            return render_template("login.html", erro="Credenciais inválidas")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))

@app.route("/livros/cadastrar")
@requires_tipo("professor")   # só professores podem cadastrar
def cadastrar_livros_page():
    return render_template("livros_cadastrar.html")


@app.route("/livros/listar", methods=["GET"])
@requires_tipo("aluno", "professor")  # só ALUNO e PROFESSOR
def listar_livros_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("livros_listar.html")

@app.route("/ranking/page", methods=["GET"])
def ranking_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("ranking.html")

@app.route("/usuarios_sessao")
def usuario_sessao():
    if "user_id" not in session:
        return jsonify({})
    return jsonify({
        "id_usuario": session["user_id"],
        "nome": session["user_nome"],
        "tipo": session["user_tipo"]
    })

@app.route("/meus-emprestimos")
@requires_tipo("aluno", "professor")  # alunos e professores podem acessar
def meus_emprestimos_page():
    return render_template("meus_emprestimos.html")

@app.route("/meu_ranking", methods=["GET"])
def meu_ranking():
    if "user_id" not in session:
        return jsonify({"msg": "Não logado"}), 401

    conn = get_db()
    cursor = conn.cursor()

    # Pega todos os usuários ordenados por pontos
    cursor.execute("""
        SELECT r.id_usuario, u.nome, r.pontos, r.nivel
        FROM ranking r
        JOIN usuarios u ON r.id_usuario = u.id_usuario
        ORDER BY r.pontos DESC
    """)
    todos = cursor.fetchall()

    posicao = None
    dados = None
    for idx, row in enumerate(todos, start=1):
        if row["id_usuario"] == session["user_id"]:
            posicao = idx
            dados = dict(row)
            break

    conn.close()

    if dados:
        return jsonify({"posicao": posicao, "nome": dados["nome"], "pontos": dados["pontos"], "nivel": dados["nivel"]})
    else:
        return jsonify({"msg": "Usuário não está no ranking"}), 404


@app.route("/usuarios/cadastrar", methods=["GET", "POST"])
@requires_tipo("professor")  # Apenas professores podem cadastrar novos usuários
def cadastrar_usuario_page():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        tipo = request.form.get("tipo")

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (nome,email,senha,tipo) VALUES (?,?,?,?)",
                           (nome, email, senha, tipo))
            conn.commit()
            msg = "Usuário cadastrado com sucesso!"
        except Exception as e:
            msg = f"Erro: {str(e)}"
        conn.close()
        return render_template("usuarios_cadastrar.html", msg=msg)

    return render_template("usuarios_cadastrar.html")

# --- Inicialização do banco ---
if __name__ == "__main__":
    init_db()
    app.run(debug=True)