import json
import os
import re

from groq import Groq

GROQ_MODEL = "llama-3.3-70b-versatile"

_SYSTEM_PROMPT = (
    "You are an expert text-forensics analyst who distinguishes AI-generated "
    "writing from human-written prose. Judge the submitted text on holistic "
    "semantic and stylistic coherence: generic hedging phrases (\"it is "
    "important to note\", \"furthermore\"), tidy parallel structure, and lack "
    "of concrete specific detail all lean AI-generated. Idiosyncratic voice, "
    "concrete specific detail, and uneven structure lean human-written. "
    "Respond with ONLY a JSON object of the form "
    '{"ai_probability": <float between 0 and 1>} '
    "where the float is your calibrated probability that the text is "
    "AI-generated. No other text."
)

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _client


def groq_ai_score(text):
    """Return a float 0-1: Groq's estimated probability the text is AI-generated."""
    completion = _get_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    parsed = json.loads(completion.choices[0].message.content)
    score = float(parsed["ai_probability"])
    return max(0.0, min(1.0, score))


_SENTENCE_SPLIT_RE = re.compile(r"[.!?]+")
_WORD_RE = re.compile(r"[A-Za-z']+")
_REPEATED_PUNCT_RE = re.compile(r"([!?])\1+")
_EXPRESSIVE_CHARS = ("—", "...", ";", ":", "(", ")", '"')


def _sentence_word_counts(text):
    sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(text) if s.strip()]
    return [len(_WORD_RE.findall(s)) for s in sentences]


def _sentence_variance_score(text):
    """Human writing tends toward uneven sentence lengths; AI text trends uniform."""
    lengths = _sentence_word_counts(text)
    if len(lengths) < 3:
        return 0.5  # too few sentences for variance to be meaningful
    mean = sum(lengths) / len(lengths)
    if mean == 0:
        return 0.5
    variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
    cv = (variance**0.5) / mean
    # cv == 0 (perfectly uniform) -> 1.0 (AI-like); cv >= 0.6 -> 0.0 (human-like)
    return max(0.0, min(1.0, 1 - cv / 0.6))


def _type_token_score(text):
    """Lower vocabulary diversity (type-token ratio) leans AI; higher leans human.

    Thresholds calibrated for paragraph-length submissions (a few sentences),
    where TTR naturally clusters around 0.75-0.95 -- not corpus-scale text,
    where TTR is much lower because repetition accumulates over length.
    """
    words = [w.lower() for w in _WORD_RE.findall(text)]
    if len(words) < 8:
        return 0.5  # too few words for TTR to be meaningful
    ttr = len(set(words)) / len(words)
    # ttr <= 0.75 -> 1.0 (AI-like); ttr >= 0.95 -> 0.0 (human-like)
    return max(0.0, min(1.0, (0.95 - ttr) / 0.20))


def _punctuation_score(text):
    """Lower density of expressive/irregular punctuation leans AI; higher leans human.

    Asymmetric on purpose: the *absence* of expressive punctuation is weak
    evidence (plenty of careful human writing -- e.g. formal/academic prose --
    uses none either), so density == 0 caps at a mild AI lean (0.6), not full
    confidence (1.0). The *presence* of expressive markers is much stronger
    evidence of a human hand, so it still scales down to 0.0.
    """
    word_count = max(1, len(_WORD_RE.findall(text)))
    expressive_chars = sum(text.count(c) for c in _EXPRESSIVE_CHARS)
    repeated_punct = len(_REPEATED_PUNCT_RE.findall(text))
    # len >= 3 excludes common short acronyms ("AI", "US", "OK") that aren't
    # actually emphasis -- only longer ALL-CAPS words read as stylistic shouting.
    all_caps_words = len(
        [w for w in _WORD_RE.findall(text) if len(w) >= 3 and w.isupper()]
    )
    density = (expressive_chars + repeated_punct + all_caps_words) / word_count
    # density >= 0.08 -> 0.0 (human-like); density == 0 -> 0.6 (mild AI-like)
    return max(0.0, min(0.6, 0.6 - density * (0.6 / 0.08)))


def stylometric_score(text):
    """Return a float 0-1: structural-heuristic probability the text is AI-generated.

    Pure Python, no external libraries, per planning.md Signal 2: combines
    sentence-length variance, type-token ratio, and punctuation density/variety.
    """
    sub_scores = (
        _sentence_variance_score(text),
        _type_token_score(text),
        _punctuation_score(text),
    )
    return sum(sub_scores) / len(sub_scores)
