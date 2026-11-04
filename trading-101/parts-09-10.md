# Trading 101 — Parts 9 & 10 (scripts for the laptop pipeline)

Same format as Parts 6–8: 30s, 6 scenes, blockframe look (`_shared/bf.mjs`), Kokoro `af_heart` 0.95 (last line 1.05),
same SFX/bed, scene starts ≈ `[0, 3, 9, 15.25, 20.5, 25.75]`, ends "Follow for more", loudnorm -14 LUFS.

---

## Part 9 — Trend lines (`videos/trading-109-trend-lines`)

Builds directly on Part 8: support/resistance, but diagonal.

| # | Scene | Voice line | Visual |
|---|-------|-----------|--------|
| 1 | hook | "Price isn't random. It leaves a trail." | Zigzag price line draws in; a dashed line snaps under the lows. |
| 2 | uptrend | "Connect the higher lows, and you get an uptrend line. Buyers keep stepping in higher." | Rising price, three lows light up (1, 2, 3), green line through them, pill "UPTREND ↗". |
| 3 | downtrend | "Connect the lower highs, and you get a downtrend line. Sellers keep pushing it down." | Falling price, three highs light up, red line across them, pill "DOWNTREND ↘". |
| 4 | break | "When price closes through the line, the trend may be changing." | Price punches down through the green uptrend line; line flashes, pill "TREND BREAK?". |
| 5 | caveat | "Two touches draw a line. Three touches make it matter." | Counter: touch 1 ✓, touch 2 ✓ ("a line"), touch 3 ✓✓ ("a trend"). |
| 6 | close | "Follow for more." | Standard close card. |

**Caption**
```
Part 9 📈 Trend lines: connect the higher lows for an uptrend, the lower highs for a downtrend. When price closes through the line, the trend may be changing. Two touches draw a line, three make it matter.
Educational only, not financial advice.
#trading101 #trendlines #chartanalysis #investingforbeginners #learnontiktok
```

---

## Part 10 — FOMO (`videos/trading-110-fomo`)

A psychology break after three chart parts; ties back to stop-loss (Part 4) and risk/reward (Part 5).

| # | Scene | Voice line | Visual |
|---|-------|-----------|--------|
| 1 | hook | "The most expensive feeling in trading? FOMO." | Big "FOMO" block slams in, price tag "$$$" wobbles. |
| 2 | chase | "Fear of missing out. A stock jumps fifty percent, and you buy at the top." | Rocket green candles, "+50%" pill, a "YOU BUY" marker lands at the peak. |
| 3 | dump | "Then early buyers sell to you, and the price falls right back." | Arrows from early-buyer dots to "YOU"; price slides down, red "-30%" pill. |
| 4 | fix | "Before you buy, write your entry, stop-loss and target. No plan, no trade." | Checklist card: ENTRY ✓, STOP-LOSS ✓, TARGET ✓, stamp "NO PLAN = NO TRADE". |
| 5 | caveat | "Missing a move costs nothing. Chasing one can cost a lot." | Two cards side by side: "MISSED IT: $0" (green) vs "CHASED IT: -$$$" (red). |
| 6 | close | "Follow for more." | Standard close card. |

**Caption**
```
Part 10 🧠 FOMO = fear of missing out. You see a stock jump 50%, buy at the top, and early buyers sell to you. Fix: write your entry, stop-loss and target before you buy. Missing a move costs nothing. Chasing one can cost a lot.
Educational only, not financial advice.
#trading101 #fomo #tradingpsychology #investingforbeginners #learnontiktok
```

---

## Prompt to paste into the laptop "Trading 101 TikTok video" chat

```
Make Trading 101 Part 9 (trend lines) and then Part 10 (FOMO) with the same pipeline, voice, style and sound as Part 8.
Use these exact voice lines and visuals:
[paste the two tables above]
Render each, check frames, loudnorm, and send both to my phone with their captions.
```

Later topics: trading volume, moving averages, fees/spread, journaling trades.
