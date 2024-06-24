from flask import Flask, request, jsonify
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from spacy_langdetect import LanguageDetector
import spacy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load language model and tokenizer (example with GPT-2)
model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Set special token ids
pad_token_id = tokenizer.eos_token_id  # Set pad_token_id to eos_token_id for open-end generation

# Set up sentiment analysis pipeline (example with Hugging Face Transformers)
sentiment_analyzer = pipeline("sentiment-analysis")
nlp = spacy.load("en_core_web_sm")

@spacy.Language.factory('language_detector')
def create_language_detector(nlp, name):
    return LanguageDetector()

nlp.add_pipe('language_detector')

def detect_language(text):
    doc = nlp(text)
    return doc._.language['language']

@app.route('/process_question', methods=['POST'])
def process_question():
    try:
        data = request.get_json()
        question = data['question']

        # Detect language of the question
        language = detect_language(question)

        # Analyze sentiment of the question
        sentiment_result = sentiment_analyzer(question)
        sentiment_label = sentiment_result[0]['label']

        # Create prompt template based on language and sentiment
        prompt_template = f"Respond in {language} with a {sentiment_label} tone like amazon customer service for this query:"
        prompt = prompt_template + question
        print(prompt)

        # Tokenize the prompt
        inputs = tokenizer(prompt, return_tensors="pt")


        # Generate response from GPT-2 model with sampling
        outputs_sampling = model.generate(
            inputs['input_ids'],
            attention_mask=inputs['attention_mask'],
            max_length=200,
            pad_token_id=pad_token_id,
            num_return_sequences=1,
            do_sample=True,
            top_p=0.95,  # Nucleus sampling
            top_k=50  # Top-k sampling
        )

        response_sampling = tokenizer.decode(outputs_sampling[0], skip_special_tokens=True)

        return jsonify({
            'response_sampling': response_sampling
        })

    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(debug=True)

