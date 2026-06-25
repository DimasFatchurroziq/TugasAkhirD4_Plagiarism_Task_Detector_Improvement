from sentence_transformers import SentenceTransformer, util
from src.infrastructures.similarity.similarity import containment_similarity


class Tahap_7:

    def get_vector_similarity(self, embedding_list_1, embedding_list_2, min_sim_score):
        
        list_approved_paraphrases = []
        intersection = 0

        length_1 = len(embedding_list_1)
        length_2 = len(embedding_list_2)

        min_length = length_1 * length_2


        for data_1 in embedding_list_1:
            for data_2 in embedding_list_2:
                similarity_score = util.cos_sim(data_1["data"]["embedding"], data_2["data"]["embedding"]).item()
                if similarity_score >= min_sim_score:
                    intersection += 1
                    list_approved_paraphrases.append({
                        "block_1_id": data_1["data"]["block_id"],
                        "block_2_id": data_2["data"]["block_id"],
                        "score": similarity_score
                    })

        similarity = containment_similarity(intersection, min_length)

        return list_approved_paraphrases, similarity