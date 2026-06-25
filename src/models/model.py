import uuid
from sqlalchemy import (
    Column, String, Text, Integer, ForeignKey,
    CheckConstraint, Boolean, Float, Index
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID, ARRAY, REAL
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

Base = declarative_base()


# ======================
# JOBS
# ======================
class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    scenario = Column(String(10), default="MULTIPLE")
    threshold = Column(Integer, default=70, nullable=False)
    status = Column(String(10), default="PENDING")
    progress = Column(Integer, default=0)
    weight_text = Column(Float, default=0.1, nullable=False)
    weight_code = Column(Float, default=0.85, nullable=False)
    weight_phrase = Column(Float, default=0.05, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'QUEUE', 'RUNNING', 'COMPLETED', 'MODIFIED', 'ERROR')", 
            name="check_job_status"
        ),
        CheckConstraint(
            "scenario IN ('SINGLE', 'MULTIPLE')",
            name="check_job_scenario"
        ),
    )

    documents = relationship(
        "Document",
        back_populates="job",
        cascade="all, delete-orphan"
    )


# ======================
# DOCUMENTS
# ======================
class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    path = Column(String(255), nullable=False)
    status = Column(String(10), default="UPLOADED")
    category = Column(String(10), default="MANY")
    created_at = Column(TIMESTAMP, server_default=func.now())

    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    __table_args__ = (
        CheckConstraint("status IN ('UPLOADED', 'PROCESSING', 'DONE', 'ERROR')", name="check_document_status"),
        CheckConstraint("category IN ('ONE', 'MANY')", name="check_document_category"),
    )

    job = relationship("Job", back_populates="documents")

    blocks = relationship(
        "Block",
        back_populates="document",
        cascade="all, delete-orphan"
    )

    hashes = relationship(
        "Hash",
        back_populates="document",
        cascade="all, delete-orphan"
    )

    comparisons_as_doc1 = relationship(
        "Comparison",
        foreign_keys="[Comparison.document_1_id]",
        cascade="all, delete-orphan"
    )

    comparisons_as_doc2 = relationship(
        "Comparison",
        foreign_keys="[Comparison.document_2_id]",
        cascade="all, delete-orphan"
    )


# ======================
# BLOCKS
# ======================
class Block(Base):
    __tablename__ = "blocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    sequence = Column(Integer)
    content = Column(Text)
    type = Column(String(10))
    source = Column(String(10))

    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    __table_args__ = (
        CheckConstraint("type IN ('TEXT', 'CODE', 'TERMINAL')", name="check_block_type"),
        CheckConstraint("source IN ('TYPING', 'IMAGE')", name="check_block_source"),
    )

    document = relationship("Document", back_populates="blocks")

    block_embedding = relationship(
        "BlockEmbedding", 
        back_populates="block", 
        uselist=False, 
        cascade="all, delete-orphan"
    )

    mapping = relationship(
        "Mapping",
        back_populates="block",
        uselist=False,
        cascade="all, delete-orphan"
    )

    sberts_1 = relationship(
        "SBert",
        foreign_keys="SBert.block_1_id",
        back_populates="block_1"
    )

    sberts_2 = relationship(
        "SBert",
        foreign_keys="SBert.block_2_id",
        back_populates="block_2"
    )


# ======================
# BLOCK EMBEDDINGS
# ======================
class BlockEmbedding(Base):
    __tablename__ = "block_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)        
    embedding = Column(ARRAY(REAL), nullable=False)

    block_id = Column(
        UUID(as_uuid=True),
        ForeignKey("blocks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    block = relationship("Block", back_populates="block_embedding")


# ======================
# HASHES
# ======================
class Hash(Base):
    __tablename__ = "hashes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    content = Column(JSONB)
    fingerprint = Column(JSONB)
    type = Column(String(10))

    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    __table_args__ = (
        CheckConstraint("type IN ('TEXT', 'CODE')", name="check_hash_type"),
    )

    document = relationship("Document", back_populates="hashes")


# ======================
# MAPPINGS
# ======================
class Mapping(Base):

    __tablename__ = "mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    mapping_doc = Column(JSONB)
    mapping_text_code = Column(JSONB)
    mapping_preprocess = Column(JSONB)
    mapping_hash = Column(JSONB)

    block_id = Column(
        UUID(as_uuid=True),
        ForeignKey("blocks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    block = relationship("Block", back_populates="mapping")


# ======================
# COMPARISONS
# ======================
class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    text_score = Column(Float, nullable=True)
    code_score = Column(Float, nullable=True)
    phrase_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    is_plagiat = Column(Boolean, default=False, server_default="false")

    document_1_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    document_2_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    __table_args__ = (
        CheckConstraint("document_1_id != document_2_id", name="no_self_comparison"),
    )

    document_1 = relationship("Document", foreign_keys=[document_1_id], back_populates="comparisons_as_doc1")
    document_2 = relationship("Document", foreign_keys=[document_2_id], back_populates="comparisons_as_doc2")

    rkrgsts = relationship(
        "Rkrgst",
        back_populates="comparison",
        cascade="all, delete-orphan"
    )

    sberts = relationship(
        "SBert",
        back_populates="comparison",
        cascade="all, delete-orphan"
    )


# ======================
# RKRGS (substring match)
# ======================
class Rkrgst(Base):
    __tablename__ = "rkrgsts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    type = Column(String(10))
    position_1_start = Column(Integer)
    position_2_start = Column(Integer)
    match_length = Column(Integer)

    comparison_id = Column(
        UUID(as_uuid=True),
        ForeignKey("comparisons.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    __table_args__ = (
        CheckConstraint("type IN ('TEXT', 'CODE')", name="check_rkrgst_type"),
    )

    comparison = relationship("Comparison", back_populates="rkrgsts")


# ======================
# SBERTS
# ======================
class SBert(Base):
    __tablename__ = "sberts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    score = Column(Float)

    block_1_id = Column(
        UUID(as_uuid=True),
        ForeignKey("blocks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    block_2_id = Column(
        UUID(as_uuid=True),
        ForeignKey("blocks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    comparison_id = Column(
        UUID(as_uuid=True),
        ForeignKey("comparisons.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    block_1 = relationship(
        "Block",
        foreign_keys=[block_1_id],
        back_populates="sberts_1"
    )

    block_2 = relationship(
        "Block",
        foreign_keys=[block_2_id],
        back_populates="sberts_2"
    )

    comparison = relationship(
        "Comparison",
        back_populates="sberts"
    )


# ======================
# INDEX OPTIMIZATION
# ======================

Index(
    "idx_sbert_blocks",
    SBert.block_1_id,
    SBert.block_2_id
)

Index(
    "idx_comparison_docs",
    Comparison.document_1_id,
    Comparison.document_2_id
)