"""Answer a question from the indexed docs and return the contexts used."""

import sys
from dataclasses import dataclass, field

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

from rag_app.settings import get_settings

PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Answer using ONLY the context below. If the answer is not in the context,"
     " say \"I don't know.\"\n\nContext:\n{context}"),
     ("human", "{question}"),
])

@dataclass
class RagResponse:
    question: str
    answer: str
    contexts: list[str]
    sources: list[str] = field(default_factory=list)

class RagPipeline:
    def __init__(self) -> None:
        s = get_settings()
        store = QdrantVectorStore.from_existing_collection(
            embedding=OpenAIEmbeddings(model=s.embedding_model,api_key=s.openai_api_key),
            collection_name= s.collection,
            path=s.qdrant_path
        )
        self.retriever = store.as_retriever(search_kwargs={"k":s.top_k})
        self.llm = ChatOpenAI(model=s.llm_model,api_key=s.openai_api_key,temperature=0)

    def answer(self,question:str) -> RagResponse:
        docs = self.retriever.invoke(question)
        contexts = [d.page_content for d in docs]
        messages = PROMPT.format_messages(
            context="\n\n--\n\n".join(contexts), question=question
        )
        reply = self.llm.invoke(messages)
        return RagResponse(
            question=question,
            answer=reply.content,
            contexts=contexts,
            sources=[d.metadata.get("source","")for d in docs],
        )

if __name__ == "__main__":
    result = RagPipeline().answer(" ".join(sys.argv[1:]))
    print(f"ANSWER:\n{result.answer}\n")
    for i, (ctx,src) in enumerate(zip(result.contexts, result.sources, strict=True),1):
        print(f"[{i}] {src}\n{ctx[:200]}...\n")