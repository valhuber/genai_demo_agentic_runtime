
# Probabilistic + Deterministic Rules: A Working Demo

## The Challenge

Agentic systems promise to transform enterprise software, but face a critical reliability challenge. As one skeptic put it: "Nobody wants a probabilistic payroll system."

**Both sides are right.** We need AI's adaptive intelligence AND deterministic guarantees. This demo shows how they work together.

## Starting Point: System Vibe

This project was created using [WebGenAI](https://apifabric.ai/admin-app/) - which generates a full-stack enterprise app from a natural language prompt in about a minute:

![WebGenAI prompt showing business requirements](images/genai-prompt-7.png)

**The prompt** (shown above) describes business requirements in natural language. GenAI-Logic translates this into a running system:

1. **declarative business rules** - 40× more concise than procedural code. For the rationale, see ["The Missing Half of GenAI"](https://medium.com/@valjhuber/the-missing-half-of-genai-and-why-microsofts-ceo-says-it-s-the-future-c6fc05d93640).
2. A multi-table API that enforces the logic
3. An multi-table Admin App to browse and update your data.

For more on *system vibe*, [click here](https://medium.com/@valjhuber/vibe-with-copilot-and-genai-logic-925894574125)

**This demo extends that foundation** to show how probabilistic AI integrates with deterministic rules:
- **When to invoke AI** - Deterministic rules decide when probabilistic decisions are needed
- **Guardrails** - Existing business rules automatically validate AI decisions
- **Governance:** - a clear record of AI-based decisions

<br>

### How It Works: The Log Tells the Story

When you add an item to a line item for an order, the debug console shows exactly what happens:

![logic-log](images/ai%20logic%20log.png)

**Step 1: Deterministic Rule Decides** - Does this product have multiple suppliers? If yes, invoke AI:
```
..Item[None] {Formula ItemUnitPriceFromSupplier(): use AI to compute unit_price by inserting SysSupplierReq
```

<br>

**Step 2: AI Reasons Probabilistically** - Given world conditions (Suez Canal blocked), AI chooses New Jersey supplier ($205) over Near East supplier ($105) for faster delivery:

```
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

......SysSupplierReq[None] {Chosen supplier 2 with reason 'The Suez Canal obstruction 
      significantly impacts lead time from Near East suppliers. Choosing a supplier 
      from New Jersey ensures quicker and more reliable delivery despite a higher 
      unit cost.' for SysSupplierReq None}
```


<br>

**Step 3: Deterministic Rules Cascade** - Item amount → Order total → Customer balance (automatically adjusted):

```
..Item[None] {Formula unit_price} unit_price: 205.00
..Item[None] {Formula amount} amount: 205.00

....Order[2] {Update - Adjusting order: amount_total} [635.00 --> 840.00]

......Customer[2] {Update - Adjusting customer: balance} [635.00 --> 840.00]
```

<br>

**Step 4: Guardrails Validate** - Credit limit constraint automatically checks if the AI's choice would violate business rules. If it does, the transaction fails with a clear error.

<br>

## The Architecture

**Two uses of GenAI:**
1. **GenAI creates deterministic rules** (from natural language) - avoiding brittle "FrankenCode"
2. **GenAI executes probabilistic decisions** (at runtime) - within deterministic guardrails

**Key insight:** Deterministic rules both trigger AND govern probabilistic AI:
- `count_suppliers` determines when AI is needed
- `credit_limit` constraint validates AI decisions
- `SysSupplierReq` captures full audit trail with reasoning

## Try It Yourself

[Installation and running instructions to be added]

## For More Detail

See `readme_prob.md` for complete technical architecture and implementation details.

