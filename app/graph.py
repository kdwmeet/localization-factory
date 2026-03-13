import operator
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

load_dotenv()

# 상태 정의
class OverallState(TypedDict):
    source_content: str         # 원본 콘텐츠
    target_languages: list[str] # 타겟 언어 목록 (예: ["영어", "일본어", "스페인어"])
    core_message: str           # 원본에서 추출한 핵심 메시지 및 톤앤매너
    # 병렬 처리된 결과를 리스트에 안전하게 병합하기 위해 operator.add 사용
    localized_contents: Annotated[list[dict], operator.add]
    final_output: str           # 최종 취합된 결과 리포트
    
class LocalizeState(TypedDict):
    language: str               # 현재 할당된 타겟 언어
    core_message: str           # 원본 핵심 메시지
    source_content: str         # 원본 콘텐츠

# 노드 구현
def analyzer_node(state: OverallState):
    """원본 콘텐츠의 핵심 메시지와 브랜드 톤앤매너를 분석합니다."""
    llm = ChatOpenAI(model="gpt-5-mini", reasoning_effort="low")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 글로벌 콘텐츠 디렉터입니다. 원본 텍스트의 핵심 메시지, 타겟 고객, 그리고 톤앤매너(어조)를 분석하여 요약하십시오."),
        ("user", "{source_content}")        
    ])
    chain = prompt | llm
    core_message = chain.invoke({"source_content": state.get("source_content", "")}).content
    return {"core_message": core_message}

def localize_node(state:LocalizeState):
    """할당된 언어로 콘텐츠를 번역하고 현지 SEO 키워드를 삽입합니다."""
    llm = ChatOpenAI(model="gpt-5-mini", reasoning_effort="low")

    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 타겟 언어({language})의 원어민 카피라이터이자 SEO 전문가입니다.
다음 지시사항에 따라 콘텐츠를 현지화하십시오:
1. 원본 콘텐츠를 {language}로 자연스럽게 번역하십시오.
2. {language}를 사용하는 국가의 검색 엔진에서 자주 검색될 만한 관련 SEO 키워드 3~5개를 선정하십시오.
3. 선정된 키워드를 번역본 본문에 자연스럽게 녹여내십시오.
4. 결과는 'SEO 키워드 목록'과 '현지화된 콘텐츠'로 명확히 구분하여 작성하십시오."""),
        ("user", "원본 핵심 메시지: {core_message}\n\n원본 콘텐츠: {source_content}")
    ])
    
    chain = prompt | llm
    result = chain.invoke({
        "language": state.get("language", ""),
        "core_message": state.get("core_message", ""),
        "source_content": state.get("source_content", "")
    }).content

    # 결과를 리스트 형태로 반환하여 OvearallState의 localized_contents에 추가(add)되도록 함
    return {"localized_contents": [{"language": state.get("language", ""), "content": result}]}

def compiler_node(state: OverallState):
    """모든 언어로 현지화된 콘텐츠를 하나의 마크다운 포맷으로 취합합니다."""
    contents = state.get("localized_contents", [])

    final_text = "# 글로벌 콘텐츠 현지화 최종 리포트\n\n"
    final_text += f"**원본 핵심 메시지 분석:**\n{state.get('core_message', '')}\n\n---\n\n"

    for item in contents:
        lang = item.get("language", "알 수 없는 언어")
        content =item.get("content", "")
        final_text += f"## {lang} 현지화 결과\n\n{content}\n\n---\n\n"
    
    return {"final_output": final_text}

# 라우팅 로직 (Map=Reduce)
def continue_to_localize(state: OverallState):
    """타겟 언어 배열을 순회하며 개별 언어마다 localize_node를 병렬로 실행하도록 지시합니다."""
    target_languages = state.get("target_languages", [])

    # 타겟 언어마다 새로운 LocalizeState를 생성하여 localize_node로 전송(send)
    return [
        Send("localize", {
            "language": lang,
            "core_message": state.get("core_message", ""),
            "source_content": state.get("source_content", "")
        }) for lang in target_languages
    ]

# 그래프 조립 및 컴파일
workflow = StateGraph(OverallState)

workflow.add_node("analyzer", analyzer_node)
workflow.add_node("localize", localize_node)
workflow.add_node("compiler", compiler_node)

workflow.add_edge(START, "analyzer")
# analzyer 완료 후 타겟 언어 개수만큼 동적 분기(Fan-out)
workflow.add_conditional_edges("analyzer", continue_to_localize, ["localize"])
# 모든 localize 작업이 끝나면 compiler 노드로 병합(Fan-in)
workflow.add_edge("localize", "compiler")
workflow.add_edge("compiler", END)

app_graph = workflow.compile()
