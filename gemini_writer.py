import os
from google import genai
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def generate_blog_post(topic_title: str, search_data: list) -> str:
    """
    Generate a blog post using Gemini, providing the search data as context.
    """
    if not API_KEY or API_KEY == "이곳에_발급받으신_제미나이_API_키를_넣어주세요":
        return "에러: GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요."
    
    # 검색 데이터를 하나의 문자열 컨텍스트로 포맷팅
    context = ""
    for i, data in enumerate(search_data):
        context += f"[{i+1}] 제목: {data.get('title')}\n"
        context += f"내용: {data.get('snippet')}\n"
        context += f"출처: {data.get('source')} - {data.get('url')}\n\n"

    if topic_title == "Education":
        target_audience = "초등학생, 중학생, 고등학교 학부모 또는 학생들"
        main_focus = "자녀 교육과 진로, 학습에 어떻게 적용할 수 있는지 논리적인 이야기 흐름으로 엮어서"
    else:
        target_audience = "AI 기술에 관심이 많은 직장인 및 일반인들"
        main_focus = "AI 기술의 발전이 우리의 일상과 업무에 어떤 영향을 미치는지 구체적인 사례를 들어"

    # 프롬프트 작성
    prompt = f"""
당신은 네이버 블로그에 유익한 전문 칼럼을 작성하는 인플루언서 블로거입니다. 
다음은 특정 일자의 '{topic_title}'에 관해 검색된 주요 뉴스 및 요약 정보입니다.

{context}

위 정보를 바탕으로 {target_audience}이(가) 알면 좋은 유익하고 가독성 좋은 블로그 포스팅을 작성해 주세요. 

[작성 가이드라인]
1. 제목: 독자들이 클릭하고 싶게 만드는 매력적인 제목을 작성해 주세요. (제목 태그 없이 그냥 작성)
2. 구조: 서론(이슈 핵심 요약) - 본론(뉴스 정리 및 전문적인 인사이트) - 결론(요약 및 시사점)의 구조로 작성해 주세요. 불필요한 일상 인사말은 완전히 제외해 주세요.
3. 톤앤매너: "~입니다", "~합니다" 형태의 신뢰감을 주는 전문적인 어체를 사용해 주세요. ("~요", "~해요" 체 사용 절대 금지)
4. 내용 구성: 검색된 정보를 단순히 나열하지 말고, {main_focus} 전문 칼럼처럼 작성해 주세요. 
5. 서식: 글을 산만하게 만드는 이모티콘(😊등) 사용은 최소화(또는 제외)해 주세요. 또한 글 내에 강조를 위한 ** 기호는 사용하지 마세요.
6. 출처: 제공된 검색 데이터의 출처 링크들을 글 마지막에 '참고자료' 섹션으로 정리해서 남겨주세요.
"""
    
    try:
        client = genai.Client(api_key=API_KEY)
        # 비용 문제(429 에러) 발생 시 더 저렴하고 빠른 flash 모델로 변경하여 시도
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        error_msg = f"에러: 제미나이 API 호출 중 오류가 발생했습니다: {e}\n"
        return error_msg
