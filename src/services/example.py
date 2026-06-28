# services/job_service.py
import os
import uuid
from src.models.model import Document

from src.api.v1.schemas.job_schema import JobUpdate 
from src.api.v1.schemas.document_schema import DocumentUpdate
from src.api.v1.schemas.comparison_schema import ComparisonCreate, ComparisonUpdate

from src.services.sbert_service import DocumentSimilaritySBERT
from typing import List
from itertools import combinations

class ProcessService:
    def __init__(self, compare_serv, 
        sbert_model_instance,
        tahap1_serv, tahap2_serv, tahap3_serv, tahap4_serv, tahap5_serv, tahap6_serv, tahap7_serv,
        job_repo, doc_repo, block_repo, map_repo, hash_repo, compare_repo, rkrgst_repo, sbert_repo, block_embed_repo
    ):
        self.compare_serv = compare_serv
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
        
    async def process_job(self, job_id: str):
        job = await self.job_repo.get(job_id)
        if not job:
            raise Exception("Job not found")

        recount = job.status == "MODIFIED"

        # 1. Update Status Job Awal
        await self.job_repo.update(job, JobUpdate(status="RUNNING"))

        job_weight_text = job.weight_text
        job_weight_code = job.weight_code
        docs = await self.doc_repo.get_all_by_job(job_id)
        processed = 0

        # =================================================================
        # OPTIMASI TAHAP 1: Pemrosesan Dokumen Masuk (Struktur & Hashing)
        # =================================================================
        for doc in docs:
            if doc.status != "UPLOADED":
                continue

            try:
                await self.doc_repo.update(doc, DocumentUpdate(status="PROCESSING"))

                list_blocks = await self.tahap1_serv.structure_extract(doc.path)
                final_data, full_cleaned = await self.tahap2_serv.preprocessing(list_blocks)

                # TODO OPTIMASI LANJUTAN: Jika repo Anda mendukung bulk_create untuk block & mapping,
                # gantilah loop di bawah ini menjadi bulk operation.
                for item in final_data:
                    block = await self.block_repo.create_block(doc.id, item["block"])
                    await self.map_repo.create_mapping(block.id, item["mapping"])

                if full_cleaned["full_cleaned_text"]:
                    final_hash_text = await self.tahap3_serv.rollinghash(full_cleaned["full_cleaned_text"], 3, 4)
                    await self.hash_repo.create_hash(doc.id, final_hash_text, "TEXT")

                if full_cleaned["full_cleaned_code"]:
                    final_hash_code = await self.tahap3_serv.rollinghash(full_cleaned["full_cleaned_code"], 3, 4)
                    await self.hash_repo.create_hash(doc.id, final_hash_code, "CODE")

                processed += 1
                await self.doc_repo.update(doc, DocumentUpdate(status="DONE"))

            except Exception as e:
                await self.doc_repo.update(doc, DocumentUpdate(status="ERROR"))
                print(f"Error processing doc {doc.id}: {e}")

        await self.job_repo.update(job, JobUpdate(progress=30))
    
        # =================================================================
        # OPTIMASI TAHAP 2: Caching RAM untuk Data Perbandingan (Membunuh N+1)
        # =================================================================
        doc_ids = [d.id for d in docs]
        
        # A. Ambil semua data perbandingan lama yang sudah ada di DB untuk Job ini sekaligus
        # Pastikan Anda mengimplementasikan method `get_all_by_job_id` di compare_repo Anda
        existing_pairs = await self.compare_repo.get_all_by_job_id(job_id) 
        pairs_cache = {(p.doc1_id, p.doc2_id): p for p in existing_pairs}

        # B. Bulk Fetch Hash: Ambil semua data hash dari seluruh dokumen dalam 1 query tunggal
        # Pastikan Anda membuat method `get_by_multiple_docs` di hash_repo Anda
        all_hashes = await self.hash_repo.get_by_multiple_docs(doc_ids)
        hashes_by_doc = {}
        for h in all_hashes:
            hashes_by_doc.setdefault(h.document_id, []).append(h)

        # C. Bulk Fetch Blocks: Ambil semua block beserta mapping untuk seluruh dokumen dalam 1 query tunggal
        # Pastikan Anda membuat method `get_by_multiple_docs_with_map` di block_repo Anda
        all_blocks = await self.block_repo.get_by_multiple_docs_with_map(doc_ids)
        blocks_by_doc = {}
        for b in all_blocks:
            blocks_by_doc.setdefault(b.document_id, []).append(b)

        # =================================================================
        # OPTIMASI TAHAP 3: Loop Utama tanpa Hit Database Berulang
        # =================================================================
        result = []
        
        for doc_1, doc_2 in combinations(docs, 2):
            # Cek dari cache RAM, bukan hit DB lewat `get_by_doc1_doc2`
            pair = pairs_cache.get((doc_1.id, doc_2.id)) or pairs_cache.get((doc_2.id, doc_1.id))

            if pair:
                if recount:
                    final_score = (pair.text_score * job_weight_text) + (pair.code_score * job_weight_code)
                    await self.compare_repo.update(pair, ComparisonUpdate(final_score=final_score))
                continue
                
            # Jika data pasangannya benar-benar baru, buat baris barunya
            comparison = await self.compare_repo.create_compare(doc_1.id, doc_2.id)
            
            # Ambil hash dari cache RAM (sangat cepat, 0ms)
            hash_1 = hashes_by_doc.get(doc_1.id, [])
            hash_2 = hashes_by_doc.get(doc_2.id, [])

            hash_text_1, fingerprint_text_1 = self.get_hash_by_type(hash_1, "TEXT")
            hash_code_1, fingerprint_code_1 = self.get_hash_by_type(hash_1, "CODE")

            hash_text_2, fingerprint_text_2 = self.get_hash_by_type(hash_2, "TEXT")
            hash_code_2, fingerprint_code_2 = self.get_hash_by_type(hash_2, "CODE")

            double_tiles_text_list, length_text_1, length_text_2 = self.tahap4_serv.rkr(
                fingerprint_text_1, fingerprint_text_2, hash_text_1, hash_text_2, 10
            )
            double_tiles_code_list, length_code_1, length_code_2 = self.tahap4_serv.rkr(
                fingerprint_code_1, fingerprint_code_2, hash_code_1, hash_code_2, 10
            )

            # TODO OPTIMASI BULK INSERT: Siapkan list di luar loop jika repository Anda mendukung `bulk_create_rkrgst`
            for item in double_tiles_text_list:
                await self.rkrgst_repo.create_rkrgst(comparison.id, item, "TEXT")
            for item in double_tiles_code_list:
                await self.rkrgst_repo.create_rkrgst(comparison.id, item, "CODE")

            # Ambil data blocks dari cache RAM (0ms)
            blocks_1 = blocks_by_doc.get(doc_1.id, [])
            blocks_2 = blocks_by_doc.get(doc_2.id, [])

            embedding_list_1 = self.tahap6_serv.embedding_sentence(blocks_1, double_tiles_text_list, 0, self.sbert_model_instance)
            embedding_list_2 = self.tahap6_serv.embedding_sentence(blocks_2, double_tiles_text_list, 1, self.sbert_model_instance)

            # TODO OPTIMASI BULK INSERT: Siapkan list untuk dieksekusi sekaligus lewat bulk embed repo
            for item in embedding_list_1:
                if not item["is_exist"]:
                    await self.block_embed_repo.create_block_embed(item["data"])
            for item in embedding_list_2:
                if not item["is_exist"]:
                    await self.block_embed_repo.create_block_embed(item["data"])

            list_approved_paraphrases, similarity = self.tahap7_serv(embedding_list_1, embedding_list_2, 0.9)

            for item in list_approved_paraphrases:
                await self.sbert_repo.create_sbert(comparison.id, item)

            similarity_text_1, similarity_text_2 = self.tahap5_serv.similarity(double_tiles_text_list, length_text_1, length_text_2)
            similarity_code_1, similarity_code_2 = self.tahap5_serv.similarity(double_tiles_code_list, length_code_1, length_code_2)
            
            final_score = (similarity_text_2 * job_weight_text) + (similarity_code_2 * job_weight_code)

            payload = ComparisonUpdate(
                text_score=similarity_text_2,
                code_score=similarity_code_2,
                final_score=final_score,
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

        # Finalisasi Status & Progress Job
        await self.job_repo.update(job, JobUpdate(status="COMPLETED", progress=100))

        return {
            "message": "Batch processing finished",
            "job_id": job_id,
            "processed": processed,
            "result": result
        }

    def get_hash_by_type(self, items, target_type):
        for item in items:
            if item.type == target_type:
                return item.content, item.fingerprint
        return None, None

    def get_block_by_type(self, items, target_type):
        for item in items:
            if item.type == target_type:
                return item.content, item.fingerprint
        return None, None











import os
import uuid
import asyncio
from src.models.model import Document

from src.api.v1.schemas.job_schema import JobUpdate 
from src.api.v1.schemas.document_schema import DocumentUpdate
from src.api.v1.schemas.comparison_schema import ComparisonCreate, ComparisonUpdate

from src.services.sbert_service import DocumentSimilaritySBERT
from typing import List
from itertools import combinations


class ProcessService:
    def __init__(self, compare_serv, 
        sbert_model_instance,
        tahap1_serv, tahap2_serv, tahap3_serv, tahap4_serv, tahap5_serv, tahap6_serv, tahap7_serv,
        job_repo, doc_repo, block_repo, map_repo, hash_repo, compare_repo, rkrgst_repo, sbert_repo, block_embed_repo
    ):
        self.compare_serv = compare_serv
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

    async def _process_single_document(self, doc):
        """Helper untuk memproses satu dokumen secara independen & konkuren"""
        if doc.status != "UPLOADED":
            return False

        try:
            # Update status ke PROCESSING
            await self.doc_repo.update(doc, DocumentUpdate(status="PROCESSING"))

            # Tahap 1 & 2
            list_blocks = await self.tahap1_serv.structure_extract(doc.path)
            final_data, full_cleaned = await self.tahap2_serv.preprocessing(list_blocks)

            # Optimasi DB: Buat block & mapping (Idealnya pakai bulk_create jika repo mendukung)
            for item in final_data:
                block = await self.block_repo.create_block(doc.id, item["block"])
                await self.map_repo.create_mapping(block.id, item["mapping"])

            # Tahap 3: Rolling Hash
            if full_cleaned.get("full_cleaned_text"):
                final_hash_text = await self.tahap3_serv.rollinghash(full_cleaned["full_cleaned_text"], 3, 4)
                await self.hash_repo.create_hash(doc.id, final_hash_text, "TEXT")

            if full_cleaned.get("full_cleaned_code"):
                final_hash_code = await self.tahap3_serv.rollinghash(full_cleaned["full_cleaned_code"], 3, 4)
                await self.hash_repo.create_hash(doc.id, final_hash_code, "CODE")

            # Update status ke DONE
            await self.doc_repo.update(doc, DocumentUpdate(status="DONE"))
            return True

        except Exception as e:
            await self.doc_repo.update(doc, DocumentUpdate(status="ERROR"))
            print(f"Error processing doc {doc.id}: {e}")
            return False
        
    async def process_job(self, job_id: str):
        job = await self.job_repo.get(job_id)
        if not job:
            raise Exception("Job not found")

        recount = (job.status == "MODIFIED")

        # Update Job Status ke RUNNING
        await self.job_repo.update(job, JobUpdate(status="RUNNING"))

        job_weight_text = job.weight_text
        job_weight_code = job.weight_code
        docs = await self.doc_repo.get_all_by_job(job_id)

        # ==========================================
        # OPTIMASI 1: Pemrosesan Dokumen secara Paralel / Konkuren
        # ==========================================
        tasks = [self._process_single_document(doc) for doc in docs]
        results = await asyncio.gather(*tasks)
        processed = sum(1 for r in results if r)

        # Update Progress Awal
        await self.job_repo.update(job, JobUpdate(progress=30))
    
        # ==========================================
        # OPTIMASI 2: Prefetching / Caching Hash Dokumen
        # ==========================================
        # Ambil semua data hash sekali saja di awal untuk menghindari N+1 query di dalam loop combinations
        hash_cache = {}
        for doc in docs:
            hash_cache[doc.id] = await self.hash_repo.get_by_doc(doc.id)

        result = []
        
        # ==========================================
        # OPTIMASI 3: Loop Perbandingan Pasangan Dokumen
        # ==========================================
        for doc_1, doc_2 in combinations(docs, 2):
            pair = await self.compare_serv.get_by_doc1_doc2(doc_1.id, doc_2.id)
            
            if pair:
                if recount:
                    final_score = (pair.text_score * job_weight_text) + (pair.code_score * job_weight_code)
                    await self.compare_repo.update(pair, ComparisonUpdate(final_score=final_score))
                continue
                
            comparison = await self.compare_repo.create_compare(doc_1.id, doc_2.id)
            
            # Ambil hash dari cache, bukan dari hit database lagi
            hash_1 = hash_cache.get(doc_1.id, [])
            hash_2 = hash_cache.get(doc_2.id, [])

            hash_text_1, fingerprint_text_1 = self.get_hash_by_type(hash_1, "TEXT")
            hash_code_1, fingerprint_code_1 = self.get_hash_by_type(hash_1, "CODE")

            hash_text_2, fingerprint_text_2 = self.get_hash_by_type(hash_2, "TEXT")
            hash_code_2, fingerprint_code_2 = self.get_hash_by_type(hash_2, "CODE")

            # Jalankan kalkulasi RKR secara sekuensial (atau bungkus dengan ThreadPool jika CPU-bound berat)
            double_tiles_text_list, length_text_1, length_text_2 = self.tahap4_serv.rkr(fingerprint_text_1, fingerprint_text_2, hash_text_1, hash_text_2, 10)
            double_tiles_code_list, length_code_1, length_code_2 = self.tahap4_serv.rkr(fingerprint_code_1, fingerprint_code_2, hash_code_1, hash_code_2, 10)

            # NOTE: Jika repositori Anda mendukung `bulk_create`, ubah loop di bawah ini menjadi bulk insert!
            for item in double_tiles_text_list:
                await self.rkrgst_repo.create_rkrgst(comparison.id, item, "TEXT")
                
            for item in double_tiles_code_list:
                await self.rkrgst_repo.create_rkrgst(comparison.id, item, "CODE")

            # Bagian Embedding SBERT
            blocks_1 = await self.block_repo.get_by_doc_with_map(doc_1.id)
            blocks_2 = await self.block_repo.get_by_doc_with_map(doc_2.id)

            embedding_list_1 = self.tahap6_serv.embedding_sentence(blocks_1, double_tiles_text_list, 0, self.sbert_model_instance)
            embedding_list_2 = self.tahap6_serv.embedding_sentence(blocks_2, double_tiles_text_list, 1, self.sbert_model_instance)

            for item in embedding_list_1:
                if not item["is_exist"]:
                    await self.block_embed_repo.create_block_embed(item["data"])

            for item in embedding_list_2:
                if not item["is_exist"]:
                    await self.block_embed_repo.create_block_embed(item["data"])

            list_approved_paraphrases, similarity = self.tahap7_serv(embedding_list_1, embedding_list_2, 0.9)

            for item in list_approved_paraphrases:
                await self.sbert_repo.create_sbert(comparison.id, item)

            # Hitung Similarity Akhir
            similarity_text_1, similarity_text_2 = self.tahap5_serv.similarity(double_tiles_text_list, length_text_1, length_text_2)
            similarity_code_1, similarity_code_2 = self.tahap5_serv.similarity(double_tiles_code_list, length_code_1, length_code_2)

            final_score = (similarity_text_2 * job_weight_text) + (similarity_code_2 * job_weight_code)

            payload = ComparisonUpdate(
                text_score=similarity_text_2,
                code_score=similarity_code_2,
                final_score=final_score,
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

        # Update status & progress ke COMPLETED
        await self.job_repo.update(job, JobUpdate(status="COMPLETED", progress=100))

        return {
            "message": "Batch processing finished",
            "job_id": job_id,
            "processed": processed,
            "result": result
        }

    def get_hash_by_type(self, items, target_type):
        if not items:
            return None, None
        for item in items:
            if item.type == target_type:
                return item.content, item.fingerprint
        return None, None

    def get_block_by_type(self, items, target_type):
        if not items:
            return None, None
        for item in items:
            if item.type == target_type:
                return item.content, item.fingerprint
        return None, None

    def compare_documents(self, docA: List[str], docB: List[str]):
        document_similarity = DocumentSimilaritySBERT()
        return document_similarity.compare(docA, docB)