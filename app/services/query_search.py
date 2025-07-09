from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from typing import List

# 임베딩 모델 로드 (저장할 때와 동일해야 함)
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def search_comments(query: str, k: int = 5) -> List[Document]:
    """
    사용자의 질의(query)에 대해 FAISS 인덱스를 통해 관련 댓글 검색
    :param query: 사용자의 질문
    :param k: 검색 결과 개수
    :return: Document 객체 리스트
    """
    db = FAISS.load_local("kickon_vector_search/faiss_index", embedding_model, allow_dangerous_deserialization=True)
    return db.similarity_search(query, k=k)

# 테스트용 main
if __name__ == "__main__":
    test_query = "FC 서울 vs 인천"
    docs = search_comments(test_query)

    print(f"🔍 Query: {test_query}\n")
    for i, doc in enumerate(docs, 1):
        print(f"[{i}] {doc.page_content}")