import re
import math
import pandas as pd
from collections import Counter

# --- OPTIONAL IMPORTS (Graceful Fallback) ---
# 1. VADER Sentiment Analysis
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _vader = SentimentIntensityAnalyzer()
except ImportError:
    _vader = None
    print("Warning: vaderSentiment not found. Using heuristic fallback for sentiment.")

# 2. NLTK (for advanced tokenization if needed, though we use regex for speed)
try:
    import nltk
    # check if punkt is downloaded, if not, try to download
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
except ImportError:
    pass

# --- CONSTANTS & CONFIGURATION ---

# Maps abstract concepts to list of acceptable phrases/regex
KEYWORD_MAP = {
    "name": ["name is", "my name is", "i am", "myself", r"\bthis is\b", r"\bmy name\b"],
    "age": ["age", "years old", r"\b\d+\s*years\s*old\b", r"\bi am \d+\b", r"\bI'm \d+\b"],
    "school": ["school", "student of", "study in", "studying in", "class of"],
    "class": ["class", "grade", "standard", r"\b8th\b", r"\b9th\b", r"\b10th\b"],
    "family": ["family", "parents", "mother", "father", "brother", "sister", r"\bwe (are|'re) \d+ people\b"],
    "hobby": ["hobby", "hobbies", "like to", "love to", "enjoy", "playing", "play"],
    "interest": ["interest", "passionate", "fan of", "interested in"],
    "goal": ["goal", "ambition", "dream", "want to be", "i want to"],
    "fun_fact": ["fun fact", "once", "secret", "don't know", "dont know", "surprising"],
}

# Filler words to detect (Used with \b regex to avoid partial matches like 'so' in 'software')
FILLER_WORDS = {
    "um", "uh", "like", "you know", "so", "actually", "basically", "right",
    "i mean", "well", "kinda", "sort of", "okay", "hmm", "ah", "erm", "huh"
}

# Salutation patterns categorized by score
SALUTATIONS = {
    "excellent": [r"i am excited to introduce", r"feeling great", r"i'm excited", r"i am excited"],
    "good": [r"good morning", r"good afternoon", r"good evening", r"good day", r"hello everyone"],
    "normal": [r"\bhi\b", r"\bhello\b"],
}

# --- HELPER FUNCTIONS ---

def _lower_and_clean(text):
    """Normalizes text to lowercase."""
    return text.lower()

def _find_any_pattern(text, patterns):
    """Returns True if any regex pattern matches the text."""
    text_l = text.lower()
    for p in patterns:
        if re.search(p, text_l):
            return True
    return False

# --- SCORING FUNCTIONS ---

def detect_salutation_level(text):
    """
    Score: 5 (Excellent), 4 (Good), 2 (Normal), 0 (None)
    """
    t = _lower_and_clean(text)
    for p in SALUTATIONS["excellent"]:
        if re.search(p, t):
            return 5, "Excellent"
    for p in SALUTATIONS["good"]:
        if re.search(p, t):
            return 4, "Good"
    for p in SALUTATIONS["normal"]:
        if re.search(p, t):
            return 2, "Normal"
    return 0, "No salutation detected"

def keyword_presence_score(text, weight=30):
    """
    Checks for Mandatory (Name, Age, School, Class, Family, Hobby)
    and Optional (Goal, Fun Fact, Interest) keywords.
    """
    t = _lower_and_clean(text)
    must = ["name", "age", "school", "class", "family", "hobby"]
    optional = ["goal", "fun_fact", "interest"]

    # Count found keywords
    found_must_list = [k for k in must if _find_any_pattern(t, KEYWORD_MAP.get(k, []))]
    found_opt_list = [k for k in optional if _find_any_pattern(t, KEYWORD_MAP.get(k, []))]
    
    found_must = len(found_must_list)
    found_opt = len(found_opt_list)

    # Weighted Calculation: 20 points for Mandatory, 10 for Optional
    must_score = (found_must / len(must)) * 20 if must else 0
    opt_score = (found_opt / len(optional)) * 10 if optional else 0
    
    raw_score = must_score + opt_score
    final_score = min(raw_score, weight)

    details = {
        "found_must": found_must_list,
        "found_optional": found_opt_list,
        "raw_score": raw_score
    }
    return final_score, details

def flow_score(text, weight=5):
    """
    Checks if the average position of concepts follows:
    Salutation -> Basic Info -> Additional Info -> Closing
    """
    t = _lower_and_clean(text)
    
    # define groups patterns
    groups_map = {
        "sal": SALUTATIONS["good"] + SALUTATIONS["normal"] + SALUTATIONS["excellent"],
        "basic": KEYWORD_MAP["name"] + KEYWORD_MAP["age"] + KEYWORD_MAP["class"] + KEYWORD_MAP["school"],
        "add": KEYWORD_MAP["hobby"] + KEYWORD_MAP["interest"] + KEYWORD_MAP["goal"] + KEYWORD_MAP["fun_fact"],
        "end": [r"thank you", r"thanks", r"thankyou", r"that's all"]
    }

    # Find average position (index) of each group in the text
    positions = {}
    for group_name, patterns in groups_map.items():
        indices = []
        for p in patterns:
            # Find all matches for this pattern
            for match in re.finditer(p, t):
                indices.append(match.start())
        
        # Calculate average position if any keywords found
        if indices:
            positions[group_name] = sum(indices) / len(indices)
        else:
            positions[group_name] = None

    # Sequence to check: Salutation < Basic < Additional < End
    sequence = ["sal", "basic", "add", "end"]
    
    correct_pairs = 0
    total_pairs = 0
    
    for i in range(len(sequence)):
        for j in range(i+1, len(sequence)):
            pos1 = positions[sequence[i]]
            pos2 = positions[sequence[j]]
            
            # We can only compare if both groups exist
            if pos1 is not None and pos2 is not None:
                total_pairs += 1
                if pos1 < pos2:
                    correct_pairs += 1
    
    # Scoring Logic
    if total_pairs == 0:
        # Fallback: If text is too short to have pairs, give partial credit if Basic info exists
        if positions["basic"] is not None:
            return 3.0, {"reason": "Short text, basic info found"}
        return 0.0, {"reason": "No structure detected"}
    
    final_score = (correct_pairs / total_pairs) * weight
    return final_score, {"correct_pairs": correct_pairs, "total_pairs": total_pairs}

def speech_rate_score(text, duration_seconds=52, weight=10):
    """
    Calculates WPM and assigns score based on rubric bands.
    """
    # Count words (simple alphanumeric split)
    words = len(re.findall(r"\w+", text))
    
    # Safety for duration
    if duration_seconds <= 0: 
        duration_seconds = 52 # Default to sample if missing
        
    wpm = words / (duration_seconds / 60.0)
    
    # Rubric Bands
    # Ideal: 111-140 (10 pts)
    # Acceptable: 81-110 OR 141-160 (6 pts)
    # Poor: <81 OR >160 (2 pts)
    
    if 111 <= wpm <= 140:
        score = 10
    elif (81 <= wpm < 111) or (141 <= wpm <= 160):
        score = 6
    else:
        score = 2
        
    return score, {"wpm": round(wpm, 1), "word_count": words, "duration": duration_seconds}

def grammar_score(text, weight=10):
    """
    Heuristic grammar check (since LanguageTool requires Java).
    Checks for: Capitalization, Lowercase 'i', Repeated words.
    """
    # Split into sentences roughly
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    num_sentences = max(1, len(sentences))
    
    errors = 0
    
    # 1. Sentence start capitalization (ignore if it starts with number/quote)
    for s in sentences:
        if s and s[0].islower():
            errors += 1
            
    # 2. Lowercase standalone 'i'
    errors += len(re.findall(r"\s+i\s+", " " + text + " "))
    
    # 3. Repeated words (e.g. "the the")
    errors += len(re.findall(r"\b(\w+)\s+\1\b", text.lower()))
    
    # Calculate rate per 100 words (heuristic scaling)
    # We assume approx 10 words per sentence for normalization if word count is weird
    estimated_words = len(re.findall(r"\w+", text)) or (num_sentences * 10)
    
    errors_per_100 = (errors / estimated_words) * 100
    
    # Formula: 1 - min(errors/10, 1)
    score_ratio = 1.0 - min(errors_per_100 / 10.0, 1.0)
    final_score = score_ratio * weight
    
    return final_score, {"errors_detected": errors, "rate_per_100": round(errors_per_100, 2)}

def vocab_ttr_score(text, weight=10):
    """
    Type-Token Ratio (Unique Words / Total Words).
    """
    words = re.findall(r"\w+", text.lower())
    total = len(words)
    if total == 0: return 0, {}
    
    distinct = len(set(words))
    ttr = distinct / total
    
    # Rubric Bands
    if ttr >= 0.9: score = weight
    elif ttr >= 0.7: score = 0.8 * weight
    elif ttr >= 0.5: score = 0.6 * weight
    elif ttr >= 0.3: score = 0.4 * weight
    else: score = 0.2 * weight
    
    return score, {"ttr": round(ttr, 2)}

def filler_word_score(text, weight=15):
    """
    Percentage of filler words in text.
    Uses \b regex to ensure we don't match substrings (e.g. 'so' in 'software').
    """
    words = re.findall(r"\w+", text.lower())
    total_words = len(words)
    if total_words == 0: return 0, {}
    
    filler_count = 0
    found_fillers = []
    
    for filler in FILLER_WORDS:
        # Important: \b matches word boundaries
        matches = re.findall(r"\b" + re.escape(filler) + r"\b", text.lower())
        count = len(matches)
        if count > 0:
            filler_count += count
            found_fillers.append(f"{filler} ({count})")
            
    rate = (filler_count / total_words) * 100
    
    # Logic: Lower rate is better
    if rate <= 3.0: score = weight       # 0-3%
    elif rate <= 6.0: score = 12         # 4-6%
    elif rate <= 9.0: score = 9          # 7-9%
    elif rate <= 12.0: score = 6         # 10-12%
    else: score = 3                      # >13%
    
    return score, {"rate_percent": round(rate, 2), "count": filler_count, "found": found_fillers}

def sentiment_score(text, weight=15):
    """
    Uses VADER compound score (-1 to 1).
    Thresholds adjusted for realistic speech (0.5 is already very positive).
    """
    if _vader:
        # Use VADER library
        pol = _vader.polarity_scores(text)
        compound = pol["compound"]
        method = "VADER"
    else:
        # Fallback Heuristic
        method = "Heuristic"
        pos_words = {"excited", "love", "great", "good", "happy", "enjoy", "confident", "passion", "thank"}
        neg_words = {"hate", "bad", "boring", "sad", "nervous"}
        
        tokens = set(re.findall(r"\w+", text.lower()))
        pos_hits = len(tokens.intersection(pos_words))
        neg_hits = len(tokens.intersection(neg_words))
        
        # Rough compound simulation
        if pos_hits > neg_hits: compound = 0.6
        elif neg_hits > pos_hits: compound = -0.3
        else: compound = 0.0

    # Scoring Bands
    if compound >= 0.5: score = weight
    elif compound >= 0.3: score = 12
    elif compound >= 0.0: score = 9
    elif compound >= -0.2: score = 6
    else: score = 3
    
    return score, {"compound": compound, "method": method}

# --- MAIN ENTRY POINT ---

def evaluate_transcript(transcript, rubric_df=None, duration_seconds=52.0):
    """
    Main function to call all scorers and aggregate results.
    """
    if not transcript or not isinstance(transcript, str):
        return 0.0, []

    criteria_list = []
    
    # 1. Salutation
    s, d = detect_salutation_level(transcript)
    criteria_list.append({"name": "Salutation Level", "score": s, "weight": 5, "details": d})
    
    # 2. Keywords
    s, d = keyword_presence_score(transcript, weight=30)
    criteria_list.append({"name": "Keyword Presence", "score": s, "weight": 30, "details": d})
    
    # 3. Flow
    s, d = flow_score(transcript, weight=5)
    criteria_list.append({"name": "Flow (Order)", "score": s, "weight": 5, "details": d})
    
    # 4. Speech Rate
    s, d = speech_rate_score(transcript, duration_seconds, weight=10)
    criteria_list.append({"name": "Speech Rate (WPM)", "score": s, "weight": 10, "details": d})
    
    # 5. Grammar
    s, d = grammar_score(transcript, weight=10)
    criteria_list.append({"name": "Grammar Errors", "score": s, "weight": 10, "details": d})
    
    # 6. Vocabulary
    s, d = vocab_ttr_score(transcript, weight=10)
    criteria_list.append({"name": "Vocabulary (TTR)", "score": s, "weight": 10, "details": d})
    
    # 7. Filler Words
    s, d = filler_word_score(transcript, weight=15)
    criteria_list.append({"name": "Filler Word Rate", "score": s, "weight": 15, "details": d})
    
    # 8. Sentiment
    s, d = sentiment_score(transcript, weight=15)
    criteria_list.append({"name": "Sentiment", "score": s, "weight": 15, "details": d})
    
    # Calculate Total
    total_score = sum(c["score"] for c in criteria_list)
    
    return total_score, criteria_list

# --- EXAMPLE USAGE FOR TESTING ---
if __name__ == "__main__":
    # Sample Text (Rahul - Ideal Candidate)
    sample_text = (
        "Hello everyone, I am excited to introduce myself. "
        "My name is Rahul and I study in class 10 at Delhi Public School. "
        "I am 15 years old and live with my family which includes my parents and younger sister. "
        "My hobby is playing chess and I have a strong interest in coding. "
        "A fun fact about me is that I can solve a cube in under a minute. "
        "My goal is to become a software engineer. Thank you for listening."
    )
    
    # Assume 30 seconds duration for this text
    final_score, breakdown = evaluate_transcript(sample_text, duration_seconds=30)
    
    print(f"Final Score: {final_score:.2f} / 100")
    print("-" * 30)
    for item in breakdown:
        print(f"{item['name']}: {item['score']:.1f}/{item['weight']} | {item['details']}")