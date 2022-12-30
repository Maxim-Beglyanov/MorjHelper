import sqlite3


con = sqlite3.connect("database/database.db")

def insert(table: str, *args, many=False, **kwargs):
    if args:
        fields = ''
    else:
        args = kwargs.values()
        fields = '('+', '.join(kwargs.keys())+')'

    cur = con.cursor()
    if many:
        args = args[0]
        placeholders = ', '.join(len(args[0])*'?')
        execute = cur.executemany
    else:
        args = tuple(args)
        placeholders = ', '.join(len(args)*'?')
        execute = cur.execute

    execute(f'INSERT INTO {table}{fields} VALUES({placeholders})', args)
    con.commit()

def update(table: str, **kwargs):
    args = ', '.join(f'SET {key} = ?' for key in kwargs)
    cur = con.cursor()
    cur.execute(f'UPDATE {table} {args}', tuple(kwargs.values()))
    con.commit()


def delete(table: str, **where):
    where_query = ''
    if where:
        where_query = 'WHERE '+' AND '.join(where+' = ?' for where in where.keys())

    cur = con.cursor()
    cur.execute(f'DELETE FROM {table} {where_query}', tuple(where.values()))
    con.commit()

def select(table: str, *fields: str, **where):
    if len(fields) == 1:
        if type(fields[0]) is str:
            fields = fields[0].split()
        else:
            fields = fields[0]
    if not fields:
        fields = '*'
    fields = ', '.join(fields)

    where_query = ''
    if where:
        where_query = 'WHERE '+' AND '.join(where+' = ?' for where in where.keys())

    cur = con.cursor()
    val = cur.execute(f'SELECT {fields} FROM {table} {where_query}', tuple(where.values()))
    return val.fetchall()


def check_db_exists():
    if not select('sqlite_master', type='table', name='offer_channels'):
        init_db()

def init_db():
    r = open('database/create_db.sql', 'r')
    sql = r.read()

    con.executescript(sql)
    con.commit()
