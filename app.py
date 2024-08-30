from flask import Flask, render_template, request, redirect, url_for
from psycopg2.extras import RealDictCursor
from db import get_db_connection, checar_tabelas

app = Flask(__name__)
app.secret_key = '1234'

checar_tabelas()    # verifica se as tabelas existem no banco de dados e as cria se não existirem


# rota da homepage
@app.route('/')
def index():
    return render_template('index.html')

# rota da pagina de itens
@app.route('/estoque')
def estoque():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM item ORDER BY id_item;')
    item = cur.fetchall()

    print(item)

    cur.close()
    conn.close()
    return render_template('estoque.html', item=item)


# rota para cadastrar um novo item na tabela "item"
@app.route('/estoque/novo', methods=['GET', 'POST'])
def novo_item():
    if request.method == 'POST':
        nome = request.form['nome']
        peso_volume = request.form.get('peso_volume')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO item (nome, peso_volume) VALUES (%s, %s)',
                    (nome, peso_volume))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('estoque'))
    return render_template('novo_item.html')


# rota da pagina da lista das cestas
@app.route('/cestas')
def cestas():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('''
        SELECT c.id_cesta, c.nome, SUM(cc.qt_itens) AS total_itens
        FROM cesta c
        LEFT JOIN componentes_cesta cc ON c.id_cesta = cc.fk_id_cesta
        GROUP BY c.id_cesta
        ORDER BY c.id_cesta
    ''')
    cesta = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('cestas.html', cesta=cesta)


# rota da página de cadastro das novas cestas
@app.route('/cestas/novo', methods=['GET', 'POST'])
def nova_cesta():
    if request.method == 'POST':
        nome = request.form['nome']
        quantidade = request.form.get('quantidade', 0)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO cesta (nome, qt_itens) VALUES (%s, %s)',
                    (nome, quantidade))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('cestas'))
    return render_template('nova_cesta.html')


# rota da pagina da lista de donatários
@app.route('/donatarios')
def donatario():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM donatario;')
    donatario = cur.fetchall()

    print(donatario)
    print(type(donatario))

    cur.close()
    conn.close()
    return render_template('donatario.html', donatario=donatario)


# rota da página de cadastro das novas cestas
@app.route('/donatario/novo', methods=['GET', 'POST'])
def novo_donatario():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        endereco = request.form['endereco']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO donatario (nome, telefone, endereco) VALUES (%s, %s, %s)',
                    (nome, telefone, endereco))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('donatario'))
    return render_template('novo_donatario.html')


# rota de editar itens do estoque
@app.route('/estoque/editar_item/<int:id>', methods=['GET', 'POST'])
def editar_item(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'POST':
        nome = request.form['nome']
        peso_volume = request.form['peso_volume']
        
        cur.execute('UPDATE item SET nome = %s, peso_volume = %s WHERE id_item = %s',
                    (nome, peso_volume, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('estoque'))
    
    cur.execute('SELECT * FROM item WHERE id_item = %s', (id,))
    items = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('editar_item.html', item=items)


# rota de editar donatários 
@app.route('/donatario/editar_donatario/<int:id>', methods=['GET', 'POST'])
def editar_donatario(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        
        cur.execute('UPDATE donatario SET nome = %s, telefone = %s, endereco = %s WHERE id_donatario = %s',
                    (nome, telefone, endereco, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('donatario'))
    
    cur.execute('SELECT * FROM donatario WHERE id_donatario = %s', (id,))
    donatario = cur.fetchone()


    cur.close()
    conn.close()
    
    return render_template('editar_donatario.html', donatario=donatario)


# rota de editar informações da cesta básica
@app.route('/cestas/editar_cesta/<int:id>', methods=['GET', 'POST'])
def editar_cesta(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        # atualiza o nome da cesta

        if request.form.get('nome'):
            nome = request.form['nome']
            cur.execute('UPDATE cesta SET nome = %s WHERE id_cesta = %s',
                        (nome, id))
        else:
            # adiciona novo item à cesta se for o caso
            fk_id_item = request.form.get('fk_id_item')
            qt_itens = request.form['qt_itens']  

            cur.execute('''
                INSERT INTO componentes_cesta (fk_id_cesta, fk_id_item, qt_itens) 
                VALUES (%s, %s, %s)
                ON CONFLICT (fk_id_cesta, fk_id_item) 
                DO UPDATE SET qt_itens = EXCLUDED.qt_itens + %s
            ''', (id, fk_id_item, qt_itens, qt_itens))
        
        conn.commit()
    
    # busca informações da cesta
    cur.execute('SELECT * FROM cesta WHERE id_cesta = %s', (id,))
    cesta = cur.fetchone()

    # busca itens da cesta
    cur.execute('''
        SELECT cc.id_componente, i.nome, i.peso_volume, cc.qt_itens 
        FROM componentes_cesta cc
        JOIN item i ON cc.fk_id_item = i.id_item
        WHERE cc.fk_id_cesta = %s
    ''', (id,))
    itens = cur.fetchall()

    # buscar todos os itens disponíveis para adicionar à cesta
    cur.execute('SELECT id_item, nome FROM item')
    todos_itens = cur.fetchall()

    cur.close()
    conn.close()
    
    return render_template('editar_cesta.html', cesta=cesta, itens=itens, todos_itens=todos_itens)

# rota para ver informações detalhadas de uma cesta em particular
@app.route('/cestas/ver_cesta/<int:id>', methods=['GET'])
def ver_cesta(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Buscar informações da cesta
    cur.execute('SELECT * FROM cesta WHERE id_cesta = %s', (id,))
    cesta = cur.fetchone()

    # Buscar itens da cesta
    cur.execute('''
        SELECT i.id_item, i.nome, i.peso_volume, cc.qt_itens 
        FROM item i 
        JOIN componentes_cesta cc ON i.id_item = cc.fk_id_item 
        WHERE cc.fk_id_cesta = %s
    ''', (id,))
    itens = cur.fetchall()

    cur.close()
    conn.close()
    
    return render_template('ver_cesta.html', cesta=cesta, itens=itens)



# rota para registrar uma doação para um donatário particular
@app.route('/registrar_doacao/<int:id_donatario>', methods=['GET', 'POST'])
def registrar_doacao(id_donatario):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        fk_id_cesta = request.form['fk_id_cesta']
        qt_cestas = int(request.form['qt_cestas'])
        
        # Inserir nova doação no banco de dados
        cur.execute('''
            INSERT INTO doacao (fk_id_donatario, fk_id_cesta, qt_cestas)
            VALUES (%s, %s, %s)
        ''', (id_donatario, fk_id_cesta, qt_cestas))
        conn.commit()
        return redirect(url_for('donatario'))
        
    # Buscar donatário e cestas disponíveis
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM donatario WHERE id_donatario = %s', (id_donatario,))
    donatario = cur.fetchone()
    
    cur.execute('SELECT * FROM cesta')
    cestas = cur.fetchall()

    return render_template('registrar_doacao.html', donatario=donatario, cestas=cestas)


# rota para mostrar o registro de doações
@app.route('/doacoes')
def doacoes():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('''
        SELECT d.id_doacao, don.nome AS donatario, c.nome AS cesta, d.qt_cestas 
        FROM doacao d
        JOIN donatario don ON d.fk_id_donatario = don.id_donatario
        JOIN cesta c ON d.fk_id_cesta = c.id_cesta
        ORDER BY d.id_doacao
    ''')
    doacoes = cur.fetchall()
    return render_template('doacoes.html', doacoes=doacoes)


# rota para remover um item do estoque
@app.route('/remover_item/<int:id_item>', methods=['POST'])
def remover_item(id_item):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM item WHERE id_item = %s', (id_item,))
        conn.commit()  
    except Exception as e:
        conn.rollback()
    return redirect(url_for('estoque'))

# rota para remover uma cesta da lista de cestas
@app.route('/remover_cesta/<int:id_cesta>', methods=['POST'])
def remover_cesta(id_cesta):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM cesta WHERE id_cesta = %s', (id_cesta,))
        conn.commit()
    except Exception as e:
        conn.rollback()
    return redirect(url_for('cestas'))


# rota para remover um donatário da lista de donatários
@app.route('/remover_donatario/<int:id_donatario>', methods=['POST'])
def remover_donatario(id_donatario):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM donatario WHERE id_donatario = %s', (id_donatario,))
        conn.commit()
    except Exception as e:
        conn.rollback()
    return redirect(url_for('donatario'))

# rota para remover um item da cesta na página de edição
@app.route('/remover_item_cesta/<int:id_componente>/<int:id_cesta>', methods=['POST'])
def remover_item_cesta(id_componente, id_cesta):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM componentes_cesta WHERE id_componente = %s', (id_componente,))
        conn.commit()
    except Exception as e:
        conn.rollback()
    return redirect(url_for('editar_cesta', id=id_cesta))



if __name__ == '__main__':
    app.run(debug=True)
