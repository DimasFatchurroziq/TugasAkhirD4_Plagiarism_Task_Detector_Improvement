# ==============================
# 2. CLASS CLASSIFICATION
# ==============================
class Classification:
    def __init__(self, model_path, tokenizer_path):
        # Load model
        self.model = load_model(model_path)

        # Load tokenizer
        with open(tokenizer_path) as f:
            data = json.load(f)
            self.tokenizer = tokenizer_from_json(json.dumps(data))

    def classify_single(self, text, max_len=100):
        sequence = self.tokenizer.texts_to_sequences([text])
        X = pad_sequences(sequence, maxlen=max_len)

        # 🔥 ganti predict
        prediction = self.model(X, training=False)

        label = np.argmax(prediction.numpy(), axis=1)[0]

        if label != 1:
            block = {
                "content": text,
                "type": "CODE",
                "source": "TYPING"
            }
            return block
        else:
            block = {
                "content": text,
                "type": "TEXT",
                "source": "TYPING"
            }
            return block


# # ==============================
# # 3. LOAD MODEL & TOKENIZER
# # ==============================
# # Upload dulu ke Colab:
# # - model.h5
# # - tokenizer.json

# model_path = "best_model.keras"
# tokenizer_path = "tokenizer.json"

# clf = Classification(model_path, tokenizer_path)


# # ==============================
# # 4. TEST PERCOBAAN
# # ==============================
# test_data = [
#     "print('Hello World')",
#     "Ini adalah contoh kalimat biasa",
#     "for i in range(10): print(i)",
#     "Saya sedang belajar machine learning",
#     "def tambah(a, b): return a + b"
# ]

# # print("\n=== HASIL SINGLE ===\n")

# single_input = "while True: print('loop')"
# for input in test_data:
#     result = clf.classify_single(input)
#     print(result)
