/**
 * Template Processor - Evaluates AIML template XML nodes
 *
 * Handles all AIML template tags including:
 * - Text output, star captures, random, condition
 * - Variable management (set, get, think, bot)
 * - Recursion (srai, sr)
 * - Text transforms (uppercase, lowercase, formal, sentence)
 * - Pronoun swaps (person, person2, gender)
 * - History (input, that, request, response)
 * - System (date, id, size, version)
 * - AIML 2.0 (map, first, rest, explode, loop)
 */

export class TemplateProcessor {
  /**
   * @param {object} engine - Reference to the AIMLEngine for srai calls
   */
  constructor(engine) {
    this.engine = engine;
    this.sraiDepth = 0;
    this.maxSraiDepth = 50; // Prevent infinite recursion
  }

  /**
   * Process a template node and return the response text
   * @param {XMLNode} templateNode - The <template> XML node
   * @param {object} stars - { pattern: [], that: [], topic: [] }
   * @param {Session} session - Current user session
   * @returns {string}
   */
  process(templateNode, stars, session) {
    session.clearLocalVars();
    return this._processChildren(templateNode, stars, session).trim().replace(/\s+/g, ' ');
  }

  /**
   * Recursively process all children of a node
   */
  _processChildren(node, stars, session) {
    let result = '';
    for (const child of node.children) {
      result += this._processNode(child, stars, session);
    }
    return result;
  }

  /**
   * Process a single XML node
   */
  _processNode(node, stars, session) {
    if (node.type === 'text' || node.type === 'cdata') {
      return node.text;
    }

    if (node.type !== 'element') return '';

    switch (node.name) {
      case 'star':
        return this._handleStar(node, stars, 'pattern');
      case 'thatstar':
        return this._handleStar(node, stars, 'that');
      case 'topicstar':
        return this._handleStar(node, stars, 'topic');

      case 'random':
        return this._handleRandom(node, stars, session);
      case 'li':
        return this._processChildren(node, stars, session);

      case 'srai':
        return this._handleSrai(node, stars, session);
      case 'sr':
        return this._handleSr(stars, session);

      case 'set':
        return this._handleSet(node, stars, session);
      case 'get':
        return this._handleGet(node, session);
      case 'bot':
        return this._handleBot(node);
      case 'think':
        // Process children but suppress output
        this._processChildren(node, stars, session);
        return '';

      case 'condition':
        return this._handleCondition(node, stars, session);

      case 'uppercase':
        return this._processChildren(node, stars, session).toUpperCase();
      case 'lowercase':
        return this._processChildren(node, stars, session).toLowerCase();
      case 'formal':
        return this.engine.normalizer.formal(this._processChildren(node, stars, session));
      case 'sentence':
        return this.engine.normalizer.sentence(this._processChildren(node, stars, session));
      case 'explode':
        return this._processChildren(node, stars, session).split('').join(' ');

      case 'person':
        return this._handlePerson(node, stars, session);
      case 'person2':
        return this._handlePerson2(node, stars, session);
      case 'gender':
        return this._handleGender(node, stars, session);

      case 'input':
        return this._handleInput(node, session);
      case 'that':
        return this._handleThat(node, session);
      case 'request':
        return session.getInput(this._getIndex(node));
      case 'response':
        return session.getResponse(this._getIndex(node));

      case 'date':
        return this._handleDate(node);
      case 'id':
        return session.userId;
      case 'size':
        return String(this.engine.graphmaster.categoryCount);
      case 'version':
      case 'program':
        return 'AIML-ALICE.js v1.0.0';
      case 'vocabulary':
        return String(this.engine.graphmaster.categoryCount);

      case 'map':
        return this._handleMap(node, stars, session);
      case 'first':
        return this._handleFirst(node, stars, session);
      case 'rest':
        return this._handleRest(node, stars, session);

      case 'learn':
        return this._handleLearn(node, stars, session);
      case 'eval':
        return this._processChildren(node, stars, session);

      case 'system':
        // Disabled for security - return empty
        return '[system commands disabled]';

      case 'javascript':
        // Not supported in pure implementation
        return '[javascript disabled]';

      case 'gossip':
        // Log but don't output
        const gossipText = this._processChildren(node, stars, session);
        if (this.engine.onGossip) this.engine.onGossip(gossipText);
        return '';

      case 'normalize':
        return this.engine.normalizer.patternFit(
          this._processChildren(node, stars, session)
        );
      case 'denormalize':
        return this._processChildren(node, stars, session).toLowerCase();

      case 'interval':
        return this._handleInterval(node, stars, session);

      case 'br':
        return '\n';

      default:
        // Unknown tag - process children
        return this._processChildren(node, stars, session);
    }
  }

  // ==================== Tag Handlers ====================

  _handleStar(node, stars, dimension) {
    const index = this._getIndex(node);
    const starList = stars[dimension] || [];
    if (index <= starList.length && index >= 1) {
      return starList[index - 1] || '';
    }
    return '';
  }

  _handleRandom(node, stars, session) {
    const items = node.getDirectChildren('li');
    if (items.length === 0) return '';
    const chosen = items[Math.floor(Math.random() * items.length)];
    return this._processChildren(chosen, stars, session);
  }

  _handleSrai(node, stars, session) {
    if (this.sraiDepth >= this.maxSraiDepth) {
      return '[SRAI recursion limit reached]';
    }
    this.sraiDepth++;
    try {
      const input = this._processChildren(node, stars, session).trim();
      if (!input) return '';
      return this.engine.respond(input, session, true);
    } finally {
      this.sraiDepth--;
    }
  }

  _handleSr(stars, session) {
    if (this.sraiDepth >= this.maxSraiDepth) {
      return '[SRAI recursion limit reached]';
    }
    const starText = (stars.pattern && stars.pattern[0]) || '';
    if (!starText) return '';
    this.sraiDepth++;
    try {
      return this.engine.respond(starText, session, true);
    } finally {
      this.sraiDepth--;
    }
  }

  _handleSet(node, stars, session) {
    const value = this._processChildren(node, stars, session).trim();
    const name = node.getAttribute('name');
    const varName = node.getAttribute('var');

    if (varName) {
      session.setLocalVar(varName, value);
    } else if (name) {
      session.setPredicate(name, value);
    }
    return value; // <set> echoes the value
  }

  _handleGet(node, session) {
    const name = node.getAttribute('name');
    const varName = node.getAttribute('var');

    if (varName) {
      return session.getLocalVar(varName);
    }
    if (name) {
      return session.getPredicate(name);
    }
    return 'unknown';
  }

  _handleBot(node) {
    const name = node.getAttribute('name');
    return this.engine.getBotProperty(name);
  }

  _handleCondition(node, stars, session) {
    const name = node.getAttribute('name');
    const varAttr = node.getAttribute('var');
    const value = node.getAttribute('value');

    // Form 1: Block condition - <condition name="x" value="y">content</condition>
    if ((name || varAttr) && value) {
      const actual = varAttr
        ? session.getLocalVar(varAttr)
        : session.getPredicate(name);
      if (this._matchConditionValue(actual, value)) {
        return this._processChildren(node, stars, session);
      }
      return '';
    }

    // Form 2: Single predicate switch - <condition name="x"><li value="v1">...</li></condition>
    if (name || varAttr) {
      const actual = varAttr
        ? session.getLocalVar(varAttr)
        : session.getPredicate(name);
      return this._evaluateConditionItems(node, stars, session, actual);
    }

    // Form 3: Multi-predicate - <condition><li name="x" value="y">...</li></condition>
    const items = node.getDirectChildren('li');
    for (const li of items) {
      const liName = li.getAttribute('name');
      const liVar = li.getAttribute('var');
      const liValue = li.getAttribute('value');

      if (!liName && !liVar && !liValue) {
        // Default case
        return this._processChildren(li, stars, session);
      }

      const actual = liVar
        ? session.getLocalVar(liVar)
        : session.getPredicate(liName);

      if (this._matchConditionValue(actual, liValue)) {
        let result = this._processChildren(li, stars, session);
        // Check for <loop/> tag
        if (this._hasLoop(li)) {
          result += this._handleCondition(node, stars, session);
        }
        return result;
      }
    }

    return '';
  }

  _evaluateConditionItems(node, stars, session, actual) {
    const items = node.getDirectChildren('li');
    for (const li of items) {
      const liValue = li.getAttribute('value');
      if (!liValue) {
        // Default case
        return this._processChildren(li, stars, session);
      }
      if (this._matchConditionValue(actual, liValue)) {
        let result = this._processChildren(li, stars, session);
        if (this._hasLoop(li)) {
          const name = node.getAttribute('name');
          const varAttr = node.getAttribute('var');
          const newActual = varAttr
            ? session.getLocalVar(varAttr)
            : session.getPredicate(name);
          result += this._evaluateConditionItems(node, stars, session, newActual);
        }
        return result;
      }
    }
    return '';
  }

  _matchConditionValue(actual, expected) {
    if (!actual || !expected) return false;
    const a = actual.trim().toUpperCase();
    const e = expected.trim().toUpperCase();
    // Support wildcard in condition value
    if (e === '*') return a.length > 0 && a !== 'UNKNOWN';
    return a === e;
  }

  _hasLoop(node) {
    return node.getElementsByTagName('loop').length > 0;
  }

  _handlePerson(node, stars, session) {
    let text = this._processChildren(node, stars, session).trim();
    if (!text && stars.pattern && stars.pattern[0]) {
      text = stars.pattern[0];
    }
    return this.engine.normalizer.person(text);
  }

  _handlePerson2(node, stars, session) {
    let text = this._processChildren(node, stars, session).trim();
    if (!text && stars.pattern && stars.pattern[0]) {
      text = stars.pattern[0];
    }
    return this.engine.normalizer.person2(text);
  }

  _handleGender(node, stars, session) {
    let text = this._processChildren(node, stars, session).trim();
    if (!text && stars.pattern && stars.pattern[0]) {
      text = stars.pattern[0];
    }
    return this.engine.normalizer.gender(text);
  }

  _handleInput(node, session) {
    return session.getInput(this._getIndex(node));
  }

  _handleThat(node, session) {
    const indexStr = node.getAttribute('index') || '1,1';
    const parts = indexStr.split(',').map(Number);
    const respIdx = parts[0] || 1;
    const sentIdx = parts[1] || 1;
    return session.getThatByIndex(respIdx, sentIdx);
  }

  _handleDate(node) {
    const format = node.getAttribute('format');
    const now = new Date();
    if (format) {
      // Basic strftime-like formatting
      return format
        .replace(/%Y/g, now.getFullYear())
        .replace(/%m/g, String(now.getMonth() + 1).padStart(2, '0'))
        .replace(/%d/g, String(now.getDate()).padStart(2, '0'))
        .replace(/%H/g, String(now.getHours()).padStart(2, '0'))
        .replace(/%M/g, String(now.getMinutes()).padStart(2, '0'))
        .replace(/%S/g, String(now.getSeconds()).padStart(2, '0'))
        .replace(/%A/g, now.toLocaleDateString('en-US', { weekday: 'long' }))
        .replace(/%B/g, now.toLocaleDateString('en-US', { month: 'long' }))
        .replace(/%a/g, now.toLocaleDateString('en-US', { weekday: 'short' }))
        .replace(/%b/g, now.toLocaleDateString('en-US', { month: 'short' }));
    }
    return now.toLocaleDateString('en-US', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });
  }

  _handleMap(node, stars, session) {
    const mapName = node.getAttribute('name');
    const key = this._processChildren(node, stars, session).trim().toUpperCase();

    // Built-in maps
    if (mapName === 'successor') {
      const n = parseInt(key);
      return isNaN(n) ? 'unknown' : String(n + 1);
    }
    if (mapName === 'predecessor') {
      const n = parseInt(key);
      return isNaN(n) ? 'unknown' : String(n - 1);
    }

    // Custom maps from engine
    const map = this.engine.maps.get(mapName.toUpperCase());
    if (map && map.has(key)) {
      return map.get(key);
    }
    return 'unknown';
  }

  _handleFirst(node, stars, session) {
    const text = this._processChildren(node, stars, session).trim();
    const words = text.split(/\s+/);
    return words[0] || '';
  }

  _handleRest(node, stars, session) {
    const text = this._processChildren(node, stars, session).trim();
    const words = text.split(/\s+/);
    return words.slice(1).join(' ');
  }

  _handleLearn(node, stars, session) {
    // Dynamic category creation
    try {
      const categories = node.getDirectChildren('category');
      for (const cat of categories) {
        // Evaluate <eval> tags within the learn block
        const evaluated = this._evaluateLearnNode(cat, stars, session);
        // Add to engine
        const patterns = evaluated.getDirectChildren('pattern');
        const templates = evaluated.getDirectChildren('template');
        const thats = evaluated.getDirectChildren('that');

        if (patterns.length && templates.length) {
          const pattern = patterns[0].getTextContent().trim().toUpperCase();
          const that = thats.length ? thats[0].getTextContent().trim().toUpperCase() : '*';
          this.engine.graphmaster.addCategory(pattern, that, '*', templates[0], 'learned');
        }
      }
    } catch (e) {
      // Silently fail on learn errors
    }
    return '';
  }

  _evaluateLearnNode(node, stars, session) {
    // Deep clone and evaluate <eval> tags
    // For simplicity, return the node as-is (eval handling is complex)
    return node;
  }

  _handleInterval(node, stars, session) {
    try {
      const fromNodes = node.getDirectChildren('from');
      const toNodes = node.getDirectChildren('to');
      const styleNodes = node.getDirectChildren('style');

      const fromStr = fromNodes.length ? this._processChildren(fromNodes[0], stars, session).trim() : '';
      const toStr = toNodes.length ? this._processChildren(toNodes[0], stars, session).trim() : '';
      const style = styleNodes.length ? this._processChildren(styleNodes[0], stars, session).trim().toLowerCase() : 'years';

      const fromDate = fromStr ? new Date(fromStr) : new Date();
      const toDate = toStr ? new Date(toStr) : new Date();

      const diffMs = toDate - fromDate;
      switch (style) {
        case 'years': return String(Math.floor(diffMs / (365.25 * 24 * 60 * 60 * 1000)));
        case 'months': return String(Math.floor(diffMs / (30.44 * 24 * 60 * 60 * 1000)));
        case 'days': return String(Math.floor(diffMs / (24 * 60 * 60 * 1000)));
        case 'hours': return String(Math.floor(diffMs / (60 * 60 * 1000)));
        case 'minutes': return String(Math.floor(diffMs / (60 * 1000)));
        case 'seconds': return String(Math.floor(diffMs / 1000));
        default: return String(Math.floor(diffMs / (365.25 * 24 * 60 * 60 * 1000)));
      }
    } catch (e) {
      return '0';
    }
  }

  _getIndex(node) {
    const idx = node.getAttribute('index');
    return idx ? parseInt(idx) || 1 : 1;
  }
}
