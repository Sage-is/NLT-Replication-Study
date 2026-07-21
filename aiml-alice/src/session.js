/**
 * Session - Per-user conversation state manager
 *
 * Tracks:
 * - User predicates (name, age, preferences, etc.)
 * - Conversation history (input[], that[], request[], response[])
 * - Topic state
 * - Local variables (template-scoped)
 */

const HISTORY_SIZE = 10;

export class Session {
  constructor(userId = 'default') {
    this.userId = userId;
    this.predicates = new Map();
    this.inputHistory = [];    // User inputs (normalized)
    this.rawInputHistory = []; // User inputs (raw)
    this.responseHistory = []; // Bot responses
    this.thatHistory = [];     // Last sentence of each bot response (normalized)
    this.localVars = new Map(); // Template-scoped variables
  }

  /**
   * Set a user predicate
   */
  setPredicate(name, value) {
    this.predicates.set(name.toLowerCase(), value);
  }

  /**
   * Get a user predicate
   */
  getPredicate(name, defaultValue = 'unknown') {
    return this.predicates.get(name.toLowerCase()) || defaultValue;
  }

  /**
   * Get the current topic
   */
  get topic() {
    return this.getPredicate('topic', '*');
  }

  /**
   * Set a local variable (template-scoped)
   */
  setLocalVar(name, value) {
    this.localVars.set(name.toLowerCase(), value);
  }

  /**
   * Get a local variable
   */
  getLocalVar(name, defaultValue = 'unknown') {
    return this.localVars.get(name.toLowerCase()) || defaultValue;
  }

  /**
   * Clear local variables (called between template evaluations)
   */
  clearLocalVars() {
    this.localVars.clear();
  }

  /**
   * Record a conversation turn
   */
  addExchange(rawInput, normalizedInput, response, normalizedThat) {
    this.rawInputHistory.unshift(rawInput);
    this.inputHistory.unshift(normalizedInput);
    this.responseHistory.unshift(response);
    this.thatHistory.unshift(normalizedThat);

    // Trim history
    if (this.rawInputHistory.length > HISTORY_SIZE) this.rawInputHistory.pop();
    if (this.inputHistory.length > HISTORY_SIZE) this.inputHistory.pop();
    if (this.responseHistory.length > HISTORY_SIZE) this.responseHistory.pop();
    if (this.thatHistory.length > HISTORY_SIZE) this.thatHistory.pop();
  }

  /**
   * Get the last bot response's last sentence (normalized) for <that> matching
   */
  getThat() {
    return this.thatHistory.length > 0 ? this.thatHistory[0] : '*';
  }

  /**
   * Get Nth previous input (1-indexed)
   */
  getInput(index = 1) {
    const i = index - 1;
    return i < this.rawInputHistory.length ? this.rawInputHistory[i] : '';
  }

  /**
   * Get Nth previous response (1-indexed)
   */
  getResponse(index = 1) {
    const i = index - 1;
    return i < this.responseHistory.length ? this.responseHistory[i] : '';
  }

  /**
   * Get Nth previous that (1-indexed)
   */
  getThatByIndex(responseIdx = 1, sentenceIdx = 1) {
    const i = responseIdx - 1;
    if (i >= this.responseHistory.length) return '';
    const response = this.responseHistory[i];
    const sentences = response.split(/[.!?]+/).map(s => s.trim()).filter(s => s);
    const j = sentenceIdx - 1;
    return j < sentences.length ? sentences[j] : response;
  }

  /**
   * Export session state for persistence
   */
  toJSON() {
    return {
      userId: this.userId,
      predicates: Object.fromEntries(this.predicates),
      inputHistory: this.inputHistory,
      rawInputHistory: this.rawInputHistory,
      responseHistory: this.responseHistory,
      thatHistory: this.thatHistory,
    };
  }

  /**
   * Import session state
   */
  static fromJSON(data) {
    const session = new Session(data.userId);
    for (const [k, v] of Object.entries(data.predicates || {})) {
      session.predicates.set(k, v);
    }
    session.inputHistory = data.inputHistory || [];
    session.rawInputHistory = data.rawInputHistory || [];
    session.responseHistory = data.responseHistory || [];
    session.thatHistory = data.thatHistory || [];
    return session;
  }
}
