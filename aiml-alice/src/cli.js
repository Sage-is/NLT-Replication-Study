#!/usr/bin/env node
/**
 * AIML-ALICE CLI — Interactive chat with the ALICE bot
 *
 * Usage:
 *   node src/cli.js                    # default brain
 *   node src/cli.js --aiml ./my-brain  # custom AIML directory
 */

import { createInterface } from 'readline';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { AIMLEngine } from './engine.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, '..');

// Parse args
const args = process.argv.slice(2);
let aimlDir = resolve(root, 'aiml');
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--aiml' && args[i + 1]) {
    aimlDir = resolve(args[i + 1]);
    i++;
  }
}

// Initialize engine
const engine = new AIMLEngine({
  substitutions: {
    normal: resolve(root, 'substitutions/normal.txt'),
    person: resolve(root, 'substitutions/person.txt'),
  },
});

// Load bot properties
engine.loadBotProperties(resolve(root, 'bot.properties'));

// Load sets
engine.loadSet('number', resolve(root, 'sets/number.txt'));
engine.loadSet('color', resolve(root, 'sets/color.txt'));

// Load maps
engine.loadMap('successor', resolve(root, 'maps/successor.txt'));

// Load AIML brain
console.log(`Loading AIML from: ${aimlDir}`);
const count = engine.loadDirectory(aimlDir);
console.log(`Loaded ${count} categories from ${engine.loadedFiles.length} file(s).`);
console.log();
console.log('╔═══════════════════════════════════════════╗');
console.log('║  ALICE — AIML 2.0 Interactive Chat        ║');
console.log('║  Type "quit" or Ctrl+C to exit            ║');
console.log('╚═══════════════════════════════════════════╝');
console.log();

// REPL
const rl = createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: 'You> ',
});

const userId = 'cli-user';

rl.prompt();

rl.on('line', (line) => {
  const input = line.trim();
  if (!input) {
    rl.prompt();
    return;
  }
  if (input.toLowerCase() === 'quit' || input.toLowerCase() === 'exit') {
    console.log('Goodbye!');
    process.exit(0);
  }

  const response = engine.respond(input, userId);
  console.log(`Alice> ${response}`);
  console.log();
  rl.prompt();
});

rl.on('close', () => {
  console.log('\nGoodbye!');
  process.exit(0);
});
