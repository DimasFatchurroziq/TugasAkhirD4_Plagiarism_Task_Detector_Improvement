# from sentence_transformers import SentenceTransformer

# class SentenceBert:
#     def __init__(self, model_name="firqaaa/indo-sentence-bert-base"): #sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
#         self.model = SentenceTransformer(model_name)

#     def get_tuple(self, list_rule_objects):
#         list_contents = [rule.content for rule in list_rule_objects]
#         return list_contents   
    
#     def get_embedding(self, list_contents):
#         """Mengubah kalimat menjadi embedding vektor"""
#         embeddings = self.model.encode(list_contents, convert_to_tensor=True)
#         return embeddings

#     def embedding_content_tupple(self, list_rule_objects):
#         list_contents = self.get_tuple(list_rule_objects)
#         list_embeddings = self.get_embedding(list_contents)
#         return list_embeddings       

    
