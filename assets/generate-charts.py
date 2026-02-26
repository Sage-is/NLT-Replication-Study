#!/usr/bin/env python3
"""Generate xkcd-style charts for the NLT Replication Study.
Data from REPLICATION_STUDY.md — 14 models, 8,560 trials."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ── Data from Appendix A ──
MODELS = [
    # (short_name, nlt_acc, struct_acc, gain, nlt_errors, struct_errors, tier)
    ('Claude Sonnet 4',    61.9, 18.8,  43.1,  0,   0,   'frontier'),
    ('Mistral 7B',         39.4,  0.0,  39.4,  0, 320,   'no-native'),
    ('Qwen3-VL*',          33.8,  0.0,  33.8,  0, 307,   'no-native'),
    ('DeepSeek-R1',        55.0, 31.0,  24.0,  0,   1,   'reasoning'),
    ('DeepSeek-V3',        90.0, 69.7,  20.3,  0,   0,   'mid-tier'),
    ('GPT-5-nano',         79.1, 59.4,  19.7,  0,   0,   'mid-tier'),
    ('Llama 3.1 8B',       47.8, 32.9,  14.9,  0,  37,   'mid-tier'),
    ('Gemini Flash Lite',  73.1, 63.1,  10.0,  0,   0,   'mid-tier'),
    ('Gemini 2.0 Flash',   85.0, 79.5,   5.5,  0,   2,   'frontier'),
    ('GPT-OSS-20B',        42.7, 39.3,   3.4, 30,  34,   'mid-tier'),
    ('GPT-5',              81.9, 80.3,   1.6,  0,   0,   'frontier'),
    ('Kimi-K2',            67.2, 67.8,  -0.6,  0,   0,   'frontier'),
    ('GPT-OSS-120B',       42.6, 49.0,  -6.4, 21,  54,   'mid-tier'),
    ('Gemini 2.5 Pro*',    48.3, 82.1, -33.7,  0,   0,   'struct-opt'),
]

TIER_COLORS = {
    'no-native':  '#e53935',   # red
    'reasoning':  '#ff9800',   # orange
    'mid-tier':   '#42a5f5',   # blue
    'frontier':   '#66bb6a',   # green
    'struct-opt': '#ab47bc',   # purple
}

TIER_LABELS = {
    'no-native':  'No native tool calling',
    'reasoning':  'Reasoning model',
    'mid-tier':   'Mid-tier',
    'frontier':   'Frontier',
    'struct-opt': 'Structured-optimized',
}


# ──────────────────────────────────────────────
# Chart 1: HERO — NLT Gain per model (horizontal bars)
# ──────────────────────────────────────────────
def chart1_hero_gains():
    with plt.xkcd(scale=1, length=100, randomness=2):
        fig, ax = plt.subplots(figsize=(12, 9))

        names = [m[0] for m in MODELS]
        gains = [m[3] for m in MODELS]
        tiers = [m[6] for m in MODELS]
        colors = [TIER_COLORS[t] for t in tiers]

        y_pos = np.arange(len(names))
        bars = ax.barh(y_pos, gains, color=colors, edgecolor='black', linewidth=0.8, height=0.7)

        # Zero line
        ax.axvline(x=0, color='black', linewidth=1.5)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=10)
        ax.invert_yaxis()
        ax.set_xlabel('NLT Accuracy Gain (percentage points)', fontsize=12)
        ax.set_title('Natural Language Tools: Who Benefits Most?\n14 Models, 8,560 Trials',
                     fontsize=16, fontweight='bold')

        # Legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=c, edgecolor='black', label=l)
                          for t, (c, l) in
                          {k: (TIER_COLORS[k], TIER_LABELS[k]) for k in
                           ['no-native', 'reasoning', 'mid-tier', 'frontier', 'struct-opt']}.items()]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

        # Annotate the big winner
        ax.annotate(
            '+43.1pp!',
            xy=(43.1, 0), fontsize=11, fontweight='bold', color='darkred',
            xytext=(30, -0.8),
        )

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        path = os.path.join(OUT, 'nlt-hero-gains.png')
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Saved: {path}")


# ──────────────────────────────────────────────
# Chart 2: The Error Cliff — 51 vs 755
# ──────────────────────────────────────────────
def chart2_error_cliff():
    with plt.xkcd(scale=1, length=100, randomness=2):
        fig, ax = plt.subplots(figsize=(10, 7))

        categories = ['NLT', 'Structured']
        errors = [51, 755]
        colors = ['#66bb6a', '#ef5350']

        bars = ax.bar(categories, errors, color=colors, edgecolor='black', linewidth=1.5, width=0.5)

        for bar, err in zip(bars, errors):
            ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 15,
                    f'{err}', ha='center', va='bottom', fontsize=22, fontweight='bold')

        ax.annotate(
            '93% fewer errors',
            xy=(0, 80), xytext=(0.5, 450),
            fontsize=16, fontweight='bold', color='green',
            arrowprops=dict(arrowstyle='->', color='green', lw=2.5),
            ha='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', alpha=0.7)
        )

        ax.set_ylabel('Total Errors (across 8,560 trials)', fontsize=13)
        ax.set_title('The Reliability Gap:\nStructured Tool Calling Is 15x More Error-Prone',
                     fontsize=16, fontweight='bold')
        ax.set_ylim(0, 900)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        path = os.path.join(OUT, 'nlt-error-cliff.png')
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Saved: {path}")


# ──────────────────────────────────────────────
# Chart 3: NLT vs Structured accuracy (paired bars)
# ──────────────────────────────────────────────
def chart3_paired_accuracy():
    with plt.xkcd(scale=1, length=100, randomness=2):
        fig, ax = plt.subplots(figsize=(14, 8))

        names = [m[0] for m in MODELS]
        nlt_acc = [m[1] for m in MODELS]
        struct_acc = [m[2] for m in MODELS]

        x = np.arange(len(names))
        width = 0.35

        bars1 = ax.bar(x - width/2, nlt_acc, width, label='NLT',
                       color='#66bb6a', edgecolor='black', linewidth=0.8)
        bars2 = ax.bar(x + width/2, struct_acc, width, label='Structured',
                       color='#ef5350', edgecolor='black', linewidth=0.8, alpha=0.8)

        ax.set_ylabel('Accuracy (%)', fontsize=13)
        ax.set_title('NLT vs Structured Accuracy Across 14 Models',
                     fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right', fontsize=9)
        ax.legend(fontsize=12, loc='upper right')
        ax.set_ylim(0, 100)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Highlight the catastrophic failures
        for i, (n, s) in enumerate(zip(nlt_acc, struct_acc)):
            if s == 0:
                ax.annotate('FAIL', xy=(i + width/2, 2), fontsize=7,
                           ha='center', color='darkred', fontweight='bold')

        plt.tight_layout()
        path = os.path.join(OUT, 'nlt-paired-accuracy.png')
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Saved: {path}")


# ──────────────────────────────────────────────
# Chart 4: Capability Gradient (the key finding)
# ──────────────────────────────────────────────
def chart4_capability_gradient():
    with plt.xkcd(scale=1, length=100, randomness=2):
        fig, ax = plt.subplots(figsize=(12, 7))

        # Group by tier and compute mean gain
        tier_order = ['no-native', 'reasoning', 'mid-tier', 'frontier', 'struct-opt']
        tier_display = [
            'No Native\nTool Calling',
            'Reasoning\nModels',
            'Mid-Tier\nModels',
            'Frontier\nModels',
            'Structured-\nOptimized'
        ]

        tier_gains = {}
        tier_models = {}
        for m in MODELS:
            t = m[6]
            if t not in tier_gains:
                tier_gains[t] = []
                tier_models[t] = []
            tier_gains[t].append(m[3])
            tier_models[t].append(m[0])

        means = [np.mean(tier_gains[t]) for t in tier_order]
        colors = [TIER_COLORS[t] for t in tier_order]

        # Individual points
        for i, t in enumerate(tier_order):
            for gain in tier_gains[t]:
                ax.scatter(i, gain, color=TIER_COLORS[t], s=120,
                          edgecolors='black', linewidth=0.8, zorder=5, alpha=0.8)

        # Mean line connecting tiers
        ax.plot(range(len(tier_order)), means, 'k--', linewidth=2, alpha=0.5, zorder=3)
        for i, m in enumerate(means):
            ax.scatter(i, m, color='black', s=200, marker='_', linewidth=3, zorder=6)

        # Zero line
        ax.axhline(y=0, color='gray', linewidth=1, linestyle=':')
        ax.text(4.3, 1.5, 'break even', fontsize=8, color='gray')

        # Shade zones
        ax.axhspan(0, 50, alpha=0.05, color='green')
        ax.axhspan(-40, 0, alpha=0.05, color='red')
        ax.text(0.05, 42, 'NLT wins ↑', fontsize=10, color='green', alpha=0.5,
                transform=ax.get_yaxis_transform())
        ax.text(0.05, -8, 'Structured wins ↓', fontsize=10, color='red', alpha=0.5,
                transform=ax.get_yaxis_transform())

        ax.set_xticks(range(len(tier_order)))
        ax.set_xticklabels(tier_display, fontsize=11)
        ax.set_ylabel('NLT Accuracy Gain (pp)', fontsize=13)
        ax.set_title('The Capability Gradient:\nNLT Advantage Decreases With Model Optimization',
                     fontsize=16, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Annotation
        ax.annotate(
            'As models get better at structured\ntool calling, NLT\'s edge narrows\n— but error rates still favor NLT',
            xy=(3.5, -15), fontsize=9, style='italic', color='#555555',
            ha='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8)
        )

        plt.tight_layout()
        path = os.path.join(OUT, 'nlt-capability-gradient.png')
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Saved: {path}")


# ──────────────────────────────────────────────
# Chart 5: Token savings
# ──────────────────────────────────────────────
def chart5_token_savings():
    with plt.xkcd(scale=1, length=100, randomness=2):
        fig, ax = plt.subplots(figsize=(8, 6))

        categories = ['NLT', 'Structured']
        tokens = [3_384_196, 4_522_651]
        colors = ['#66bb6a', '#ef5350']

        bars = ax.bar(categories, [t / 1_000_000 for t in tokens],
                     color=colors, edgecolor='black', linewidth=1.5, width=0.45)

        for bar, tok in zip(bars, tokens):
            ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.05,
                    f'{tok/1_000_000:.1f}M', ha='center', va='bottom',
                    fontsize=16, fontweight='bold')

        ax.annotate(
            '25.2% fewer tokens\n= 25.2% cost savings',
            xy=(0.5, 3.8), fontsize=13, fontweight='bold', color='green',
            ha='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', alpha=0.7)
        )

        ax.set_ylabel('Total Tokens (millions)', fontsize=13)
        ax.set_title('NLT Uses Fewer Tokens Too',
                     fontsize=16, fontweight='bold')
        ax.set_ylim(0, 5.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        path = os.path.join(OUT, 'nlt-token-savings.png')
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Saved: {path}")


if __name__ == '__main__':
    chart1_hero_gains()
    chart2_error_cliff()
    chart3_paired_accuracy()
    chart4_capability_gradient()
    chart5_token_savings()
    print("\nAll NLT charts generated!")
