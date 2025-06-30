
from flask import Flask, request, jsonify, render_template, redirect, flash
import html
import json
import os

app = Flask(__name__)
app.secret_key = 'secretkey'  # Untuk flash message

DATABASE_FILE = 'answers.json'

if not os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, 'w') as f:
        json.dump([], f)

@app.route('/api/answers', methods=['POST'])
def create_answer():
    data = request.get_json()
    answer_text = data.get('answer')
    with open(DATABASE_FILE, 'r') as f:
        answers = json.load(f)
    new_id = max([a['id'] for a in answers], default=0) + 1
    new_answer = {"id": new_id, "answer": answer_text}
    answers.append(new_answer)
    with open(DATABASE_FILE, 'w') as f:
        json.dump(answers, f, indent=4)
    return jsonify(new_answer), 201

@app.route('/api/answers', methods=['GET'])
def get_answers():
    with open(DATABASE_FILE, 'r') as f:
        answers = json.load(f)
    return jsonify(answers)
@app.route('/api/answers/<int:answer_id>', methods=['GET'])
def get_answer_by_id(answer_id):
    with open(DATABASE_FILE, 'r') as f:
        answers = json.load(f)
    answer = next((a for a in answers if a['id'] == answer_id), None)
    if answer is None:
        return jsonify({"error": "Answer not found"}), 404
    return jsonify(answer)


@app.route('/api/answers/<int:answer_id>', methods=['PUT'])
def update_answer(answer_id):
    data = request.get_json()
    updated_answer = data.get('answer')
    with open(DATABASE_FILE, 'r') as f:
        answers = json.load(f)
    for answer in answers:
        if answer['id'] == answer_id:
            answer['answer'] = updated_answer
            break
    else:
        return jsonify({"error": "Answer not found"}), 404
    with open(DATABASE_FILE, 'w') as f:
        json.dump(answers, f, indent=4)
    return jsonify(answer)

@app.route('/api/answers/<int:answer_id>', methods=['DELETE'])
def delete_answer(answer_id):
    with open(DATABASE_FILE, 'r') as f:
        answers = json.load(f)
    answers = [answer for answer in answers if answer['id'] != answer_id]
    with open(DATABASE_FILE, 'w') as f:
        json.dump(answers, f, indent=4)
    return jsonify({"message": "Answer deleted"}), 200

@app.route('/')
def home():
    with open(DATABASE_FILE, 'r') as f:
        answers = json.load(f)
    return render_template('index.html', answers=answers)

@app.route('/submit', methods=['POST'])
def submit_answer():
    answer_text = request.form.get('answer', '').strip()

    # Validasi input
    if not answer_text:
        flash('Jawaban tidak boleh kosong.')
        return redirect('/')
    if len(answer_text) > 20:
        flash('Jawaban terlalu panjang (maksimal 20 karakter).')
        return redirect('/')

    # Sanitasi (hindari XSS)
    safe_answer = html.escape(answer_text)

    with open(DATABASE_FILE, 'r') as f:
        answers = json.load(f)

    new_id = max([a['id'] for a in answers], default=0) + 1
    new_answer = {"id": new_id, "answer": safe_answer}
    answers.append(new_answer)

    with open(DATABASE_FILE, 'w') as f:
        json.dump(answers, f, indent=4)

    flash('Jawaban berhasil ditambahkan!')
    return redirect('/')

@app.route('/edit/<int:answer_id>', methods=['GET', 'POST'])
def edit_answer(answer_id):
    with open(DATABASE_FILE, 'r') as f:
        answers = json.load(f)

    # Cari jawaban berdasarkan ID
    answer = next((a for a in answers if a['id'] == answer_id), None)
    if not answer:
        return "Jawaban tidak ditemukan", 404

    if request.method == 'POST':
        # Perbarui jawaban
        updated_text = request.form.get('answer')
        answer['answer'] = updated_text
        with open(DATABASE_FILE, 'w') as f:
            json.dump(answers, f, indent=4)
        return redirect('/')

    # Tampilkan form edit
    return render_template('edit.html', answer=answer)

@app.route('/update/<int:answer_id>', methods=['POST'])
def update_answer_web(answer_id):
    new_text = request.form.get('answer')
    with open(DATABASE_FILE, 'r') as f:
        answers = json.load(f)
    for a in answers:
        if a['id'] == answer_id:
            a['answer'] = new_text
            break
    with open(DATABASE_FILE, 'w') as f:
        json.dump(answers, f, indent=4)
    return redirect('/')

@app.route('/delete/<int:answer_id>', methods=['POST'])
def delete_answer_web(answer_id):
    with open(DATABASE_FILE, 'r') as f:
        answers = json.load(f)

    new_answers = [a for a in answers if a['id'] != answer_id]

    if len(new_answers) == len(answers):
        return "Jawaban tidak ditemukan", 404

    with open(DATABASE_FILE, 'w') as f:
        json.dump(new_answers, f, indent=4)

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

