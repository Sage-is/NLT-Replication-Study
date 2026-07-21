/**
 * AIML Parser - Pure JS XML parser for AIML files
 *
 * Parses AIML XML into a DOM-like structure without external dependencies.
 * Handles: elements, attributes, text nodes, self-closing tags, CDATA, comments.
 */

export class XMLNode {
  constructor(type, name = '', attributes = {}) {
    this.type = type;       // 'element', 'text', 'cdata', 'root'
    this.name = name;       // Tag name (lowercase)
    this.attributes = attributes;
    this.children = [];
    this.text = '';         // For text/cdata nodes
    this.parent = null;
  }

  /**
   * Get all child elements with a given tag name
   */
  getElementsByTagName(name) {
    const results = [];
    const lower = name.toLowerCase();
    for (const child of this.children) {
      if (child.type === 'element' && child.name === lower) {
        results.push(child);
      }
      if (child.type === 'element') {
        results.push(...child.getElementsByTagName(name));
      }
    }
    return results;
  }

  /**
   * Get direct child elements with a given tag name
   */
  getDirectChildren(name) {
    const lower = name.toLowerCase();
    return this.children.filter(c => c.type === 'element' && c.name === lower);
  }

  /**
   * Get attribute value
   */
  getAttribute(name) {
    return this.attributes[name.toLowerCase()] || this.attributes[name] || '';
  }

  /**
   * Get text content (recursive)
   */
  getTextContent() {
    let text = '';
    for (const child of this.children) {
      if (child.type === 'text' || child.type === 'cdata') {
        text += child.text;
      } else if (child.type === 'element') {
        text += child.getTextContent();
      }
    }
    return text;
  }
}

export class AIMLParser {
  /**
   * Parse an AIML XML string into a DOM tree
   */
  parse(xmlString) {
    const root = new XMLNode('root', 'document');
    const stack = [root];
    let i = 0;
    const len = xmlString.length;

    while (i < len) {
      if (xmlString[i] === '<') {
        // Check for comment
        if (xmlString.startsWith('<!--', i)) {
          const end = xmlString.indexOf('-->', i);
          i = end === -1 ? len : end + 3;
          continue;
        }

        // Check for CDATA
        if (xmlString.startsWith('<![CDATA[', i)) {
          const end = xmlString.indexOf(']]>', i);
          const text = end === -1 ? xmlString.substring(i + 9) : xmlString.substring(i + 9, end);
          const node = new XMLNode('cdata');
          node.text = text;
          stack[stack.length - 1].children.push(node);
          i = end === -1 ? len : end + 3;
          continue;
        }

        // Check for processing instruction
        if (xmlString.startsWith('<?', i)) {
          const end = xmlString.indexOf('?>', i);
          i = end === -1 ? len : end + 2;
          continue;
        }

        // Check for DOCTYPE
        if (xmlString.startsWith('<!DOCTYPE', i) || xmlString.startsWith('<!doctype', i)) {
          const end = xmlString.indexOf('>', i);
          i = end === -1 ? len : end + 1;
          continue;
        }

        // Closing tag
        if (xmlString[i + 1] === '/') {
          const end = xmlString.indexOf('>', i);
          if (end === -1) break;
          stack.pop();
          i = end + 1;
          continue;
        }

        // Opening tag or self-closing tag
        const tagEnd = xmlString.indexOf('>', i);
        if (tagEnd === -1) break;

        const tagContent = xmlString.substring(i + 1, tagEnd);
        const selfClosing = tagContent.endsWith('/');
        const cleanContent = selfClosing ? tagContent.slice(0, -1).trim() : tagContent.trim();

        // Parse tag name and attributes
        const { name, attributes } = this._parseTag(cleanContent);
        const node = new XMLNode('element', name.toLowerCase(), attributes);
        node.parent = stack[stack.length - 1];
        stack[stack.length - 1].children.push(node);

        if (!selfClosing) {
          stack.push(node);
        }

        i = tagEnd + 1;
      } else {
        // Text content
        const nextTag = xmlString.indexOf('<', i);
        const text = nextTag === -1 ? xmlString.substring(i) : xmlString.substring(i, nextTag);
        if (text.trim()) {
          const node = new XMLNode('text');
          node.text = text;
          stack[stack.length - 1].children.push(node);
        } else if (text.includes(' ') || text.includes('\n')) {
          // Preserve whitespace-only text between elements if it has spaces
          const node = new XMLNode('text');
          node.text = text;
          stack[stack.length - 1].children.push(node);
        }
        i = nextTag === -1 ? len : nextTag;
      }
    }

    return root;
  }

  /**
   * Parse tag name and attributes from tag content
   */
  _parseTag(content) {
    const attributes = {};
    const parts = content.match(/^(\S+)(.*)/s);
    if (!parts) return { name: content, attributes };

    const name = parts[1];
    let attrStr = parts[2].trim();

    // Parse attributes: name="value" or name='value'
    const attrRegex = /(\w[\w\-.:]*)\s*=\s*(?:"([^"]*)"|'([^']*)')/g;
    let match;
    while ((match = attrRegex.exec(attrStr)) !== null) {
      const attrName = match[1].toLowerCase();
      const attrValue = match[2] !== undefined ? match[2] : match[3];
      attributes[attrName] = attrValue;
    }

    return { name, attributes };
  }
}

/**
 * Load and parse AIML categories from parsed XML
 * Returns array of { pattern, that, topic, template, filename }
 */
export function extractCategories(xmlDoc, filename = '') {
  const categories = [];
  const aimlElements = xmlDoc.getElementsByTagName('aiml');

  for (const aiml of aimlElements) {
    // Process top-level categories
    for (const child of aiml.children) {
      if (child.type !== 'element') continue;

      if (child.name === 'category') {
        const cat = _extractCategory(child, '*', filename);
        if (cat) categories.push(cat);
      } else if (child.name === 'topic') {
        const topicName = child.getAttribute('name') || '*';
        for (const topicChild of child.children) {
          if (topicChild.type === 'element' && topicChild.name === 'category') {
            const cat = _extractCategory(topicChild, topicName, filename);
            if (cat) categories.push(cat);
          }
        }
      }
    }
  }

  return categories;
}

function _extractCategory(catNode, topic, filename) {
  const patterns = catNode.getDirectChildren('pattern');
  const templates = catNode.getDirectChildren('template');
  const thats = catNode.getDirectChildren('that');

  if (patterns.length === 0 || templates.length === 0) return null;

  // Get pattern text - handle inline set tags
  const pattern = _getPatternText(patterns[0]);
  const that = thats.length > 0 ? _getPatternText(thats[0]) : '*';
  const template = templates[0]; // Keep as XML node for template processing

  return { pattern, that, topic, template, filename };
}

/**
 * Extract pattern text, converting <set> tags to SET:NAME markers
 */
function _getPatternText(node) {
  let text = '';
  for (const child of node.children) {
    if (child.type === 'text' || child.type === 'cdata') {
      text += child.text;
    } else if (child.type === 'element') {
      if (child.name === 'set') {
        // <set>name</set> in pattern -> SET:NAME marker
        const setName = child.getTextContent().trim().toUpperCase();
        text += ` SET:${setName} `;
      } else if (child.name === 'bot') {
        // <bot name="prop"/> in pattern - would need runtime resolution
        // For now, treat as a placeholder
        text += ` BOT:${child.getAttribute('name').toUpperCase()} `;
      } else {
        text += child.getTextContent();
      }
    }
  }
  return text.replace(/\s+/g, ' ').trim().toUpperCase();
}
