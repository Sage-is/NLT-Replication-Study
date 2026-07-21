/**
 * Browser entry point for AIML-ALICE
 * Inlines brain files and substitutions, exposes engine on window.
 */

import { AIMLParser, extractCategories } from './parser.js';
import { Graphmaster } from './graphmaster.js';
import { Normalizer } from './normalizer.js';
import { TemplateProcessor } from './template-processor.js';
import { Session } from './session.js';

// Browser-compatible engine (no fs dependency)
class AIMLEngineBrowser {
  constructor() {
    this.parser = new AIMLParser();
    this.graphmaster = new Graphmaster();
    this.normalizer = new Normalizer();
    this.templateProcessor = new TemplateProcessor(this);
    this.botProperties = new Map();
    this.maps = new Map();
    this.sessions = new Map();
    this.loadedFiles = [];
  }

  loadAIML(aimlString, filename = 'inline') {
    const doc = this.parser.parse(aimlString);
    const categories = extractCategories(doc, filename);
    for (const cat of categories) {
      this.graphmaster.addCategory(cat.pattern, cat.that, cat.topic, cat.template, cat.filename);
    }
    this.loadedFiles.push(filename);
    return categories.length;
  }

  loadBotPropertiesFromObject(props) {
    for (const [key, value] of Object.entries(props)) {
      this.botProperties.set(key.toLowerCase(), String(value));
    }
  }

  respond(input, sessionOrId) {
    const session = this._resolveSession(sessionOrId);
    const sentences = this.normalizer.normalize(input);
    if (sentences.length === 0) return this._defaultResponse();

    const responses = [];
    for (const sentence of sentences) {
      if (!sentence) continue;
      const that = session.getThat();
      const topic = session.topic;
      const result = this.graphmaster.match(sentence, that, topic);

      if (result) {
        const response = this.templateProcessor.process(result.template, result.stars, session);
        if (response) {
          responses.push(response);
          // Normalize the last sentence of the response for <that> matching
          const lastSentence = response.split(/[.!?]+/).filter(s => s.trim()).pop() || response;
          const normalizedThat = this.normalizer.patternFit(lastSentence);
          session.addExchange(input, sentence, response, normalizedThat);
        }
      }
    }

    if (responses.length === 0) return this._defaultResponse();
    return responses.join(' ');
  }

  _resolveSession(sessionOrId) {
    if (sessionOrId instanceof Session) return sessionOrId;
    const id = String(sessionOrId || 'default');
    if (!this.sessions.has(id)) {
      this.sessions.set(id, new Session(id));
    }
    return this.sessions.get(id);
  }

  _defaultResponse() {
    const defaults = [
      "I'm not sure I understand. Could you rephrase that?",
      "That's interesting. Tell me more.",
      "I see. Can you elaborate?",
    ];
    return defaults[Math.floor(Math.random() * defaults.length)];
  }
}

// Expose globally for the HTML page
window.AIMLEngineBrowser = AIMLEngineBrowser;
