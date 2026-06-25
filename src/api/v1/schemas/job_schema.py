from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

class JobCreate(BaseModel):
    name: str
    description: str
    scenario: str
    threshold: int = Field(..., ge=40, le=100)
    weight_text: float
    weight_code: float
    weight_phrase: float

    @model_validator(mode='after')
    def validate_weights_total(self) -> Self:
        total_weight = self.weight_text + self.weight_code + self.weight_phrase
        
        # Menggunakan abs() dan tolerance kecil untuk menghindari isu floating-point di Python
        if abs(total_weight - 1.0) > 1e-9:
            raise ValueError(f"Jumlah dari weight_text, weight_code, dan weight_phrase harus sama dengan 1. Total saat ini: {total_weight}")
        
        return self

class JobUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    threshold: int | None = Field(None, ge=40, le=100)
    status: str | None = None
    progress: int | None = None
    weight_text: float | None = None
    weight_code: float | None = None
    weight_phrase: float | None = None

    @model_validator(mode='after')
    def validate_weights_total(self) -> Self:
        # 1. Cek apakah ada salah satu weight yang dikirim oleh user
        weights = [self.weight_text, self.weight_code, self.weight_phrase]
        any_weight_provided = any(w is not None for w in weights)
        
        if any_weight_provided:
            # 2. Jika ada weight yang dikirim, pastikan ketiganya WAJIB diisi semua
            if self.weight_text is None or self.weight_code is None or self.weight_phrase is None:
                raise ValueError(
                    "Jika ingin mengubah weight, kamu harus mengirimkan ketiga nilai sekaligus "
                    "(weight_text, weight_code, weight_phrase) agar totalnya bisa divalidasi."
                )
            
            # 3. Validasi jumlah totalnya harus sama dengan 1
            total_weight = self.weight_text + self.weight_code + self.weight_phrase
            if abs(total_weight - 1.0) > 1e-9:
                raise ValueError(f"Jumlah dari weight_text, weight_code, dan weight_phrase harus sama dengan 1. Total saat ini: {total_weight}")
        
        return self

# class JobResponse(BaseModel):
#     id: int
#     name: str
#     email: str

#     class Config:
#         from_attributes = True
