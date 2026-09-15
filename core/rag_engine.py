import os

from langchain_groq import ChatGroq #LLM
from langchain_core.prompts import ChatPromptTemplate #Sys behave blahblah
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from core.vector_store import ( #Three functionalities from vector_store.py
    build_vector_store,
    load_vector_store,
    get_retriever
)


def get_llm(): #LLM LAO TO GENERATE THE ANS OBVI
    return ChatGroq(
        model="openai/gpt-oss-20b",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
        max_tokens=1000
    )


def format_docs(docs): #DOCS FORMAT KRNE JISMAI PAGE CONTENT WRAP KIYA THA, list -> string
    return "\n\n".join(
        doc.page_content
        for doc in docs
    )


def build_rag_chain(transcript: str):
    vector_store = build_vector_store(transcript) #Transcript in vector store, build vector store call krke

    retriever = get_retriever(
        vector_store,
        k=10
    )

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
"""
You are an AI meeting assistant.

Answer the user's question ONLY using the provided
meeting transcript context.

Rules:
- Use the transcript context carefully.
- Do not use outside knowledge.
- Do not invent information.
- If the answer is present in the context, answer it directly.
- Use related information from the context even if the
  exact wording of the question is different.
- For questions about decisions, distinguish between a proposal
  and an actually accepted decision.
- A suggestion or proposal is NOT automatically a decision.
- Phrases such as "I suggest", "maybe we should", "how about",
  or "let's try" do NOT by themselves prove that the group
  accepted the proposal.
- Treat something as a decision only when the transcript clearly
  shows that participants accepted, agreed to, confirmed,
  approved, chose, finalized, or committed to it.
- If a proposal is followed by clear acceptance or confirmation,
  treat it as a decision.
- If there is no clear acceptance or confirmation, describe it
  as proposed or discussed, NOT decided.
- If the evidence is ambiguous, say that the transcript does not
  clearly establish whether it was adopted. Do not guess.
- When asked "What was decided about X?", first determine whether
  X was actually accepted. If it was only proposed or discussed,
  say so instead of calling it a decision.
- For questions about action items, identify the task and
  responsible person if explicitly mentioned.
- Keep the answer concise and clear.
- Only say "I could not find this information in the meeting transcript."
  when the required information is genuinely absent from the context.

Meeting transcript context:

{context}
"""
        ),
        ("human", "{question}")
    ])

    rag_chain = ( #full LCEL Pipeline
        {
            "context": retriever | RunnableLambda(format_docs), #relevant chunks retrieved nd docs returned in string format as did in functionality before
            "question": RunnablePassthrough() #runnable pass thru meaning i d have the ques but yeh func trigeer jab hota hai it will get passed directly
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def load_rag_chain(transcript: str): #Create upar kiya ab load krre
    vector_store = load_vector_store(transcript)

    retriever = get_retriever(
        vector_store,
        k=10
    )

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
"""
You are an AI meeting assistant.

Answer the user's question ONLY using the provided
meeting transcript context.

Rules:
- Use the transcript context carefully.
- Do not use outside knowledge.
- Do not invent information.
- If the answer is present in the context, answer it directly.
- Use related information from the context even if the
  exact wording of the question is different.
- For questions about decisions, distinguish between a proposal
  and an actually accepted decision.
- A suggestion or proposal is NOT automatically a decision.
- Phrases such as "I suggest", "maybe we should", "how about",
  or "let's try" do NOT by themselves prove that the group
  accepted the proposal.
- Treat something as a decision only when the transcript clearly
  shows that participants accepted, agreed to, confirmed,
  approved, chose, finalized, or committed to it.
- If a proposal is followed by clear acceptance or confirmation,
  treat it as a decision.
- If there is no clear acceptance or confirmation, describe it
  as proposed or discussed, NOT decided.
- If the evidence is ambiguous, say that the transcript does not
  clearly establish whether it was adopted. Do not guess.
- When asked "What was decided about X?", first determine whether
  X was actually accepted. If it was only proposed or discussed,
  say so instead of calling it a decision.
- For questions about action items, identify the task and
  responsible person if explicitly mentioned.
- Keep the answer concise and clear.
- Only say "I could not find this information in the meeting transcript."
  when the required information is genuinely absent from the context.

Meeting transcript context:

{context}
"""
        ),
        ("human", "{question}")
    ])

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def ask_question(rag_chain, question: str):
    try:
        answer = rag_chain.invoke(question)
        return answer

    except Exception as e:
        error_message = str(e)

        if "429" in error_message or "rate limit" in error_message.lower():
            return "Groq API rate limit exceeded. Please wait and try again."

        return "Sorry, I could not process your question right now."