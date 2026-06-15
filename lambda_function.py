import json
import re
import datetime
import boto3

s3 = boto3.client('s3', region_name='us-east-1')

# ============================================================
# CHANGE THIS TO YOUR S3 BUCKET NAME
# ============================================================
BUCKET_NAME = 'cs524-haseeb-website'
# ============================================================


# ==================== NLP ENGINE ====================

POSITIVE_WORDS = set([
    'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome',
    'love', 'happy', 'joy', 'beautiful', 'best', 'perfect', 'brilliant',
    'outstanding', 'superb', 'delightful', 'pleasant', 'nice', 'enjoy', 'glad',
    'thankful', 'grateful', 'exciting', 'impressive', 'remarkable', 'incredible',
    'magnificent', 'marvelous', 'terrific', 'fabulous', 'splendid', 'superior',
    'positive', 'succeed', 'success', 'win', 'winning', 'like', 'loved', 'loving',
    'helpful', 'comfortable', 'satisfied', 'proud', 'confident', 'optimistic',
    'cheerful', 'peaceful', 'calm', 'relaxed', 'inspired', 'motivated', 'strong',
    'reliable', 'efficient', 'innovative', 'creative', 'talented', 'skilled',
    'dedicated', 'passionate', 'enthusiastic', 'friendly', 'kind', 'generous',
    'warm', 'bright', 'clean', 'fresh', 'smooth', 'easy', 'free', 'safe',
    'secure', 'fast', 'quick', 'smart', 'wise', 'clever', 'fun', 'interesting',
    'engaging', 'valuable', 'useful', 'powerful', 'effective', 'productive',
    'healthy', 'vibrant', 'dynamic', 'modern', 'advanced', 'premium', 'quality',
    'recommended', 'popular', 'trusted', 'proven', 'exceptional', 'extraordinary'
])

NEGATIVE_WORDS = set([
    'bad', 'terrible', 'horrible', 'awful', 'worst', 'hate', 'sad', 'angry',
    'poor', 'disappointing', 'disgusting', 'dreadful', 'ugly', 'annoying',
    'boring', 'fail', 'failure', 'wrong', 'broken', 'useless', 'waste',
    'problem', 'issue', 'error', 'difficult', 'hard', 'pain', 'hurt', 'sick',
    'worried', 'afraid', 'fear', 'scared', 'anxious', 'stressed', 'frustrated',
    'confused', 'lost', 'lonely', 'miserable', 'unhappy', 'upset', 'regret',
    'sorry', 'unfortunately', 'worse', 'damage', 'destroy', 'ruin', 'crash',
    'bug', 'slow', 'expensive', 'overpriced', 'complicated', 'complex',
    'dangerous', 'risky', 'threat', 'weak', 'unreliable', 'unstable', 'messy',
    'dirty', 'noisy', 'crowded', 'chaotic', 'stressful', 'overwhelming',
    'exhausting', 'tiring', 'painful', 'suffering', 'struggling', 'lacking',
    'missing', 'incomplete', 'inadequate', 'insufficient', 'mediocre', 'average',
    'ordinary', 'subpar', 'inferior', 'flawed', 'defective', 'faulty', 'toxic',
    'harmful', 'negative', 'hostile', 'aggressive', 'violent', 'cruel', 'unfair',
    'unjust', 'dishonest', 'corrupt', 'fraud', 'scam', 'fake', 'spam'
])

COMMON_WORDS = set([
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'shall', 'can', 'to', 'of', 'in', 'for', 'on',
    'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before',
    'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'both',
    'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 'and', 'but', 'or',
    'if', 'while', 'because', 'until', 'about', 'against', 'it', 'its', 'this',
    'that', 'these', 'those', 'i', 'me', 'my', 'we', 'our', 'you', 'your',
    'he', 'him', 'his', 'she', 'her', 'they', 'them', 'their', 'what', 'which',
    'who', 'whom', 'up', 'out', 'just', 'also', 'now', 'new', 'like', 'get',
    'make', 'go', 'know', 'take', 'see', 'come', 'think', 'look', 'want',
    'give', 'use', 'find', 'tell', 'ask', 'work', 'seem', 'feel', 'try',
    'leave', 'call', 'keep', 'let', 'begin', 'show', 'hear', 'play', 'run',
    'move', 'live', 'believe', 'bring', 'happen', 'write', 'provide', 'sit',
    'stand', 'lose', 'pay', 'meet', 'include', 'continue', 'set', 'learn',
    'change', 'lead', 'understand', 'watch', 'follow', 'stop', 'create',
    'speak', 'read', 'allow', 'add', 'spend', 'grow', 'open', 'walk', 'offer',
    'remember', 'consider', 'appear', 'buy', 'wait', 'serve', 'die', 'send',
    'expect', 'build', 'stay', 'fall', 'cut', 'reach', 'kill', 'remain', 'am'
])

ENTITY_PATTERNS = {
    'PERSON': r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b',
    'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'URL': r'https?://[^\s]+',
    'PHONE': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    'DATE': r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',
    'NUMBER': r'\b\d+(?:\.\d+)?%?\b',
    'ORGANIZATION': r'\b(?:University|Institute|College|Inc|Corp|LLC|Ltd|Company|Association|Foundation|Academy|School|Department)\b',
}

KNOWN_LOCATIONS = [
    'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Hoboken',
    'New Jersey', 'California', 'Texas', 'Florida', 'Stevens', 'Manhattan',
    'Brooklyn', 'San Francisco', 'Seattle', 'Boston', 'Washington', 'London',
    'Paris', 'Tokyo', 'India', 'China', 'Germany', 'France', 'Canada',
    'Mexico', 'Brazil', 'America', 'United States', 'United Kingdom',
    'Europe', 'Asia', 'Africa', 'Australia', 'Virginia', 'Pennsylvania',
    'Ohio', 'Georgia', 'Michigan', 'North Carolina', 'New Hampshire',
    'Massachusetts', 'Connecticut', 'Oregon', 'Colorado', 'Nevada',
    'Arizona', 'Illinois', 'Maryland', 'Delaware', 'Vermont', 'Maine',
    'Miami', 'Dallas', 'Denver', 'Atlanta', 'Portland', 'Nashville',
    'San Diego', 'San Jose', 'Austin', 'Charlotte', 'Philadelphia',
    'Pittsburgh', 'Baltimore', 'Detroit', 'Minneapolis', 'Tampa',
    'Jersey City', 'Newark', 'Edison', 'Princeton', 'New Brunswick'
]


def analyze_sentiment(text):
    """Analyze the sentiment of the input text."""
    words = re.findall(r'\b[a-z]+\b', text.lower())
    if not words:
        return {
            'overall': 'NEUTRAL',
            'confidence': '100.0%',
            'scores': {'Positive': '0.0%', 'Negative': '0.0%', 'Neutral': '100.0%', 'Mixed': '0.0%'},
            'positiveWords': [],
            'negativeWords': []
        }

    pos_found = [w for w in words if w in POSITIVE_WORDS]
    neg_found = [w for w in words if w in NEGATIVE_WORDS]

    pos_count = len(pos_found)
    neg_count = len(neg_found)
    total = len(words)

    pos_score = pos_count / total
    neg_score = neg_count / total
    neutral_score = max(0, 1 - pos_score - neg_score)

    # Determine overall sentiment
    if pos_score > neg_score and pos_score > 0.03:
        sentiment = 'POSITIVE'
    elif neg_score > pos_score and neg_score > 0.03:
        sentiment = 'NEGATIVE'
    elif pos_count > 0 and neg_count > 0 and abs(pos_score - neg_score) < 0.02:
        sentiment = 'MIXED'
    else:
        sentiment = 'NEUTRAL'

    # Calculate confidence
    confidence = max(pos_score, neg_score, neutral_score)

    # Normalize scores to percentages
    norm = pos_score + neg_score + neutral_score
    if norm > 0:
        pos_pct = round((pos_score / norm) * 100, 2)
        neg_pct = round((neg_score / norm) * 100, 2)
        neu_pct = round((neutral_score / norm) * 100, 2)
    else:
        pos_pct = neg_pct = 0.0
        neu_pct = 100.0

    mixed_pct = round(min(pos_pct, neg_pct), 2)

    return {
        'overall': sentiment,
        'confidence': str(round(confidence * 100, 2)) + '%',
        'scores': {
            'Positive': str(pos_pct) + '%',
            'Negative': str(neg_pct) + '%',
            'Neutral': str(neu_pct) + '%',
            'Mixed': str(mixed_pct) + '%'
        },
        'positiveWords': list(set(pos_found)),
        'negativeWords': list(set(neg_found))
    }


def extract_entities(text):
    """Extract named entities from the text."""
    entities = []
    seen = set()

    # Pattern-based entity extraction
    for etype, pattern in ENTITY_PATTERNS.items():
        for match in re.finditer(pattern, text):
            val = match.group().strip()
            if val not in seen and len(val) > 1:
                seen.add(val)
                entities.append({
                    'text': val,
                    'type': etype,
                    'position': match.start(),
                    'confidence': '85.0%'
                })

    # Known location detection
    for loc in KNOWN_LOCATIONS:
        if loc.lower() in text.lower() and loc not in seen:
            seen.add(loc)
            idx = text.lower().find(loc.lower())
            entities.append({
                'text': loc,
                'type': 'LOCATION',
                'position': idx,
                'confidence': '90.0%'
            })

    # Sort by position in text
    entities.sort(key=lambda x: x['position'])
    return entities


def extract_key_phrases(text):
    """Extract key phrases from the text."""
    sentences = re.split(r'[.!?]+', text)
    phrases = []
    seen = set()

    for sent in sentences:
        words = sent.strip().split()
        for i in range(len(words)):
            for n in range(2, min(5, len(words) - i + 1)):
                phrase = ' '.join(words[i:i + n])
                clean = re.sub(r'[^a-z\s]', '', phrase.lower()).strip()
                phrase_words = clean.split()
                if (len(phrase_words) >= 2 and
                    not all(w in COMMON_WORDS for w in phrase_words) and
                    clean not in seen and
                    len(clean) > 4):
                    seen.add(clean)
                    score = 75 + len(phrase_words) * 5
                    phrases.append({
                        'text': phrase.strip(' ,;:'),
                        'confidence': str(round(score, 2)) + '%'
                    })

    # Sort by confidence (highest first) and return top 10
    phrases.sort(key=lambda x: float(x['confidence'].replace('%', '')), reverse=True)
    return phrases[:10]


def get_text_stats(text):
    """Calculate text statistics and readability metrics."""
    words = text.split()
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

    if not words:
        return {
            'wordCount': 0,
            'sentenceCount': 0,
            'avgWordsPerSentence': 0,
            'characterCount': 0,
            'readabilityScore': 0,
            'readabilityLevel': 'N/A',
            'topWords': []
        }

    # Calculate syllables per word
    syllable_count = sum(
        max(1, len(re.findall(r'[aeiouy]+', w.lower())))
        for w in words
    )
    avg_syllables = syllable_count / len(words)
    avg_sentence_len = len(words) / len(sentences) if sentences else 0

    # Flesch Reading Ease Score
    flesch = 206.835 - 1.015 * avg_sentence_len - 84.6 * avg_syllables
    flesch = max(0, min(100, flesch))

    # Determine readability level
    if flesch >= 80:
        level = 'Very Easy (6th grade)'
    elif flesch >= 60:
        level = 'Standard (8th-9th grade)'
    elif flesch >= 40:
        level = 'Difficult (College level)'
    else:
        level = 'Very Difficult (Professional)'

    # Word frequency analysis
    word_freq = {}
    for w in re.findall(r'\b[a-z]+\b', text.lower()):
        if w not in COMMON_WORDS and len(w) > 2:
            word_freq[w] = word_freq.get(w, 0) + 1

    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        'wordCount': len(words),
        'sentenceCount': len(sentences),
        'avgWordsPerSentence': round(avg_sentence_len, 1),
        'characterCount': len(text),
        'readabilityScore': round(flesch, 1),
        'readabilityLevel': level,
        'topWords': [{'word': w, 'count': c} for w, c in top_words]
    }


# ==================== LAMBDA HANDLER ====================

def lambda_handler(event, context):
    """Main Lambda handler - processes text analysis requests."""

    # CORS headers for cross-origin requests
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS, GET'
    }

    # Get HTTP method
    method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')

    # Handle CORS preflight request
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps('OK')
        }

    # Handle GET request (browser direct visit)
    if method == 'GET':
        return {
            'statusCode': 200,
            'headers': {**headers, 'Content-Type': 'text/html'},
            'body': '''
                <html>
                <head><title>CS524 AI Text Analyzer API</title></head>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px;">
                    <h2>CS524 AI Text Analyzer API</h2>
                    <p>This is the backend API for the CS524 AI-Powered Web Application.</p>
                    <p><b>Usage:</b> Send a POST request with a JSON body:</p>
                    <pre style="background: #f0f0f0; padding: 15px; border-radius: 5px;">
{
    "text": "Your text to analyze here"
}</pre>
                    <p><b>Response:</b> Sentiment analysis, entity extraction, key phrases, and readability statistics.</p>
                    <p style="color: #666; margin-top: 30px;">Stevens Institute of Technology - CS524 Cloud Computing</p>
                </body>
                </html>
            '''
        }

    # Handle POST request (text analysis)
    try:
        # Parse request body
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)

        text = body.get('text', '')

        if not text:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'No text provided. Send a JSON body with {"text": "your text here"}'
                })
            }

        if len(text) > 10000:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Text too long. Maximum 10,000 characters allowed.'
                })
            }

        # ===== Run all NLP analyses =====
        sentiment = analyze_sentiment(text)
        entities = extract_entities(text)
        key_phrases = extract_key_phrases(text)
        stats = get_text_stats(text)

        # Build results object
        results = {
            'inputText': text,
            'timestamp': datetime.datetime.now().isoformat(),
            'aiEngine': 'CS524 Custom NLP Engine (Python-based)',
            'sentiment': sentiment,
            'entities': entities,
            'keyPhrases': key_phrases,
            'textStatistics': stats
        }

        # ===== Store results in S3 =====
        try:
            ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            s3_key = f'results/analysis-{ts}.json'
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=json.dumps(results, indent=2),
                ContentType='application/json'
            )
            results['storedAt'] = f's3://{BUCKET_NAME}/{s3_key}'
        except Exception as e:
            results['storageNote'] = f'Could not store in S3: {str(e)}'

        # Return results
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(results)
        }

    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'Invalid JSON in request body.'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
