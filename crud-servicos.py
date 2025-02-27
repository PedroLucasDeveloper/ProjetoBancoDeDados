import psycopg2 as pg
from sqlalchemy import create_engine
from tkinter import *
from tkinter import messagebox, ttk
import pandas as pd

def conectar_bd_psycopg2():
    try:
        return pg.connect(
            host='localhost',
            dbname='banco',
            user='postgres',
            password='rootuser'
        )
    except Exception as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados: {str(e)}")
        return None

cnx = 'postgresql://postgres:rootuser@localhost/banco'
engine = create_engine(cnx)

def criar_servico():
    try:
        con = conectar_bd_psycopg2()
        if not con:
            return

        id_usuario = int(id_usuario_entry.get())
        horas_cobradas = int(horas_cobradas_entry.get())
        categoria = categoria_entry.get().strip()
        descricao = descricao_text.get("1.0", END).strip()

        if not categoria or not descricao or horas_cobradas <= 0:
            messagebox.showwarning("Entrada Inválida", "Preencha todos os campos corretamente.")
            return

        query = """
        INSERT INTO servicos (id_usuario_comum, horas_cobradas, categoria, descricao)
        VALUES (%s, %s, %s, %s)
        """
        with con.cursor() as cursor:
            cursor.execute(query, (id_usuario, horas_cobradas, categoria, descricao))
            con.commit()
        messagebox.showinfo("Sucesso", "Serviço criado com sucesso!")
        limpar_campos()
        atualizar_tabela()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao criar serviço: {str(e)}")
    finally:
        if con:
            con.close()

def ler_servicos():
    try:
        query = "SELECT id, id_usuario_comum, horas_cobradas, categoria, descricao FROM servicos"
        df = pd.read_sql(query, engine)
        return df.to_records(index=False).tolist()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao ler serviços: {str(e)}")
        return []

def pesquisar_servicos():
    try:
        filtro_categoria = categoria_pesquisa_entry.get().strip()
        filtro_id_usuario = usuario_pesquisa_entry.get().strip()

        query = "SELECT id, id_usuario_comum, horas_cobradas, categoria, descricao FROM servicos WHERE 1=1"
        params = {}

        if filtro_categoria:
            query += " AND categoria ILIKE %(categoria)s"
            params["categoria"] = f"%{filtro_categoria}%"
        if filtro_id_usuario:
            query += " AND id_usuario_comum = %(id_usuario)s"
            params["id_usuario"] = int(filtro_id_usuario)

        df = pd.read_sql(query, engine, params=params)
        return df.to_records(index=False).tolist()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao pesquisar serviços: {str(e)}")
        return []

def atualizar_servico():
    try:
        con = conectar_bd_psycopg2()
        if not con:
            return

        id_servico = int(id_servico_entry.get())
        horas_cobradas = horas_cobradas_entry.get().strip()
        categoria = categoria_entry.get().strip()
        descricao = descricao_text.get("1.0", END).strip()

        query = "UPDATE servicos SET "
        params = []
        updates = []

        if horas_cobradas:
            updates.append("horas_cobradas = %s")
            params.append(int(horas_cobradas))
        if categoria:
            updates.append("categoria = %s")
            params.append(categoria)
        if descricao:
            updates.append("descricao = %s")
            params.append(descricao)

        if not updates:
            messagebox.showwarning("Entrada Inválida", "Preencha pelo menos um campo para atualizar.")
            return

        query += ", ".join(updates) + " WHERE id = %s"
        params.append(id_servico)

        with con.cursor() as cursor:
            cursor.execute(query, params)
            con.commit()
        messagebox.showinfo("Sucesso", "Serviço atualizado com sucesso!")
        limpar_campos()
        atualizar_tabela()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao atualizar serviço: {str(e)}")
    finally:
        if con:
            con.close()

def excluir_servico():
    try:
        con = conectar_bd_psycopg2()
        if not con:
            return

        id_servico = int(id_servico_entry.get())

        query = "DELETE FROM servicos WHERE id = %s"
        with con.cursor() as cursor:
            cursor.execute(query, (id_servico,))
            con.commit()
        messagebox.showinfo("Sucesso", "Serviço excluído com sucesso!")
        limpar_campos()
        atualizar_tabela()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao excluir serviço: {str(e)}")
    finally:
        if con:
            con.close()

def limpar_campos():
    id_servico_entry.delete(0, END)
    id_usuario_entry.delete(0, END)
    horas_cobradas_entry.delete(0, END)
    categoria_entry.delete(0, END)
    descricao_text.delete("1.0", END)

def preencher_campos(event):
    try:
        item = tabela.selection()[0]
        valores = tabela.item(item, "values")
        limpar_campos()
        id_servico_entry.insert(0, valores[0])  # ID do Serviço
        id_usuario_entry.insert(0, valores[1])  # ID do Usuário
        horas_cobradas_entry.insert(0, valores[2])  # Horas Cobradas
        categoria_entry.insert(0, valores[3])  # Categoria
        descricao_text.insert("1.0", valores[4])  # Descrição
    except IndexError:
        pass

def atualizar_tabela(dados=None):
    for row in tabela.get_children():
        tabela.delete(row)
    if not dados:
        dados = ler_servicos()
    for dado in dados:
        tabela.insert("", "end", values=dado)

def executar_pesquisa():
    dados = pesquisar_servicos()
    atualizar_tabela(dados)

root = Tk()
root.title("CRUD de Serviços")
root.geometry("1200x600")

Label(root, text="ID do Serviço").grid(row=0, column=0, padx=10, pady=5)
id_servico_entry = Entry(root)
id_servico_entry.grid(row=0, column=1, padx=10, pady=5)

Label(root, text="ID do Usuário Comum").grid(row=1, column=0, padx=10, pady=5)
id_usuario_entry = Entry(root)
id_usuario_entry.grid(row=1, column=1, padx=10, pady=5)

Label(root, text="Horas Cobradas").grid(row=2, column=0, padx=10, pady=5)
horas_cobradas_entry = Entry(root)
horas_cobradas_entry.grid(row=2, column=1, padx=10, pady=5)

Label(root, text="Categoria").grid(row=3, column=0, padx=10, pady=5)
categoria_entry = Entry(root)
categoria_entry.grid(row=3, column=1, padx=10, pady=5)

Label(root, text="Descrição").grid(row=4, column=0, padx=10, pady=5)
descricao_text = Text(root, width=40, height=5)
descricao_text.grid(row=4, column=1, padx=10, pady=5)

Button(root, text="Criar Serviço", command=criar_servico).grid(row=5, column=0, padx=10, pady=5)
Button(root, text="Atualizar Serviço", command=atualizar_servico).grid(row=5, column=1, padx=10, pady=5)
Button(root, text="Excluir Serviço", command=excluir_servico).grid(row=5, column=2, padx=10, pady=5)
Button(root, text="Limpar Campos", command=limpar_campos).grid(row=5, column=3, padx=10, pady=5)

Label(root, text="Pesquisar por Categoria").grid(row=6, column=0, padx=10, pady=5)
categoria_pesquisa_entry = Entry(root)
categoria_pesquisa_entry.grid(row=6, column=1, padx=10, pady=5)

Label(root, text="Pesquisar por ID Usuário").grid(row=7, column=0, padx=10, pady=5)
usuario_pesquisa_entry = Entry(root)
usuario_pesquisa_entry.grid(row=7, column=1, padx=10, pady=5)

Button(root, text="Pesquisar", command=executar_pesquisa).grid(row=7, column=2, padx=10, pady=5)

colunas = ("ID", "ID Usuário", "Horas Cobradas", "Categoria", "Descrição")
tabela = ttk.Treeview(root, columns=colunas, show="headings")
for coluna in colunas:
    tabela.heading(coluna, text=coluna)
    tabela.column(coluna, width=150)
tabela.column("Descrição", width=500)
tabela.grid(row=8, column=0, columnspan=4, padx=10, pady=10)
tabela.bind("<<TreeviewSelect>>", preencher_campos)

atualizar_tabela()
root.mainloop()