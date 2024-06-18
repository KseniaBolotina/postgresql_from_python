import psycopg2

#1. Функция, создающая структуру БД (таблицы)
def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        drop table if exists phone_number;
        drop table if exists client;
        """)

        cur.execute("""
        create table if not exists client(
        id serial primary key,
        name varchar(60) not null,
        surname varchar(60) not null,
        email varchar(60) not null
        );
        """)

        cur.execute("""
        create table if not exists phone_number(
        client_id integer not null references client(id),
        phone varchar(11)
        );
        """)
        conn.commit()

#2. Функция, позволяющая добавить нового клиента
def add_client(conn, name, surname, email):
    with conn.cursor() as cur:
        cur.execute("""
        insert into client(name, surname, email) values(%s, %s, %s)
        returning id, name, surname, email;
        """, (name, surname, email))
        return cur.fetchone()

#3. Функция, позволяющая добавить телефон для существующего клиента
def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
        insert into phone_number(client_id, phone) values (%s, %s)
        returning client_id, phone;
        """, (client_id, phone))
        return cur.fetchone()

#4. Функция, позволяющая изменить данные о клиенте
def change_client(conn, client_id, name=None, surname=None, email=None):
    with conn.cursor() as cur:
        update_query = """
        update client 
        set name = coalesce(%s, name), 
            surname = coalesce(%s, surname), 
            email = coalesce(%s, email)
        where id = %s
        returning id, name, surname, email;
        """
        cur.execute(update_query, (name, surname, email, client_id))
        return cur.fetchone()

#5. Функция, позволяющая удалить телефон для существующего клиента
def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
        delete from phone_number
        where client_id = %s and phone = %s;
        """, (client_id, phone))
        return 'Телефон удален'

#6. Функция, позволяющая удалить существующего клиента
def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
        delete from phone_number
        where client_id = %s
        """, (client_id,))
        cur.execute("""
        delete from client 
        where id = %s
        """, (client_id,))
        return 'Клиент удален'

#7. Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону
def find_client(conn, name=None, surname=None, email=None, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
        select client.id, client.name, client.surname, client.email, phone_number.phone
        from client 
        left join phone_number on client.id = phone_number.client_id
        where client.name = %s or client.surname = %s or client.email = %s or phone_number.phone = %s
        """, (name, surname, email, phone))
        return cur.fetchone()

conn = psycopg2.connect(database="personal_information", user="postgres", password="UhjvVjkybb1155+")
#создание БД
create_db(conn)
print('Новый клиент -', add_client(conn, 'Alexandr', 'Alexandrov', 'alal@mail.ru'))
print('Новый клиент -', add_client(conn, 'Ivan', 'Ivanov', 'vanya@mail.ru'))
print('Новый клиент -', add_client(conn, 'Vasiliy', 'Vasilev', 'vasya@mail.ru'))
print('Телефон клиента -', add_phone(conn, 1, '79998765432'))
print('Телефон клиента -', add_phone(conn, 1, '78889088877'))
print('Телефон клиента -', add_phone(conn, 1, '77776665544'))
print('Телефон клиента -', add_phone(conn, 2, '79000007722'))
# print('Телефон клиента -', add_phone(conn, 3, '70898877776'))
print('Изменение данных клиента -', change_client(conn, 1, 'Alex', 'Alexandrov', 'alalexb@mail.ru'))
print('Удаление телефона клиента -', delete_phone(conn, 1, '78889088877'))

with conn.cursor() as cur:
    cur.execute("""select * from phone_number;""")
    print('Телефоны клиентов', cur.fetchall())

print('Удаление клиента -', delete_client(conn, 2))

with conn.cursor() as cur:
    cur.execute("""select * from client;""")
    print('Клиенты -', cur.fetchall())

print('Поиск клиента - ', find_client(conn, None, 'Alexandrov', None, None))
print('Поиск клиента - ', find_client(conn, None, None, 'vasya@mail.ru', None))

conn.close()
