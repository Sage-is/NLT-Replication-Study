/**
 * AIMLEngine - Core AIML 2.0 Interpreter
 *
 * Orchestrates all components:
 * - Parser: Loads and parses AIML files
 * - Graphmaster: Pattern matching trie
 * - Normalizer: Input normalization
 * - TemplateProcessor: Response generation
 * - Session: Per-user state management
 *
 * Supports loading multiple AIML files, bot properties, sets, and maps.
 */

import { readFileSync, readdirSync, existsSync } from 'fs';
import { join, resolve } from 'path';
import { AIMLParser, extractCategories } from './parser.js';
import { Graphmaster } from './graphmaster.js';
import { Normalizer } from './normalizer.js';
import { TemplateProcessor } from './template-processor.js';
import { Session } from './session.js';

export class AIMLEngine {
  constructor(options = {}) {
    this.parser = new AIMLParser();
    this.graphmaster = new Graphmaster();
    this.normalizer = new Normalizer(options.substitutions);
    this.templateProcessor = new TemplateProcessor(this);

    // Bot properties (read-only globals)
    this.botProperties = new Map();

    // Named maps for <map> tag
    this.maps = new Map();

    // Sessions keyed by userId
    this.sessions = new Map();

    // Callbacks
    this.onGossip = options.onGossip || null;
    this.onTrace = options.onTrace || null;

    // Loaded file tracking
    this.loadedFiles = [];
  }

  // ==================== Loading ====================

  /**
   * Load AIML from a string
   */
  loadAIML(aimlString, filename = 'inline') {
    const doc = this.parser.parse(aimlString);
    const categories = extractCategories(doc, filename);

    for (const cat of categories) {
      this.graphmaster.addCategory(
        cat.pattern, cat.that, cat.topic, cat.template, cat.filename
      );
    }

    this.loadedFiles.push(filename);
    return categories.length;
  }

  /**
   * Load an AIML file from disk
   */
  loadFile(filePath) {
    const absPath = resolve(filePath);
    if (!existsSync(absPath)) {
      throw new Error(`AIML file not found: ${absPath}`);
    }
    const content = readFileSync(absPath, 'utf-8');
    return this.loadAIML(content, absPath);
  }

  /**
   * Load all .aiml files from a directory
   */
  loadDirectory(dirPath) {
    const absDir = resolve(dirPath);
    if (!existsSync(absDir)) {
      throw new Error(`AIML directory not found: ${absDir}`);
    }

    const files = readdirSync(absDir)
      .filter(f => f.endsWith('.aiml'))
      .sort();

    let totalCategories = 0;
    for (const file of files) {
      const count = this.loadFile(join(absDir, file));
      totalCategories += count;
    }
    return totalCategories;
  }

  /**
   * Load bot properties from a key=value file or object
   */
  loadBotProperties(source) {
    if (typeof source === 'string') {
      // File path - parse key=value lines
      const absPath = resolve(source);
      if (existsSync(absPath)) {
        const content = readFileSync(absPath, 'utf-8');
        for (const line of content.split('\n')) {
          const trimmed = line.trim();
          if (!trimmed || trimmed.startsWith('#') || trimmed.startsWith('//')) continue;
          const eqIdx = trimmed.indexOf('=');
          if (eqIdx > 0) {
            const key = trimmed.substring(0, eqIdx).trim();
            const value = trimmed.substring(eqIdx + 1).trim();
            this.botProperties.set(key.toLowerCase(), value);
          }
        }
      }
    } else if (typeof source === 'object') {
      for (const [key, value] of Object.entries(source)) {
        this.botProperties.set(key.toLowerCase(), String(value));
      }
    }
  }

  /**
   * Load a named set from a file (one value per line) or array
   */
  loadSet(name, source) {
    let values;
    if (typeof source === 'string') {
      const absPath = resolve(source);
      if (existsSync(absPath)) {
        const content = readFileSync(absPath, 'utf-8');
        values = content.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('#'));
      } else {
        values = [];
      }
    } else if (Array.isArray(source)) {
      values = source;
    } else {
      values = [];
    }
    this.graphmaster.loadSet(name, values);
  }

  /**
   * Load a named map from a file (key:value per line) or object
   */
  loadMap(name, source) {
    const map = new Map();
    if (typeof source === 'string') {
      const absPath = resolve(source);
      if (existsSync(absPath)) {
        const content = readFileSync(absPath, 'utf-8');
        for (const line of content.split('\n')) {
          const trimmed = line.trim();
          if (!trimmed || trimmed.startsWith('#')) continue;
          const colonIdx = trimmed.indexOf(':');
          if (colonIdx > 0) {
            map.set(
              trimmed.substring(0, colonIdx).trim().toUpperCase(),
              trimmed.substring(colonIdx + 1).trim()
            );
          }
        }
      }
    } else if (typeof source === 'object' && !Array.isArray(source)) {
      for (const [k, v] of Object.entries(source)) {
        map.set(k.toUpperCase(), String(v));
      }
    }
    this.maps.set(name.toUpperCase(), map);
  }

  // ==================== Response Generation ====================

  /**
   * Get a response for user input
   * @param {string} input - Raw user input
   * @param {Session|string} sessionOrId - Session object or userId string
   * @param {boolean} isSrai - Whether this is an internal SRAI call
   * @returns {string} Bot response
   */
  respond(input, sessionOrId, isSrai = false) {
    const session = this._resolveSession(sessionOrId);

    // Normalize input
    const sentences = isSrai
      ? [this.normalizer.patternFit(input)]
      : this.normalizer.normalize(input);

    if (sentences.length === 0) {
      return this._defaultResponse();
    }

    const responses = [];

    for (const sentence of sentences) {
      if (!sentence) continue;

      // Build match context
      const that = this.normalizer.patternFit(session.getThat());
      const topic = this.normalizer.patternFit(session.topic);

      // Trace
      if (this.onTrace) {
        this.onTrace({
          input: sentence,
          that,
          topic,
          isSrai,
        });
      }

      // Match against graphmaster
      const match = this.graphmaster.match(sentence, that, topic);

      if (match) {
        const response = this.templateProcessor.process(
          match.template, match.stars, session
        );
        responses.push(response);
      } else {
        responses.push(this._defaultResponse());
      }
    }

    const fullResponse = responses.join(' ').trim();

    // Record exchange (only for top-level, not SRAI)
    if (!isSrai) {
      const lastSentence = this._lastSentence(fullResponse);
      const normalizedThat = this.normalizer.patternFit(lastSentence);
      session.addExchange(input, sentences[0], fullResponse, normalizedThat);
    }

    return fullResponse;
  }

  /**
   * Precache gate: attempt a response WITHOUT the default fallback.
   *
   * Returns { matched, reply, hits, total }. `matched` is true only when every
   * non-empty normalized sentence hits a real AIML category — i.e. a confident,
   * deterministic answer the bot can serve for free. On a miss, `reply` is null
   * and session state is left untouched, so an LLM agent router can own the turn.
   *
   * Intended use: call this first; on a hit, serve `reply` (cache hit); on a
   * miss, route to the agent.
   *
   * A match against the catch-all wildcard (`<pattern>*</pattern>`) carries zero
   * literal anchors (specificity 0) and is treated as a MISS — that is exactly the
   * generic filler the agent should override. `minSpecificity` (default 1) is the
   * number of literal tokens a sentence must match to count as a confident hit.
   *
   * @param {string} input - Raw user input
   * @param {Session|string} sessionOrId
   * @param {{minSpecificity?: number}} [opts]
   * @returns {{matched: boolean, reply: string|null, hits: number, total: number, minSpecificity: number}}
   */
  tryRespond(input, sessionOrId, opts = {}) {
    const minSpecificity = opts.minSpecificity ?? 1;
    const session = this._resolveSession(sessionOrId);
    const sentences = this.normalizer.normalize(input).filter(Boolean);

    if (sentences.length === 0) {
      return { matched: false, reply: null, hits: 0, total: 0, minSpecificity };
    }

    // Cheap match-only pre-pass (no template side effects) to decide hit/miss.
    // `that`/`topic` are constant across sentences within a single turn, mirroring respond().
    const that = this.normalizer.patternFit(session.getThat());
    const topic = this.normalizer.patternFit(session.topic);
    let hits = 0;
    for (const sentence of sentences) {
      const m = this.graphmaster.match(sentence, that, topic);
      if (m && m.specificity >= minSpecificity) hits++;
    }

    if (hits !== sentences.length) {
      return { matched: false, reply: null, hits, total: sentences.length, minSpecificity };
    }

    // Full hit: reuse respond() for real template processing + exchange recording.
    const reply = this.respond(input, session);
    return { matched: true, reply, hits, total: sentences.length, minSpecificity };
  }

  /**
   * Get a bot property
   */
  getBotProperty(name) {
    return this.botProperties.get(name.toLowerCase()) || 'unknown';
  }

  /**
   * Get or create a session for a user
   */
  getSession(userId = 'default') {
    if (!this.sessions.has(userId)) {
      this.sessions.set(userId, new Session(userId));
    }
    return this.sessions.get(userId);
  }

  // ==================== Helpers ====================

  _resolveSession(sessionOrId) {
    if (sessionOrId instanceof Session) return sessionOrId;
    if (typeof sessionOrId === 'string') return this.getSession(sessionOrId);
    return this.getSession('default');
  }

  _defaultResponse() {
    const defaults = [
      "I don't understand.",
      "Can you rephrase that?",
      "Tell me more.",
      "That is interesting.",
      "I see.",
    ];
    return defaults[Math.floor(Math.random() * defaults.length)];
  }

  _lastSentence(text) {
    const sentences = text.split(/[.!?]+/).map(s => s.trim()).filter(s => s);
    return sentences.length > 0 ? sentences[sentences.length - 1] : text;
  }

  /**
   * Get engine stats
   */
  stats() {
    return {
      categories: this.graphmaster.categoryCount,
      files: this.loadedFiles.length,
      botProperties: this.botProperties.size,
      sessions: this.sessions.size,
      sets: this.graphmaster.sets.size,
      maps: this.maps.size,
    };
  }
}
