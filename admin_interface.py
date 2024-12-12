import tkinter as tk
from tkinter import ttk, messagebox
import requests
import webbrowser

# URL base do backend
BASE_URL = "http://127.0.0.1:5000"

# Função para centralizar a janela
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

# Função para exibir mensagens de erro
def show_error(message):
    messagebox.showerror("Erro", message)

# Classe Inicial
class InitialInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Biblioteca - Bem-vindo")
        center_window(self.root, 400, 300)

        # Título
        title_label = tk.Label(root, text="Bem-vindo à Biblioteca", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        # Botões para Registro, Login e OAuth
        login_button = tk.Button(root, text="Login", width=20, command=self.open_login)
        login_button.pack(pady=10)

        register_button = tk.Button(root, text="Registrar-se", width=20, command=self.open_register)
        register_button.pack(pady=10)

    def open_login(self):
        self.root.destroy()
        root = tk.Tk()
        LoginWindow(root)
        root.mainloop()

    def open_register(self):
        self.root.destroy()
        root = tk.Tk()
        RegisterWindow(root)
        root.mainloop()

# Classe de Registro
class RegisterWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Registro - Biblioteca")
        center_window(self.root, 400, 300)

        # Título
        title_label = tk.Label(root, text="Registrar-se", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        # Campos de Registro
        tk.Label(root, text="Utilizador:").pack(pady=5)
        self.username_entry = tk.Entry(root, width=30)
        self.username_entry.pack(pady=5)

        tk.Label(root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(root, width=30, show="*")
        self.password_entry.pack(pady=5)

        tk.Label(root, text="E-mail:").pack(pady=5)
        self.email_entry = tk.Entry(root, width=30)
        self.email_entry.pack(pady=5)

        # Botão de Registro
        register_button = tk.Button(root, text="Registrar", width=20, command=self.register)
        register_button.pack(pady=10)

        # Botão de Voltar
        back_button = tk.Button(root, text="Voltar", width=20, command=self.go_back)
        back_button.pack(pady=5)

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()

        if not username or not password or not email:
            show_error("Todos os campos são obrigatórios.")
            return

        try:
            response = requests.post(f"{BASE_URL}/register", json={
                "username": username,
                "password": password,
                "email": email
            })
            if response.status_code == 201:
                messagebox.showinfo("Sucesso", "Registro realizado com sucesso! Verifique o seu e-mail para o ver o código MFA.")
                self.go_back()
            else:
                show_error(response.json().get("error", "Erro ao registrar."))
        except requests.RequestException as e:
            show_error(f"Erro de conexão: {e}")

    def go_back(self):
        self.root.destroy()
        root = tk.Tk()
        InitialInterface(root)
        root.mainloop()

# Classe de Login
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Biblioteca")
        center_window(self.root, 400, 350)

        # Título
        title_label = tk.Label(root, text="Login", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        # Campos de Login Normal
        tk.Label(root, text="Utilizador:").pack(pady=5)
        self.username_entry = tk.Entry(root, width=30)
        self.username_entry.pack(pady=5)

        tk.Label(root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(root, width=30, show="*")
        self.password_entry.pack(pady=5)

        tk.Label(root, text="Código MFA:").pack(pady=5)
        self.mfa_entry = tk.Entry(root, width=30)
        self.mfa_entry.pack(pady=5)

        # Botão de Login Normal
        login_button = tk.Button(root, text="Login", width=20, command=self.login)
        login_button.pack(pady=10)
        
        # Botão de Login com GitHub (OAuth)
        github_button = tk.Button(root, text="Login com GitHub", width=20, command=self.github_login)
        github_button.pack(pady=5)

        # Botão de Voltar
        back_button = tk.Button(root, text="Voltar", width=20, command=self.go_back)
        back_button.pack(pady=5)

    def login(self):
        """Login usando username, password e MFA."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        mfa_code = self.mfa_entry.get()

        if not username or not password or not mfa_code:
            show_error("Por favor, preencha todos os campos.")
            return

        try:
            response = requests.post(f"{BASE_URL}/login", json={
                "username": username,
                "password": password,
                "mfa_code": mfa_code
            })
            if response.status_code == 200:
                messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
                self.open_admin_interface()
            else:
                show_error(response.json().get("error", "Erro ao fazer login."))
        except requests.RequestException as e:
            show_error(f"Erro de conexão: {e}")
        
    def github_login(self):
        """Inicia o fluxo de login via GitHub OAuth."""
        try:
            webbrowser.open(f"{BASE_URL}/login")
            messagebox.showinfo("Login GitHub", "Conclua o login no navegador.")
            # Inicia apenas uma verificação
            if not hasattr(self, "_github_check_in_progress") or not self._github_check_in_progress:
                self._github_check_in_progress = True
                self.check_github_login()
        except Exception as e:
            show_error(f"Erro ao iniciar login GitHub: {e}")

    def check_github_login(self):
        """Verifica se o login via GitHub foi concluído e abre a interface administrativa."""
        try:
            # Faz uma chamada para o endpoint do backend para verificar a autenticação
            response = requests.get(f"{BASE_URL}/github-success")
            print("Resposta do servidor:", response.json())
            if response.status_code == 200:
                # Decodifica a resposta JSON
                data = response.json()
                user_data = data.get("user", {})
                username = user_data.get("username", "Utilizador")
                print("Utilizador autenticado:", username)
                # Exibe mensagem de sucesso
                messagebox.showinfo("Sucesso", f"Login realizado como {username}!")
                print("Abrindo a interface administrativa...")
                self._github_check_in_progress = False  # Finaliza a verificação
                self.open_admin_interface()
            else:
                print("Login ainda não concluído. Tentando novamente...")
                self.root.after(5000, self.check_github_login)
        except requests.RequestException as e:
            print(f"Erro de conexão ao verificar login: {e}")
            show_error(f"Erro de conexão: {e}")
            self._github_check_in_progress = False  # Finaliza a verificação
        except Exception as e:
            print(f"Erro inesperado: {e}")
            self._github_check_in_progress = False  # Finaliza a verificação
            
    def stop_github_check(self):
        """Interrompe a verificação do login via GitHub."""
        if hasattr(self, "_github_check_in_progress") and self._github_check_in_progress:
            self._github_check_in_progress = False        

    def go_back(self):
        """Volta para a interface inicial."""
        self.root.destroy()
        root = tk.Tk()
        InitialInterface(root)
        root.mainloop()

    def open_admin_interface(self):
        """Abre a interface administrativa."""
        self.root.destroy()
        root = tk.Tk()
        AdminInterface(root)
        root.mainloop()


# Classe principal para a interface administrativa
class AdminInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Interface Administrativa - Biblioteca")
        center_window(self.root, 500, 400)

        # Título
        title_label = tk.Label(
            root, text="Interface Administrativa", font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)

        # Botões
        books_button = tk.Button(root, text="Gestão de Livros", width=20, command=self.open_books_window)
        books_button.pack(pady=5)

        users_button = tk.Button(root, text="Gestão de  Utilizadores", width=20, command=self.open_users_window)
        users_button.pack(pady=5)

        loans_button = tk.Button(root, text="Gestão de Empréstimos", width=20, command=self.open_loans_window)
        loans_button.pack(pady=5)

        external_books_button = tk.Button(root, text="Pesquisar Livros Externos", width=20, command=self.open_external_books_window)
        external_books_button.pack(pady=5)

        reports_button = tk.Button(root, text="Relatórios de Atividades", width=20, command=self.open_reports_window)
        reports_button.pack(pady=5)
        
        exit_button = tk.Button(root, text="Sair", width=20, command=self.root.quit)
        exit_button.pack(pady=20)

    # Métodos para abrir as opções de gestão
    def open_books_window(self):
        BooksWindow(self.root)

    def open_users_window(self):
        UsersWindow(self.root)

    def open_loans_window(self):
        LoansWindow(self.root)

    def open_external_books_window(self):
        ExternalBooksWindow(self.root)

    def open_reports_window(self):
        ReportsWindow(self.root)


# Classe para gestão de livros
class BooksWindow:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Gerenciar Livros")
        center_window(self.window, 600, 400)

        # Tabela de livros
        self.tree = ttk.Treeview(self.window, columns=("ID", "Título", "Autor"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Autor", text="Autor")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Botões
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)
        
        add_book_button = tk.Button(button_frame, text="Inserir Livro", command=self.add_book)
        add_book_button.pack(side=tk.LEFT, padx=5)

        refresh_button = tk.Button(button_frame, text="Atualizar", command=self.load_books)
        refresh_button.pack(side=tk.LEFT, padx=5)

        # Carregar os livros ao abrir o menu
        self.load_books()

    def load_books(self):
        try:
            response = requests.get(f"{BASE_URL}/books")
            response.raise_for_status()
            books = response.json()

            # Limpar a tabela
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Adicionar os livros
            for book in books:
                self.tree.insert("", "end", values=(book["id"], book["titulo"], book["autor"]))
        except requests.RequestException as e:
            show_error(f"Erro ao carregar livros: {e}")
            
    def add_book(self):
        """Abre a janela para adicionar um novo livro."""
        add_window = tk.Toplevel(self.window)
        add_window.title("Adicionar Livro")
        center_window(add_window, 300, 200)

        tk.Label(add_window, text="Título do Livro:").pack(pady=5)
        title_entry = tk.Entry(add_window, width=30)
        title_entry.pack(pady=5)

        tk.Label(add_window, text="Autor:").pack(pady=5)
        author_entry = tk.Entry(add_window, width=30)
        author_entry.pack(pady=5)

        def submit_book():
            title = title_entry.get()
            author = author_entry.get()
            if not title or not author:
                show_error("Todos os campos são obrigatórios!")
                return
            try:
                response = requests.post(f"{BASE_URL}/books", json={"titulo": title, "autor": author})
                if response.status_code == 201:
                    messagebox.showinfo("Sucesso", "Livro adicionado com sucesso!")
                    self.load_books()
                    add_window.destroy()
                else:
                    show_error(response.json().get("error", "Erro ao adicionar livro."))
            except requests.RequestException as e:
                show_error(f"Erro de conexão: {e}")

        tk.Button(add_window, text="Salvar", command=submit_book).pack(pady=10)

# Classe para gestão de utilizadores
class UsersWindow:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Gestão de Utilizadores")
        center_window(self.window, 600, 400)

        # Tabela de utilizadores
        self.tree = ttk.Treeview(self.window, columns=("ID", "Nome", "Email"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Email", text="Email")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Botões
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)
        
        delete_user_button = tk.Button(button_frame, text="Apagar Utilizador", command=self.delete_user)
        delete_user_button.pack(side=tk.LEFT, padx=5)

        refresh_button = tk.Button(button_frame, text="Atualizar", command=self.load_users)
        refresh_button.pack(side=tk.LEFT, padx=5)

        # Carregar os utilizadores ao abrir o menu
        self.load_users()

    def load_users(self):
        try:
            response = requests.get(f"{BASE_URL}/users")
            response.raise_for_status()
            users = response.json()

            # Limpar a tabela
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Adicionar os utilizadores
            for user in users:
                self.tree.insert("", "end", values=(user["id"], user["nome"], user["email"]))
        except requests.RequestException as e:
            show_error(f"Erro ao carregar usuários: {e}")
            
    def delete_user(self):
        """Apaga o utilizador selecionado."""
        selected_item = self.tree.selection()
        if not selected_item:
            show_error("Selecione um utilizador para apagar.")
            return
        user_id = self.tree.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirmação", "Tem certeza que deseja apagar este utilizador?")
        if confirm:
            try:
                response = requests.delete(f"{BASE_URL}/users/{user_id}")
                if response.status_code == 200:
                    messagebox.showinfo("Sucesso", "Utilizador apagado com sucesso!")
                    self.load_users()
                else:
                    show_error(response.json().get("error", "Erro ao apagar utilizador."))
            except requests.RequestException as e:
                show_error(f"Erro de conexão: {e}")

# Classe para gestão de empréstimos
class LoansWindow:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Gestão de Empréstimos")
        center_window(self.window, 800, 400)

        # Tabela de empréstimos
        self.tree = ttk.Treeview(
            self.window, 
            columns=("ID", "Utilizador", "Livro", "Data Empréstimo", "Data Devolução"), 
            show="headings"
        )
        self.tree.heading("ID", text="ID")
        self.tree.heading("Utilizador", text="Utilizador")
        self.tree.heading("Livro", text="Livro")
        self.tree.heading("Data Empréstimo", text="Data Empréstimo")
        self.tree.heading("Data Devolução", text="Data Devolução")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Botões
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)
        
        request_loan_button = tk.Button(button_frame, text="Pedir Livro", command=self.request_loan)
        request_loan_button.pack(side=tk.LEFT, padx=5)

        return_loan_button = tk.Button(button_frame, text="Devolver Livro", command=self.return_loan)
        return_loan_button.pack(side=tk.LEFT, padx=5)

        refresh_button = tk.Button(button_frame, text="Atualizar", command=self.load_loans)
        refresh_button.pack(side=tk.LEFT, padx=5)

        # Carregar os empréstimos ao abrir o menu
        self.load_loans()

    def load_loans(self):
        try:
            response = requests.get(f"{BASE_URL}/loans")
            response.raise_for_status()
            loans = response.json()

            # Limpar a tabela
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Adicionar os empréstimos
            if loans:
                for loan in loans:
                    self.tree.insert(
                        "", 
                        "end", 
                        values=(
                            loan["emprestimo_id"], 
                            loan["utilizador"], 
                            loan["livro"], 
                            loan["data_emprestimo"], 
                            loan["data_devolucao"] or "Não devolvido"
                        )
                    )
            else:
                show_error("Nenhum empréstimo encontrado.")
        except requests.RequestException as e:
            show_error(f"Erro ao carregar empréstimos: {e}")
            
    def request_loan(self):
        """Pede um livro emprestado."""
        request_window = tk.Toplevel(self.window)
        request_window.title("Pedir Livro")
        center_window(request_window, 300, 200)

        tk.Label(request_window, text="ID do Utilizador:").pack(pady=5)
        user_id_entry = tk.Entry(request_window, width=30)
        user_id_entry.pack(pady=5)

        tk.Label(request_window, text="ID do Livro:").pack(pady=5)
        book_id_entry = tk.Entry(request_window, width=30)
        book_id_entry.pack(pady=5)

        def submit_request():
            user_id = user_id_entry.get()
            book_id = book_id_entry.get()
            if not user_id or not book_id:
                show_error("Todos os campos são obrigatórios!")
                return
            try:
                response = requests.post(f"{BASE_URL}/borrow", json={"user_id": user_id, "book_id": book_id})
                if response.status_code == 201:
                    messagebox.showinfo("Sucesso", "Empréstimo registrado com sucesso!")
                    self.load_loans()
                    request_window.destroy()
                else:
                    show_error(response.json().get("error", "Erro ao registrar empréstimo."))
            except requests.RequestException as e:
                show_error(f"Erro de conexão: {e}")

        tk.Button(request_window, text="Pedir", command=submit_request).pack(pady=10)

    def return_loan(self):
        """Devolve um livro emprestado."""
        selected_item = self.tree.selection()
        if not selected_item:
            show_error("Selecione um empréstimo para devolver.")
            return
        loan_id = self.tree.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirmação", "Tem certeza que deseja devolver este livro?")
        if confirm:
            try:
                response = requests.put(f"{BASE_URL}/return", json={"loan_id": loan_id})
                if response.status_code == 200:
                    messagebox.showinfo("Sucesso", "Devolução registrada com sucesso!")
                    self.load_loans()
                else:
                    show_error(response.json().get("error", "Erro ao devolver livro."))
            except requests.RequestException as e:
                show_error(f"Erro de conexão: {e}")

# Classe para pesquisar livros externos
class ExternalBooksWindow:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Pesquisar Livros Externos")
        center_window(self.window, 800, 600)

        # Campo de pesquisa
        self.search_label = tk.Label(self.window, text="Digite o título ou autor do livro:")
        self.search_label.pack(pady=10)

        self.search_entry = tk.Entry(self.window, width=50)
        self.search_entry.pack(pady=5)

        self.search_button = tk.Button(self.window, text="Pesquisar", command=self.search_books)
        self.search_button.pack(pady=5)

        # Tabela para exibir os livros
        self.tree = ttk.Treeview(
            self.window,
            columns=("Título", "Autor"),
            show="headings",
        )
        self.tree.heading("Título", text="Título")
        self.tree.heading("Autor", text="Autor")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

    def search_books(self):
        query = self.search_entry.get()
        if not query:
            show_error("Digite um termo para pesquisar.")
            return

        try:
            response = requests.get(f"{BASE_URL}/external-books", params={"query": query})
            response.raise_for_status()
            books = response.json()

            # Limpar a tabela
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Adicionar os resultados à tabela
            for book in books:
                self.tree.insert("", "end", values=(book.get("title"), book.get("author", "Autor desconhecido")))

        except requests.RequestException as e:
            show_error(f"Erro ao pesquisar livros externos: {e}")

# Classe para exibir relatórios de atividades
class ReportsWindow:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Relatórios de Atividades")
        center_window(self.window, 800, 600)

        self.tree = ttk.Treeview(
            self.window,
            columns=("ID Empréstimo", "Livro", "Utilizador", "Data Empréstimo", "Data Devolução"),
            show="headings"
        )
        self.tree.heading("ID Empréstimo", text="ID Empréstimo")
        self.tree.heading("Livro", text="Livro")
        self.tree.heading("Utilizador", text="Utilizador")
        self.tree.heading("Data Empréstimo", text="Data Empréstimo")
        self.tree.heading("Data Devolução", text="Data Devolução")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        refresh_button = tk.Button(self.window, text="Atualizar", command=self.load_reports)
        refresh_button.pack(pady=10)

        self.load_reports()

    def load_reports(self):
        try:
            response = requests.get(f"{BASE_URL}/reports")
            response.raise_for_status()
            reports = response.json()

            # Limpar a tabela
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Adicionar os relatórios à tabela
            if isinstance(reports, list):
                for report in reports:
                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            report.get("emprestimo_id", "N/A"),
                            report.get("data_emprestimo", "N/A"),
                            report.get("data_devolucao", "N/A"),
                            report.get("utilizador", "N/A"),
                            report.get("livro", "N/A"),
                        ),
                    )
            else:
                # Caso a resposta não seja uma lista
                show_error("Formato inesperado no retorno dos relatórios.")
        except requests.RequestException as e:
            show_error(f"Erro ao carregar relatórios: {e}")
            
    def clear_reports(self):
        """Limpa todos os registros de atividades."""
        confirm = messagebox.askyesno("Confirmação", "Tem certeza que deseja limpar todos os registros?")
        if confirm:
            try:
                response = requests.delete(f"{BASE_URL}/reports")
                if response.status_code == 200:
                    messagebox.showinfo("Sucesso", "Registros limpos com sucesso!")
                    self.load_reports()
                else:
                    show_error(response.json().get("error", "Erro ao limpar registros."))
            except requests.RequestException as e:
                show_error(f"Erro de conexão: {e}")

# Executar a interface
if __name__ == "__main__":
    root = tk.Tk()
    app = InitialInterface(root)
    root.mainloop()
    

