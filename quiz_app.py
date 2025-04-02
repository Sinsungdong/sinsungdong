from flask import Flask, render_template, request, redirect, url_for, session
import random
import os
import socket

app = Flask(__name__)
# 세션 시크릿 키를 환경 변수에서 가져오거나 기본값 사용
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-here')

# 퀴즈 문제 리스트
quiz_list = [
    {"question": "양액에서 Ca²⁺와 SO₄²⁻를 같은 용액에 넣으면 왜 안 될까?", 
     "options": ["색깔 변화", "냄새 발생", "침전물 생성", "맛 변화"],
     "answer": "3", 
     "explanation": "Ca²⁺와 SO₄²⁻가 만나면 CaSO₄(석고) 같은 침전물이 생겨서 양액이 탁해지고 영양소 흡수가 어려워집니다."},
    {"question": "KNO₃ 1mM은 K를 몇 me/L 공급할까?", 
     "options": ["2", "3", "4", "1"],
     "answer": "4", 
     "explanation": "K⁺의 원자가는 1이므로, 1mM(밀리몰/L)은 1me/L(밀리당량/L)과 같습니다."},
    {"question": "MgSO₄·7H₂O 246mg/L는 Mg를 몇 me/L 공급할까? (몰질량: 246g/mol)", 
     "options": ["3", "2", "4", "1"],
     "answer": "2", 
     "explanation": "246mg/L ÷ 246g/mol = 1mM이고, Mg²⁺의 원자가는 2이므로 1mM × 2 = 2me/L입니다."},
    {"question": "양액 제조에서 A액과 B액을 나누는 이유는 무엇일까?", 
     "options": ["색깔 조절", "이온 간 침전 방지", "농도 증가", "맛을 내기 위해"],
     "answer": "2", 
     "explanation": "Ca²⁺와 SO₄²⁻, PO₄³⁻가 섞이면 침전물이 생길 수 있어서 A액과 B액으로 나눕니다."},
    {"question": "Ca(NO₃)₂·4H₂O의 몰질량은 얼마일까?", 
     "options": ["236g/mol", "150g/mol", "101g/mol", "200g/mol"],
     "answer": "1", 
     "explanation": "Ca(40) + 2×N(14) + 6×O(16) + 4×H₂O(18) = 236g/mol입니다."},
    {"question": "KNO₃는 어떤 원소를 공급할까?", 
     "options": ["Mg와 N", "Ca와 S", "K와 P", "K와 NO₃-N"],
     "answer": "4", 
     "explanation": "KNO₃는 칼륨(K⁺)과 질산염 질소(NO₃-N)를 제공합니다. P는 포함되지 않습니다."},
    {"question": "me/L를 mM으로 바꾸려면 무엇을 해야 할까?", 
     "options": ["몰질량으로 곱하기", "원자가로 곱하기", "원자가로 나누기", "몰질량으로 나누기"],
     "answer": "3", 
     "explanation": "me/L는 전하를 고려한 단위이므로 원자가로 나누면 mM(몰 농도)이 됩니다."},
    {"question": "ppm 단위는 무엇을 뜻할까?", 
     "options": ["밀리몰 농도", "백만분율", "백분율", "몰질량 단위"],
     "answer": "2", 
     "explanation": "ppm은 parts per million으로, 용질의 질량이 용액에서 백만분의 몇인지 나타냅니다."},
    {"question": "Mg²⁺의 원자가는 얼마일까?", 
     "options": ["4", "1", "3", "2"],
     "answer": "4", 
     "explanation": "Mg는 2가 양이온(Mg²⁺)이므로 원자가가 2입니다."},
    {"question": "KH₂PO₄ 1mM은 P를 몇 me/L 공급할까?", 
     "options": ["1", "2", "3", "4"],
     "answer": "1", 
     "explanation": "H₂PO₄⁻의 원자가는 1이므로, 1mM은 1me/L를 공급합니다."},
    {"question": "NO₃-N 14mg/L는 몇 ppm일까?", 
     "options": ["20", "10", "14", "28"],
     "answer": "3", 
     "explanation": "물 1L에서 1mg/L는 1ppm이므로, 14mg/L는 14ppm입니다."},
    {"question": "Ca(NO₃)₂·4H₂O 1mM은 Ca를 몇 me/L 공급할까?", 
     "options": ["3", "4", "1", "2"],
     "answer": "4", 
     "explanation": "Ca²⁺의 원자가는 2이므로 1mM × 2 = 2me/L입니다."},
    {"question": "K₂SO₄는 A액에 넣을까, B액에 넣을까?", 
     "options": ["둘 다 가능", "B액", "A액", "둘 다 안 됨"],
     "answer": "2", 
     "explanation": "SO₄²⁻가 포함돼 있어서 침전 방지를 위해 B액에 넣습니다."},
    {"question": "양액에서 질소는 어떤 형태로 공급될 수 있을까?", 
     "options": ["K-N만", "NH₄-N만", "NO₃-N과 NH₄-N", "NO₃-N만"],
     "answer": "3", 
     "explanation": "질소는 질산염(NO₃-N)과 암모늄(NH₄-N) 형태로 공급됩니다."},
    {"question": "Ca(NO₃)₂·2H₂O 1mM은 Ca를 몇 me/L 공급할까?", 
     "options": ["1", "2", "3", "4"],
     "answer": "2", 
     "explanation": "Ca²⁺의 원자가는 2이므로 1mM × 2 = 2me/L입니다."},
    {"question": "mM을 mg/L로 변환하려면 무엇을 곱해야 할까?", 
     "options": ["몰질량", "밀도", "원자가", "부피"],
     "answer": "1", 
     "explanation": "mM(몰 농도)을 질량(mg/L)으로 바꾸려면 몰질량(g/mol)을 곱합니다."},
    {"question": "NH₄NO₃ 80mg/L는 NH₄-N를 몇 me/L 공급할까? (몰질량: 80g/mol)", 
     "options": ["2", "3", "1", "4"],
     "answer": "3", 
     "explanation": "80mg/L ÷ 80g/mol = 1mM이고, NH₄⁺ 원자가 1이므로 1me/L입니다."},
    {"question": "SO₄-S 8me/L를 맞추려면 K₂SO₄ 몇 mM이 필요할까?", 
     "options": ["6", "8", "2", "4"],
     "answer": "4", 
     "explanation": "SO₄²⁻의 원자가는 2이므로 8me/L ÷ 2 = 4mM입니다."},
    {"question": "양액에서 P는 주로 어떤 비료에서 공급될까?", 
     "options": ["KNO₃", "MgSO₄", "KH₂PO₄", "Ca(NO₃)₂"],
     "answer": "3", 
     "explanation": "KH₂PO₄는 인(P)을 공급하는 대표적인 비료입니다."},
    {"question": "KNO₃ 101mg/L는 K를 몇 me/L 공급할까? (몰질량: 101g/mol)", 
     "options": ["2", "3", "4", "1"],
     "answer": "4", 
     "explanation": "101mg/L ÷ 101g/mol = 1mM이고, K⁺ 원자가 1이므로 1me/L입니다."},
    {"question": "MgSO₄·7H₂O는 어떤 액에 넣어야 할까?", 
     "options": ["A액", "둘 다 가능", "둘 다 안 됨", "B액"],
     "answer": "4", 
     "explanation": "SO₄²⁻가 포함돼 있어서 B액에 넣어야 침전이 생기지 않습니다."},
    {"question": "Ca²⁺ 10me/L를 Ca(NO₃)₂·4H₂O로 공급하면 몇 mg/L일까? (몰질량: 236g/mol)", 
     "options": ["1770", "1180", "590", "2360"],
     "answer": "2", 
     "explanation": "10me/L ÷ 원자가 2 = 5mM이고, 5 × 236 = 1180mg/L입니다."},
    {"question": "양액에서 K가 초과되면 어떤 문제가 생길 수 있을까?", 
     "options": ["뿌리 성장 촉진", "영양 불균형", "색깔 변화", "엽록소 증가"],
     "answer": "2", 
     "explanation": "K가 너무 많으면 다른 영양소 흡수를 방해할 수 있습니다."},
    {"question": "NO₃-N과 NH₄-N의 차이는 무엇일까?", 
     "options": ["흡수 속도", "냄새", "색깔", "맛"],
     "answer": "1", 
     "explanation": "NO₃-N은 빠르게 흡수되고, NH₄-N은 천천히 흡수됩니다."},
    {"question": "K₂SO₄ 1mM은 K를 몇 me/L 공급할까?", 
     "options": ["3", "4", "1", "2"],
     "answer": "4", 
     "explanation": "K₂SO₄는 K⁺ 2개를 제공하고 원자가 1이므로, 1mM × 2 = 2me/L입니다."},
    {"question": "NH₄NO₃는 어떤 원소를 공급할까?", 
     "options": ["K와 N", "NH₄-N과 NO₃-N", "Ca와 P", "Mg와 S"],
     "answer": "2", 
     "explanation": "NH₄NO₃는 암모늄 질소(NH₄-N)와 질산염 질소(NO₃-N)를 제공합니다."},
    {"question": "Ca(NO₃)₂·4H₂O 236mg/L는 NO₃-N를 몇 me/L 공급할까? (몰질량: 236g/mol)", 
     "options": ["3", "1", "2", "4"],
     "answer": "3", 
     "explanation": "236mg/L ÷ 236g/mol = 1mM이고, NO₃⁻ 2개이므로 1mM × 2 = 2me/L입니다."},
    {"question": "양액에서 Mg는 어떤 역할을 할까?", 
     "options": ["뿌리 성장", "꽃 피우기", "엽록소 형성", "열매 맺기"],
     "answer": "3", 
     "explanation": "Mg는 엽록소의 핵심 성분으로 광합성에 중요합니다."},
    {"question": "KNO₃ 2mM은 NO₃-N를 몇 me/L 공급할까?", 
     "options": ["1", "3", "4", "2"],
     "answer": "4", 
     "explanation": "NO₃⁻의 원자가는 1이므로 2mM × 1 = 2me/L입니다."},
    {"question": "SO₄-S 4me/L를 MgSO₄·7H₂O로 공급하면 몇 mg/L일까? (몰질량: 246g/mol)", 
     "options": ["246", "492", "738", "984"],
     "answer": "2", 
     "explanation": "4me/L ÷ 원자가 2 = 2mM이고, 2 × 246 = 492mg/L입니다."},
    {"question": "양액에서 P가 부족하면 어떤 문제가 생길까?", 
     "options": ["뿌리 발달 저하", "줄기 길어짐", "잎 색깔 변화", "꽃 과다"],
     "answer": "1", 
     "explanation": "P는 뿌리 발달과 에너지 전달에 필수입니다."},
    {"question": "KH₂PO₄ 136mg/L는 P를 몇 me/L 공급할까? (몰질량: 136g/mol)", 
     "options": ["2", "3", "4", "1"],
     "answer": "4", 
     "explanation": "136mg/L ÷ 136g/mol = 1mM이고, P 원자가 1이므로 1me/L입니다."},
    {"question": "K₂SO₄ 174mg/L는 SO₄-S를 몇 me/L 공급할까? (몰질량: 174g/mol)", 
     "options": ["3", "1", "2", "4"],
     "answer": "3", 
     "explanation": "174mg/L ÷ 174g/mol = 1mM이고, SO₄²⁻ 원자가 2이므로 1mM × 2 = 2me/L입니다."},
    {"question": "Ca²⁺와 PO₄³⁻가 섞이면 어떤 침전물이 생길까?", 
     "options": ["CaSO₄", "CaNO₃", "Ca₃(PO₄)₂", "CaK₂"],
     "answer": "3", 
     "explanation": "Ca²⁺와 PO₄³⁻는 Ca₃(PO₄)₂(인산칼슘)를 형성합니다."},
    {"question": "KNO₃는 A액과 B액 중 어디에 넣어도 괜찮을까?", 
     "options": ["아니요", "네", "A액만", "B액만"],
     "answer": "2", 
     "explanation": "KNO₃는 침전물을 만들지 않으므로 어느 액에나 넣을 수 있습니다."},
    {"question": "MgSO₄·7H₂O 1mM은 Mg를 몇 mg/L로 공급할까? (몰질량: 246g/mol)", 
     "options": ["492", "123", "738", "246"],
     "answer": "4", 
     "explanation": "1mM × 246g/mol = 246mg/L입니다."},
    {"question": "양액에서 Ca는 어떤 역할을 할까?", 
     "options": ["광합성 촉진", "뿌리 길어짐", "세포벽 형성", "열매 색깔"],
     "answer": "3", 
     "explanation": "Ca는 세포벽을 튼튼하게 만드는 데 중요합니다."},
    {"question": "NH₄NO₃ 1mM은 NO₃-N를 몇 me/L 공급할까?", 
     "options": ["2", "3", "4", "1"],
     "answer": "4", 
     "explanation": "NO₃⁻ 원자가 1이므로 1mM × 1 = 1me/L입니다."},
    {"question": "K₂SO₄ 2mM은 K를 몇 me/L 공급할까?", 
     "options": ["6", "2", "8", "4"],
     "answer": "4", 
     "explanation": "K⁺ 2개가 제공되고 원자가 1이므로 2mM × 2 = 4me/L입니다."},
    {"question": "Ca(NO₃)₂·4H₂O 472mg/L는 Ca를 몇 me/L 공급할까? (몰질량: 236g/mol)", 
     "options": ["6", "8", "2", "4"],
     "answer": "4", 
     "explanation": "472 ÷ 236 = 2mM이고, Ca²⁺ 원자가 2이므로 2mM × 2 = 4me/L입니다."},
    {"question": "양액에서 S는 어떤 비료에서 주로 공급될까?", 
     "options": ["KNO₃", "KH₂PO₄", "MgSO₄·7H₂O", "Ca(NO₃)₂"],
     "answer": "3", 
     "explanation": "MgSO₄·7H₂O는 황(S)을 SO₄-S 형태로 제공합니다."},
    {"question": "KH₂PO₄ 1mM은 K를 몇 me/L 공급할까?", 
     "options": ["2", "3", "4", "1"],
     "answer": "4", 
     "explanation": "K⁺ 원자가 1이므로 1mM × 1 = 1me/L입니다."},
    {"question": "NO₃-N 2me/L를 KNO₃로 공급하면 몇 mg/L일까? (몰질량: 101g/mol)", 
     "options": ["101", "303", "202", "404"],
     "answer": "3", 
     "explanation": "2me/L ÷ 원자가 1 = 2mM이고, 2 × 101 = 202mg/L입니다."},
    {"question": "양액에서 K는 어떤 역할을 할까?", 
     "options": ["뿌리 발달", "수분 조절", "열매 크기", "잎 두께"],
     "answer": "2", 
     "explanation": "K는 식물의 수분 조절과 광합성에 도움을 줍니다."},
    {"question": "MgSO₄·7H₂O 492mg/L는 SO₄-S를 몇 me/L 공급할까? (몰질량: 246g/mol)", 
     "options": ["6", "8", "2", "4"],
     "answer": "4", 
     "explanation": "492 ÷ 246 = 2mM이고, SO₄²⁻ 원자가 2이므로 2mM × 2 = 4me/L입니다."},
    {"question": "K₂SO₄ 348mg/L는 K를 몇 me/L 공급할까? (몰질량: 174g/mol)", 
     "options": ["6", "2", "8", "4"],
     "answer": "4", 
     "explanation": "348 ÷ 174 = 2mM이고, K⁺ 2개이므로 2mM × 2 = 4me/L입니다."},
    {"question": "Ca(NO₃)₂·4H₂O는 어떤 액에 넣어야 할까?", 
     "options": ["A액", "둘 다 가능", "B액", "둘 다 안 됨"],
     "answer": "1", 
     "explanation": "Ca²⁺가 포함돼 있어서 A액에 넣어야 침전이 생기지 않습니다."},
    {"question": "KH₂PO₄ 272mg/L는 P를 몇 me/L 공급할까? (몰질량: 136g/mol)", 
     "options": ["3", "1", "2", "4"],
     "answer": "3", 
     "explanation": "272 ÷ 136 = 2mM이고, P 원자가 1이므로 2mM × 1 = 2me/L입니다."},
    {"question": "양액에서 NH₄-N이 너무 많으면 어떤 문제가 생길까?", 
     "options": ["잎 성장 촉진", "줄기 길어짐", "뿌리 손상", "꽃 증가"],
     "answer": "3", 
     "explanation": "NH₄-N이 과다하면 뿌리에 독성을 줄 수 있습니다."},
    {"question": "KNO₃ 303mg/L는 NO₃-N를 몇 me/L 공급할까? (몰질량: 101g/mol)", 
     "options": ["1", "2", "3", "4"],
     "answer": "3", 
     "explanation": "303 ÷ 101 = 3mM이고, NO₃⁻ 원자가 1이므로 3mM × 1 = 3me/L입니다."}
]

@app.route('/')
def index():
    # 세션 초기화
    session.clear()
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    # 세션에 문제 번호와 점수 초기화
    if 'question_number' not in session:
        session['question_number'] = 1
        session['score'] = 0
        session['total_questions'] = 10
        # 사용된 문제 번호를 저장할 리스트 초기화
        session['used_questions'] = []
    
    # 10문제를 모두 풀었는지 확인
    if session['question_number'] > session['total_questions']:
        return redirect(url_for('final_result'))
    
    # 사용되지 않은 문제 중에서 랜덤하게 선택
    available_questions = [i for i in range(len(quiz_list)) if i not in session['used_questions']]
    if not available_questions:
        return redirect(url_for('final_result'))
    
    quiz_index = random.choice(available_questions)
    quiz = quiz_list[quiz_index]
    
    # 사용된 문제 번호 저장
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
    
    # 정답이면 점수 추가
    if is_correct:
        session['score'] += 10
    
    # 다음 문제 번호 증가
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

if __name__ == '__main__':
    # 컴퓨터 IP 주소 가져오기
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f' * Local IP: {local_ip}')
    print(f' * 접속 URL: http://{local_ip}:5000')
    
    # 외부 접속 허용 (모든 IP에서 접속 가능)
    app.run(host='0.0.0.0', port=5000)
