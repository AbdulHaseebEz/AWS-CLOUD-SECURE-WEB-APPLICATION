const API_URL = 'https://wqjynsr74tock6q4pd33kg3meu0mzkde.lambda-url.us-east-1.on.aws/';

const analyzeBtn = document.getElementById('analyzeBtn');
const textInput = document.getElementById('textInput');
const statusMessage = document.getElementById('statusMessage');
const resultsSection = document.getElementById('resultsSection');

const sentimentResult = document.getElementById('sentimentResult');
const entitiesResult = document.getElementById('entitiesResult');
const keyPhrasesResult = document.getElementById('keyPhrasesResult');
const statsResult = document.getElementById('statsResult');

function escapeHtml(value) {
  if (value === null || value === undefined) return '';
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function renderSentiment(sentiment) {
  if (!sentiment) {
    sentimentResult.innerHTML = '<p>No sentiment data found.</p>';
    return;
  }

  const scores = sentiment.scores || {};

  sentimentResult.innerHTML = `
    <p><strong>Overall:</strong> ${escapeHtml(sentiment.overall || 'N/A')}</p>
    <p><strong>Confidence:</strong> ${escapeHtml(sentiment.confidence || 'N/A')}</p>
    <br>
    <p><strong>Scores:</strong></p>
    <ul>
      <li>Positive: ${escapeHtml(scores.Positive || '0%')}</li>
      <li>Negative: ${escapeHtml(scores.Negative || '0%')}</li>
      <li>Neutral: ${escapeHtml(scores.Neutral || '0%')}</li>
      <li>Mixed: ${escapeHtml(scores.Mixed || '0%')}</li>
    </ul>
    <br>
    <p><strong>Positive Words:</strong> ${
      sentiment.positiveWords && sentiment.positiveWords.length
        ? escapeHtml(sentiment.positiveWords.join(', '))
        : 'None'
    }</p>
    <p><strong>Negative Words:</strong> ${
      sentiment.negativeWords && sentiment.negativeWords.length
        ? escapeHtml(sentiment.negativeWords.join(', '))
        : 'None'
    }</p>
  `;
}

function renderEntities(entities) {
  if (!entities || entities.length === 0) {
    entitiesResult.innerHTML = '<p>No entities found.</p>';
    return;
  }

  let html = '<ul>';
  entities.forEach((entity) => {
    html += `
      <li>
        <strong>${escapeHtml(entity.text)}</strong>
        — ${escapeHtml(entity.type || 'Unknown')}
        (${escapeHtml(entity.confidence || 'N/A')})
      </li>
    `;
  });
  html += '</ul>';

  entitiesResult.innerHTML = html;
}

function renderKeyPhrases(keyPhrases) {
  if (!keyPhrases || keyPhrases.length === 0) {
    keyPhrasesResult.innerHTML = '<p>No key phrases found.</p>';
    return;
  }

  let html = '<ul>';
  keyPhrases.forEach((phrase) => {
    html += `
      <li>
        <strong>${escapeHtml(phrase.text)}</strong>
        — ${escapeHtml(phrase.confidence || 'N/A')}
      </li>
    `;
  });
  html += '</ul>';

  keyPhrasesResult.innerHTML = html;
}

function renderStats(stats) {
  if (!stats) {
    statsResult.innerHTML = '<p>No text statistics found.</p>';
    return;
  }

  let topWordsHtml = 'None';
  if (stats.topWords && stats.topWords.length > 0) {
    topWordsHtml = '<ul>';
    stats.topWords.forEach((item) => {
      topWordsHtml += `<li>${escapeHtml(item.word)} — ${escapeHtml(item.count)}</li>`;
    });
    topWordsHtml += '</ul>';
  }

  statsResult.innerHTML = `
    <p><strong>Word Count:</strong> ${escapeHtml(stats.wordCount ?? 'N/A')}</p>
    <p><strong>Sentence Count:</strong> ${escapeHtml(stats.sentenceCount ?? 'N/A')}</p>
    <p><strong>Average Words per Sentence:</strong> ${escapeHtml(stats.avgWordsPerSentence ?? 'N/A')}</p>
    <p><strong>Character Count:</strong> ${escapeHtml(stats.characterCount ?? 'N/A')}</p>
    <p><strong>Readability Score:</strong> ${escapeHtml(stats.readabilityScore ?? 'N/A')}</p>
    <p><strong>Readability Level:</strong> ${escapeHtml(stats.readabilityLevel ?? 'N/A')}</p>
    <br>
    <p><strong>Top Words:</strong></p>
    ${topWordsHtml}
  `;
}

async function analyzeText() {
  const text = textInput.value.trim();

  if (!text) {
    statusMessage.textContent = 'Please enter some text first.';
    resultsSection.classList.add('hidden');
    return;
  }

  statusMessage.textContent = 'Analyzing...';
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = 'Analyzing...';

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text })
    });

    const rawData = await response.json();

    if (!response.ok) {
      throw new Error(rawData.error || 'Something went wrong while analyzing the text.');
    }

    renderSentiment(rawData.sentiment);
    renderEntities(rawData.entities);
    renderKeyPhrases(rawData.keyPhrases);
    renderStats(rawData.textStatistics);

    resultsSection.classList.remove('hidden');
    statusMessage.textContent = 'Analysis completed successfully.';
  } catch (error) {
    console.error('Error:', error);
    statusMessage.textContent = `Error: ${error.message}`;
    resultsSection.classList.add('hidden');
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = 'Analyze Text';
  }
}

analyzeBtn.addEventListener('click', analyzeText);