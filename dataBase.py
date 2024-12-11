import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student', 'instructor', 'admin'))
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT NOT NULL,
    course_description TEXT NOT NULL,
    instructor_id INTEGER NOT NULL,
    FOREIGN KEY (instructor_id) REFERENCES users(user_id)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS course_chapters (
    chapter_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_title TEXT NOT NULL,
    chapter_content TEXT,
    course_id INTEGER NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS course_enrollments (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (student_id) REFERENCES users(user_id),
    UNIQUE (course_id, student_id)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS grades (
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    grade INTEGER CHECK (grade BETWEEN 0 AND 100),
    FOREIGN KEY (student_id) REFERENCES users(user_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    UNIQUE (student_id, course_id)
);
''')


sample_users = [
    ("student", "password", "student"),
    ("student2", "password", "student"),
    ("student3", "password", "student"),
    ("teacher", "password", "instructor"),
    ("admin", "password", "admin"),
]

cursor.executemany('''
    INSERT INTO users (username, password, role) VALUES (?, ?, ?);
    ''', sample_users)


sample_courses = [
    ("Математика 101", "Базовый курс математики", 4),
    ("Программирование 101", "Основы программирования", 4),
]

sample_chapters = [
    (1, "Введение в математику", "Что такое математика?"),
    (1, "Алгебра", "Основы алгебры"),
    (2, "Введение в программирование", "История программирования"),
    (2, "Язык Python", "Основы Python"),
]

sample_enrollments = [
    (1, 1),
    (2, 1),
    (3, 2),
    (1, 2),
]

sample_grades = [
    (1, 1, 85),
    (2, 1, 90),
    (3, 2, 75),
    (1, 2, 88),
]



cursor.executemany('''
    INSERT INTO courses (course_name, course_description, instructor_id) 
    VALUES (?, ?, ?);
    ''', sample_courses)


cursor.executemany('''
    INSERT INTO course_chapters (course_id, chapter_title, chapter_content) 
    VALUES (?, ?, ?);
    ''', sample_chapters)


cursor.executemany('''
    INSERT INTO course_enrollments (student_id, course_id) 
    VALUES (?, ?);
    ''', sample_enrollments)

cursor.executemany('''
    INSERT INTO grades (student_id, course_id, grade)
    VALUES (?, ?, ?);
    ''', sample_grades)

conn.commit()
conn.close()

print("База данных и таблицы успешно созданы!")
import sqlite3
import pydot

def generate_er_diagram(database_file, output_file):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Fetch table information
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Graphviz DOT representation
    graph = pydot.Dot(graph_type="digraph", rankdir="LR")

    for table_name, in tables:
        if table_name == "sqlite_sequence":  # Skip SQLite internal table
            continue

        # Fetch table columns
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        # Fetch foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        foreign_keys = cursor.fetchall()

        # Add table node
        table_label = f"{table_name} | " + "\\l".join([f"{col[1]} ({col[2]})" for col in columns]) + "\\l"
        graph.add_node(pydot.Node(table_name, label=f"{{ {table_label} }}", shape="record"))

        # Add foreign key relationships
        for fk in foreign_keys:
            graph.add_edge(pydot.Edge(table_name, fk[2]))

    # Save output file
    graph.
    print(f"ER diagram saved as {output_file}")

# Usage
generate_er_diagram("database.db", "er_diagram.png")
