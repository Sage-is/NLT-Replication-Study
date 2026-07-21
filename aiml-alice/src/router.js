/**
 * Precache router — AIML as a deterministic first-pass cache before agent routing.
 *
 * For each turn:
 *   1. Ask the AIML engine (tryRespond). A confident, specific match is a cache
 *      HIT — serve it for free, instantly, no LLM call.
 *   2. On a MISS (no specific pattern, or only the catch-all wildcard), hand the
 *      turn to the agent — an async function you supply that calls your LLM /
 *      tool-routing stack.
 *
 * The agent is fully pluggable: pass `options.agent` to wire in a real model.
 * Without one, a labeled placeholder keeps the app functional end-to-end.
 */

/** Placeholder agent used when no real agent is wired in. */
async function defaultAgent(message /*, sessionId, gate */) {
  return `[agent] would route to the LLM here for: "${message}"`;
}

/**
 * @param {object} engine - An AIMLEngine instance (must expose tryRespond).
 * @param {object} [options]
 * @param {(message:string, sessionId:string, gate:object)=>Promise<string>|string} [options.agent]
 * @param {number} [options.minSpecificity=1] - Literal-token threshold for a hit.
 */
export function createRouter(engine, options = {}) {
  const agent = options.agent || defaultAgent;
  const minSpecificity = options.minSpecificity ?? 1;
  const stats = { total: 0, precacheHits: 0, agentRoutes: 0 };

  async function handle(message, sessionId = 'anon') {
    stats.total++;
    const gate = engine.tryRespond(message, sessionId, { minSpecificity });

    if (gate.matched) {
      stats.precacheHits++;
      return {
        reply: gate.reply,
        source: 'precache',
        matched: true,
        hits: gate.hits,
        total: gate.total,
      };
    }

    stats.agentRoutes++;
    const reply = await agent(message, sessionId, gate);
    return { reply, source: 'agent', matched: false, hits: gate.hits, total: gate.total };
  }

  function metrics() {
    const { total, precacheHits, agentRoutes } = stats;
    return {
      ...stats,
      deflectionRate: total ? +(precacheHits / total).toFixed(3) : 0,
    };
  }

  return { handle, metrics, stats, engine };
}
