from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSequenceClassification,
)

# Sentiment Analysis Model
class SAM:
    """
    Sentiment analysis model using a pretrained pipeline.
    """

    def __init__(self):
        """
        Initialize the sentiment analysis model.
        """
         
        self.model_name = 'distilbert-base-uncased-finetuned-sst-2-english'
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.pipeline = pipeline(task='sentiment-analysis', model=self.model, tokenizer=self.tokenizer)

    def analyze_sentiment(self, text):
        """
        Analyze the sentiment for the given text.
        """

        results = self.pipeline(text)
        label = results[0]['label']
        score = results[0]['score']
        return {'label': label, 'score': score}