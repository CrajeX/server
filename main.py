from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import re
import random
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

app = FastAPI()

class TextInput(BaseModel):
    text: str

# --- Helper Functions ---
def sentence_tokenize(text):
    text = re.sub(r'(?<=[A-Za-z])\.(?=[A-Z])', '. ', text)
    text = re.sub(r'Mr\.', 'Mr_DOT_', text)
    text = re.sub(r'Mrs\.', 'Mrs_DOT_', text)
    text = re.sub(r'Dr\.', 'Dr_DOT_', text)
    text = re.sub(r'Ph\.D\.', 'PhD_DOT_', text)
    text = re.sub(r'i\.e\.', 'ie_DOT_', text)
    text = re.sub(r'e\.g\.', 'eg_DOT_', text)
    text = re.sub(r'etc\.', 'etc_DOT_', text)
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    sentences = [s.replace('Mr_DOT_', 'Mr.') for s in sentences]
    sentences = [s.replace('Mrs_DOT_', 'Mrs.') for s in sentences]
    sentences = [s.replace('Dr_DOT_', 'Dr.') for s in sentences]
    sentences = [s.replace('PhD_DOT_', 'Ph.D.') for s in sentences]
    sentences = [s.replace('ie_DOT_', 'i.e.') for s in sentences]
    sentences = [s.replace('eg_DOT_', 'e.g.') for s in sentences]
    sentences = [s.replace('etc_DOT_', 'etc.') for s in sentences]
    return [s.strip() for s in sentences if s.strip()]

def extract_key_sentences(text, num_sentences=3):
    sentences = sentence_tokenize(text)
    return sentences[:num_sentences]

def extract_entities(text):
    nlp = pipeline("ner", grouped_entities=True)
    entities = nlp(text)
    return [entity['word'] for entity in entities]

def extract_key_phrases(text):
    return extract_entities(text)

def generate_basic_questions(sentence):
    questions = []
    if " is " in sentence:
        parts = sentence.split(" is ")
        if len(parts) == 2:
            questions.append(f"What is {parts[0]}?")
    if " are " in sentence:
        parts = sentence.split(" are ")
        if len(parts) == 2:
            questions.append(f"What are {parts[0]}?")
    return questions

def generate_question_answer_pairs(text):
    sentences = sentence_tokenize(text)
    key_sentences = extract_key_sentences(text, num_sentences=2)
    entities = extract_entities(text)
    questions = []
    for sent in key_sentences:
        questions += generate_basic_questions(sent)
    return [(q, "Answer not available") for q in questions]

def generate_why_question_answer_pairs(text):
    sentences = sentence_tokenize(text)
    if not sentences:
        return []
    sentence = random.choice(sentences)
    question = f"Why is {sentence.lower()}?"
    answer = sentence
    return [(question, answer)]

def generate_how_question_answer_pairs(text):
    sentences = sentence_tokenize(text)
    if not sentences:
        return []
    sentence = random.choice(sentences)
    question = f"How does {sentence.lower()}?"
    answer = sentence
    return [(question, answer)]

def generate_who_question_answer_pairs(text):
    entities = extract_entities(text)
    if not entities:
        return []
    entity = random.choice(entities)
    question = f"Who is {entity}?"
    answer = f"{entity} is a key figure mentioned in the text."
    return [(question, answer)]

def generate_what_question_answer_pairs(text):
    key_phrases = extract_key_phrases(text)
    if not key_phrases:
        return []
    phrase = random.choice(key_phrases)
    question = f"What is {phrase}?"
    answer = f"{phrase} is discussed in the text."
    return [(question, answer)]

def generate_when_question_answer_pairs(text):
    date_patterns = [r"\b\d{4}\b", r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\b"]
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            question = f"When did {match.group()} happen?"
            answer = f"The event occurred around {match.group()}."
            return [(question, answer)]
    return []

def generate_questions_answers(paragraphs):
    qa_pairs = []
    for para in paragraphs:
        qa_pairs += generate_question_answer_pairs(para)
        qa_pairs += generate_why_question_answer_pairs(para)
        qa_pairs += generate_how_question_answer_pairs(para)
        qa_pairs += generate_who_question_answer_pairs(para)
        qa_pairs += generate_what_question_answer_pairs(para)
        qa_pairs += generate_when_question_answer_pairs(para)
    return qa_pairs

def split_text_into_paragraphs(text, min_length=100):
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    return [p for p in paragraphs if len(p) >= min_length]

# --- API Endpoint ---
@app.post("/generate")
async def generate_qa(input: TextInput):
    text = input.text
    paragraphs = split_text_into_paragraphs(text)
    qa_pairs = generate_questions_answers(paragraphs)
    return {"qa_pairs": qa_pairs}
