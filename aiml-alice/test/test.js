#!/usr/bin/env node
/**
 * AIML-ALICE Test Suite
 *
 * Tests core AIML 2.0 functionality:
 * - Pattern matching (exact, wildcards)
 * - SRAI (symbolic reduction)
 * - Variables (set/get)
 * - Random responses
 * - Bot properties
 * - Condition tags
 * - Star captures
 */

import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { AIMLEngine } from '../src/engine.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, '..');

let passed = 0;
let failed = 0;

function assert(label, actual, expected) {
  if (expected instanceof RegExp) {
    if (expected.test(actual)) {
      passed++;
      console.log(`  ✅ ${label}`);
    } else {
      failed++;
      console.log(`  ❌ ${label}`);
      console.log(`     Expected: ${expected}`);
      console.log(`     Got:      "${actual}"`);
    }
  } else if (expected === null) {
    // Just check it's not empty
    if (actual && actual.trim().length > 0) {
      passed++;
      console.log(`  ✅ ${label} → "${actual.substring(0, 60)}..."`);
    } else {
      failed++;
      console.log(`  ❌ ${label} — empty response`);
    }
  } else {
    if (actual === expected) {
      passed++;
      console.log(`  ✅ ${label}`);
    } else {
      failed++;
      console.log(`  ❌ ${label}`);
      console.log(`     Expected: "${expected}"`);
      console.log(`     Got:      "${actual}"`);
    }
  }
}

// Initialize
const engine = new AIMLEngine({
  substitutions: {
    normal: resolve(root, 'substitutions/normal.txt'),
    person: resolve(root, 'substitutions/person.txt'),
  },
});

engine.loadBotProperties(resolve(root, 'bot.properties'));
engine.loadSet('number', resolve(root, 'sets/number.txt'));
engine.loadSet('color', resolve(root, 'sets/color.txt'));
engine.loadMap('successor', resolve(root, 'maps/successor.txt'));

const count = engine.loadDirectory(resolve(root, 'aiml'));
console.log(`Loaded ${count} categories.\n`);

const userId = 'test-user';

// ── Tests ──

console.log('Pattern Matching:');
assert('Exact match (HELLO)', engine.respond('Hello', userId), null);
assert('Wildcard match (*)', engine.respond('I like pizza', userId), null);
assert('What is AIML', engine.respond('What is AIML', userId), /AIML stands for/);

console.log('\nSRAI (Symbolic Reduction):');
assert('HI -> HELLO', engine.respond('Hi', userId), null);
assert('BYE -> GOODBYE', engine.respond('Bye', userId), null);
assert('THANKS -> THANK YOU', engine.respond('Thanks', userId), null);

console.log('\nVariable Set/Get:');
engine.respond('My name is TestUser', userId);
assert('Get name after set', engine.respond('What is my name', userId), /TestUser/);

console.log('\nBot Properties:');
assert('Bot name', engine.respond('What is your name', userId), /Alice/);
assert('Who are you', engine.respond('Who are you', userId), /Alice/);

console.log('\nRandom Responses:');
const r1 = engine.respond('Tell me a joke', userId);
const r2 = engine.respond('Tell me a joke', userId);
const r3 = engine.respond('Tell me a joke', userId);
assert('Joke response is non-empty', r1, null);
// Random might give same result, but at least one should exist
assert('Multiple joke calls work', r3, null);

console.log('\nConditions:');
// Name was set to TestUser above
assert('Condition (name set)', engine.respond('What is my name', userId), /TestUser/);
// New session — name unknown
assert('Condition (name unknown)', engine.respond('What is my name', 'new-user'), /haven't told me/);

console.log('\nConversational Flow:');
assert('How are you', engine.respond('How are you', userId), null);
assert('I am sad', engine.respond('I am sad', userId), /sorry/i);
assert('I am happy', engine.respond('I am happy', userId), /wonderful|happy/i);

console.log('\nIdentity:');
assert('Are you a robot', engine.respond('Are you a robot', userId), /chatbot/i);
assert('ChatGPT comparison', engine.respond('What is the difference between you and ChatGPT', userId), /neural network|pattern matching/i);
assert('How do you work', engine.respond('How do you work', userId), /Graphmaster|pattern/i);

console.log('\nCategory Count:');
assert('Size > 0', engine.graphmaster.categoryCount > 0, true);

// ── Summary ──

console.log('\n═══════════════════════════════════════');
console.log(`  Results: ${passed} passed, ${failed} failed (${passed + failed} total)`);
console.log('═══════════════════════════════════════');

process.exit(failed > 0 ? 1 : 0);
