import os
import sys
from pathlib import Path

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

# 确保可以导入 app.config
_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _base not in sys.path:
    sys.path.insert(0, _base)

class EmotionAnalystRAG:
    """
    企业级情绪分析师 RAG 系统
    """
    def __init__(
        self,
        vector_db_uri: str | None = None,
        collection_name: str = "soulchat_collection",
        embedding_model_name: str = "BAAI/bge-small-zh-v1.5",
        llm_model_name: str = "qwen-plus",
        temperature: float = 0.4
    ):
        if vector_db_uri is None:
            base_dir = Path(__file__).resolve().parent
            vector_db_uri = str(base_dir / "chroma_db")

        # 1. 载入词嵌入模型
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs={'device': 'mps'}, # 针对 macOS 优化
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 2. 连接已有向量数据库
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=vector_db_uri
        )
        
        # 3. 配置支持多查询(Multi-Query)的高级 Retriever，提升检索鲁棒性
        from app.config import settings as app_settings
        self.llm = ChatOpenAI(
            model=llm_model_name,
            temperature=temperature,
            api_key=app_settings.openai_api_key,
            base_url=app_settings.openai_base_url,
        )
        base_retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        try:
            from langchain.retrievers.multi_query import MultiQueryRetriever
        except ModuleNotFoundError:
            MultiQueryRetriever = None

        if MultiQueryRetriever is None:
            self.retriever = base_retriever
        else:
            self.retriever = MultiQueryRetriever.from_llm(
                retriever=base_retriever,
                llm=self.llm
            )
        
        # 4. 构建陪伴式对话 Prompt
        self.prompt = PromptTemplate.from_template(
            """你是一个温暖、真诚的情绪陪伴者，名字叫"心语"。你不是心理医生，也不是冷冰冰的机器人。你是一个愿意倾听、能够共情的朋友。

你的说话方式：
- 像朋友聊天一样自然，不要用专业术语，不要说"根据知识库"或"参考片段"
- 先共情，再回应。不要一上来就给建议
- 适度使用温暖的口语表达："我懂"、"这种感觉真的很难受"、"谢谢你愿意告诉我"
- 不要用模板化的结构回复（不要列1234条），要自然地组织语言
- 回复长度适中，1-3段就好，不要太长

以下是你可以参考的陪伴知识和回应思路：
{context}

你需要回应的话：
{question}

自然地回应："""
        )
        
        # 5. 构建 RAG Pipeline (LCEL)
        self.rag_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def analyze_and_respond(self, user_input: str) -> str:
        print(f"🔄 正在检索知识库并分析请求: {user_input} ...")
        response = self.rag_chain.invoke(user_input)
        return response

if __name__ == "__main__":
    # 需要在环境变量中设置 OPENAI_API_KEY
    # export OPENAI_API_KEY="your-api-key"

    agent = EmotionAnalystRAG()
    
    test_queries = [
        "我因为系统扣错了费用，打给你们客服还不理我，我快气疯了，你们到底行不行啊！！！",
        "我最近每天晚上都做同样的噩梦，感觉生活好没有希望，甚至觉得不想活了。"
    ]
    
    for q in test_queries:
        print(f"\n🙋‍♂️ 用户诉求：{q}")
        print("🤖 开始响应...")
        reply = agent.analyze_and_respond(q)
        print(f"\n💡 分析结果：\n{reply}")
        print("="*60)
