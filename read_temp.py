# import os
# import json
# import random
# import re
# from tqdm import tqdm

# def sentence_tokenize(text):
#     """Simple sentence tokenizer without using NLTK."""
#     # Handle common abbreviations to avoid splitting them
#     text = re.sub(r'(?<=[A-Za-z])\.(?=[A-Z])', '. ', text)  # Fix missing spaces after periods
#     text = re.sub(r'Mr\.', 'Mr_DOT_', text)
#     text = re.sub(r'Mrs\.', 'Mrs_DOT_', text)
#     text = re.sub(r'Dr\.', 'Dr_DOT_', text)
#     text = re.sub(r'Ph\.D\.', 'PhD_DOT_', text)
#     text = re.sub(r'i\.e\.', 'ie_DOT_', text)
#     text = re.sub(r'e\.g\.', 'eg_DOT_', text)
#     text = re.sub(r'etc\.', 'etc_DOT_', text)
    
#     # Split by sentence-ending punctuation followed by space and capital letter
#     sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    
#     # Restore abbreviations
#     sentences = [s.replace('Mr_DOT_', 'Mr.') for s in sentences]
#     sentences = [s.replace('Mrs_DOT_', 'Mrs.') for s in sentences]
#     sentences = [s.replace('Dr_DOT_', 'Dr.') for s in sentences]
#     sentences = [s.replace('PhD_DOT_', 'Ph.D.') for s in sentences]
#     sentences = [s.replace('ie_DOT_', 'i.e.') for s in sentences]
#     sentences = [s.replace('eg_DOT_', 'e.g.') for s in sentences]
#     sentences = [s.replace('etc_DOT_', 'etc.') for s in sentences]
    
#     return [s.strip() for s in sentences if s.strip()]

# def read_text_file(file_path):
#     """Read content from a text file."""
#     try:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             return file.read()
#     except FileNotFoundError:
#         print(f"Error: File '{file_path}' not found.")
#         return None
#     except Exception as e:
#         print(f"Error reading file: {e}")
#         return None

# def split_text_into_paragraphs(text, min_length=100):
#     """Split text into paragraphs, filtering out very short ones."""
#     paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
#     return [p for p in paragraphs if len(p) >= min_length]

# def extract_key_sentences(paragraph, max_sentences=3):
#     """Extract key sentences from a paragraph."""
#     sentences = sentence_tokenize(paragraph)
#     # If paragraph has fewer sentences than max_sentences, return all sentences
#     if len(sentences) <= max_sentences:
#         return sentences
#     # Otherwise, select sentences with some randomness to ensure variety
#     return random.sample(sentences, max_sentences)

# def initialize_text_generator():
#     """Initialize text generation model with proper error handling."""
#     text_generator = None
    
#     # Try to import transformers and initialize models
#     try:
#         from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
        
#         # Try to initialize text generation model
#         try:
#             print("Loading text generation model...")
#             tokenizer = AutoTokenizer.from_pretrained("facebook/bart-base")
#             model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-base")
#             text_generator = pipeline("text2text-generation", model=model, tokenizer=tokenizer)
#             print("Device set to use cpu")
#             print("Text generation model loaded successfully!")
#         except Exception as e:
#             print(f"Warning: Could not load text generation model: {e}")
#             print("Will use basic question generation instead.")
            
#     except ImportError as e:
#         print(f"Could not import transformers library: {e}")
#         print("Please install required packages:")
#         print("pip install transformers torch tqdm")
    
#     return text_generator

# def extract_entities(sentence):
#     """Extract potential named entities from a sentence."""
#     entities = []
    
#     # Find capitalized words not at the beginning of the sentence
#     words = sentence.split()
#     for i, word in enumerate(words):
#         # Skip first word of sentence and check for capitalization
#         if i > 0 and word and word[0].isupper() and len(word) > 1:
#             # Remove punctuation
#             clean_word = re.sub(r'[^\w\s]', '', word)
#             if clean_word:
#                 entities.append(clean_word)
    
#     # Find phrases in quotes
#     quoted = re.findall(r'"([^"]*)"', sentence)
#     entities.extend(quoted)
    
#     # Find potential organizations, locations, etc. with multiple capital words
#     capital_sequences = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', sentence)
#     entities.extend(capital_sequences)
    
#     # Remove duplicates while preserving order
#     unique_entities = []
#     for entity in entities:
#         if entity and entity not in unique_entities:
#             unique_entities.append(entity)
    
#     return unique_entities

# def extract_key_phrases(sentence):
#     """Extract key phrases from a sentence using simple rules."""
#     key_phrases = []
    
#     # Get noun phrases (simplified approach)
#     # This looks for adjective + noun patterns or noun sequences
#     words = sentence.split()
#     for i in range(len(words) - 1):
#         # Simple heuristic: capitalize words might be important
#         if words[i][0].isupper() and i > 0:
#             if i + 1 < len(words):
#                 phrase = f"{words[i]} {words[i+1]}"
#                 key_phrases.append(phrase.strip(".,;:()[]{}\"'"))
    
#     # Get verb phrases (simplified)
#     # Look for verb + object patterns
#     for i in range(len(words) - 2):
#         if words[i].lower().endswith(("ed", "ing", "s", "es")) and len(words[i]) > 3:
#             phrase = f"{words[i]} {words[i+1]}"
#             if i + 2 < len(words):
#                 phrase += f" {words[i+2]}"
#             key_phrases.append(phrase.strip(".,;:()[]{}\"'"))
    
#     # Extract prepositional phrases
#     prep_phrases = re.findall(r'\b(in|on|at|by|with|from|to|for|of|about) ([^,.!?;:]+)', sentence)
#     for prep, phrase in prep_phrases:
#         if len(phrase.split()) >= 2:  # Only phrases with at least 2 words
#             key_phrases.append(f"{prep} {phrase}")
    
#     # If we couldn't extract good phrases, take some n-grams
#     if not key_phrases and len(words) >= 3:
#         for i in range(len(words) - 2):
#             key_phrases.append(' '.join(words[i:i+3]).strip(".,;:()[]{}\"'"))
    
#     # Remove duplicates and very short phrases
#     unique_phrases = []
#     for phrase in key_phrases:
#         if phrase and len(phrase) > 5 and phrase not in unique_phrases:
#             unique_phrases.append(phrase)
    
#     return unique_phrases[:3]  # Return top 3 phrases

# def generate_basic_questions(sentence):
#     """Generate basic questions from a sentence without ML models."""
#     questions = []
    
#     # Extract potential entities
#     entities = extract_entities(sentence)
    
#     # Extract key phrases
#     key_phrases = extract_key_phrases(sentence)
    
#     # Find action verbs (simplified approach)
#     words = sentence.split()
#     action_words = []
#     for word in words:
#         # Simple check for common verbs (simplified)
#         if word.lower().endswith(("ed", "ing", "s", "es")) and len(word) > 3:
#             action_words.append(word.strip('.,;:()[]{}'))
    
#     # Create questions about entities
#     for entity in entities[:2]:  # Limit to 2 entities
#         questions.append({
#             "question": f"What is mentioned about {entity}?",
#             "answer": sentence,
#             "entity": entity
#         })
    
#     # Create questions about key phrases
#     for phrase in key_phrases[:2]:  # Limit to 2 key phrases
#         questions.append({
#             "question": f"What does the text say about {phrase}?",
#             "answer": sentence,
#             "entity": phrase
#         })
    
#     # Create questions about actions
#     for action in action_words[:1]:  # Limit to 1 action
#         questions.append({
#             "question": f"What is {action} in this context?",
#             "answer": sentence,
#             "entity": action
#         })
    
#     # If no entities or actions found, create a general question
#     if not questions and len(sentence) > 20:
#         # Extract a key phrase (simplified)
#         key_phrase = ' '.join(words[1:4]) if len(words) > 4 else ' '.join(words[:3])
#         questions.append({
#             "question": f"What does the text say about {key_phrase}?",
#             "answer": sentence,
#             "entity": key_phrase
#         })
    
#     # Add a "What" question based on the sentence structure
#     if sentence.lower().startswith(("the", "a", "in", "on", "this")):
#         what_question = "What " + ' '.join(words[1:5]) + "?"
#         questions.append({
#             "question": what_question,
#             "answer": sentence,
#             "entity": "main subject"
#         })
    
#     # Generate a "Why" question if appropriate keywords are present
#     if any(word.lower() in sentence.lower() for word in ["because", "since", "therefore", "result", "cause", "reason"]):
#         questions.append({
#             "question": f"Why is this happening according to the text?",
#             "answer": sentence,
#             "entity": "reason"
#         })
    
#     # Generate a "How" question if appropriate
#     if any(word.lower() in sentence.lower() for word in ["method", "process", "step", "procedure", "technique"]):
#         questions.append({
#             "question": f"How is this done according to the text?",
#             "answer": sentence,
#             "entity": "method"
#         })
    
#     return questions

# def generate_questions_answers(paragraphs):
#     """Generate question-answer pairs using basic techniques only."""
#     qa_pairs = []
    
#     # Initialize text generator (if available)
#     text_generator = initialize_text_generator()
    
#     print("Generating questions and answers...")
#     for paragraph in tqdm(paragraphs):
#         try:
#             # Extract key sentences from the paragraph
#             key_sentences = extract_key_sentences(paragraph)
            
#             paragraph_qa_pairs = []
            
#             # Generate basic questions for each sentence
#             for sentence in key_sentences:
#                 # Skip very short or very long sentences
#                 if len(sentence) < 10 or len(sentence) > 500:
#                     continue
                    
#                 # Generate basic questions
#                 basic_qa_pairs = generate_basic_questions(sentence)
#                 paragraph_qa_pairs.extend(basic_qa_pairs)
            
#             # Improve questions if we have a text generator
#             if text_generator and paragraph_qa_pairs:
#                 for qa_pair in paragraph_qa_pairs:
#                     # Try to generate a better question
#                     prompt = f"Create a specific question about '{qa_pair['entity']}' based on this text: {qa_pair['answer']}"
                    
#                     try:
#                         improved_question = text_generator(
#                             prompt, 
#                             max_length=50, 
#                             do_sample=True,
#                             num_return_sequences=1
#                         )[0]["generated_text"]
                        
#                         # Use the improved question if it looks reasonable
#                         if len(improved_question) > 10 and "?" in improved_question:
#                             qa_pair["question"] = improved_question
#                     except Exception as e:
#                         # If improvement fails, keep the original question
#                         pass
            
#             # Add the paragraph context and save the QA pairs
#             for qa_pair in paragraph_qa_pairs:
#                 qa_pairs.append({
#                     "context": paragraph,
#                     "question": qa_pair["question"],
#                     "answer": qa_pair["answer"]
#                 })
#         except Exception as e:
#             print(f"Error generating Q&A for paragraph: {e}")
#             continue
    
#     return qa_pairs

# def save_qa_dataset(qa_pairs, output_file="qa_dataset.json"):
#     """Save the QA pairs to a JSON file."""
#     try:
#         with open(output_file, 'w', encoding='utf-8') as f:
#             json.dump({"data": qa_pairs}, f, indent=2)
#         print(f"Dataset saved successfully to {output_file}")
#         return True
#     except Exception as e:
#         print(f"Error saving dataset: {e}")
#         return False

# def main():
#     input_file = "temp.txt"
#     output_file = "qa_dataset.json"
    
#     # Read file content
#     text_content = read_text_file(input_file)
#     if not text_content:
#         return
    
#     # Split into paragraphs
#     print("Processing text...")
#     paragraphs = split_text_into_paragraphs(text_content)
#     print(f"Found {len(paragraphs)} paragraphs of sufficient length")
    
#     # Limit the number of paragraphs to process if there are too many
#     max_paragraphs = 100
#     if len(paragraphs) > max_paragraphs:
#         print(f"Processing only the first {max_paragraphs} paragraphs to avoid excessive processing time")
#         paragraphs = paragraphs[:max_paragraphs]
    
#     # Generate QA pairs
#     qa_pairs = generate_questions_answers(paragraphs)
#     print(f"Generated {len(qa_pairs)} question-answer pairs")
    
#     # Save dataset
#     save_qa_dataset(qa_pairs, output_file)
    
#     # Print sample of the dataset
#     sample_size = min(3, len(qa_pairs))
#     if sample_size > 0:
#         print("\nSample of generated QA pairs:")
#         for i, qa in enumerate(qa_pairs[:sample_size]):
#             print(f"\nPair {i+1}:")
#             print(f"Context: {qa['context'][:100]}...")
#             print(f"Question: {qa['question']}")
#             print(f"Answer: {qa['answer']}")
#     else:
#         print("\nNo QA pairs were generated. Please check the logs above for errors.")

# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         print("\nProcess interrupted by user. Saving any progress...")
#     except Exception as e:
#         print(f"\nAn error occurred: {e}")
#         print("Please make sure you have all required libraries installed:")
#         print("pip install transformers tqdm")
#         print("For PyTorch users: pip install torch")


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

def generate_questions_answers(paragraphs, batch_size=50):
    """Generate question-answer pairs using basic techniques only, in batches."""
    qa_pairs = []
    
    # Initialize text generator (if available)
    text_generator = initialize_text_generator()
    
    # Process paragraphs in batches to prevent memory issues
    total_batches = (len(paragraphs) + batch_size - 1) // batch_size
    
    print(f"Generating questions and answers for {len(paragraphs)} paragraphs...")
    print(f"Processing in {total_batches} batches of {batch_size} paragraphs each")
    
    for batch_idx in range(total_batches):
        start_idx = batch_idx * batch_size
        end_idx = min((batch_idx + 1) * batch_size, len(paragraphs))
        
        print(f"\nProcessing batch {batch_idx + 1}/{total_batches} (paragraphs {start_idx + 1}-{end_idx})...")
        batch_paragraphs = paragraphs[start_idx:end_idx]
        
        batch_qa_pairs = []
        for paragraph in tqdm(batch_paragraphs):
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
                    batch_qa_pairs.append({
                        "context": paragraph,
                        "question": qa_pair["question"],
                        "answer": qa_pair["answer"]
                    })
            except Exception as e:
                print(f"Error generating Q&A for paragraph: {e}")
                continue
        
        # Add batch results to overall results
        qa_pairs.extend(batch_qa_pairs)
        print(f"Generated {len(batch_qa_pairs)} QA pairs in this batch. Total: {len(qa_pairs)}")
        
        # Optional: Save intermediate results for large datasets
        if total_batches > 1:
            temp_output_file = f"qa_dataset_batch_{batch_idx + 1}.json"
            try:
                with open(temp_output_file, 'w', encoding='utf-8') as f:
                    json.dump({"data": batch_qa_pairs}, f, indent=2)
                print(f"Intermediate batch results saved to {temp_output_file}")
            except Exception as e:
                print(f"Warning: Could not save intermediate results: {e}")
    
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
    
    # Get user-defined parameters with defaults
    try:
        max_paragraphs = int(input("Enter maximum number of paragraphs to process (default: 1000, enter 0 for all): ") or 1000)
        batch_size = int(input("Enter batch size for processing (default: 50): ") or 50)
    except ValueError:
        print("Invalid input. Using default values: max_paragraphs=1000, batch_size=50")
        max_paragraphs = 1000
        batch_size = 50
    
    # Read file content
    text_content = read_text_file(input_file)
    if not text_content:
        return
    
    # Split into paragraphs
    print("Processing text...")
    paragraphs = split_text_into_paragraphs(text_content)
    print(f"Found {len(paragraphs)} paragraphs of sufficient length")
    
    # Limit the number of paragraphs to process if specified
    if max_paragraphs > 0 and len(paragraphs) > max_paragraphs:
        print(f"Processing only the first {max_paragraphs} paragraphs as specified")
        paragraphs = paragraphs[:max_paragraphs]
    else:
        print(f"Processing all {len(paragraphs)} paragraphs")
    
    # Generate QA pairs with batching for large datasets
    qa_pairs = generate_questions_answers(paragraphs, batch_size=batch_size)
    print(f"Generated a total of {len(qa_pairs)} question-answer pairs")
    
    # Save final dataset
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