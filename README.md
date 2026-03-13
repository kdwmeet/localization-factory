# Global Content Localization & SEO Factory (글로벌 콘텐츠 현지화 및 SEO 최적화 팩토리)

## 1. 프로젝트 개요

Global Content Localization & SEO Factory는 단일 언어로 작성된 마케팅 콘텐츠나 블로그 글을 다수의 타겟 언어로 동시에 번역하고, 각 국가의 검색 엔진 최적화(SEO) 키워드를 매핑하여 대량 생산하는 자동화 파이프라인입니다.

본 프로젝트는 LangGraph의 동적 병렬 처리(Map-Reduce) 아키텍처인 `Send` API를 핵심 기술로 사용합니다. 사용자가 선택한 타겟 언어의 개수만큼 서브 그래프(Sub-graph)를 동적으로 생성하여 동시에 현지화를 수행하므로, 번역 대상 언어가 늘어나도 처리 시간이 선형적으로 증가하지 않고 일정한 속도를 유지할 수 있습니다.

## 2. 시스템 아키텍처

본 시스템은 Map-Reduce 패턴을 적용하여 다음과 같은 분기(Fan-out) 및 병합(Fan-in) 워크플로우를 가집니다.

1. **Analyzer Node:** 원본 콘텐츠에서 핵심 메시지, 타겟 고객층, 브랜드의 톤앤매너(어조)를 분석하고 추출합니다.
2. **Dynamic Routing (Map/Fan-out):** 추출된 핵심 메시지와 원본 텍스트를 바탕으로, 사용자가 지정한 타겟 언어 배열을 순회하며 언어별로 `Localize Node`를 병렬 호출(`Send`)합니다.
3. **Localize Node (Parallel Execution):** * 할당된 언어의 원어민 및 SEO 전문가 페르소나를 부여받은 에이전트가 번역을 수행합니다.
   * 단순 직역을 피하고 원본의 톤앤매너를 현지 문화에 맞게 의역합니다.
   * 해당 국가의 검색 엔진에서 유입을 높일 수 있는 타겟 SEO 키워드 3~5개를 도출하여 본문에 자연스럽게 삽입합니다.
4. **Compiler Node (Reduce/Fan-in):** 모든 언어의 현지화 작업이 완료되면, 개별 결과물들을 취합하여 하나의 마크다운 리포트로 렌더링합니다.

## 3. 기술 스택

* **Language:** Python 3.10+
* **Package Manager:** uv
* **LLM:** OpenAI gpt-4o (현지화 및 SEO), gpt-4o-mini (원본 톤앤매너 분석)
* **Orchestration:** LangGraph (Send API 적용), LangChain (langchain_core)
* **Web Framework:** Streamlit

## 4. 프로젝트 구조

```text
localization-factory/
├── .env                  # OpenAI API 키 설정
├── requirements.txt      # 의존성 패키지 목록
├── main.py               # Streamlit 기반 다국어 현지화 관제 UI
└── app/
    ├── __init__.py
    └── graph.py          # 상태 정의, Map-Reduce 기반 동적 라우팅 워크플로우 구현
```

## 5. 설치 및 실행 가이드
### 5.1. 환경 변수 설정
프로젝트 루트 경로에 .env 파일을 생성하고 API 키를 입력하십시오.

```Ini, TOML
OPENAI_API_KEY=sk-your-api-key-here
```
### 5.2. 의존성 설치 및 앱 실행
가상환경을 구성하고 애플리케이션을 구동합니다.

```Bash
uv venv
uv pip install -r requirements.txt
uv run streamlit run main.py
```
## 6. 테스트 시나리오 및 검증 방법
1. **다국어 병렬 처리 검증**: 애플리케이션 실행 후 원본 마케팅 문구를 입력하고 3개 이상의 타겟 언어를 선택하여 실행합니다. 로그 화면에서 선택한 언어 개수만큼 현지화 노드가 병렬로 동시 실행되는지 확인합니다.

2. **톤앤매너 유지 검증**: 소셜 미디어용의 가벼운 문체로 작성된 원본을 입력했을 때, 출력된 다국어 결과물이 딱딱한 직역이 아닌 현지 트렌드에 맞는 유연한 문체로 번역되었는지 확인합니다.

3. **SEO 키워드 도출 검증**: 최종 결과물에서 각 언어별로 지정된 SEO 키워드가 해당 국가의 언어로 명확히 제시되었으며, 본문 내에 자연스럽게 배치되었는지 확인합니다.

## 7. 실행 화면
<img width="1299" height="792" alt="스크린샷 2026-03-13 102051" src="https://github.com/user-attachments/assets/8b6f835b-f1e6-4f31-95a1-1e2a6f3a8062" />
<img width="1300" height="825" alt="스크린샷 2026-03-13 102108" src="https://github.com/user-attachments/assets/d268e091-7d50-40b8-971c-9668dbd145da" />


