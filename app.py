from flask import Flask, render_template, request, redirect
import sqlite3
import os
from datetime import datetime

# Crear la base de datos si no existe
DB_NAME = "ideas.db"
if not os.path.exists(DB_NAME):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            resumen TEXT,
            estado TEXT DEFAULT 'PENDIENTE',
            readme TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_prevista_entrega DATE
        )
    ''')
    conn.commit()
    conn.close()

app = Flask(__name__)
DATABASE = 'ideas.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    db = get_db()
    ideas = db.execute('''
    SELECT * FROM ideas
    ORDER BY 
        CASE estado 
            WHEN 'COMPLETADA' THEN 1
            WHEN 'EN CURSO' THEN 2
            WHEN 'PENDIENTE' THEN 3
        END,
        fecha_creacion DESC
''').fetchall()

    return render_template('index.html', ideas=ideas)

@app.route('/nueva', methods=['GET', 'POST'])
def nueva():
    db = get_db()
    if request.method == 'POST':
        titulo = request.form['titulo']
        resumen = request.form['resumen']
        readme = request.form.get('readme', '')
        estado = request.form.get('estado', 'PENDIENTE')
        fecha_prevista = request.form.get('fecha_prevista_entrega', None)

        # Convertir cadena vacía a None para la base de datos
        if fecha_prevista == '':
            fecha_prevista = None

        db.execute('INSERT INTO ideas (titulo, resumen, readme, estado, fecha_prevista_entrega) VALUES (?, ?, ?, ?, ?)',
                   (titulo, resumen, readme, estado, fecha_prevista))
        db.commit()
        return redirect('/')
    return render_template('nueva.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    db = get_db()
    idea = db.execute('SELECT * FROM ideas WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        titulo = request.form['titulo']
        resumen = request.form['resumen']
        readme = request.form['readme']
        estado = request.form['estado']
        fecha_prevista = request.form.get('fecha_prevista_entrega', None)

        # Convertir cadena vacía a None para la base de datos
        if fecha_prevista == '':
            fecha_prevista = None

        db.execute('UPDATE ideas SET titulo = ?, resumen = ?, readme = ?, estado = ?, fecha_prevista_entrega = ? WHERE id = ?',
                   (titulo, resumen, readme, estado, fecha_prevista, id))
        db.commit()
        return redirect('/')
    return render_template('editar.html', idea=idea)

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    db = get_db()
    db.execute('DELETE FROM ideas WHERE id = ?', (id,))
    db.commit()
    return redirect('/')
if __name__ == '__main__':
    app.run(debug=True)
