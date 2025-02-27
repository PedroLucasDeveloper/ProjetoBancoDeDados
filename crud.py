# AlUNO: Pedro Lucas Silva dos Santos
# MATRICULA: 554973
#---------------------------------------------------------
# Importação de bibliotecas

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import psycopg2
from datetime import datetime

# Configuração do banco de dados
DATABASE_URL = "postgresql+psycopg2://postgres:@Localhost/BHS_ProjetoFBD"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class UsuarioComum(Base):
    __tablename__ = 'usuariocomum'
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    email = Column(String)
    cpf = Column(String)
    saldo_horas = Column(Float)

class Mensagem(Base):
    __tablename__ = 'mensagem'
    id = Column(Integer, primary_key=True)
    id_emissor = Column(Integer, ForeignKey('usuariocomum.id'))
    id_receptor = Column(Integer, ForeignKey('usuariocomum.id'))
    data_hora = Column(DateTime, default=datetime.utcnow)
    texto = Column(String)
    emissor = relationship("UsuarioComum", foreign_keys=[id_emissor])
    receptor = relationship("UsuarioComum", foreign_keys=[id_receptor])

Base.metadata.create_all(engine)

# Configuração da interface gráfica
root = tk.Tk()
root.title("Gerenciador de Mensagens")
root.geometry("800x600")

def carregar_usuarios():
    usuarios = session.query(UsuarioComum).all()
    return {usuario.nome: usuario.id for usuario in usuarios}

usuarios_dict = carregar_usuarios()

def limpar_campos():
    emissor_combobox.set("")
    receptor_combobox.set("")
    texto_entry.delete(0, tk.END)

def adicionar_mensagem():
    emissor_nome = emissor_combobox.get()
    receptor_nome = receptor_combobox.get()
    texto = texto_entry.get()
    if emissor_nome and receptor_nome and texto:
        id_emissor = usuarios_dict.get(emissor_nome)
        id_receptor = usuarios_dict.get(receptor_nome)
        if id_emissor and id_receptor:
            nova_mensagem = Mensagem(id_emissor=id_emissor, id_receptor=id_receptor, texto=texto)
            session.add(nova_mensagem)
            session.commit()
            messagebox.showinfo("Sucesso", "Mensagem adicionada com sucesso!")
            listar_mensagens()
            limpar_campos()
        else:
            messagebox.showerror("Erro", "Usuário não encontrado")
    else:
        messagebox.showerror("Erro", "Todos os campos são obrigatórios")

def listar_mensagens():
    for row in tree.get_children():
        tree.delete(row)
    mensagens = session.query(Mensagem).all()
    for mensagem in mensagens:
        emissor_nome = mensagem.emissor.nome if mensagem.emissor else "Desconhecido"
        receptor_nome = mensagem.receptor.nome if mensagem.receptor else "Desconhecido"
        tree.insert("", tk.END, values=(mensagem.id, emissor_nome, receptor_nome, mensagem.texto))

def excluir_mensagem():
    selected_item = tree.selection()
    if selected_item:
        mensagem_id = tree.item(selected_item)['values'][0]
        mensagem = session.query(Mensagem).get(mensagem_id)
        if mensagem:
            session.delete(mensagem)
            session.commit()
            messagebox.showinfo("Sucesso", "Mensagem excluída com sucesso!")
            listar_mensagens()
        else:
            messagebox.showerror("Erro", "Mensagem não encontrada")
    else:
        messagebox.showerror("Erro", "Selecione uma mensagem para excluir")

def editar_mensagem():
    selected_item = tree.selection()
    if selected_item:
        mensagem_id = tree.item(selected_item)['values'][0]
        mensagem = session.query(Mensagem).get(mensagem_id)
        if mensagem:
            texto_entry.delete(0, tk.END)
            texto_entry.insert(0, mensagem.texto)
            
            def salvar_edicao():
                mensagem.texto = texto_entry.get()
                session.commit()
                messagebox.showinfo("Sucesso", "Mensagem editada com sucesso!")
                listar_mensagens()
                limpar_campos()
                salvar_edicao_btn.grid_forget()  # Esconde o botão após edição
            
            salvar_edicao_btn = tk.Button(frame, text="Salvar Edição", command=salvar_edicao)
            salvar_edicao_btn.grid(row=6, column=0, columnspan=2, pady=10)
        else:
            messagebox.showerror("Erro", "Mensagem não encontrada")
    else:
        messagebox.showerror("Erro", "Selecione uma mensagem para editar")

# Função para testar a conexão com o banco de dados usando psycopg2
def testar_conexao():
    try:
        conn = psycopg2.connect(
            dbname="BHS_ProjetoFBD",
            user="postgres",
            password="",
            host="localhost"
        )
        conn.close()
        messagebox.showinfo("Sucesso", "Conexão com o banco de dados bem-sucedida!")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha na conexão com o banco de dados: {e}")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill="both", expand=True)

tk.Label(frame, text="Emissor").grid(row=0, column=0, padx=5, pady=5)
emissor_combobox = ttk.Combobox(frame, values=list(usuarios_dict.keys()))
emissor_combobox.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Receptor").grid(row=1, column=0, padx=5, pady=5)
receptor_combobox = ttk.Combobox(frame, values=list(usuarios_dict.keys()))
receptor_combobox.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame, text="Texto").grid(row=2, column=0, padx=5, pady=5)
texto_entry = tk.Entry(frame, width=50)
texto_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Button(frame, text="Adicionar Mensagem", command=adicionar_mensagem).grid(row=3, column=0, columnspan=2, pady=10)
tk.Button(frame, text="Editar Mensagem", command=editar_mensagem).grid(row=4, column=0, columnspan=2, pady=10)
tk.Button(frame, text="Excluir Mensagem", command=excluir_mensagem).grid(row=5, column=0, columnspan=2, pady=10)
tk.Button(frame, text="Testar Conexão", command=testar_conexao).grid(row=6, column=0, columnspan=2, pady=10)

tree_frame = tk.Frame(root)
tree_frame.pack(fill="both", expand=True)

columns = ("ID", "Emissor", "Receptor", "Texto")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
tree.column("ID", width=50, anchor="center")
tree.column("Emissor", anchor="center")
tree.column("Receptor", anchor="center")
tree.column("Texto", anchor="center")
for col in columns:
    tree.heading(col, text=col, anchor="center")
tree.pack(fill="both", expand=True)

listar_mensagens()
root.mainloop()
