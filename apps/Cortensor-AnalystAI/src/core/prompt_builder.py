# src/core/prompt_builder.py

def build_analyst_prompt(market_data: dict, news_data: list[dict]) -> str:
    """
    Builds a DeepSeek R1–compatible prompt for zero‑hallucination, strict sentiment alignment,
    and English‑only expert analysis.
    """
    asset_type = market_data.get('type', 'Asset')
    asset_name = market_data.get('name', 'N/A')

    # Market Data block
    summary = [f"## MARKET DATA for {asset_name.upper()} ({asset_type.upper()}):"]
    if asset_type == "Crypto":
        summary += [
            f"- Current Price: ${market_data.get('current_price', 0):,.2f} USD",
            f"- 24h Change: {market_data.get('price_change_24h_pct', 0):+.2f}%",
            f"- 7d Change: {market_data.get('price_change_7d_pct', 0):+.2f}%",
            f"- 30d Change: {market_data.get('price_change_30d_pct', 0):+.2f}%",
            f"- 24h Volume: ${market_data.get('trading_volume_24h', 0):,.0f} USD",
            f"- Market Cap: ${market_data.get('market_cap', 0):,.0f} USD"
        ]
    else: # Stock type
        summary += [
            f"- Current Price: ${market_data.get('current_price', 0):,.2f} USD",
            f"- Today’s Change: {market_data.get('price_change_pct', 0):+.2f}%",
            f"- 7d Change: {market_data.get('price_change_7d_pct', 0):+.2f}%",
            f"- 30d Change: {market_data.get('price_change_30d_pct', 0):+.2f}%",
            f"- Volume Today: {market_data.get('trading_volume', 0):,.0f} shares",
            f"- Market Cap: ${market_data.get('market_cap', 0):,.0f} USD",
            f"- P/E Ratio: {market_data.get('pe_ratio', 'N/A')}",
            f"- EPS (TTM): {market_data.get('eps_ttm', 'N/A')}"
        ]

    # News block
    if news_data:
        news_lines = ["## NEWS SUMMARY (for reference):"]
        for i, n in enumerate(news_data, start=1):
            news_lines.append(f"- News {i}: {n['title']}")
            if n.get('description'):
                news_lines.append(f"  Description: {n['description']}")
        news_instruction = (
            "You may reference news by its label (News 1, News 2, etc.). "
            "Cite “News [#]” when using an insight."
        )
    else:
        news_lines = ["## NEWS SUMMARY: No news provided."]
        news_instruction = "You MUST base all opinions solely on the market data above."

    prompt = f"""
ROLE: You are a DeepSeek R1 financial analyst. Produce factual, concise English-only analysis.
Do NOT hallucinate. Use ONLY the provided DATA and NEWS.

TASK:
1) Generate EXACTLY THREE distinct expert opinions.
2) Generate EXACTLY ONE final key takeaway sentence.

{chr(10).join(summary)}

{chr(10).join(news_lines)}

RULES FOR OPINIONS:
- Language: English only.
- Quantity: Exactly three unique opinions.
- Data exclusivity: Do NOT use or invent any external information.
- Citation: Quote data points verbatim (e.g. “+2.34%”, “$180.34 USD”). If using news, cite “News [#]”.
- Sentiment alignment:
  • Positive change (+X%): Bullish or Neutral. The justification must not repeat the sentiment word.
  • Negative change (–X%): Neutral or Bearish. The justification must not repeat the sentiment word.
  • Mixed periods: Sentiment should reflect the most recent data period cited. The justification must not repeat the sentiment word.
- {news_instruction}

RULES FOR KEY TAKEAWAY:
- Language: English only.
- Exactly one concise sentence.
- Summarize the overall sentiment and drivers from your opinions.
- Do NOT introduce any new facts or numbers.

OUTPUT FORMAT:
Opinion 1: [Sentiment]: [Justification citing data/news]
Opinion 2: [Sentiment]: [Justification citing data/news]
Opinion 3: [Sentiment]: [Justification citing data/news]
Key Takeaway: [One-sentence summary]

Begin.
"""
    return prompt