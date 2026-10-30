import hashlib
import hmac
import json
import secrets
import tkinter as tk
from pathlib import Path
from tkinter import messagebox


ACCOUNT = Path(__file__).resolve().parent / 'data' / 'cuenta.json'


def password_hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                               bytes.fromhex(salt), 600_000).hex()


def create_account(username, password, path=ACCOUNT):
    username = username.strip()
    if not username or len(password) < 8:
        raise ValueError('Escribe un usuario y una contraseña de al menos 8 caracteres.')
    salt = secrets.token_hex(16)
    account = {'usuario': username, 'salt': salt,
               'hash': password_hash(password, salt)}
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as handle:
        json.dump(account, handle)


def authenticate(username, password, path=ACCOUNT):
    with Path(path).open(encoding='utf-8') as handle:
        account = json.load(handle)
    candidate = password_hash(password, account['salt'])
    return (hmac.compare_digest(candidate, account['hash'])
            and username.strip() == account['usuario'])


class LoginApp:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.first_use = not ACCOUNT.exists()
        root.title('DriveGuard AI | Acceso')
        root.geometry('440x420')
        root.minsize(440, 420)
        root.configure(bg='#E9EEF5')
        self.frame = tk.Frame(root, bg='#FFFFFF', padx=30, pady=25)
        self.frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.label('DriveGuard AI', 22)
        self.label('Crear cuenta local' if self.first_use else 'Iniciar sesión', 13)
        self.label('Usuario')
        self.username = tk.Entry(self.frame, font=('Segoe UI', 12))
        self.username.pack(fill='x', pady=(0, 10))
        self.label('Contraseña')
        self.password = tk.Entry(self.frame, show='*', font=('Segoe UI', 12))
        self.password.pack(fill='x', pady=(0, 15))
        tk.Button(self.frame, text='Crear cuenta' if self.first_use else 'Entrar',
                  command=self.submit, bg='#2563EB', fg='white',
                  font=('Segoe UI', 11, 'bold'), pady=8).pack(fill='x')
        self.label('Cuenta local de demostración.', 10)
        self.password.bind('<Return>', lambda _event: self.submit())
        self.username.focus_set()

    def label(self, text, size=11):
        tk.Label(self.frame, text=text, bg='#FFFFFF', fg='#1E2A3A',
                 font=('Segoe UI', size)).pack(anchor='w', pady=(0, 8))

    def submit(self):
        username = self.username.get()
        password = self.password.get()
        try:
            if self.first_use:
                create_account(username, password)
                self.first_use = False
            elif not authenticate(username, password):
                self.password.delete(0, tk.END)
                messagebox.showerror('Acceso denegado', 'Usuario o contraseña incorrectos.')
                return
        except FileExistsError:
            messagebox.showerror('Cuenta existente',
                                 'Ya existe una cuenta. Cierra y vuelve a abrir la aplicación.')
            return
        except (OSError, ValueError, KeyError, TypeError):
            messagebox.showerror('No se pudo acceder',
                                 'Revisa los datos (mínimo 8 caracteres de contraseña), '
                                 'el archivo de cuenta y los permisos de la carpeta data.')
            return
        self.password.delete(0, tk.END)
        self.frame.destroy()
        self.on_success()
