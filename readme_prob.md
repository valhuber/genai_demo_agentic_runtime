# Deterministic Rules vs Probabilistic Rules in Business Logic

This demo project explores the integration of **Deterministic Rules (DRs)** and **Probabilistic Rules (PRs)** within the ApiLogicServer/GenAI-Logic framework.

## 🎯 **Conceptual Overview**

### **Deterministic Rules (DRs)**
Traditional business logic that produces **consistent, predictable outcomes**:
- Mathematical calculations (amount = quantity × unit_price)
- Aggregations (customer balance = sum of order totals)
- Constraints (balance ≤ credit_limit)
- Copies/lookups from reference data

**Characteristics:**
- ✅ Same input → Same output (always)
- ✅ Fully explainable and auditable
- ✅ Legally compliant and predictable
- ✅ Fast execution with minimal overhead

### **Probabilistic Rules (PRs)**
AI-driven business logic that produces **contextual, optimized decisions**:
- Supplier selection based on multiple criteria
- Dynamic pricing recommendations
- Risk assessment and fraud detection
- Personalization and recommendation engines

**Characteristics:**
- 🎲 Same input → Potentially different outputs
- 🧠 Learns from data and adapts over time
- 🎯 Optimizes for complex, multi-dimensional criteria
- 📊 Requires explanation frameworks for transparency

## 🤝 **Why Both Are Essential**

Modern business applications require **hybrid logic systems**:

| Aspect | Deterministic Rules | Probabilistic Rules |
|--------|-------------------|-------------------|
| **Use Cases** | Compliance, calculations, validations | Optimization, predictions, recommendations |
| **Reliability** | 100% consistent | Contextually optimal |
| **Auditability** | Transparent by design | Requires explainability tools |
| **Performance** | Microseconds | Milliseconds to seconds |
| **Maintenance** | Rule updates | Model retraining |

**Example Scenario**: Order Processing
- **DR**: Calculate line item amounts, validate credit limits, enforce business constraints
- **PR**: Select optimal supplier, recommend quantity discounts, predict delivery times

## 🔧 **Implementation Summary**

### **Current Architecture**

#### **Deterministic Rules Analysis** 
Based on analysis of `logic/logic_discovery/check_credit.py` and `app_integration.py`, the current DR implementation demonstrates the **44X code reduction** principle from declarative business logic:

**Core Use Cases Currently Handled by DRs:**

1. **Check Credit Use Case** - Multi-table derivation chain:
   ```python
   # 5 lines of declarative rules replace ~220 lines of procedural code
   Rule.constraint(validate=models.Customer, as_condition=lambda row: row.balance <= row.credit_limit)
   Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None)
   Rule.sum(derive=models.Order.amount_total, as_sum_of=models.Item.amount)
   Rule.formula(derive=models.Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
   Rule.count(derive=models.Product.count_suppliers, as_count_of=models.ProductSupplier)
   ```

2. **App Integration Use Case** - Event-driven processing:
   ```python
   # Kafka integration triggered by data changes
   Rule.after_flush_row_event(on_class=models.Order, calling=kafka_producer.send_row_to_kafka,
                             if_condition=lambda row: row.date_shipped is not None)
   ```

**Key DR Patterns Demonstrated:**
- **Automatic Recomputation**: When `Item.quantity` changes, `Item.amount` → `Order.amount_total` → `Customer.balance` cascade automatically
- **Multi-table Constraints**: Credit limit validation spans Customer/Order/Item tables with zero additional code
- **Optimized Execution**: LogicBank's pruning algorithms eliminate unnecessary SQL operations
- **Event Integration**: Business rule changes trigger external system notifications

**Complex Scenario Example**: Changing `Item.product_id` triggers:
1. Old product's `count_suppliers` decremented
2. New product's `count_suppliers` incremented  
3. `Item.unit_price` recalculated via supplier logic
4. `Item.amount` recalculated (quantity × new unit_price)
5. `Order.amount_total` recalculated (sum of all items)
6. `Customer.balance` recalculated (sum of all orders)
7. Credit limit constraint re-validated
8. If order ships, Kafka message sent

*This represents the "declarative logic in a procedural world" - business rules expressed as intentions, executed by an optimized runtime engine.*

## ⚡ **The Performance Revolution: Adjustment vs Aggregation**

### **The Fundamental Breakthrough**

Most business rule engines and ORMs suffer from a critical performance flaw: **they recalculate aggregates instead of maintaining them**. LogicBank's revolutionary approach uses **incremental adjustments**, delivering performance improvements of 120X or more in real-world scenarios.

### **Traditional Approach: The Aggregation Trap**

**Example**: Maintaining a count of New York citizens

**Rete Engines, Hibernate, Most ORMs:**
```sql
-- Every time someone moves to/from NY, recalculate everything
SELECT COUNT(*) FROM citizens WHERE state = 'NY'
-- With millions of records = expensive query every time
-- O(n) complexity where n = total citizen count
```

**Business Impact:**
- 4-minute transactions for complex business rules
- Performance degrades linearly with data growth
- Database bottlenecks under concurrent load
- Real-time processing becomes impossible at scale

### **LogicBank's Adjustment Pattern**

**Same Business Rule, Revolutionary Execution:**
```python
Rule.count(derive=models.State.citizen_count, as_count_of=models.Citizen)
```

**Behind the Scenes Magic:**
```python
# New citizen moves to NY: citizen_count += 1 (O(1))
# Citizen moves NY → CA: NY.citizen_count -= 1, CA.citizen_count += 1 (O(1))  
# Citizen changes name: NO OPERATION (pruned - irrelevant to count)
```

**Performance Characteristics:**
- **O(1) complexity** - independent of data size
- **Intelligent pruning** - irrelevant changes ignored
- **Incremental maintenance** - aggregates adjusted, not recalculated
- **120X performance improvement** in real-world scenarios

### **Complex Multi-Table Example**

**Business Rule**: Customer balance = sum of unshipped order totals
```python
Rule.sum(derive=models.Customer.balance, 
         as_sum_of=models.Order.amount_total,
         where=lambda row: row.date_shipped is None)
```

**Traditional Execution** (when Item.quantity changes):
```sql
-- Recalculate entire customer balance from scratch
SELECT SUM(amount_total) FROM orders 
WHERE customer_id = 123 AND date_shipped IS NULL
-- Plus recalculate order total:
SELECT SUM(amount) FROM items WHERE order_id = 456
```

**LogicBank Execution** (same change):
```python
# Step 1: Calculate net change to item amount
old_item_amount = old_row.quantity * old_row.unit_price
new_item_amount = row.quantity * row.unit_price
delta = new_item_amount - old_item_amount

# Step 2: Adjust order total (O(1))
order.amount_total += delta

# Step 3: Adjust customer balance (O(1))  
customer.balance += delta

# Total: 3 operations vs. 2 aggregate queries over potentially millions of records
```

### **Pruning Intelligence**

LogicBank's engine builds sophisticated dependency graphs to determine what actually needs to be recalculated:

**Smart Pruning Examples:**
- Customer name change → **No financial recalculations** (pruned)
- Item product_id change → **Price and totals affected** (executed)
- Order ship_date change → **Customer balance affected** (executed - order now excluded from balance)
- Product description change → **No calculations needed** (pruned)

**Dependency Analysis:**
```python
# The engine automatically determines:
Customer.balance depends on → Order.amount_total (where unshipped)
Order.amount_total depends on → Item.amount  
Item.amount depends on → Item.quantity, Item.unit_price
Item.unit_price depends on → Product.unit_price (or AI supplier selection)

# Changes cascade efficiently through this dependency chain
# Irrelevant changes are pruned before any processing occurs
```

### **Real-World Performance Impact**

**Case Study Metrics:**
- **Before**: 4-minute transaction processing complex order changes
- **After**: 2-second transaction processing (120X improvement)
- **Scalability**: Performance independent of database size
- **Concurrency**: Multiple users can modify data simultaneously without aggregate query conflicts

**Why Traditional Approaches Fail at Scale:**
1. **Aggregate Query Bottlenecks**: Each rule execution triggers expensive database operations
2. **Lock Contention**: Multiple transactions recalculating same aggregates create deadlocks
3. **Linear Degradation**: Performance worsens proportionally with data growth
4. **Resource Exhaustion**: Database CPU and I/O overwhelmed by unnecessary calculations

### **AI Integration Performance Benefits**

The adjustment pattern amplifies AI integration advantages:

**Intelligent AI Invocation:**
```python
# AI called only when supplier selection actually needed
def ItemUnitPriceFromSupplier(row: models.Item, old_row, logic_row):
    if row.product.count_suppliers == 0:
        return row.product.unit_price  # No AI call needed
    # AI service called only for products with multiple suppliers
```

**Cached AI Decision Adjustments:**
- AI decisions stored in `SysSupplierReq` for reuse
- Price changes adjusted incrementally when supplier rates change
- Complex AI-driven business rules become practical at enterprise scale

### **Architectural Advantages**

**1. Scalability Transformation**
- Traditional: O(n) complexity limits real-time processing
- LogicBank: O(1) adjustments enable real-time enterprise applications

**2. Database Efficiency**  
- Eliminates expensive aggregate queries
- Reduces database I/O by orders of magnitude
- Minimizes lock contention and deadlock scenarios

**3. Concurrent Processing**
- Multiple users can modify related data simultaneously
- No aggregate query bottlenecks
- Natural support for high-throughput scenarios

**4. Predictable Performance**
- Performance independent of data volume
- Consistent response times under load
- Reliable basis for SLA commitments

*This adjustment pattern represents the missing piece that makes declarative business logic practical for enterprise-scale applications - combining the expressiveness of rule-based systems with the performance characteristics required for production deployment.*

#### **Probabilistic Rules** (Integration Architecture)

**Current Implementation** (`choose_supplier_for_item_with_ai`):
```python
def choose_supplier_for_item_with_ai(row: models.SysSupplierReq, old_row, logic_row):
    """
    Probabilistic rule: AI-driven supplier selection
    Seamlessly integrated with DR execution flow
    """
    if logic_row.is_inserted():
        # Triggered when Item needs supplier selection
        # Current: Simple first-candidate selection (deterministic fallback)
        for each_supplier in row.product.ProductSupplierList:
            if row.chosen_supplier is None:
                row.chosen_supplier_id = each_supplier.supplier_id
                row.chosen_unit_price = each_supplier.unit_cost
                break
                
        # TODO: Replace with AI service call:
        # - Input: Product specs, supplier history, market conditions
        # - Processing: ML model with multi-criteria optimization
        # - Output: chosen_supplier_id, confidence_score, reasoning
        
Rule.early_row_event(models.SysSupplierReq, calling=choose_supplier_for_item_with_ai)
```

**Integration Trigger** (`ItemUnitPriceFromSupplier`):
```python
def ItemUnitPriceFromSupplier(row: models.Item, old_row, logic_row):
    """
    DR-to-PR Bridge: When Item needs unit_price, potentially invoke AI
    """
    if row.product.count_suppliers == 0:
        return row.product.unit_price  # Fallback to deterministic
    
    # Create SysSupplierReq → triggers AI supplier selection
    sys_supplier_req = logic_row.new_logic_row(models.SysSupplierReq)
    sys_supplier_req.row.product_id = row.product_id
    sys_supplier_req.row.item_id = row.id
    sys_supplier_req.insert()  # Triggers choose_supplier_for_item_with_ai
    
    return sys_supplier_req.row.chosen_unit_price  # AI result feeds back to DR

Rule.formula(derive=models.Item.unit_price, calling=ItemUnitPriceFromSupplier)
```

**The "Missing Half of GenAI"**: This architecture addresses the critical business logic layer that pure GenAI often overlooks - the reliable, auditable, and performant execution of business rules that integrate AI decisions into operational workflows.

## 🛡️ **AI Safety Guardrails: When DRs Protect Against PR Decisions**

### **The Critical Challenge**

AI systems can make optimal decisions within their training parameters, but they may not understand broader business constraints. **Deterministic Rules provide automatic safety nets** that protect against AI decisions that might violate fundamental business requirements.

### **Real-World Example: Credit Limit Protection**

**Scenario**: AI chooses premium supplier for better quality, but at higher cost.

**The AI Decision (PR)**:
```python
def choose_supplier_for_item_with_ai(row: models.SysSupplierReq, old_row, logic_row):
    # AI optimizes for quality and delivery speed
    chosen_supplier = ai_service.optimize_supplier_selection(
        product=row.product,
        criteria={"priority": "quality", "urgency": "high", "cost": "secondary"}
    )
    row.chosen_supplier_id = chosen_supplier.id
    row.chosen_unit_price = chosen_supplier.premium_price  # AI chose expensive option
    logic_row.log(f"AI selected premium supplier {chosen_supplier.name} at ${chosen_supplier.premium_price}")
```

**The Safety Net (DR)**:
```python
# Existing business rule automatically provides protection
Rule.constraint(validate=models.Customer,
               as_condition=lambda row: row.balance <= row.credit_limit,
               error_msg="Order would exceed customer credit limit - consider different supplier")
```

**What Happens Automatically**:
1. **AI Decision**: Selects premium supplier (higher cost, better service)
2. **Cascade Calculation**: Item price ↑ → Item amount ↑ → Order total ↑ → Customer balance ↑
3. **Safety Check**: Credit limit constraint automatically validates the result
4. **Protection**: If AI choice causes credit violation, transaction fails with business-friendly error
5. **Feedback Loop**: System can retry with cost-conscious AI parameters

### **The Beauty of Automatic Protection**

**No Additional Safety Code Required**:
- Existing DRs automatically validate AI decisions
- Business constraints apply regardless of decision source (human or AI)
- Same safety net protects against both user errors and AI mistakes
- Consistent error handling and user experience

**Smart Error Recovery**:
```python
def choose_supplier_with_fallback(row: models.SysSupplierReq, old_row, logic_row):
    try:
        # First attempt: AI optimizes for quality
        ai_choice = ai_service.optimize_supplier(criteria={"priority": "quality"})
        row.chosen_supplier_id = ai_choice.id
        row.chosen_unit_price = ai_choice.price
    except CreditLimitException:
        # Automatic fallback: AI optimizes for cost
        logic_row.log("Premium choice exceeds credit limit, optimizing for cost")
        cost_choice = ai_service.optimize_supplier(criteria={"priority": "cost"})
        row.chosen_supplier_id = cost_choice.id
        row.chosen_unit_price = cost_choice.price
```

### **Additional Guardrail Examples**

#### **Inventory Capacity Protection**
```python
# PR: AI forecasts demand and optimizes order quantities
# DR: Automatically ensures warehouse capacity isn't exceeded
Rule.constraint(validate=models.Warehouse,
               as_condition=lambda row: row.total_inventory <= row.max_capacity,
               error_msg="AI order recommendation exceeds warehouse capacity")
```

#### **Pricing Boundary Enforcement**
```python
# PR: AI sets dynamic pricing based on market conditions
# DR: Automatically enforces business-acceptable price ranges
Rule.constraint(validate=models.Item,
               as_condition=lambda row: (row.unit_price >= row.product.min_price and 
                                       row.unit_price <= row.product.max_price),
               error_msg="AI pricing outside acceptable business range")
```

#### **Supplier Relationship Protection**
```python
# PR: AI might select new supplier for optimal terms
# DR: Automatically enforces minimum order commitments to preferred partners
Rule.constraint(validate=models.Order,
               as_condition=lambda row: validate_supplier_commitments(row),
               error_msg="Order allocation violates preferred supplier agreements")
```

### **Enterprise Benefits**

#### **1. Risk Mitigation**
- **Automatic Protection**: Business constraints enforced regardless of decision source
- **Fail-Safe Operation**: AI can't accidentally violate fundamental business rules
- **Consistent Compliance**: Same rules apply to human and AI decisions
- **Clear Error Messages**: Business-friendly explanations when constraints are violated

#### **2. AI Development Safety**
- **Safe Experimentation**: Can test aggressive AI strategies with confidence
- **Gradual Rollout**: DR safety nets enable incremental AI deployment
- **Learning Feedback**: Constraint violations provide training data for AI improvement
- **Fallback Reliability**: System operates safely even with AI service failures

#### **3. Business Confidence**
- **Transparent Protection**: Business users understand how their constraints are preserved
- **Predictable Behavior**: AI operates within well-defined business boundaries
- **Audit Trail**: All constraint checks logged with clear business justification
- **Executive Assurance**: C-level confidence in AI decision-making

### **The Synergy Effect**

**DRs + PRs = Intelligent Bounded Optimization**

- **DRs Define the Playing Field**: Establish non-negotiable business constraints
- **PRs Optimize Within Bounds**: AI finds best solutions within acceptable parameters  
- **Automatic Feedback**: Constraint violations inform AI parameter adjustment
- **Continuous Improvement**: System learns optimal balance between innovation and safety

**This represents the ideal enterprise AI architecture**: AI systems free to optimize and innovate, but operating within automatically enforced business guardrails that ensure every decision remains compliant, safe, and aligned with organizational requirements.

### **Data Model Integration**
- **`SysSupplierReq`**: Audit trail for AI decisions with payload/reasoning
- **`ProductSupplier`**: Supplier options with deterministic data (cost, lead_time)
- **Hybrid workflow**: DRs trigger PRs, PRs inform DRs

### **Benefits of Hybrid DR+PR Integration**

#### **1. Architectural Advantages**
- **Seamless Workflow**: AI decisions triggered automatically by business rule execution
- **Transaction Safety**: PR decisions participate in database transactions with rollback capability
- **Performance Optimization**: AI called only when business rules determine it's needed
- **Fallback Resilience**: DRs provide deterministic behavior when PRs are unavailable

#### **2. Operational Benefits**
- **Complete Auditability**: All AI decisions logged in `SysSupplierReq` with reasoning and payload
- **Explainable AI**: Integration with deterministic context provides clear decision trails
- **Incremental Adoption**: PRs can be added to existing DR systems without disruption
- **Domain Expert Leverage**: Business users can understand and modify DR triggers for PR invocation

#### **3. Enterprise Compliance**
- **Regulatory Requirements**: DRs handle compliance-critical calculations and constraints
- **AI Governance**: PRs operate within guardrails established by deterministic business rules
- **Change Management**: Business rule changes tracked and versioned alongside AI model updates
- **Risk Management**: Deterministic fallbacks ensure system operation during AI service outages

#### **4. Technical Excellence**
- **Code Reduction**: Maintains the 44X advantage of declarative rules while adding AI capabilities
- **Natural Language to Logic**: Business requirements expressed as declarative rules + AI integration points
- **Runtime Optimization**: LogicBank's execution engine optimizes both DR and PR performance
- **Microservice Integration**: PRs can call external AI services while maintaining transactional integrity

## 🚀 **Demo Scenarios & Next Steps**

### **Current Demo Capabilities**
1. **Pure DR Workflow**: Order entry → automatic calculations → credit validation → shipping integration
2. **DR+PR Integration Point**: Item entry → supplier selection trigger → AI decision placeholder → price determination
3. **Complex Change Propagation**: Product changes cascade through multi-table derivations
4. **Event-Driven Integration**: Business rule changes trigger external system notifications

### **Planned PR Enhancements**
- **AI Service Integration**: Replace placeholder with actual ML model for supplier selection
- **Explainability Framework**: Extend `SysSupplierReq` with detailed reasoning and confidence scores
- **Additional PR Use Cases**: Dynamic pricing, inventory optimization, delivery predictions
- **Performance Optimization**: Caching, async processing, and batch AI operations

### **Research Foundation**
This implementation builds on three key insights from declarative business logic research:
1. **44X Code Reduction**: Declarative rules dramatically reduce implementation complexity
2. **Procedural World Integration**: DSL + runtime engine approach enables natural AI integration
3. **Missing Half of GenAI**: Business logic layer is critical for enterprise AI applications

---

## 📝 **Implementation Journal**

### **Phase 1: Data Model Foundation** ✅
1. Added core tables (Supplier, ProductSupplier) using GitHub Copilot assistance
2. Enhanced with SysSupplierReq for AI decision audit trail
3. Updated database schema, admin UI, and DBML documentation
4. Applied Alembic migrations successfully

### **Phase 2: Deterministic Rules Implementation** ✅  
1. Analyzed existing DR use cases (check credit, app integration)
2. Implemented supplier count derivation and unit price logic
3. Created integration points for probabilistic rule invocation
4. Documented 44X code reduction principle in practice

### **Phase 3: Probabilistic Rules Architecture** ✅
1. Designed DR-to-PR trigger mechanism via `ItemUnitPriceFromSupplier`
2. Implemented PR integration point in `choose_supplier_for_item_with_ai`
3. Created audit trail through `SysSupplierReq` model
4. Established fallback patterns for AI service unavailability

### **Phase 4: Conceptual Framework** ✅
1. Researched declarative logic foundations and GenAI integration patterns
2. Documented hybrid DR+PR architecture benefits and use cases  
3. Established demo scenarios showcasing both deterministic and probabilistic capabilities
4. Created foundation for explainable AI integration within business rule context

### **Next: Production Implementation** 🚧
- AI service integration with multi-criteria supplier selection
- Extended explainability and confidence scoring
- Performance testing and optimization strategies