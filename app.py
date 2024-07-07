from textblob import TextBlob
from dataclasses import dataclass

@dataclass
class Mood:
    emoji: str 
    sentiment: float 


def get_mood(input_text: str, *, threshold: float) -> Mood:
    sentiment: float = TextBlob(input_text).sentiment.polarity
    
    friendly_threshold: float = threshold
    hostile_threshold: float = -threshold

    if sentiment >= friendly_threshold:
        return Mood ('HAPPY OR POSITIVE 😀', sentiment)
    elif sentiment <= friendly_threshold:
        return Mood ('ANGRY OR NEGATIVE 😡', sentiment)
    else:
        return Mood ('NEUTRAL 😐', sentiment)
    

if __name__ == '__main__':
    while True:
        text: str = input('Text: ')
        mood: Mood = get_mood(text, threshold=0.3)

        print(f'{mood.emoji} ({mood.sentiment})')
