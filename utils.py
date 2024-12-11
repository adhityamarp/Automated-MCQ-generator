import spacy
import random
import PyPDF2
from docx import Document

nlp = spacy.load("en_core_web_sm")

def extract_keywords(text):
    doc = nlp(text)
    keywords = [token.text for token in doc if token.pos_ in ("NOUN", "PROPN") and len(token.text) > 2]
    return list(set(keywords))

def generate_distractors(correct_answer, keywords):
    distractors = [word for word in keywords if word.lower() != correct_answer.lower()]
    random.shuffle(distractors)
    return distractors[:3]

def generate_mcq_dynamic(text):
    keywords = extract_keywords(text)
    doc = nlp(text)
    questions = []
    for sentence in doc.sents:
        if "is" in sentence.text or "are" in sentence.text:
            question_formats = [
                lambda ans, sent: sent.text.replace(ans, "_____"),
                lambda ans, sent: f"What is {sent.text.split('is')[1].strip()}?" if len(sent.text.split('is')) > 1 else sent.text.replace(ans, "_____"),
                lambda ans, sent: f"Which of the following is {sent.text.split('is')[0].strip().replace(ans.strip(),'')}?" if len(sent.text.split('is')) > 1 else sent.text.replace(ans, "_____")
            ]
            correct_answer = next((word for word in keywords if word in sentence.text), None)
            if correct_answer:
                distractors = generate_distractors(correct_answer, keywords)
                question_format = random.choice(question_formats)
                questions.append({
                    "question": question_format(correct_answer, sentence),
                    "correct_answer": correct_answer,
                    "options": [correct_answer] + distractors
                })
    return questions

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text
