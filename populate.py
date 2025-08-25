import sqlite3
import random

DATABASE = "apple.db"

# --- Conectar banco ---
def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

def popular_banco():
    conn = get_db()
    cursor = conn.cursor()

    # -----------------------
    # Criar 27 alunos
    # -----------------------
    nomes_alunos = [
        "Ana Reis", "Bruno Pires", "Carlos Santos", "Daniela Oliveira", "Eduardo Glória", "Fernanda Cruz", "Gabriel Santos", "Karem Almeida", "Igor Ribeiro",
        "Joana Silva", "Cleber Souza", "Larissa Pereira", "Marcos Leite", "Natália Machado", "Miguel Silva", "Samuel Lima", "Enzo Gomes", "Sophia Santos",
        "Manuela Ferreira", "Beatriz Pinto", "Sophia Santos", "Lorenzo Ribeiro", "Davi Souza", "Arthur Santos", "Guilherme Costa", "Valentina Souza", "Júlia Alves"
    ]

    for nome in nomes_alunos:
        cursor.execute("""
        INSERT OR IGNORE INTO usuarios (nome,email,senha,tipo)
        VALUES (?,?,?,?)
        """, (nome, f"{nome.lower()}@escolamateamargo.rs.gov.br", "123", "aluno"))

    # -----------------------
    # Criar 15 livros de literatura brasileira
    # -----------------------
    livros_brasileiros = [
        ("Dom Casmurro", "Machado de Assis", 1899),
        ("Memórias Póstumas de Brás Cubas", "Machado de Assis", 1881),
        ("O Guarani", "José de Alencar", 1857),
        ("Iracema", "José de Alencar", 1865),
        ("Senhora", "José de Alencar", 1875),
        ("O Cortiço", "Aluísio Azevedo", 1890),
        ("Triste Fim de Policarpo Quaresma", "Lima Barreto", 1915),
        ("Capitães da Areia", "Jorge Amado", 1937),
        ("Gabriela, Cravo e Canela", "Jorge Amado", 1958),
        ("Grande Sertão: Veredas", "Guimarães Rosa", 1956),
        ("A Moreninha", "Joaquim Manuel de Macedo", 1844),
        ("Macunaíma", "Mário de Andrade", 1928),
        ("Marília de Dirceu", "Tomás Antônio Gonzaga", 1792),
        ("Claro Enigma", "Carlos Drummond de Andrade", 1951),
        ("Poemas escolhidos", "Cecília Meireles", 1940)
    ]

    for titulo, autor, ano in livros_brasileiros:
        cursor.execute("""
        INSERT OR IGNORE INTO livros (titulo, autor, ano) VALUES (?,?,?)
        """, (titulo, autor, ano))

    # -----------------------
    # Criar 23 livros diversos
    # -----------------------
    livros_diversos = [
        ("Harry Potter e a Pedra Filosofal", "J.K. Rowling", 1997),
        ("O Senhor dos Anéis", "J.R.R. Tolkien", 1954),
        ("1984", "George Orwell", 1949),
        ("A Revolução dos Bichos", "George Orwell", 1945),
        ("O Hobbit", "J.R.R. Tolkien", 1937),
        ("Admirável Mundo Novo", "Aldous Huxley", 1932),
        ("A Menina que Roubava Livros", "Markus Zusak", 2005),
        ("O Código Da Vinci", "Dan Brown", 2003),
        ("Anjos e Demônios", "Dan Brown", 2000),
        ("O Alquimista", "Paulo Coelho", 1988),
        ("Onze Minutos", "Paulo Coelho", 2003),
        ("O Pequeno Príncipe", "Antoine de Saint-Exupéry", 1943),
        ("Percy Jackson e o Ladrão de Raios", "Rick Riordan", 2005),
        ("Jogos Vorazes", "Suzanne Collins", 2008),
        ("Em Chamas", "Suzanne Collins", 2009),
        ("A Esperança", "Suzanne Collins", 2010),
        ("Crepúsculo", "Stephenie Meyer", 2005),
        ("Lua Nova", "Stephenie Meyer", 2006),
        ("Eclipse", "Stephenie Meyer", 2007),
        ("Amanhecer", "Stephenie Meyer", 2008),
        ("It - A Coisa", "Stephen King", 1986),
        ("O Iluminado", "Stephen King", 1977),
        ("Misery", "Stephen King", 1987)
    ]

    for titulo, autor, ano in livros_diversos:
        cursor.execute("""
        INSERT OR IGNORE INTO livros (titulo, autor, ano) VALUES (?,?,?)
        """, (titulo, autor, ano))

    # -----------------------
    # Criar movimentação para ranking
    # -----------------------
    cursor.execute("SELECT id_usuario FROM usuarios")
    alunos_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id_livro FROM livros")
    livros_ids = [row[0] for row in cursor.fetchall()]

    for aluno in alunos_ids:
        # Cada aluno lê entre 1 e 5 livros
        livros_lidos = random.sample(livros_ids, random.randint(1, 5))
        pontos = len(livros_lidos) * 10
        nivel = (pontos // 50) + 1

        cursor.execute("""
        INSERT OR REPLACE INTO ranking (id_usuario, pontos, nivel)
        VALUES (?,?,?)
        """, (aluno, pontos, nivel))

    conn.commit()
    conn.close()
    print("✅ Banco populado com alunos, livros e ranking!")

if __name__ == "__main__":
    popular_banco()
