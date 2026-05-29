import os
import shutil
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def process_markdown_knowledge_base(md_file_path: str):
    """
    读取企业级 Markdown 知识库，并智能切分成 Chunks。
    """
    if not os.path.exists(md_file_path):
        raise FileNotFoundError(f"找不到知识库文件: {md_file_path}")

    # 读取纯文本
    loader = TextLoader(md_file_path, encoding='utf-8')
    docs = loader.load()
    
    # 针对 Markdown 进行基于标题层级的智能切分
    # 这样每个切片都会保留它是属于哪个标题（如 3.1 核心负面情绪）的上下文
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    # 将加载好的纯文本进行切分
    md_header_splits = markdown_splitter.split_text(docs[0].page_content)
    
    # 补充基础 Metadata
    for split in md_header_splits:
        split.metadata["source"] = md_file_path
        split.metadata["type"] = "enterprise_knowledge_base"

    return md_header_splits

def build_vector_db():
    # 数据集路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    kb_path = os.path.join(base_dir, "emotion_knowledge_base.md")
    
    print(f"📄 正在读取并处理企业级知识库: {kb_path}")
    chunks = process_markdown_knowledge_base(kb_path)
    print(f"✅ 成功将 Markdown 知识库智能切分为 {len(chunks)} 个语义区块（Chunks）。\n")
    
    # === 开始存入向量数据库 ===
    # 1. 配置 Embedding 模型
    print("⏳ 正在加载 Embedding 模型 (BAAI/bge-small-zh-v1.5)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-zh-v1.5",
        model_kwargs={'device': 'mps'}, # 使用 macOS mps 加速，如果没有mps可改为cpu
        encode_kwargs={'normalize_embeddings': True}
    )

    # 2. 定义 Chroma 向量数据库的本地持久化路径
    chroma_uri = os.path.join(base_dir, "chroma_db")
    collection_name = "soulchat_collection"

    # 清理旧的目录，避免重复叠加
    if os.path.exists(chroma_uri):
        try:
            shutil.rmtree(chroma_uri)
            print("已经清理旧的 Collection 数据。")
        except Exception as e:
            print(f"清理旧数据时提示: {e}")

    # 3. 将 chunks 存入 Chroma 向量数据库
    print(f"⏳ 正在计算向量并将数据存入本地 Chroma 数据库: {chroma_uri}")
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=chroma_uri,
        collection_name=collection_name
    )
    
    print("🎉 知识库向量化并持久化存储成功！现在可以启动 FastAPI 服务进行测试了。")

if __name__ == "__main__":
    build_vector_db()
