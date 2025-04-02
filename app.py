from flask import Flask, render_template, request, redirect, url_for, session
import random
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-here')

# 퀴즈 문제 리스트
quiz_list = [
    # ... (기존 quiz_list 내용)
]

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    if 'question_number' not in session:
        session['question_number'] = 1
        session['score'] = 0
        session['total_questions'] = 10
        session['used_questions'] = []
    
    if session['question_number'] > session['total_questions']:
        return redirect(url_for('final_result'))
    
    available_questions = [i for i in range(len(quiz_list)) if i not in session['used_questions']]
    if not available_questions:
        return redirect(url_for('final_result'))
    
    quiz_index = random.choice(available_questions)
    quiz = quiz_list[quiz_index]
    
    session['used_questions'].append(quiz_index)
    session['current_quiz'] = quiz
    
    return render_template('quiz.html', quiz=quiz, question_number=session['question_number'])

@app.route('/check_answer', methods=['POST'])
def check_answer():
    if 'current_quiz' not in session:
        return redirect(url_for('index'))
    
    user_answer = request.form.get('answer')
    current_quiz = session['current_quiz']
    
    is_correct = user_answer == current_quiz['answer']
    
    if is_correct:
        session['score'] += 10
    
    session['question_number'] += 1
    
    return render_template('result.html', 
                         quiz=current_quiz,
                         user_answer=user_answer,
                         is_correct=is_correct,
                         question_number=session['question_number'])

@app.route('/final_result')
def final_result():
    if 'score' not in session:
        return redirect(url_for('index'))
    
    score = session['score']
    return render_template('final_result.html', score=score)

def handler(event, context):
    return app(event, context) 