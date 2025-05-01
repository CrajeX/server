# import json
# import os
# import re
# import string
# import random
# import argparse
# from collections import Counter
# import math
# from tqdm import tqdm

# class QASystem:
#     def __init__(self, qa_dataset_path, model_output_path="qa_model.json"):
#         """Initialize the QA system with a dataset"""
#         self.qa_dataset_path = qa_dataset_path
#         self.model_output_path = model_output_path
#         self.qa_data = None
#         self.index = None
#         self.idf_scores = None
#         self.context_embeddings = None
#         self.question_embeddings = None
#         self.custom_stopwords = {
#             'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about',
#             'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
#             'do', 'does', 'did', 'and', 'or', 'but', 'if', 'then', 'else', 'when',
#             'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
#             'other', 'some', 'such', 'that', 'this', 'these', 'those', 'which', 'what',
#             'of', 'can', 'will', 'just', 'should', 'now'
#         }
        
#     def load_data(self):
#         """Load QA dataset from file"""
#         try:
#             with open(self.qa_dataset_path, 'r', encoding='utf-8') as f:
#                 self.qa_data = json.load(f)
#             print(f"Loaded {len(self.qa_data.get('data', []))} QA pairs from {self.qa_dataset_path}")
#             return True
#         except Exception as e:
#             print(f"Error loading QA dataset: {e}")
#             return False
    
#     def preprocess_text(self, text):
#         """Preprocess text by lowercasing, removing punctuation, and tokenizing"""
#         # Convert to lowercase
#         text = text.lower()
#         # Remove punctuation
#         text = text.translate(str.maketrans('', '', string.punctuation))
#         # Tokenize (split into words)
#         tokens = text.split()
#         # Remove stopwords
#         tokens = [t for t in tokens if t not in self.custom_stopwords]
#         return tokens
    
#     def build_inverted_index(self):
#         """Build an inverted index from the QA dataset"""
#         print("Building inverted index...")
#         self.index = {}
#         document_count = 0
#         term_document_counts = Counter()
        
#         if not self.qa_data:
#             print("No data loaded. Please load data first.")
#             return False
        
#         # Process each QA pair
#         for i, qa_pair in enumerate(tqdm(self.qa_data.get('data', []))):
#             document_count += 1
            
#             # Get context and question
#             context = qa_pair.get('context', '')
#             question = qa_pair.get('question', '')
#             answer = qa_pair.get('answer', '')
            
#             # Create a combined text for indexing
#             combined_text = f"{context} {question} {answer}"
            
#             # Preprocess the text
#             tokens = self.preprocess_text(combined_text)
            
#             # Count unique tokens in this document
#             doc_terms = set(tokens)
#             for term in doc_terms:
#                 term_document_counts[term] += 1
            
#             # Add tokens to inverted index
#             for token in tokens:
#                 if token not in self.index:
#                     self.index[token] = []
#                 if i not in [idx for idx, _ in self.index[token]]:
#                     self.index[token].append((i, tokens.count(token)))
        
#         # Calculate IDF scores
#         self.idf_scores = {}
#         for term, doc_count in term_document_counts.items():
#             self.idf_scores[term] = math.log(document_count / (1 + doc_count))
        
#         print(f"Inverted index built with {len(self.index)} terms")
#         return True
    
#     def try_load_transformers(self):
#         """Try to load transformers library and models for better embeddings"""
#         try:
#             from transformers import AutoTokenizer, AutoModel
#             import torch
            
#             print("Loading sentence transformer model...")
#             # Try to load a smaller model first
#             try:
#                 model_name = "sentence-transformers/all-MiniLM-L6-v2"
#                 tokenizer = AutoTokenizer.from_pretrained(model_name)
#                 model = AutoModel.from_pretrained(model_name)
#                 print(f"Loaded {model_name}")
#                 return tokenizer, model, torch
#             except Exception as e:
#                 print(f"Failed to load all-MiniLM-L6-v2: {e}")
#                 try:
#                     # Try an even smaller model as fallback
#                     model_name = "sentence-transformers/paraphrase-MiniLM-L3-v2"
#                     tokenizer = AutoTokenizer.from_pretrained(model_name)
#                     model = AutoModel.from_pretrained(model_name)
#                     print(f"Loaded {model_name}")
#                     return tokenizer, model, torch
#                 except Exception as e2:
#                     print(f"Failed to load paraphrase-MiniLM-L3-v2: {e2}")
#                     return None, None, None
#         except ImportError:
#             print("Transformers library not found. Using basic TF-IDF instead.")
#             return None, None, None
    
#     def mean_pooling(self, model_output, attention_mask, torch):
#         """Mean pooling for sentence embeddings"""
#         token_embeddings = model_output[0]
#         input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
#         return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
#     def get_embeddings(self, texts, tokenizer, model, torch):
#         """Create embeddings for a list of texts using a transformer model"""
#         # Tokenize texts
#         encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors='pt', max_length=512)
        
#         # Compute token embeddings
#         with torch.no_grad():
#             model_output = model(**encoded_input)
        
#         # Mean pooling
#         embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'], torch)
#         return embeddings
    
#     def compute_embeddings(self):
#         """Compute embeddings for contexts and questions if transformers library is available"""
#         tokenizer, model, torch = self.try_load_transformers()
        
#         if tokenizer and model and torch:
#             print("Computing embeddings for QA pairs...")
#             contexts = []
#             questions = []
            
#             for qa_pair in tqdm(self.qa_data.get('data', [])):
#                 context = qa_pair.get('context', '')
#                 question = qa_pair.get('question', '')
#                 contexts.append(context)
#                 questions.append(question)
            
#             # Process in batches to avoid memory issues
#             batch_size = 8
            
#             # Compute context embeddings
#             context_embeddings = []
#             for i in range(0, len(contexts), batch_size):
#                 batch = contexts[i:i+batch_size]
#                 batch_embeddings = self.get_embeddings(batch, tokenizer, model, torch)
#                 context_embeddings.append(batch_embeddings)
            
#             self.context_embeddings = torch.cat(context_embeddings) if context_embeddings else None
            
#             # Compute question embeddings
#             question_embeddings = []
#             for i in range(0, len(questions), batch_size):
#                 batch = questions[i:i+batch_size]
#                 batch_embeddings = self.get_embeddings(batch, tokenizer, model, torch)
#                 question_embeddings.append(batch_embeddings)
            
#             self.question_embeddings = torch.cat(question_embeddings) if question_embeddings else None
            
#             print("Embeddings computed successfully")
#             return True
#         else:
#             print("Skipping embeddings computation due to missing dependencies")
#             return False
    
#     def train(self, compute_embeddings=True):
#         """Train the QA system by building the index and computing embeddings"""
#         if not self.load_data():
#             return False
        
#         if not self.build_inverted_index():
#             return False
        
#         if compute_embeddings:
#             self.compute_embeddings()
        
#         # Save the model
#         self.save_model()
#         return True
    
#     def save_model(self):
#         """Save the model (index and IDF scores) to a file"""
#         try:
#             # We can't save PyTorch tensors directly to JSON, so we'll exclude them
#             model_data = {
#                 "index": {term: [(doc_id, count) for doc_id, count in postings] 
#                           for term, postings in self.index.items()},
#                 "idf_scores": self.idf_scores,
#                 "has_embeddings": self.context_embeddings is not None,
#                 "dataset_path": self.qa_dataset_path
#             }
            
#             with open(self.model_output_path, 'w', encoding='utf-8') as f:
#                 json.dump(model_data, f)
            
#             print(f"Model saved to {self.model_output_path}")
#             return True
#         except Exception as e:
#             print(f"Error saving model: {e}")
#             return False
    
#     def load_model(self):
#         """Load the model from a file"""
#         try:
#             with open(self.model_output_path, 'r', encoding='utf-8') as f:
#                 model_data = json.load(f)
            
#             self.index = {term: [(int(doc_id), count) for doc_id, count in postings] 
#                           for term, postings in model_data["index"].items()}
#             self.idf_scores = model_data["idf_scores"]
#             dataset_path = model_data.get("dataset_path", self.qa_dataset_path)
            
#             # Load the QA dataset
#             self.qa_dataset_path = dataset_path
#             self.load_data()
            
#             print(f"Model loaded from {self.model_output_path}")
#             return True
#         except Exception as e:
#             print(f"Error loading model: {e}")
#             return False

#     def calculate_tfidf(self, query_tokens, doc_id):
#         """Calculate TF-IDF score for a document given query tokens"""
#         score = 0.0
        
#         for token in query_tokens:
#             if token in self.index:
#                 # Find if this token exists in this document
#                 doc_entries = [entry for entry in self.index[token] if entry[0] == doc_id]
#                 if doc_entries:
#                     # TF: Term frequency in document
#                     tf = doc_entries[0][1]
#                     # IDF: Inverse document frequency
#                     idf = self.idf_scores.get(token, 0)
#                     # Add to score
#                     score += tf * idf
        
#         return score
    
#     def query(self, question, top_k=3, use_embeddings=True):
#         """Query the QA system with a question"""
#         if not self.index or not self.qa_data:
#             print("Model not loaded. Please train or load the model first.")
#             return []
        
#         # Try to use embeddings first if available
#         if use_embeddings and self.context_embeddings is not None:
#             try:
#                 # Get transformers again
#                 tokenizer, model, torch = self.try_load_transformers()
#                 if tokenizer and model and torch:
#                     # Get embedding for this question
#                     query_embedding = self.get_embeddings([question], tokenizer, model, torch)
                    
#                     # Calculate similarity scores
#                     similarity_scores = []
#                     for i in range(len(self.qa_data.get('data', []))):
#                         context_emb = self.context_embeddings[i].unsqueeze(0)
#                         question_emb = self.question_embeddings[i].unsqueeze(0)
                        
#                         # Combine similarity with context and question
#                         context_sim = torch.nn.functional.cosine_similarity(query_embedding, context_emb).item()
#                         question_sim = torch.nn.functional.cosine_similarity(query_embedding, question_emb).item()
                        
#                         # Weight context similarity more than question similarity
#                         combined_sim = 0.7 * context_sim + 0.3 * question_sim
#                         similarity_scores.append((i, combined_sim))
                    
#                     # Sort by similarity score (descending)
#                     similarity_scores.sort(key=lambda x: x[1], reverse=True)
                    
#                     # Return top_k results
#                     results = []
#                     for doc_id, score in similarity_scores[:top_k]:
#                         qa_pair = self.qa_data['data'][doc_id]
#                         results.append({
#                             'context': qa_pair.get('context', ''),
#                             'question': qa_pair.get('question', ''),
#                             'answer': qa_pair.get('answer', ''),
#                             'score': score
#                         })
                    
#                     return results
#             except Exception as e:
#                 print(f"Error using embeddings for query: {e}")
#                 print("Falling back to TF-IDF")
        
#         # Fall back to TF-IDF if embeddings are not available or failed
#         # Preprocess the query
#         query_tokens = self.preprocess_text(question)
        
#         # Calculate scores for all documents
#         scores = []
#         for i in range(len(self.qa_data.get('data', []))):
#             score = self.calculate_tfidf(query_tokens, i)
#             scores.append((i, score))
        
#         # Sort by score (descending)
#         scores.sort(key=lambda x: x[1], reverse=True)
        
#         # Return top_k results
#         results = []
#         for doc_id, score in scores[:top_k]:
#             if score > 0:  # Only include results with non-zero scores
#                 qa_pair = self.qa_data['data'][doc_id]
#                 results.append({
#                     'context': qa_pair.get('context', ''),
#                     'question': qa_pair.get('question', ''),
#                     'answer': qa_pair.get('answer', ''),
#                     'score': score
#                 })
        
#         return results

#     def interactive_query(self):
#         """Run an interactive query session"""
#         print("\n===== QA System Interactive Mode =====")
#         print("Type 'exit' or 'quit' to end the session")
        
#         while True:
#             query = input("\nEnter your question: ").strip()
            
#             if query.lower() in ['exit', 'quit']:
#                 print("Exiting interactive mode...")
#                 break
            
#             if not query:
#                 continue
            
#             results = self.query(query)
            
#             if not results:
#                 print("No relevant information found for your question.")
#                 continue
            
#             print("\nTop results:")
#             for i, result in enumerate(results):
#                 print(f"\nResult {i+1} (Score: {result['score']:.4f}):")
#                 print(f"Q: {result['question']}")
#                 print(f"A: {result['answer']}")
#                 print(f"Context: {result['context'][:150]}...")
            
#             # Determine the final answer based on the top result
#             if results:
#                 print("\n========================")
#                 print("Final Answer:")
#                 print(results[0]['answer'])
#                 print("========================")

# def main():
#     parser = argparse.ArgumentParser(description='Train and use a QA system')
#     parser.add_argument('--train', action='store_true', help='Train the QA system')
#     parser.add_argument('--dataset', type=str, default='qa_dataset.json', help='Path to QA dataset')
#     parser.add_argument('--model', type=str, default='qa_model.json', help='Path to model file')
#     parser.add_argument('--query', type=str, help='Query the QA system and exit')
#     parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
#     parser.add_argument('--no-embeddings', action='store_true', help='Disable transformer embeddings')
    
#     args = parser.parse_args()
    
#     qa_system = QASystem(args.dataset, args.model)
    
#     if args.train:
#         print(f"Training QA system using dataset: {args.dataset}")
#         qa_system.train(compute_embeddings=not args.no_embeddings)
#     elif args.query:
#         # Load the model
#         if not qa_system.load_model():
#             return
        
#         # Query the system
#         results = qa_system.query(args.query)
        
#         if not results:
#             print("No relevant information found for your question.")
#             return
        
#         print("\nTop results:")
#         for i, result in enumerate(results):
#             print(f"\nResult {i+1} (Score: {result['score']:.4f}):")
#             print(f"Q: {result['question']}")
#             print(f"A: {result['answer']}")
#             print(f"Context: {result['context'][:150]}...")
        
#         # Determine the final answer based on the top result
#         if results:
#             print("\n========================")
#             print("Final Answer:")
#             print(results[0]['answer'])
#             print("========================")
#     elif args.interactive:
#         # Load the model
#         if not qa_system.load_model():
#             return
        
#         # Run interactive mode
#         qa_system.interactive_query()
#     else:
#         print("Please specify either --train, --query, or --interactive")
#         print("Use --help for more information")

# if __name__ == "__main__":
#     main()
import os
import json
import random
import re
from tqdm import tqdm

def sentence_tokenize(text):
    """Simple sentence tokenizer without using NLTK."""
    # Handle common abbreviations to avoid splitting them
    text = re.sub(r'(?<=[A-Za-z])\.(?=[A-Z])', '. ', text)  # Fix missing spaces after periods
    text = re.sub(r'Mr\.', 'Mr_DOT_', text)
    text = re.sub(r'Mrs\.', 'Mrs_DOT_', text)
    text = re.sub(r'Dr\.', 'Dr_DOT_', text)
    text = re.sub(r'Ph\.D\.', 'PhD_DOT_', text)
    text = re.sub(r'i\.e\.', 'ie_DOT_', text)
    text = re.sub(r'e\.g\.', 'eg_DOT_', text)
    text = re.sub(r'etc\.', 'etc_DOT_', text)
    
    # Split by sentence-ending punctuation followed by space and capital letter
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    
    # Restore abbreviations
    sentences = [s.replace('Mr_DOT_', 'Mr.') for s in sentences]
    sentences = [s.replace('Mrs_DOT_', 'Mrs.') for s in sentences]
    sentences = [s.replace('Dr_DOT_', 'Dr.') for s in sentences]
    sentences = [s.replace('PhD_DOT_', 'Ph.D.') for s in sentences]
    sentences = [s.replace('ie_DOT_', 'i.e.') for s in sentences]
    sentences = [s.replace('eg_DOT_', 'e.g.') for s in sentences]
    sentences = [s.replace('etc_DOT_', 'etc.') for s in sentences]
    
    return [s.strip() for s in sentences if s.strip()]

def read_text_file(file_path):
    """Read content from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def split_text_into_paragraphs(text, min_length=100):
    """Split text into paragraphs, filtering out very short ones."""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    return [p for p in paragraphs if len(p) >= min_length]

def extract_key_sentences(paragraph, max_sentences=3):
    """Extract key sentences from a paragraph."""
    sentences = sentence_tokenize(paragraph)
    # If paragraph has fewer sentences than max_sentences, return all sentences
    if len(sentences) <= max_sentences:
        return sentences
    # Otherwise, select sentences with some randomness to ensure variety
    return random.sample(sentences, max_sentences)

def initialize_text_generator():
    """Initialize text generation model with proper error handling."""
    text_generator = None
    
    # Try to import transformers and initialize models
    try:
        from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
        
        # Try to initialize text generation model
        try:
            print("Loading text generation model...")
            tokenizer = AutoTokenizer.from_pretrained("facebook/bart-base")
            model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-base")
            text_generator = pipeline("text2text-generation", model=model, tokenizer=tokenizer)
            print("Device set to use cpu")
            print("Text generation model loaded successfully!")
        except Exception as e:
            print(f"Warning: Could not load text generation model: {e}")
            print("Will use basic question generation instead.")
            
    except ImportError as e:
        print(f"Could not import transformers library: {e}")
        print("Please install required packages:")
        print("pip install transformers torch tqdm")
    
    return text_generator

def extract_entities(sentence):
    """Extract potential named entities from a sentence."""
    entities = []
    
    # Find capitalized words not at the beginning of the sentence
    words = sentence.split()
    for i, word in enumerate(words):
        # Skip first word of sentence and check for capitalization
        if i > 0 and word and word[0].isupper() and len(word) > 1:
            # Remove punctuation
            clean_word = re.sub(r'[^\w\s]', '', word)
            if clean_word:
                entities.append(clean_word)
    
    # Find phrases in quotes
    quoted = re.findall(r'"([^"]*)"', sentence)
    entities.extend(quoted)
    
    # Find potential organizations, locations, etc. with multiple capital words
    capital_sequences = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', sentence)
    entities.extend(capital_sequences)
    
    # Remove duplicates while preserving order
    unique_entities = []
    for entity in entities:
        if entity and entity not in unique_entities:
            unique_entities.append(entity)
    
    return unique_entities

def extract_key_phrases(sentence):
    """Extract key phrases from a sentence using simple rules."""
    key_phrases = []
    
    # Get noun phrases (simplified approach)
    # This looks for adjective + noun patterns or noun sequences
    words = sentence.split()
    for i in range(len(words) - 1):
        # Simple heuristic: capitalize words might be important
        if words[i][0].isupper() and i > 0:
            if i + 1 < len(words):
                phrase = f"{words[i]} {words[i+1]}"
                key_phrases.append(phrase.strip(".,;:()[]{}\"'"))
    
    # Get verb phrases (simplified)
    # Look for verb + object patterns
    for i in range(len(words) - 2):
        if words[i].lower().endswith(("ed", "ing", "s", "es")) and len(words[i]) > 3:
            phrase = f"{words[i]} {words[i+1]}"
            if i + 2 < len(words):
                phrase += f" {words[i+2]}"
            key_phrases.append(phrase.strip(".,;:()[]{}\"'"))
    
    # Extract prepositional phrases
    prep_phrases = re.findall(r'\b(in|on|at|by|with|from|to|for|of|about) ([^,.!?;:]+)', sentence)
    for prep, phrase in prep_phrases:
        if len(phrase.split()) >= 2:  # Only phrases with at least 2 words
            key_phrases.append(f"{prep} {phrase}")
    
    # If we couldn't extract good phrases, take some n-grams
    if not key_phrases and len(words) >= 3:
        for i in range(len(words) - 2):
            key_phrases.append(' '.join(words[i:i+3]).strip(".,;:()[]{}\"'"))
    
    # Remove duplicates and very short phrases
    unique_phrases = []
    for phrase in key_phrases:
        if phrase and len(phrase) > 5 and phrase not in unique_phrases:
            unique_phrases.append(phrase)
    
    return unique_phrases[:3]  # Return top 3 phrases

def generate_basic_questions(sentence):
    """Generate basic questions from a sentence without ML models."""
    questions = []
    
    # Extract potential entities
    entities = extract_entities(sentence)
    
    # Extract key phrases
    key_phrases = extract_key_phrases(sentence)
    
    # Find action verbs (simplified approach)
    words = sentence.split()
    action_words = []
    for word in words:
        # Simple check for common verbs (simplified)
        if word.lower().endswith(("ed", "ing", "s", "es")) and len(word) > 3:
            action_words.append(word.strip('.,;:()[]{}'))
    
    # Create questions about entities
    for entity in entities[:2]:  # Limit to 2 entities
        questions.append({
            "question": f"What is mentioned about {entity}?",
            "answer": sentence,
            "entity": entity
        })
    
    # Create questions about key phrases
    for phrase in key_phrases[:2]:  # Limit to 2 key phrases
        questions.append({
            "question": f"What does the text say about {phrase}?",
            "answer": sentence,
            "entity": phrase
        })
    
    # Create questions about actions
    for action in action_words[:1]:  # Limit to 1 action
        questions.append({
            "question": f"What is {action} in this context?",
            "answer": sentence,
            "entity": action
        })
    
    # If no entities or actions found, create a general question
    if not questions and len(sentence) > 20:
        # Extract a key phrase (simplified)
        key_phrase = ' '.join(words[1:4]) if len(words) > 4 else ' '.join(words[:3])
        questions.append({
            "question": f"What does the text say about {key_phrase}?",
            "answer": sentence,
            "entity": key_phrase
        })
    
    # Add a "What" question based on the sentence structure
    if sentence.lower().startswith(("the", "a", "in", "on", "this")):
        what_question = "What " + ' '.join(words[1:5]) + "?"
        questions.append({
            "question": what_question,
            "answer": sentence,
            "entity": "main subject"
        })
    
    # Generate a "Why" question if appropriate keywords are present
    if any(word.lower() in sentence.lower() for word in ["because", "since", "therefore", "result", "cause", "reason"]):
        questions.append({
            "question": f"Why is this happening according to the text?",
            "answer": sentence,
            "entity": "reason"
        })
    
    # Generate a "How" question if appropriate
    if any(word.lower() in sentence.lower() for word in ["method", "process", "step", "procedure", "technique"]):
        questions.append({
            "question": f"How is this done according to the text?",
            "answer": sentence,
            "entity": "method"
        })
    
    return questions

def generate_questions_answers(paragraphs):
    """Generate question-answer pairs using basic techniques only."""
    qa_pairs = []
    
    # Initialize text generator (if available)
    text_generator = initialize_text_generator()
    
    print("Generating questions and answers...")
    for paragraph in tqdm(paragraphs):
        try:
            # Extract key sentences from the paragraph
            key_sentences = extract_key_sentences(paragraph)
            
            paragraph_qa_pairs = []
            
            # Generate basic questions for each sentence
            for sentence in key_sentences:
                # Skip very short or very long sentences
                if len(sentence) < 10 or len(sentence) > 500:
                    continue
                    
                # Generate basic questions
                basic_qa_pairs = generate_basic_questions(sentence)
                paragraph_qa_pairs.extend(basic_qa_pairs)
            
            # Improve questions if we have a text generator
            if text_generator and paragraph_qa_pairs:
                for qa_pair in paragraph_qa_pairs:
                    # Try to generate a better question
                    prompt = f"Create a specific question about '{qa_pair['entity']}' based on this text: {qa_pair['answer']}"
                    
                    try:
                        improved_question = text_generator(
                            prompt, 
                            max_length=50, 
                            do_sample=True,
                            num_return_sequences=1
                        )[0]["generated_text"]
                        
                        # Use the improved question if it looks reasonable
                        if len(improved_question) > 10 and "?" in improved_question:
                            qa_pair["question"] = improved_question
                    except Exception as e:
                        # If improvement fails, keep the original question
                        pass
            
            # Add the paragraph context and save the QA pairs
            for qa_pair in paragraph_qa_pairs:
                qa_pairs.append({
                    "context": paragraph,
                    "question": qa_pair["question"],
                    "answer": qa_pair["answer"]
                })
        except Exception as e:
            print(f"Error generating Q&A for paragraph: {e}")
            continue
    
    return qa_pairs

def save_qa_dataset(qa_pairs, output_file="qa_dataset.json"):
    """Save the QA pairs to a JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"data": qa_pairs}, f, indent=2)
        print(f"Dataset saved successfully to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving dataset: {e}")
        return False

def main():
    input_file = "temp.txt"
    output_file = "qa_dataset.json"
    
    # Read file content
    text_content = read_text_file(input_file)
    if not text_content:
        return
    
    # Split into paragraphs
    print("Processing text...")
    paragraphs = split_text_into_paragraphs(text_content)
    print(f"Found {len(paragraphs)} paragraphs of sufficient length")
    
    # Limit the number of paragraphs to process if there are too many
    max_paragraphs = 1000
    if len(paragraphs) > max_paragraphs:
        print(f"Processing only the first {max_paragraphs} paragraphs to avoid excessive processing time")
        paragraphs = paragraphs[:max_paragraphs]
    
    # Generate QA pairs
    qa_pairs = generate_questions_answers(paragraphs)
    print(f"Generated {len(qa_pairs)} question-answer pairs")
    
    # Save dataset
    save_qa_dataset(qa_pairs, output_file)
    
    # Print sample of the dataset
    sample_size = min(3, len(qa_pairs))
    if sample_size > 0:
        print("\nSample of generated QA pairs:")
        for i, qa in enumerate(qa_pairs[:sample_size]):
            print(f"\nPair {i+1}:")
            print(f"Context: {qa['context'][:100]}...")
            print(f"Question: {qa['question']}")
            print(f"Answer: {qa['answer']}")
    else:
        print("\nNo QA pairs were generated. Please check the logs above for errors.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Saving any progress...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please make sure you have all required libraries installed:")
        print("pip install transformers tqdm")
        print("For PyTorch users: pip install torch")