/**
 * Normalizer - Input normalization pipeline for AIML
 *
 * Handles:
 * - Substitution normalization (contractions, spelling, abbreviations)
 * - Sentence splitting
 * - Pattern fitting (uppercase, strip punctuation, collapse whitespace)
 * - Person/person2/gender pronoun substitutions
 */

// Default substitution maps
const DEFAULT_NORMAL_SUBS = {
  "aren't": "are not",
  "can't": "can not",
  "couldn't": "could not",
  "didn't": "did not",
  "doesn't": "does not",
  "don't": "do not",
  "hadn't": "had not",
  "hasn't": "has not",
  "haven't": "have not",
  "he'd": "he would",
  "he'll": "he will",
  "he's": "he is",
  "i'd": "i would",
  "i'll": "i will",
  "i'm": "i am",
  "i've": "i have",
  "isn't": "is not",
  "it'd": "it would",
  "it'll": "it will",
  "it's": "it is",
  "let's": "let us",
  "mightn't": "might not",
  "mustn't": "must not",
  "shan't": "shall not",
  "she'd": "she would",
  "she'll": "she will",
  "she's": "she is",
  "shouldn't": "should not",
  "that's": "that is",
  "there's": "there is",
  "they'd": "they would",
  "they'll": "they will",
  "they're": "they are",
  "they've": "they have",
  "wasn't": "was not",
  "we'd": "we would",
  "we'll": "we will",
  "we're": "we are",
  "we've": "we have",
  "weren't": "were not",
  "what's": "what is",
  "where's": "where is",
  "who's": "who is",
  "won't": "will not",
  "wouldn't": "would not",
  "you'd": "you would",
  "you'll": "you will",
  "you're": "you are",
  "you've": "you have",
  "wanna": "want to",
  "gonna": "going to",
  "gotta": "got to",
  "coulda": "could have",
  "shoulda": "should have",
  "woulda": "would have",
  "whatcha": "what are you",
  "kinda": "kind of",
  "sorta": "sort of",
  "dunno": "do not know",
  "lemme": "let me",
  "gimme": "give me",
  "ya": "you",
  "u": "you",
  "r": "are",
  "ur": "your",
  "thx": "thanks",
  "pls": "please",
  "plz": "please",
  "bc": "because",
  "cuz": "because",
  "coz": "because",
  "nope": "no",
  "yep": "yes",
  "yup": "yes",
  "yeah": "yes",
  "nah": "no",
  "ok": "okay",
  "k": "okay",
  "btw": "by the way",
  "imo": "in my opinion",
  "lol": "laughing out loud",
  "omg": "oh my god",
  "idk": "i do not know",
  "brb": "be right back",
  "dr.": "doctor",
  "mr.": "mister",
  "mrs.": "missus",
  "ms.": "miss",
  "jr.": "junior",
  "sr.": "senior",
  "prof.": "professor",
  "etc.": "et cetera",
  "vs.": "versus",
  "dept.": "department",
};

// Person substitution pairs (1st <-> 2nd person)
const PERSON_SUBS = [
  [/\bwith me\b/gi, "WITH_YOU_TEMP"],
  [/\bwith you\b/gi, "with me"],
  [/\bWITH_YOU_TEMP\b/g, "with you"],
  [/\bi was\b/gi, "YOU_WERE_TEMP"],
  [/\byou were\b/gi, "i was"],
  [/\bYOU_WERE_TEMP\b/g, "you were"],
  [/\bi am\b/gi, "YOU_ARE_TEMP"],
  [/\byou are\b/gi, "i am"],
  [/\bYOU_ARE_TEMP\b/g, "you are"],
  [/\bmy\b/gi, "YOUR_TEMP"],
  [/\byour\b/gi, "my"],
  [/\bYOUR_TEMP\b/g, "your"],
  [/\bmine\b/gi, "YOURS_TEMP"],
  [/\byours\b/gi, "mine"],
  [/\bYOURS_TEMP\b/g, "yours"],
  [/\bmyself\b/gi, "YOURSELF_TEMP"],
  [/\byourself\b/gi, "myself"],
  [/\bYOURSELF_TEMP\b/g, "yourself"],
  [/\bme\b/gi, "YOU_TEMP"],
  [/\byou\b/gi, "me"],
  [/\bYOU_TEMP\b/g, "you"],
  [/\bi\b/gi, "YOU_TEMP2"],
  [/\bYOU_TEMP2\b/g, "you"],
];

// Person2 substitution pairs (1st <-> 3rd person)
const PERSON2_SUBS = [
  [/\bi was\b/gi, "he or she was"],
  [/\bi am\b/gi, "he or she is"],
  [/\bmy\b/gi, "his or her"],
  [/\bmine\b/gi, "his or hers"],
  [/\bmyself\b/gi, "him or herself"],
  [/\bme\b/gi, "him or her"],
  [/\bi\b/gi, "he or she"],
];

// Gender substitution pairs
const GENDER_SUBS = [
  [/\bhe\b/gi, "SHE_TEMP"],
  [/\bshe\b/gi, "he"],
  [/\bSHE_TEMP\b/g, "she"],
  [/\bhis\b/gi, "HER_TEMP"],
  [/\bher\b/gi, "his"],
  [/\bHER_TEMP\b/g, "her"],
  [/\bhim\b/gi, "HER_TEMP2"],
  [/\bHER_TEMP2\b/g, "her"],
  [/\bhimself\b/gi, "herself"],
  [/\bherself\b/gi, "himself"],
];

export class Normalizer {
  constructor(customSubs = {}) {
    this.substitutions = { ...DEFAULT_NORMAL_SUBS, ...customSubs };
  }

  /**
   * Full normalization pipeline: substitute -> split -> fit
   * Returns array of normalized sentences
   */
  normalize(input) {
    if (!input || typeof input !== 'string') return [''];
    let text = input.trim();
    if (!text) return [''];

    // Step 1: Apply substitutions (contractions, abbreviations, etc.)
    text = this.applySubstitutions(text);

    // Step 2: Split into sentences
    const sentences = this.splitSentences(text);

    // Step 3: Pattern-fit each sentence
    return sentences.map(s => this.patternFit(s)).filter(s => s.length > 0);
  }

  /**
   * Apply substitution normalization
   */
  applySubstitutions(text) {
    let result = text.toLowerCase();
    // Sort by length descending to match longer phrases first
    const sorted = Object.entries(this.substitutions)
      .sort((a, b) => b[0].length - a[0].length);

    for (const [from, to] of sorted) {
      const escaped = from.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`\\b${escaped}\\b`, 'gi');
      result = result.replace(regex, to);
    }
    return result;
  }

  /**
   * Split input into sentences on . ! ?
   */
  splitSentences(text) {
    // Split on sentence-ending punctuation, keeping non-empty parts
    const parts = text.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 0);
    return parts.length > 0 ? parts : [text];
  }

  /**
   * Pattern fitting: uppercase, remove non-alphanumeric, collapse spaces
   */
  patternFit(text) {
    return text
      .toUpperCase()
      .replace(/[^A-Z0-9\s]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  /**
   * Apply person substitutions (swap 1st/2nd person)
   */
  person(text) {
    let result = text;
    for (const [pattern, replacement] of PERSON_SUBS) {
      result = result.replace(pattern, replacement);
    }
    return result;
  }

  /**
   * Apply person2 substitutions (swap 1st/3rd person)
   */
  person2(text) {
    let result = text;
    for (const [pattern, replacement] of PERSON2_SUBS) {
      result = result.replace(pattern, replacement);
    }
    return result;
  }

  /**
   * Apply gender substitutions (swap he/she)
   */
  gender(text) {
    let result = text;
    for (const [pattern, replacement] of GENDER_SUBS) {
      result = result.replace(pattern, replacement);
    }
    return result;
  }

  /**
   * Formal case: Capitalize First Letter Of Each Word
   */
  formal(text) {
    return text.replace(/\b\w/g, c => c.toUpperCase());
  }

  /**
   * Sentence case: capitalize first letter only
   */
  sentence(text) {
    if (!text) return '';
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
  }
}
