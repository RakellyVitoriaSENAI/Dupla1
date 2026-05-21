from flask import Flask,render_template,request,redirect,flash
import psycopg2
import os #bilioteca que trabalha com arquivos
app = Flask(__name__)
app.secret_key='NaoLembro'
pasta = "static/assets/img/livros"
app.config["pasta"] = pasta

def ligar_banco():
    banco = psycopg2.connect(
        host="localhost",
        dbname="ReadSpace",
        user="postgres",
        password="senai",
        port="5432"
    )
    return banco
                                                ### Inicio ###
@app.route('/')
def inicio():
    return render_template('index.html')


                                                    ### livros ###
@app.route('/livros')
def Livros():
    banco=ligar_banco()
    cursor = banco.cursor()
    cursor.execute("""
        SELECT id, titulo, autor, categoria, descricao, arquivo, ativo, ano_publicacao
        FROM livro
        WHERE ativo = TRUE 
    """)
    livros = cursor.fetchall()
    print(livros)
    return render_template('livros.html', livros=livros)


@app.route('/livros/admin')
def livros_admin():
    banco=ligar_banco()
    cursor = banco.cursor()
    cursor.execute("""
     SELECT id, titulo, autor, categoria,descricao,arquivo,ativo,ano_publicacao
     FROM livro
    """)
    livros = cursor.fetchall()
    cursor.close()
    banco.close()
    return render_template('livros_admin.html',livros=livros)

@app.route('/livros/admin/cadastrar')
def cadastrar_livro():
    return render_template('cadastrar_livros_admin.html')

@app.route('/livros/admin/criar', methods=['POST'])
def criar_livros():
    titulo = request.form['titulo']
    autor = request.form['autor']
    categoria = request.form['categoria']
    descricao = request.form['descricao']
    ativo = True
    foto = request.files.get('foto')  #O 'get' é nescessário quando estamos pegando arquivos do formulário, porém pode ser utilizado em várias ocasiões
    nome_arquivo = foto.filename
    caminho_foto = os.path.join(app.config["pasta"], nome_arquivo)
    foto.save(caminho_foto)
    ano_publicacao = request.form['ano_publicacao']
    banco = ligar_banco()
    cursor = banco.cursor()
    cursor.execute("""
            INSERT INTO livro(titulo, autor, categoria,descricao,arquivo,ativo,ano_publicacao)
            VALUES (%s, %s, %s, %s, %s, %s,%s)
        """, (titulo, autor, categoria, descricao, nome_arquivo, ativo, ano_publicacao ))
    banco.commit()
    cursor.close()
    banco.close()
    return redirect("/livros/admin")

@app.route('/livros/admin/excluir/<int:id>')
def excluir_livro(id):
    banco = ligar_banco()
    cursor = banco.cursor()
    cursor.execute("SELECT arquivo FROM livro WHERE id = %s", (id,))  # três aspas serve para códigos SQLs que tem mais que uma linha
    resultado = cursor.fetchone()
    nome_foto = resultado[0]
    caminho_foto = os.path.join(app.config["pasta"], nome_foto)
    os.remove(caminho_foto)
    cursor.execute("DELETE FROM livro WHERE id = %s", (id,))
    banco.commit()
    cursor.close()
    banco.close()
    flash('Livro excluido com sucesso!')
    return redirect("/livros/admin")

@app.route('/livros/admin/editar/<int:id>')
def editar_livro(id):
    banco = ligar_banco()
    cursor = banco.cursor()
    cursor.execute("""
        SELECT id, titulo, autor, categoria, descricao, arquivo, ativo, ano_publicacao
        FROM livro
        WHERE id = %s
    """, (id,))
    livro = cursor.fetchone()
    cursor.close()
    banco.close()
    return render_template('editar_livros.html', livro=livro)

@app.route('/livros/admin/alterar/<int:id>', methods=['POST'])
def alterar_livro(id):
    titulo = request.form['titulo']
    autor = request.form['autor']
    categoria = request.form['categoria']
    descricao = request.form['descricao']
    ano_publicacao = request.form['ano_publicacao']
    ativo = request.form.get('ativo')
    if ativo == 'on':
        ativo = True
    else:
        ativo = False
    banco = ligar_banco()
    cursor = banco.cursor()
    cursor.execute("SELECT arquivo FROM livro WHERE id = %s", (id,))
    resultado = cursor.fetchone()
    foto_atual = resultado[0]
    foto = request.files.get('foto')
    if foto.filename != "":
        nome_arquivo = foto.filename
        caminho_foto = os.path.join(app.config['pasta'], nome_arquivo)
        foto.save(caminho_foto)
        caminho_foto_antiga = os.path.join(app.config["pasta"], foto_atual)
        os.remove(caminho_foto_antiga)
        cursor.execute("""
                        UPDATE livro
                        SET titulo=%s, autor=%s, categoria=%s, descricao=%s, arquivo=%s, ativo=%s, ano_publicacao=%s
                        WHERE id=%s
                        """, (titulo, autor, categoria, descricao, nome_arquivo, ativo, ano_publicacao, id))
    else:
        cursor.execute("""
                       UPDATE livro
                        SET titulo=%s, autor=%s, categoria=%s,descricao=%s, ativo=%s, ano_publicacao=%s
                       WHERE id = %s
                       """, ( titulo, autor, categoria,descricao,ativo,ano_publicacao, id))
    banco.commit()
    cursor.close()
    banco.close()
    return redirect("/livros/admin")

if __name__ == '__main__':
    app.run()
