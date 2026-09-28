import os
import torch
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from torch.optim import AdamW

# 1. Configuration & Label Mapping
MODEL_NAME = "distilbert-base-uncased"
OUTPUT_DIR = "models/distilbert_safety_model"
EPOCHS = 3
BATCH_SIZE = 8
LEARNING_RATE = 5e-5

LABEL_TO_ID = {
    "safe": 0,
    "violence": 1,
    "self_harm": 2,
    "ai_dependency": 3,
    "dangerous_instructions": 4
}
ID_TO_LABEL = {v: k for k, v in LABEL_TO_ID.items()}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using compute device: {device}")

# 2. PyTorch Dataset Wrapper
class SafetyDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=64):
        self.encodings = tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt"
        )
        self.labels = [LABEL_TO_ID[label] for label in labels]

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

    def __len__(self):
        return len(self.labels)

# 3. Load Dataset & Tokenizer
df = pd.read_csv("safety_dataset.csv").dropna()
texts = df["text"].tolist()
labels = df["label"].tolist()

print(f"Loading {MODEL_NAME} tokenizer and base model...")
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)
model = DistilBertForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(LABEL_TO_ID),
    id2label=ID_TO_LABEL,
    label2id=LABEL_TO_ID
)
model.to(device)

dataset = SafetyDataset(texts, labels, tokenizer)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)

# 4. Training Loop
print(f"\nStarting fine-tuning across {len(texts)} samples for {EPOCHS} epochs...\n")
model.train()

for epoch in range(1, EPOCHS + 1):
    total_loss = 0.0
    for step, batch in enumerate(dataloader):
        optimizer.zero_grad()
        
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        batch_labels = batch["labels"].to(device)

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=batch_labels
        )

        loss = outputs.loss
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    avg_loss = total_loss / len(dataloader)
    print(f"Epoch {epoch}/{EPOCHS} complete | Average Loss: {avg_loss:.4f}")

# 5. Save Model and Tokenizer
os.makedirs(OUTPUT_DIR, exist_ok=True)
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"\nModel and tokenizer saved successfully to '{OUTPUT_DIR}'!")