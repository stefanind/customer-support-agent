from pathlib import Path
import re

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import MarkdownHeaderTextSplitter


KNOWLEDGE_DIRECTORY = Path(__file__).parent / "data" / "knowledge"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MIN_SIMILARITY = 0.25
TOP_K = 2


class MiniLMEmbeddings(Embeddings):
    """Run the MiniLM embedding model on this computer."""

    def __init__(self):

        from sentence_transformers import SentenceTransformer

        try:
            self.model = SentenceTransformer(MODEL_NAME, local_files_only=True)
        except OSError:
            self.model = SentenceTransformer(MODEL_NAME)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:

        encodings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False
        ).tolist() # numpy array -> to python list

        return encodings

    def embed_query(self, text: str) -> list[float]:

        # put in list since embed_documents expects it
        texts = [text] 

        embeddings = self.embed_documents(texts)

        first_embedding = embeddings[0]

        return first_embedding


def load_public_sections(directory: Path = KNOWLEDGE_DIRECTORY) -> list[Document]:
    """Load each public Markdown section as a searchable document."""

    splitter = MarkdownHeaderTextSplitter(
        [("#", "title"), ("##", "section")]
    )
    sections = []

    for path in sorted(directory.glob("*.md")):

        text = path.read_text(encoding="utf-8")

        # check to ensure that it isn't a private doc
        if not re.search(r"^access_level: public$", text, re.MULTILINE):
            continue

        # captures the doc_id at the top of the .md files
        doc_id = re.search(r"^doc_id: (.+)$", text, re.MULTILINE).group(1)

        # captures the body after the metadata
        body = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.DOTALL)

        # iterate over the body where it contains the text split on '#' and '##'
        for section in splitter.split_text(body):

            # only want docs where there is "section" in the metadata
            if "section" not in section.metadata:
                continue

            # add doc id and the path name to the Document metadata
            section.metadata.update({"doc_id": doc_id, "source": path.name})

            # splitter removes the headings naturally
            # so add them back into the page content to help the embeddings
            section.page_content = (
                f"{section.metadata['title']}\n"
                f"{section.metadata['section']}\n"
                f"{section.page_content}"
            )

            sections.append(section)

    return sections


# init to None 
_vector_store = None

# only create vector store when the function is called for the first time
def get_vector_store() -> InMemoryVectorStore:
    """Build the in-memory index once, then reuse it."""

    # assign globally rather than locally in the function
    global _vector_store

    if _vector_store is None:

        embedding_model = MiniLMEmbeddings()
        _vector_store = InMemoryVectorStore(embedding_model)

        sections = load_public_sections() 
        _vector_store.add_documents(sections)

    return _vector_store


def search_knowledge(question: str, vector_store=None) -> list[Document]:
    """Return the two most relevant public knowledge sections."""

    if not question.strip():
        return []

    # vector_store can be from tests/test_knowledge.py for testing
    store = vector_store or get_vector_store()

    # matches -> list[(Document, similarity_score)]
    matches = store.similarity_search_with_score(question, k=TOP_K) 

    # matches is returned in descending sorted order of the score
    # so matches[0][1] is the barrier for min similarity
    if not matches or matches[0][1] < MIN_SIMILARITY:
        return []

    return [document for document, _score in matches]
