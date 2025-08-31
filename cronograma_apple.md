
# 📅 Cronograma de Implementação - Projeto AppLê

Este cronograma organiza o desenvolvimento do MVP em **sprints semanais**, alinhando os objetivos do projeto com o código existente e os pontos a implementar.

---

## 🚀 Sprint 1 - Estrutura Básica e Usuários (Semana 1)
- [x] Configuração inicial do projeto Flask + SQLite.
- [x] Criação do banco de dados e tabelas (`usuarios`, `livros`, `emprestimos`, `ranking`).
- [ ] Implementar **hash de senhas** (bcrypt/werkzeug.security).
- [ ] Criar funcionalidade de recuperação de senha.
- [ ] Melhorar sessão do usuário (cookies seguros).

**Entregáveis:**
- Cadastro/login seguro de usuários.
- Diferenciação clara entre `aluno`, `professor` e `pai`.

---

## 📖 Sprint 2 - Biblioteca e Empréstimos (Semana 2)
- [x] Cadastro de livros com título, autor e ano.
- [x] Controle de disponibilidade de livros.
- [x] Registro de empréstimos e devoluções.
- [ ] Implementar **prazo de devolução** (7 dias).
- [ ] Notificação de livros atrasados (visual/email).
- [ ] Adicionar categorias/assuntos aos livros.
- [ ] Criar busca de livros por título/autor/categoria.

**Entregáveis:**
- Sistema completo de gerenciamento de acervo.
- Histórico de empréstimos por usuário.

---

## 🏆 Sprint 3 - Gamificação (Semana 3)
- [x] Ranking básico por pontos.
- [ ] Regras avançadas de pontuação:
  - +10 pontos por devolução no prazo.
  - +5 pontos por avaliação de livro.
  - +15 pontos por devolução antecipada.
- [ ] Implementar conquistas/medalhas (ex.: "Primeiro Livro", "Leitor Frequente").
- [ ] Criar ranking mensal e por escola.

**Entregáveis:**
- Ranking dinâmico e motivador.
- Sistema de conquistas para aumentar engajamento.

---

## 📊 Sprint 4 - Relatórios e Estatísticas (Semana 4)
- [x] Estatísticas básicas (alunos, livros, empréstimos, pontos).
- [ ] Relatórios detalhados:
  - Top 5 livros mais lidos.
  - Usuários mais ativos do mês.
  - Empréstimos atrasados.
- [ ] Criar dashboard interativo em HTML/JS (Chart.js ou Recharts).

**Entregáveis:**
- Relatórios para escolas e professores.
- Visualização gráfica em dashboard.

---

## 🎨 Sprint 5 - Front-end e Experiência do Usuário (Semana 5)
- [ ] Criar páginas HTML responsivas (Bootstrap/Tailwind):
  - Login/Logout.
  - Biblioteca (listar e buscar livros).
  - Ranking visual (medalhas e níveis).
  - Estatísticas (gráficos).
- [ ] Melhorar usabilidade no celular.

**Entregáveis:**
- Interface amigável e intuitiva.
- Aplicação acessível via desktop e mobile.

---

## 🔐 Sprint 6 - Segurança e Ajustes Finais (Semana 6)
- [ ] Revisar segurança (inputs, SQL Injection, XSS).
- [ ] Proteger endpoints com `@requires_tipo`.
- [ ] Revisar e documentar o código.
- [ ] Testes finais (unitários e manuais).

**Entregáveis:**
- Aplicação segura e estável.
- MVP pronto para testes em ambiente escolar.

---

# ✅ Resumo Final
- **Total de sprints:** 6 (6 semanas).
- **Foco inicial:** Estrutura + Usuários.
- **Foco intermediário:** Biblioteca e Gamificação.
- **Foco final:** Relatórios, Front-end e Segurança.

O resultado será um MVP funcional, seguro e engajador, pronto para validação em escolas.
