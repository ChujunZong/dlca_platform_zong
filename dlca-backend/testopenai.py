# testopenai.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # 读取 .env 中的 OPENAI_API_KEY
client = OpenAI()

response = client.responses.create(
    model="gpt-4o-mini",               # 或 gpt-4o / gpt-5 等
    input="写一句话介绍 Neo4j 图数据库"
)

print(response.output_text)