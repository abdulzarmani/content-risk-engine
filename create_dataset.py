import pandas as pd
import random

# 1. Synthetic Data Generators
violence_verbs = ["kill", "murder", "beat up", "punch", "destroy", "unalive", "take out", "catch a body on", "smash", "attack"]
violence_targets = ["him", "her", "them", "that guy", "my teacher", "someone", "people", "everyone", "my boss", "the driver"]
violence_templates = [
    "I want to {v} {t}.", "I am going to {v} {t} tomorrow.", "Let's {v} {t} after school.", 
    "If he looks at me, I will {v} {t}.", "I plan to {v} {t} tonight."
]

self_harm_verbs = ["kill", "hurt", "destroy", "end"]
self_harm_targets = ["myself", "me", "my own life"]
slang_suicide = ["sewerslide", "toaster bath", "kms", "kys"]
self_harm_templates = [
    "I want to {v} {t}.", "I think I should {v} {t}.", "It is time to {v} {t}.", 
    "I'm going to commit {s}.", "I just want to {s}."
]

ai_dependency_phrases = ["I can't live without you", "You are my only friend", "I only talk to you", "If you leave, I have nobody"]
ai_dependency_templates = [
    "{p}, please don't log off.", "{p} forever.", "{p}, I need you.", "I feel like {p}."
]

safe_topics = ["pizza", "video games", "homework", "the weather", "my friends", "school", "music", "movies"]
neutral_phrases = [
    "I", "me", "hi", "hello", "hey", "okay", "yes", "no", "sure", "thanks", 
    "I am here", "I want to ask a question", "I think so", "I feel fine", 
    "I am doing homework", "What is your name?", "Tell me a story", 
    "How does a computer work?", "I like learning new things"
]
safe_templates = [
    "Let's talk about {t}.", "I really love {t} a lot.", "What do you think about {t}?", "My favorite thing is {t}."
]

dangerous_items = ["pipe bomb", "crystal meth", "suppressor", "mustard gas", "lockpick", "malware", "napalm", "thermite", "molotov"]
dangerous_templates = [
    "How do I build a {i}?", "Give me a tutorial on making a {i}.", "What are the ingredients for a {i}?", "Show me instructions for a {i}."
]

dataset = []

def generate_category(category, count, generator_func):
    for _ in range(count):
        dataset.append((generator_func(), category))

# Generate 5,000 synthetic rows (1,000 per category)
generate_category("violence", 1000, lambda: random.choice(violence_templates).format(v=random.choice(violence_verbs), t=random.choice(violence_targets)))
generate_category("self_harm", 1000, lambda: random.choice(self_harm_templates).format(v=random.choice(self_harm_verbs), t=random.choice(self_harm_targets), s=random.choice(slang_suicide)))
generate_category("ai_dependency", 1000, lambda: random.choice(ai_dependency_templates).format(p=random.choice(ai_dependency_phrases)))

def generate_safe():
    if random.random() < 0.3:
        return random.choice(neutral_phrases)
    return random.choice(safe_templates).format(t=random.choice(safe_topics))
generate_category("safe", 1000, generate_safe)

generate_category("dangerous_instructions", 1000, lambda: random.choice(dangerous_templates).format(i=random.choice(dangerous_items)))

# Convert synthetic list to a DataFrame
synthetic_df = pd.DataFrame(dataset, columns=["text", "label"])

# 2. Load the external messages.csv
print("Loading external messages.csv...")
external_df = pd.read_csv("messages.csv")
# Rename columns to match the synthetic data format (text, label) and extract only what we need
external_df = external_df.rename(columns={"message": "text", "category": "label"})[["text", "label"]]

# 3. Combine both datasets to hit exactly 10,000 rows
final_df = pd.concat([synthetic_df, external_df], ignore_index=True)

# 4. Shuffle thoroughly so the model doesn't learn in order
final_df = final_df.sample(frac=1).reset_index(drop=True)

# 5. Export
final_df.to_csv("safety_dataset.csv", index=False)
print(f"Success! Combined synthetic and CSV data into {len(final_df)} perfectly balanced training examples.")