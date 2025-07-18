from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
DATABASE = 'ideas.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    db = get_db()
    ideas = db.execute('SELECT * FROM ideas ORDER BY fecha_creacion DESC').fetchall()
    return render_template('index.html', ideas=ideas)

@app.route('/nueva', methods=['GET', 'POST'])
def nueva():
    db = get_db()
    if request.method == 'POST':
        titulo = request.form['titulo']
        resumen = request.form['resumen']
        estado = request.form['estado']
        en_curso = db.execute("SELECT COUNT(*) FROM ideas WHERE estado = 'EN CURSO'").fetchone()[0]
        if estado == 'EN CURSO' and en_curso >= 1:
            return "❌ Ya tienes una idea en curso."
        db.execute('INSERT INTO ideas (titulo, resumen, estado) VALUES (?, ?, ?)', (titulo, resumen, estado))
        db.commit()
        return redirect('/')
    return render_template('nueva.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    db = get_db()
    idea = db.execute('SELECT * FROM ideas WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        resumen = request.form['resumen']
        readme = request.form['readme']
        estado = request.form['estado']
        en_curso = db.execute("SELECT COUNT(*) FROM ideas WHERE estado = 'EN CURSO' AND id != ?", (id,)).fetchone()[0]
        if estado == 'EN CURSO' and en_curso >= 1:
            return "❌ Ya tienes otra idea en curso."
        db.execute('UPDATE ideas SET resumen = ?, readme = ?, estado = ? WHERE id = ?', (resumen, readme, estado, id))
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
