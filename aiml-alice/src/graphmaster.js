/**
 * Graphmaster - Trie-based pattern matching engine for AIML
 *
 * Implements the AIML pattern matching algorithm with:
 * - Wildcard priority: $ > # > _ > exact > <set> > ^ > *
 * - Three-key matching: pattern + <that> + <topic>
 * - Depth-first search with backtracking
 * - Star capture for wildcards
 */

// Sentinel tokens used to separate the three match dimensions
const THAT_SEPARATOR = '<that>';
const TOPIC_SEPARATOR = '<topic>';

class GraphNode {
  constructor() {
    // Children keyed by branch type
    this.hash = null;       // # wildcard (zero or more, high priority)
    this.underscore = null;  // _ wildcard (one or more, high priority)
    this.dollar = new Map(); // $ priority words
    this.words = new Map();  // Exact word matches
    this.sets = new Map();   // <set> matches
    this.caret = null;       // ^ wildcard (zero or more, low priority)
    this.star = null;        // * wildcard (one or more, low priority)

    // Leaf data
    this.template = null;    // Template XML node if this is a leaf
    this.filename = null;    // Source file for debugging
  }
}

export class Graphmaster {
  constructor() {
    this.root = new GraphNode();
    this.categoryCount = 0;
    this.sets = new Map(); // Named sets for <set> pattern matching
  }

  /**
   * Load a named set (for AIML 2.0 <set> in patterns)
   */
  loadSet(name, values) {
    const normalized = new Set();
    for (const v of values) {
      normalized.add(v.toUpperCase().trim());
    }
    this.sets.set(name.toUpperCase(), normalized);
  }

  /**
   * Add a category to the graph
   * @param {string} pattern - Normalized pattern text
   * @param {string} that - Normalized that text (default "*")
   * @param {string} topic - Normalized topic text (default "*")
   * @param {object} template - Template XML node
   * @param {string} filename - Source file
   */
  addCategory(pattern, that, topic, template, filename = '') {
    // Build the full path: pattern <that> that <topic> topic
    const patternWords = pattern.split(/\s+/).filter(w => w);
    const thatWords = (that || '*').split(/\s+/).filter(w => w);
    const topicWords = (topic || '*').split(/\s+/).filter(w => w);

    const path = [...patternWords, THAT_SEPARATOR, ...thatWords, TOPIC_SEPARATOR, ...topicWords];

    let node = this.root;
    for (const word of path) {
      node = this._getOrCreateChild(node, word);
    }

    node.template = template;
    node.filename = filename;
    this.categoryCount++;
  }

  _getOrCreateChild(node, word) {
    if (word === '#') {
      if (!node.hash) node.hash = new GraphNode();
      return node.hash;
    }
    if (word === '_') {
      if (!node.underscore) node.underscore = new GraphNode();
      return node.underscore;
    }
    if (word === '^') {
      if (!node.caret) node.caret = new GraphNode();
      return node.caret;
    }
    if (word === '*') {
      if (!node.star) node.star = new GraphNode();
      return node.star;
    }
    if (word.startsWith('$')) {
      const w = word.substring(1);
      if (!node.dollar.has(w)) node.dollar.set(w, new GraphNode());
      return node.dollar.get(w);
    }
    // Check if it's a set reference: SET_NAME (stored as <SET>NAME</SET> -> SET:NAME)
    if (word.startsWith('SET:')) {
      const setName = word.substring(4);
      if (!node.sets.has(setName)) node.sets.set(setName, new GraphNode());
      return node.sets.get(setName);
    }
    // Separators — store as-is (don't uppercase)
    if (word === THAT_SEPARATOR || word === TOPIC_SEPARATOR) {
      if (!node.words.has(word)) node.words.set(word, new GraphNode());
      return node.words.get(word);
    }
    // Exact words — uppercase for case-insensitive matching
    const upper = word.toUpperCase();
    if (!node.words.has(upper)) node.words.set(upper, new GraphNode());
    return node.words.get(upper);
  }

  /**
   * Match an input against the graph
   * @param {string} input - Normalized input
   * @param {string} that - Normalized previous bot response
   * @param {string} topic - Normalized current topic
   * @returns {object|null} { template, stars: { pattern: [], that: [], topic: [] } }
   */
  match(input, that, topic) {
    const inputWords = input.split(/\s+/).filter(w => w);
    const thatWords = (that || '*').split(/\s+/).filter(w => w);
    const topicWords = (topic || '*').split(/\s+/).filter(w => w);

    const path = [...inputWords, THAT_SEPARATOR, ...thatWords, TOPIC_SEPARATOR, ...topicWords];

    const result = this._matchNode(this.root, path, 0, {
      pattern: [],
      that: [],
      topic: [],
    }, 'pattern', 0);

    return result;
  }

  /**
   * Recursive depth-first matching with backtracking.
   * @param {number} lit - Count of literal (non-wildcard) tokens matched in the
   *   pattern dimension so far. Surfaced on the result as `specificity`; a pure
   *   catch-all `*` match yields specificity 0, letting callers treat it as a miss.
   */
  _matchNode(node, path, index, stars, dimension, lit = 0) {
    // Base case: consumed all input
    if (index >= path.length) {
      if (node.template) {
        return { template: node.template, stars: { ...stars }, filename: node.filename, specificity: lit };
      }
      return null;
    }

    const word = path[index];

    // Handle separators - switch dimension
    if (word === THAT_SEPARATOR) {
      if (node.words.has(THAT_SEPARATOR)) {
        return this._matchNode(node.words.get(THAT_SEPARATOR), path, index + 1, stars, 'that', lit);
      }
      return null;
    }
    if (word === TOPIC_SEPARATOR) {
      if (node.words.has(TOPIC_SEPARATOR)) {
        return this._matchNode(node.words.get(TOPIC_SEPARATOR), path, index + 1, stars, 'topic', lit);
      }
      return null;
    }

    // Find the next separator index for bounding wildcard consumption
    let separatorIdx = path.length;
    for (let i = index; i < path.length; i++) {
      if (path[i] === THAT_SEPARATOR || path[i] === TOPIC_SEPARATOR) {
        separatorIdx = i;
        break;
      }
    }

    let result;

    // Literal matches (exact word, $ priority, <set>) increment specificity in
    // the pattern dimension; wildcards (#, _, ^, *) do not.
    const litInc = dimension === 'pattern' ? 1 : 0;

    // Priority 1: $ priority words
    for (const [w, child] of node.dollar) {
      if (word === w) {
        result = this._matchNode(child, path, index + 1, stars, dimension, lit + litInc);
        if (result) return result;
      }
    }

    // Priority 2: # (zero or more, high priority)
    if (node.hash) {
      // Try zero words first, then increasing
      for (let len = 0; len <= separatorIdx - index; len++) {
        const captured = path.slice(index, index + len).join(' ');
        const newStars = { ...stars, [dimension]: [...stars[dimension], captured] };
        result = this._matchNode(node.hash, path, index + len, newStars, dimension, lit);
        if (result) return result;
      }
    }

    // Priority 3: _ (one or more, high priority)
    if (node.underscore) {
      for (let len = 1; len <= separatorIdx - index; len++) {
        const captured = path.slice(index, index + len).join(' ');
        const newStars = { ...stars, [dimension]: [...stars[dimension], captured] };
        result = this._matchNode(node.underscore, path, index + len, newStars, dimension, lit);
        if (result) return result;
      }
    }

    // Priority 4: Exact word match
    const upper = word.toUpperCase();
    if (node.words.has(upper)) {
      result = this._matchNode(node.words.get(upper), path, index + 1, stars, dimension, lit + litInc);
      if (result) return result;
    }

    // Priority 5: <set> membership
    for (const [setName, child] of node.sets) {
      const setValues = this.sets.get(setName);
      if (setValues && setValues.has(upper)) {
        const newStars = { ...stars, [dimension]: [...stars[dimension], upper] };
        result = this._matchNode(child, path, index + 1, newStars, dimension, lit + litInc);
        if (result) return result;
      }
      // Also try multi-word set values
      if (setValues) {
        for (let len = 2; len <= separatorIdx - index; len++) {
          const phrase = path.slice(index, index + len).join(' ').toUpperCase();
          if (setValues.has(phrase)) {
            const newStars = { ...stars, [dimension]: [...stars[dimension], phrase] };
            result = this._matchNode(child, path, index + len, newStars, dimension, lit + litInc);
            if (result) return result;
          }
        }
      }
    }

    // Priority 6: ^ (zero or more, low priority)
    if (node.caret) {
      for (let len = 0; len <= separatorIdx - index; len++) {
        const captured = path.slice(index, index + len).join(' ');
        const newStars = { ...stars, [dimension]: [...stars[dimension], captured] };
        result = this._matchNode(node.caret, path, index + len, newStars, dimension, lit);
        if (result) return result;
      }
    }

    // Priority 7: * (one or more, low priority)
    if (node.star) {
      for (let len = 1; len <= separatorIdx - index; len++) {
        const captured = path.slice(index, index + len).join(' ');
        const newStars = { ...stars, [dimension]: [...stars[dimension], captured] };
        result = this._matchNode(node.star, path, index + len, newStars, dimension, lit);
        if (result) return result;
      }
    }

    return null; // No match - backtrack
  }
}
