# conexão com o postgres

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="estoque",
        user="usuario",
        password="123"
    )
    return conn

# substituir database, user e password com o que tiver na máquina local



# essa função faz a checagem da existência das tabelas do esquema. Caso não tenha tabelas, estas serão criadas

def checar_tabelas():
    conn = get_db_connection()
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # verifica se a tabela existe
    checa_tabelas_query = """
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        AND table_name = %s
    );
    """

    # queries de criação de tabelas
    tabelas = {
        "item": """
        CREATE TABLE item (
            id_item SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            peso_volume VARCHAR(10)
        );
        """,
        "cesta": """
        CREATE TABLE cesta (
            id_cesta SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            qt_itens INTEGER NOT NULL
        );
        """,
        "componentes_cesta": """
        CREATE TABLE componentes_cesta (
            id_componente SERIAL PRIMARY KEY,
            fk_id_cesta INTEGER REFERENCES cesta(id_cesta) ON DELETE CASCADE ON UPDATE CASCADE,
            fk_id_item INTEGER REFERENCES item(id_item) ON DELETE CASCADE ON UPDATE CASCADE,
            qt_itens INTEGER NOT NULL
        ); 
        CREATE UNIQUE INDEX idx_cesta_item ON componentes_cesta(fk_id_cesta, fk_id_item)
        """,
        "donatario": """
        CREATE TABLE donatario (
            id_donatario SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            telefone CHAR(9) NOT NULL,
            endereco TEXT
        );
        """,
        "doacao": """
        CREATE TABLE doacao (
            id_doacao SERIAL PRIMARY KEY,
            fk_id_donatario INTEGER REFERENCES donatario(id_donatario) ON UPDATE CASCADE ON DELETE SET NULL,
            fk_id_cesta INTEGER REFERENCES cesta(id_cesta) ON DELETE CASCADE ON UPDATE CASCADE,
            qt_cestas INTEGER NOT NULL
        );
        """
    }

    # faz a verificação da existência das tabelas. Cria caso não existam
    for tabnome, cria_query in tabelas.items():
        cur.execute(checa_tabelas_query, (tabnome,))
        exists = cur.fetchone()[0]

        if not exists:
            cur.execute(cria_query)
            print(f"Tabela '{tabnome}' criada com sucesso.")
        else:
            print(f"Tabela '{tabnome}' já existe.")

    cur.close()
    conn.close()