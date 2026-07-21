#!/usr/bin/env node
/**
 * AIML-ALICE Demo — Non-interactive test of the engine
 *
 * Runs a set of test inputs and prints responses.
 */

import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { AIMLEngine } from './engine.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, '..');

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

const userId = 'demo-user';

const testInputs = [
  'Hello',
  'What is your name?',
  'Who are you?',
  'How are you?',
  'My name is Alex',
  'What is my name?',
  'What is AIML?',
  'Tell me a joke',
  'What is the meaning of life?',
  'How do you work?',
  'Are you a robot?',
  'What is the difference between you and ChatGPT?',
  'Do you like music?',
  'I am sad',
  'Thank you',
  'Goodbye',
];

console.log('═══════════════════════════════════════');
console.log('  AIML-ALICE Demo — Test Conversation');
console.log('═══════════════════════════════════════\n');

for (const input of testInputs) {
  const response = engine.respond(input, userId);
  console.log(`  You>   ${input}`);
  console.log(`  Alice> ${response}`);
  console.log();
}

console.log('═══════════════════════════════════════');
console.log(`  ${testInputs.length} exchanges completed.`);
console.log('═══════════════════════════════════════');
