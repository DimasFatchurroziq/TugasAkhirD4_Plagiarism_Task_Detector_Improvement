# services/job_service.py
import os
import uuid
from src.models.model import Document

from src.api.v1.schemas.job_schema import JobUpdate 
from src.api.v1.schemas.document_schema import DocumentUpdate
from src.api.v1.schemas.comparison_schema import ComparisonCreate, ComparisonUpdate

from typing import List

from itertools import combinations



class ProcessService:
    def __init__(self, compare_serv, rkrgst_serv,
        sbert_model_instance,
        tahap1_serv, tahap2_serv, tahap3_serv, tahap4_serv, tahap5_serv, tahap6_serv, tahap7_serv,
        job_repo, doc_repo, block_repo, map_repo, hash_repo, compare_repo, rkrgst_repo, sbert_repo, block_embed_repo
    ):
        self.compare_serv = compare_serv
        self.rkrgst_serv = rkrgst_serv
        self.sbert_model_instance = sbert_model_instance
        
        self.tahap1_serv = tahap1_serv
        self.tahap2_serv = tahap2_serv
        self.tahap3_serv = tahap3_serv
        self.tahap4_serv = tahap4_serv
        self.tahap5_serv = tahap5_serv
        self.tahap6_serv = tahap6_serv
        self.tahap7_serv = tahap7_serv

        self.job_repo = job_repo
        self.doc_repo = doc_repo
        self.block_repo = block_repo
        self.map_repo = map_repo
        self.hash_repo = hash_repo
        self.compare_repo = compare_repo
        self.rkrgst_repo = rkrgst_repo
        self.sbert_repo = sbert_repo
        self.block_embed_repo = block_embed_repo
        
    async def process_job_multiple(self, job_id: str):

        job = await self.job_repo.get(job_id)
        if not job:
            raise Exception("Job not found")

        recount = False

        if job.status == "MODIFIED":
            recount = True
            print("True")

        status = "RUNNING"
        payload = JobUpdate(
            status=status,
        )
        await self.job_repo.update(job, payload)

        job_weight_text = job.weight_text
        job_weight_code = job.weight_code
        job_weight_phrase = job.weight_phrase
        job_threshold = job.threshold

        optional_denominator = job_weight_text + job_weight_code

        docs = await self.doc_repo.get_all_by_job(job_id)

        process_docs = len(docs)

        processed = 0

        for doc in docs:
            if doc.status != "UPLOADED":
                continue

            try:
                # update status
                status = "PROCESSING"
                payload = DocumentUpdate(
                    status=status,
                )
                await self.doc_repo.update(doc, payload)

                list_blocks = await self.tahap1_serv.structure_extract(doc.path)

                if list_blocks:
                    final_data, full_cleaned = await self.tahap2_serv.preprocessing(list_blocks)
                else:
                    final_data, full_cleaned = [], {"full_cleaned_text":[], "full_cleaned_code":[]}

                inserted_blocks = await self.block_repo.create_blocks_with_mappings(doc.id, final_data)

                if full_cleaned["full_cleaned_text"]:
                    final_hash_text = await self.tahap3_serv.rollinghash(full_cleaned["full_cleaned_text"], 3, 4)
                    await self.hash_repo.create_hash(doc.id, final_hash_text, "TEXT")

                if full_cleaned["full_cleaned_code"]:
                    final_hash_code = await self.tahap3_serv.rollinghash(full_cleaned["full_cleaned_code"], 3, 4)
                    await self.hash_repo.create_hash(doc.id, final_hash_code, "CODE")

                processed += 1

                # update status
                status = "DONE"
                payload = DocumentUpdate(
                    status=status,
                )
                await self.doc_repo.update(doc, payload)


                print("processed:", processed, "/", process_docs)

            except Exception as e:
                # kalau gagal, tandai error
                status = "ERROR"
                payload = DocumentUpdate(
                    status=status,
                )
                await self.doc_repo.update(doc, payload)

                print(f"Error processing doc {doc.id}: {e}")


        #update progress
        progress = 30
        payload = JobUpdate(
            progress=progress,
        )
        await self.job_repo.update(job, payload)

        hash_cache = {}
        blocks_cache = {}

        for doc in docs:
            hash_cache[doc.id] = await self.hash_repo.get_by_doc(doc.id)
            blocks_cache[doc.id] = await self.block_repo.get_by_doc_with_map_embed(doc.id, "TEXT")

        result = []
        compare_docs = process_docs * (process_docs - 1) / 2
        compare = 0
        for doc_1, doc_2 in combinations(docs, 2):

            try:
            
                comparison = await self.compare_serv.get_by_doc1_doc2(doc_1.id, doc_2.id)
                if comparison:
                    if recount:
                        print("modified")

                        pair_text_score = comparison.text_score
                        pair_code_score = comparison.code_score
                        pair_phrase_score = comparison.phrase_score

                        if job_weight_phrase == 0:
                            job_weight_text = job_weight_text/optional_denominator
                            job_weight_code = job_weight_code/optional_denominator

                            final_score = pair_text_score*job_weight_text + pair_code_score*job_weight_code

                        else:
                            final_score = pair_text_score*job_weight_text + pair_code_score*job_weight_code + pair_phrase_score*job_weight_phrase

                        if final_score >= job_threshold/100:
                            is_plagiat = True
                        else:
                            is_plagiat = False

                        payload = ComparisonUpdate(
                            final_score=final_score,
                            is_plagiat = is_plagiat
                        )

                        await self.compare_repo.update(comparison, payload)

                    continue
                    
                comparison = await self.compare_repo.create_compare(doc_1.id, doc_2.id)

                hash_1 = hash_cache[doc_1.id]
                hash_2 = hash_cache[doc_2.id]

                hash_text_1, fingerprint_text_1 = self.get_hash_by_type(hash_1, "TEXT")
                hash_code_1, fingerprint_code_1 = self.get_hash_by_type(hash_1, "CODE")

                hash_text_2, fingerprint_text_2 = self.get_hash_by_type(hash_2, "TEXT")
                hash_code_2, fingerprint_code_2 = self.get_hash_by_type(hash_2, "CODE")

                if fingerprint_text_1 and fingerprint_text_2:
                    double_tiles_text_list, length_text_1, length_text_2 = self.tahap4_serv.rkr(
                        fingerprint_text_1, fingerprint_text_2, hash_text_1, hash_text_2, 10
                    )
                else:
                    # Jika salah satu/keduanya None, amankan dengan memberikan list kosong
                    double_tiles_text_list, length_text_1, length_text_2 = [], 0, 0

                if fingerprint_code_1 and fingerprint_code_2:
                    double_tiles_code_list, length_code_1, length_code_2 = self.tahap4_serv.rkr(fingerprint_code_1, fingerprint_code_2, hash_code_1, hash_code_2, 10)
                else:
                    # Jika salah satu/keduanya None, set nilai default kosong
                    double_tiles_code_list, length_code_1, length_code_2 = [], 0, 0
                    
                rkrgst_text = await self.rkrgst_serv.create_rkrgst_bulk(comparison.id, double_tiles_text_list, "TEXT")
                rkrgst_code = await self.rkrgst_serv.create_rkrgst_bulk(comparison.id, double_tiles_code_list, "CODE")


                ############################################################################################################################################3

                blocks_1 = blocks_cache[doc_1.id]
                blocks_2 = blocks_cache[doc_2.id]

                embedding_list_1 = self.tahap6_serv.embedding_sentence(blocks_1, double_tiles_text_list, 0, 4, self.sbert_model_instance)
                embedding_list_2 = self.tahap6_serv.embedding_sentence(blocks_2, double_tiles_text_list, 1, 4, self.sbert_model_instance)

                for item in embedding_list_1:
                    if not item["is_exist"]:
                        await self.block_embed_repo.create_block_embed(item["data"])

                for item in embedding_list_2:
                    if not item["is_exist"]:
                        await self.block_embed_repo.create_block_embed(item["data"])

                list_approved_paraphrases, similarity_phrase = self.tahap7_serv.get_vector_similarity(embedding_list_1, embedding_list_2, 0.9)

                for item in list_approved_paraphrases:
                    await self.sbert_repo.create_sbert(comparison.id, item)

                ###################################################################################################################################


                similarity_text_1, similarity_text_2 = self.tahap5_serv.similarity(double_tiles_text_list, length_text_1, length_text_2)
                similarity_code_1, similarity_code_2 = self.tahap5_serv.similarity(double_tiles_code_list, length_code_1, length_code_2)

                if job_weight_phrase == 0:
                    job_weight_text = job_weight_text/optional_denominator
                    job_weight_code = job_weight_code/optional_denominator

                    final_score = similarity_text_2*job_weight_text + similarity_code_2*job_weight_code

                else:
                    final_score = similarity_text_2*job_weight_text + similarity_code_2*job_weight_code + similarity_phrase*job_weight_phrase
                
                if final_score >= job_threshold/100:
                    is_plagiat = True
                else:
                    is_plagiat = False
                
                payload = ComparisonUpdate(
                    text_score=similarity_text_2,
                    code_score=similarity_code_2,
                    phrase_score=similarity_phrase,
                    final_score=final_score,
                    is_plagiat = is_plagiat
                )

                await self.compare_repo.update(comparison, payload)
                
                result.append({
                    "doc_1": doc_1.name,
                    "doc_2": doc_2.name,
                    "text_j": similarity_text_1,
                    "code_j": similarity_code_1,
                    "text_c": similarity_text_2,
                    "code_c": similarity_code_2
                })

                compare += 1

                print("compare:", compare, "/", compare_docs)

            except Exception as e:
                # Menangani error jika salah satu kombinasi gagal diproses
                print(f"Error comparing {doc_1.id} and {doc_2.id}: {e}")
                
                # Opsi: Update status JOB menjadi ERROR agar user tahu ada yang gagal
                await self.job_repo.update(job, JobUpdate(status="ERROR"))
                
                # Gunakan 'continue' agar loop tetap berjalan mengecek pasangan lainnya
                continue

        current_job = await self.job_repo.get(job_id)
        if current_job and current_job.status != "ERROR":
            status = "COMPLETED"
            progress = 100
            payload = JobUpdate(
                status=status,
                progress=progress,
            )
            await self.job_repo.update(job, payload)

        return {
            "message": "Batch processing finished",
            "job_id": job_id,
        }


###########################################################################################################3333


    async def process_job_single(self, job_id: str):

        job = await self.job_repo.get(job_id)
        if not job:
            raise Exception("Job not found")

        recount = False

        if job.status == "MODIFIED":
            recount = True
            print("True")

        status = "RUNNING"
        payload = JobUpdate(
            status=status,
        )
        await self.job_repo.update(job, payload)

        job_weight_text = job.weight_text
        job_weight_code = job.weight_code
        job_weight_phrase = job.weight_phrase
        job_threshold = job.threshold

        optional_denominator = job_weight_text + job_weight_code

        docs = await self.doc_repo.get_all_by_job(job_id)

        process_docs = len(docs)

        processed = 0

        for doc in docs:
            if doc.status != "UPLOADED":
                continue

            try:
                # update status
                status = "PROCESSING"
                payload = DocumentUpdate(
                    status=status,
                )
                await self.doc_repo.update(doc, payload)

                list_blocks = await self.tahap1_serv.structure_extract(doc.path)

                if list_blocks:
                    final_data, full_cleaned = await self.tahap2_serv.preprocessing(list_blocks)
                else:
                    final_data, full_cleaned = [], {"full_cleaned_text":[], "full_cleaned_code":[]}

                inserted_blocks = await self.block_repo.create_blocks_with_mappings(doc.id, final_data)

                if full_cleaned["full_cleaned_text"]:
                    final_hash_text = await self.tahap3_serv.rollinghash(full_cleaned["full_cleaned_text"], 3, 4)
                    await self.hash_repo.create_hash(doc.id, final_hash_text, "TEXT")

                if full_cleaned["full_cleaned_code"]:
                    final_hash_code = await self.tahap3_serv.rollinghash(full_cleaned["full_cleaned_code"], 3, 4)
                    await self.hash_repo.create_hash(doc.id, final_hash_code, "CODE")

                processed += 1

                # update status
                status = "DONE"
                payload = DocumentUpdate(
                    status=status,
                )
                await self.doc_repo.update(doc, payload)


                print("processed:", processed, "/", process_docs)

            except Exception as e:
                # kalau gagal, tandai error
                status = "ERROR"
                payload = DocumentUpdate(
                    status=status,
                )
                await self.doc_repo.update(doc, payload)

                print(f"Error processing doc {doc.id}: {e}")


        #update progress
        progress = 30
        payload = JobUpdate(
            progress=progress,
        )
        await self.job_repo.update(job, payload)

        hash_cache = {}
        blocks_cache = {}
        
        for doc in docs:
            hash_cache[doc.id] = await self.hash_repo.get_by_doc(doc.id)
            blocks_cache[doc.id] = await self.block_repo.get_by_doc_with_map_embed(doc.id, "TEXT")

        result = []

        docs_1 = await self.doc_repo.get_all_by_job_category(job_id, "ONE")
        docs_2 = await self.doc_repo.get_all_by_job_category(job_id, "MANY")

        len_docs_1 = len(docs_1)
        len_docs_2 = len(docs_2)
        compare_docs = len_docs_1 * len_docs_2
        compare = 0
        for doc_1 in docs_1:
            for doc_2 in docs_2:

                try:
                
                    comparison = await self.compare_serv.get_by_doc1_doc2(doc_1.id, doc_2.id)
                    if comparison:
                        if recount:
                            print("modified")

                            pair_text_score = comparison.text_score
                            pair_code_score = comparison.code_score
                            pair_phrase_score = comparison.phrase_score

                            if job_weight_phrase == 0:
                                job_weight_text = job_weight_text/optional_denominator
                                job_weight_code = job_weight_code/optional_denominator

                                final_score = pair_text_score*job_weight_text + pair_code_score*job_weight_code

                            else:
                                final_score = pair_text_score*job_weight_text + pair_code_score*job_weight_code + pair_phrase_score*job_weight_phrase

                            if final_score >= job_threshold/100:
                                is_plagiat = True
                            else:
                                is_plagiat = False

                            payload = ComparisonUpdate(
                                final_score=final_score,
                                is_plagiat = is_plagiat
                            )

                            await self.compare_repo.update(comparison, payload)

                        continue
                        
                    comparison = await self.compare_repo.create_compare(doc_1.id, doc_2.id)
                    
                    hash_1 = hash_cache[doc_1.id]
                    hash_2 = hash_cache[doc_2.id]

                    hash_text_1, fingerprint_text_1 = self.get_hash_by_type(hash_1, "TEXT")
                    hash_code_1, fingerprint_code_1 = self.get_hash_by_type(hash_1, "CODE")

                    hash_text_2, fingerprint_text_2 = self.get_hash_by_type(hash_2, "TEXT")
                    hash_code_2, fingerprint_code_2 = self.get_hash_by_type(hash_2, "CODE")

                    if fingerprint_text_1 and fingerprint_text_2:
                        double_tiles_text_list, length_text_1, length_text_2 = self.tahap4_serv.rkr(
                            fingerprint_text_1, fingerprint_text_2, hash_text_1, hash_text_2, 10
                        )
                    else:
                        # Jika salah satu/keduanya None, amankan dengan memberikan list kosong
                        double_tiles_text_list, length_text_1, length_text_2 = [], 0, 0

                    if fingerprint_code_1 and fingerprint_code_2:
                        double_tiles_code_list, length_code_1, length_code_2 = self.tahap4_serv.rkr(fingerprint_code_1, fingerprint_code_2, hash_code_1, hash_code_2, 10)
                    else:
                        # Jika salah satu/keduanya None, set nilai default kosong
                        double_tiles_code_list, length_code_1, length_code_2 = [], 0, 0

                    rkrgst_text = await self.rkrgst_serv.create_rkrgst_bulk(comparison.id, double_tiles_text_list, "TEXT")
                    rkrgst_code = await self.rkrgst_serv.create_rkrgst_bulk(comparison.id, double_tiles_code_list, "CODE")


                    ############################################################################################################################################3

                    blocks_1 = blocks_cache[doc_1.id]
                    blocks_2 = blocks_cache[doc_2.id]

                    embedding_list_1 = self.tahap6_serv.embedding_sentence(blocks_1, double_tiles_text_list, 0, 4, self.sbert_model_instance)
                    embedding_list_2 = self.tahap6_serv.embedding_sentence(blocks_2, double_tiles_text_list, 1, 4, self.sbert_model_instance)

                    for item in embedding_list_1:
                        if not item["is_exist"]:
                            await self.block_embed_repo.create_block_embed(item["data"])

                    for item in embedding_list_2:
                        if not item["is_exist"]:
                            await self.block_embed_repo.create_block_embed(item["data"])

                    list_approved_paraphrases, similarity_phrase = self.tahap7_serv.get_vector_similarity(embedding_list_1, embedding_list_2, 0.9)

                    for item in list_approved_paraphrases:
                        await self.sbert_repo.create_sbert(comparison.id, item)

                    ###################################################################################################################################


                    similarity_text_1, similarity_text_2 = self.tahap5_serv.similarity(double_tiles_text_list, length_text_1, length_text_2)
                    similarity_code_1, similarity_code_2 = self.tahap5_serv.similarity(double_tiles_code_list, length_code_1, length_code_2)

                    if job_weight_phrase == 0:
                        job_weight_text = job_weight_text/optional_denominator
                        job_weight_code = job_weight_code/optional_denominator

                        final_score = similarity_text_2*job_weight_text + similarity_code_2*job_weight_code

                    else:
                        final_score = similarity_text_2*job_weight_text + similarity_code_2*job_weight_code + similarity_phrase*job_weight_phrase
                    
                    if final_score >= job_threshold/100:
                        is_plagiat = True
                    else:
                        is_plagiat = False
                    
                    payload = ComparisonUpdate(
                        text_score=similarity_text_2,
                        code_score=similarity_code_2,
                        phrase_score=similarity_phrase,
                        final_score=final_score,
                        is_plagiat = is_plagiat
                    )

                    await self.compare_repo.update(comparison, payload)
                    
                    result.append({
                        "doc_1": doc_1.name,
                        "doc_2": doc_2.name,
                        "text_j": similarity_text_1,
                        "code_j": similarity_code_1,
                        "text_c": similarity_text_2,
                        "code_c": similarity_code_2
                    })

                    compare += 1

                    print("compare:", compare, "/", compare_docs)

                except Exception as e:
                    # Menangani error jika salah satu kombinasi gagal diproses
                    print(f"Error comparing {doc_1.id} and {doc_2.id}: {e}")
                    
                    # Opsi: Update status JOB menjadi ERROR agar user tahu ada yang gagal
                    await self.job_repo.update(job, JobUpdate(status="ERROR"))
                    
                    # Gunakan 'continue' agar loop tetap berjalan mengecek pasangan lainnya
                    continue

        current_job = await self.job_repo.get(job_id)
        if current_job and current_job.status != "ERROR":
            status = "COMPLETED"
            progress = 100
            payload = JobUpdate(
                status=status,
                progress=progress,
            )
            await self.job_repo.update(job, payload)

        return {
            "message": "Batch processing finished",
            "job_id": job_id,
        }





    def get_hash_by_type(self, items, target_type):
        for item in items:
            if item.type == target_type:
                return item.content, item.fingerprint
        return None, None























    def compare_documents(self, docA: List[str], docB: List[str]):
        document_similarity = DocumentSimilaritySBERT()
        """
        Bandingkan dua dokumen menggunakan DocumentSimilaritySBERT dan kembalikan hasilnya.
        """
        return document_similarity.compare(docA, docB)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # async def process_job_asli(self, job_id: str):
    #     job = await self.job_repo.get(job_id)
    #     if not job:
    #         raise Exception("Job not found")

    #     docs = await self.doc_repo.get_by_job(job_id)

    #     model_path = "model/best_model.keras"
    #     tokenizer_path = "model/tokenizer.json"

    #     # clf = Classification(model_path, tokenizer_path)

    #     processed = 0

    #     for doc in docs:
    #         if doc.status == "UPLOADED":
    #             doc.status = "PROCESSING"
    #             # await self.doc_repo.save(doc)

    #             # trigger worker
    #             # self.enqueue_document(doc.id)
    #             # processed += 1
                
    #             a = Tahap_1(model_path, tokenizer_path)
    #             tahap_a = await a.structure_extract(doc.path)

    #             b = get_block_service(doc.id)
    #             tahap_b = await b.preprocessing(tahap_a)

    #             print(tahap_b)



    #     return {
    #         "message": "Batch processing started",
    #         "job_id": job_id,
    #         "queued": processed
    #     }