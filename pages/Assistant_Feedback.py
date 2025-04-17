import streamlit as st
import streamlit_survey as ss
import uuid
import datetime
import boto3

# DynamoDB setup
session = boto3.Session()
dynamodb = session.resource('dynamodb', region_name='eu-west-1')
table = dynamodb.Table('chatbot_feedback')

def main():
    st.set_page_config(page_title="Faber - Feedback", page_icon="assets/chatbotlogocropped.png")

    st.header("📋 Review your previous chat with Faber")

    try:
        # Ensure chat history is long enough (at least one user question + assistant answer)
        if "messages" in st.session_state and len(st.session_state.messages) > 1:
            qna_pairs = []

            # Create Q&A pairs: every user message + assistant response
            for i in range(1, len(st.session_state.messages), 2):
                user_msg = st.session_state.messages[i]
                assistant_msg = st.session_state.messages[i + 1] if i + 1 < len(st.session_state.messages) else {"role": "assistant", "content": "(No response)"}
                qna_pairs.append((user_msg, assistant_msg))

            survey = ss.StreamlitSurvey("Faber Feedback Survey")
            npages = len(qna_pairs)
            page = survey.pages(npages, on_submit=lambda: st.success("✅ Thanks! Your feedback has been saved."))

            with page:
                """#### 💬 Chat Excerpt"""
                for message in qna_pairs[page.current]:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                """#### 📝 Your Feedback"""
                col1, col2 = st.columns([1, 2])
                with col1:
                    survey.text_input("User alias:")
                with col2:
                    survey.select_slider(
                        "How helpful was the answer?",
                        options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                        id=f"likert_{page.current}"
                    )

                survey.text_area("Additional comments or suggestions:", id=f"notes_{page.current}")

                # Add Q&A pair to survey data (so we save the reviewed content as well)
                qna_pair_id = f"qna_pair_{page.current}"
                survey_data_key = '__streamlit-survey-data_Faber Feedback Survey'
                if survey_data_key in st.session_state:
                    st.session_state[survey_data_key][qna_pair_id] = {
                        "question": qna_pairs[page.current][0]['content'],
                        "answer": qna_pairs[page.current][1]['content']
                    }

            # Save to DynamoDB once survey is submitted
            if st.session_state.get('__streamlit-survey-data_Faber Feedback Survey_Pages__btn_submit') == True:
                feedback_json = survey.to_json()
                table.put_item(Item={
                    'datetime': str(datetime.datetime.now()),
                    'SessionId': str(uuid.uuid4()),
                    'info': feedback_json
                })

        else:
            st.warning("💡 The conversation history is empty. Please chat with Faber first before leaving feedback.")

    except AttributeError:
        st.info("🔄 Start a conversation with Faber, then come back here to provide your feedback.")

if __name__ == '__main__':
    main()
