from flask import Flask, request, jsonify, render_template
import os
from datetime import datetime
import time

# Import functions from existing modules
from search_engine import search_news
from gemini_writer import generate_blog_post

app = Flask(__name__)

TOPICS = {
    "Education": ["초등 교육", "중등 교육", "고교 교육", "학부모 교육", "대입", "초중고 교육 정책"],
    "AI": ["AI 최신 기술", "인공지능 트렌드", "인공지능 교육 활용", "생성형 AI"]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_post():
    data = request.json
    target_date_str = data.get('date')
    topic = data.get('topic')

    if not target_date_str or not topic:
        return jsonify({'error': '날짜와 주제를 모두 선택해주세요.'}), 400

    if topic not in TOPICS:
        return jsonify({'error': '유효하지 않은 주제입니다.'}), 400
        
    try:
        # target_date는 'YYYY-MM-DD' 형식의 문자열
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': '잘못된 날짜 형식입니다.'}), 400

    keyword_list = TOPICS[topic]
    all_search_data = []
    
    print(f"[{topic}] {target_date_str} 기사 검색 중...")
    
    for kw in keyword_list:
        # 각 키워드별로 검색 (키워드당 최대 3개씩)
        # target_date를 파라미터로 넘김 (수정된 search_engine.py 기준)
        results = search_news(topic=kw, target_date=target_date, max_results=3)
        if results:
            all_search_data.extend(results)
        time.sleep(1) # 검색 요청 간 짧은 대기 시간 추가 (차단 방지)

    if not all_search_data:
        return jsonify({'error': f'{target_date_str} 일자의 {topic} 관련 검색 결과가 없습니다.'}), 404

    print(f"[{topic}] 검색 완료! 총 {len(all_search_data)}개의 데이터로 제미나이 글 작성 시작...")
    
    # 제미나이를 통한 포스팅 작성
    blog_post_content = generate_blog_post(topic, all_search_data)

    if blog_post_content.startswith("에러"):
        return jsonify({'error': blog_post_content}), 500

    # (선택) 기존처럼 파일로도 저장
    OUTPUT_DIR = "posts"
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    filename = f"{OUTPUT_DIR}/{target_date_str.replace('-', '')}_{topic}_post.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(blog_post_content)

    return jsonify({
        'content': blog_post_content,
        'filename': filename,
        'message': '성공적으로 블로그 글이 생성되었습니다.'
    })

if __name__ == '__main__':
    # Flask 서버 실행
    app.run(debug=True, host='127.0.0.1', port=5000)
