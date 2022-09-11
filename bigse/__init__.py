import os
from sentence_transformers import SentenceTransformer
import torch
import dotenv
from bigse.database import manager

dotenv.load_dotenv(".env")

model = SentenceTransformer('all-MiniLM-L6-v2')
# Check if CUDA is available ans switch to GPU
if torch.cuda.is_available():
   model = model.to(torch.device("cuda"))

dbm = manager.DatabaseInteractionManager()
dbm.create_schema()
dbm.close_connection()
