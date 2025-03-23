from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline

# ✅ Define model name
model_name = "deepset/roberta-large-squad2"

# ✅ Initialize pipeline for question answering
qa_pipeline = pipeline('question-answering', model=model_name, tokenizer=model_name)


async def query_llm2(transcript_text: str, question: str) -> str:
    try:
        # ✅ Prepare input for the model
        QA_input = {
            'question': question,
            'context': transcript_text
        }

        result = qa_pipeline(QA_input)

        # ✅ Extract and return the answer
        answer = result['answer'].strip()

        if not answer:
            return "Sorry, I couldn't find an answer in the transcript."

        return answer

    except Exception as e:
        return f"Error during LLM processing: {str(e)}"
