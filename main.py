import streamlit as st
from app.graph import app_graph

st.set_page_config(page_title="글로벌 콘텐츠 현지화 팩토리", layout="wide")

st.title("글로벌 콘텐츠 현지화 및 SEO 최적화 팩토리")
st.markdown("원본 콘텐츠를 입력하고 타겟 언어를 선택하면, AI가 동적 병렬 처리(Map-Reduce)를 통해 각 언어별 맞춤형 SEO 콘텐츠를 대량 생산합니다.")
st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    source_input = st.text_area(
        "원본 마케팅 콘텐츠 (블로그 글, 제품 설명서 등)",
        height=200,
        placeholder="예: 당사의 새로운 노이즈 캔슬링 무선 이어폰 '사운드맥스 프로'가 출시되었습니다. 최대 40시간의 배터리 수명과..."
    )

with col2:
    st.markdown("##### 타겟 언어 선택")
    langs = ["영어 (미국)", "일본어", "스페인어", "프랑스어", "독일어", "중국어 (간체)"]
    selected_langs = st.multiselect("현지화할 언어를 모두 선택하십시오.", langs, default=["영어 (미국)", "일본어"])

if st.button("다국어 현지화 및 SEO 생성 시작", type="primary", use_container_width=True):
    if source_input.strip() and selected_langs:
        initial_state = {
            "source_content": source_input,
            "target_languages": selected_langs,
            "localized_contents": []
        }

        st.subheader("실시간 처리 로그")
        log_container = st.container(border=True)
        final_state = None

        with st.spinner(f"[시스템] 원본 분석 및 {len(selected_langs)}개 언어에 대한 병렬 현지화를 진행 중입니다..."):
            for output in app_graph.stream(initial_state):
                for node_name, state_update in output.items():
                    with log_container:
                        if node_name == "analyzer":
                            st.info("원본 콘텐츠의 핵심 메시지 및 톤앤매너 분석을 완료했습니다.")
                        elif node_name == "localize":
                            st.success(f"개별 언어 현지화 및 SEO 키워드 매핑 노드가 완료되었습니다.")
                        elif node_name == "compiler":
                            st.info("모든 다국어 콘텐츠 병합을 완료했습니다.")
                    
                    final_state = state_update
        
        st.divider()
        st.subheader("최종 현지화 리포트")
        if final_state and final_state.get("final_output"):
            st.markdown(final_state.get("final_output"))
    
    else:
        st.warning("원본 콘텐츠를 입력하고 최소 1개 이상의 타겟 언어를 선택해 주십시오.")