# ADR-003: Graduated Autonomy Model

**Status:** Accepted
**Date:** 2025-12-27
**Decision Makers:** Troy Shields (Chief Architect)
**Tags:** ai-safety, autonomy, agent-architecture, trust

---

## Context

Sentinel is a multi-agent AI system that makes decisions affecting real-world outcomes (job applications, GitHub triage, research prioritization). Giving AI agents unfettered autonomy poses significant risks:

**Safety Concerns:**
- **Incorrect Actions** - AI makes mistakes, misinterprets context
- **Cascading Failures** - One bad decision triggers downstream problems
- **Trust Calibration** - Users need time to build confidence in AI decisions
- **Accountability** - Clear human oversight required for critical actions

**Operational Reality:**
- Some tasks are safe to automate fully (data analysis, reporting)
- Other tasks require human judgment (sending emails, financial decisions)
- User trust grows gradually through demonstrated reliability

**Key Challenge:** Balance automation efficiency with safety and user trust.

## Decision

Implement a **three-tier Graduated Autonomy Model** that progressively increases agent independence based on task criticality and proven reliability.

### Autonomy Tiers

```
┌─────────────────────────────────────────────────────────┐
│  TIER 3: FULL AUTONOMY                                  │
│  Agent executes immediately without approval            │
│  ✓ Read-only operations                                 │
│  ✓ Analysis and reporting                               │
│  ✓ Data aggregation                                     │
│  ✓ Notification generation                              │
└─────────────────────────────────────────────────────────┘
                        ↑
                   Proven Trust
                        ↑
┌─────────────────────────────────────────────────────────┐
│  TIER 2: CONDITIONAL AUTONOMY                           │
│  Agent executes with confirmation for specific actions  │
│  ✓ Low-risk write operations                            │
│  ✓ Internal system updates                              │
│  ✓ Draft generation (requires review)                   │
│  ⚠ Threshold-based approval (impact score < 7.0)        │
└─────────────────────────────────────────────────────────┘
                        ↑
                  Building Trust
                        ↑
┌─────────────────────────────────────────────────────────┐
│  TIER 1: DIAGNOSTIC MODE (Current Implementation)       │
│  Agent identifies issues, recommends actions, no exec   │
│  ✓ Bottleneck identification                            │
│  ✓ Recommendation generation                            │
│  ✓ Priority ranking                                     │
│  ✗ No automatic execution                               │
└─────────────────────────────────────────────────────────┘
```

### Implementation Strategy

**Phase 1: Diagnostic Mode (Current)**
- All agents operate in read-only mode
- Output: Identified bottlenecks + recommended actions
- Human reviews and executes all actions
- Build confidence through accuracy metrics

**Phase 2: Conditional Autonomy (Future)**
- Enable execution for low-impact actions
- Require confirmation for high-impact actions (impact_score >= 7.0)
- Track success/failure rates
- Gradually adjust thresholds based on performance

**Phase 3: Full Autonomy (Future)**
- Proven agents execute without confirmation
- Real-time monitoring with circuit breakers
- Automatic rollback on anomaly detection
- Human override always available

### Tier Classification Logic

```python
class AutonomyTier(Enum):
    DIAGNOSTIC = 1      # Recommend only
    CONDITIONAL = 2     # Execute with approval
    FULL = 3           # Execute immediately

class AgentAutonomyManager:
    def determine_tier(self, agent_id: str, action: Action) -> AutonomyTier:
        """Determine autonomy tier for a given action."""

        # Check agent trust score (historical accuracy)
        agent_score = self.get_agent_trust_score(agent_id)

        # Check action risk level
        risk_level = self.assess_action_risk(action)

        # Tier decision matrix
        if risk_level == RiskLevel.NONE:
            return AutonomyTier.FULL  # Safe operations

        if agent_score >= 0.9 and risk_level == RiskLevel.LOW:
            return AutonomyTier.CONDITIONAL  # Trusted agent, low risk

        return AutonomyTier.DIAGNOSTIC  # Default to safest tier
```

## Rationale

### Why Graduated (Not Binary)?

**Binary Autonomy Problems:**
- ❌ All-or-nothing doesn't reflect task nuances
- ❌ No path to earn increased autonomy
- ❌ Can't differentiate agent reliability

**Graduated Benefits:**
- ✅ Progressive trust building
- ✅ Task-specific autonomy levels
- ✅ Risk-proportional oversight
- ✅ Clear upgrade path

### Why Three Tiers (Not More)?

**Too Few Tiers (2):**
- Insufficient granularity
- Jump from "no autonomy" to "full autonomy" too risky

**Too Many Tiers (4+):**
- Overcomplicated for users
- Unclear tier boundaries
- Hard to explain and manage

**Three Tiers:**
- Simple mental model: Recommend → Confirm → Execute
- Clear progression path
- Enough flexibility without complexity

### Trust Calibration Mechanism

Agents earn higher autonomy through:

1. **Accuracy Metrics**
   - Confidence vs. actual outcomes
   - False positive/negative rates
   - User feedback on recommendations

2. **Impact Score Validation**
   - Did predicted impact match reality?
   - Were blocking dependencies accurate?
   - How often were recommendations accepted?

3. **Time-Based Progression**
   - Minimum observation period (e.g., 30 days)
   - Sustained performance required
   - Regression triggers tier demotion

**Example Metrics:**
```python
class AgentTrustScore:
    accuracy_rate: float        # 0.0-1.0 (95% = 0.95)
    recommendation_acceptance: float  # % of recommendations user accepted
    false_positive_rate: float   # How often flagged non-issues
    execution_success_rate: float # When executing, success rate
    days_active: int            # Observation period

    def calculate_trust_score(self) -> float:
        """Weighted composite score."""
        return (
            0.4 * self.accuracy_rate +
            0.3 * self.recommendation_acceptance +
            0.2 * self.execution_success_rate +
            0.1 * min(self.days_active / 30, 1.0)
        )
```

## Consequences

### Positive

✅ **Safety First** - Start conservative, prove before trusting
✅ **User Control** - Maintains human oversight for critical actions
✅ **Gradual Adoption** - Users build confidence incrementally
✅ **Performance Tracking** - Quantifiable metrics for promotion
✅ **Flexibility** - Different tasks have different autonomy levels
✅ **Rollback Safety** - Easy to demote underperforming agents

### Negative

⚠️ **Implementation Complexity** - Requires robust action classification
⚠️ **Delayed Value** - Full automation benefits take time to realize
⚠️ **Metrics Dependency** - Requires accurate performance measurement
⚠️ **Edge Cases** - Some actions hard to classify by risk level

### Risks and Mitigations

**Risk: Agents stuck in Tier 1 indefinitely**
- Mitigation: Clear upgrade criteria, automated promotion when thresholds met

**Risk: User bypasses system, executes blindly**
- Mitigation: UI design encourages review, easy "approve all from this agent" option

**Risk: Malicious agent gaming metrics**
- Mitigation: Multiple independent metrics, human spot-checks, anomaly detection

## Implementation Notes

### Current State (Diagnostic Mode)

All agents currently operate in **Tier 1 (Diagnostic Mode)**:

```python
# src/agents/base_agent.py
async def diagnose(self) -> Dict[str, Any]:
    """Identify bottleneck and recommend action (Tier 1)."""
    bottleneck = await self._identify_bottleneck()

    # Log decision for audit trail
    self.log_decision(
        decision_type="bottleneck_identified",
        decision_data=bottleneck,
        reasoning=bottleneck.get("reasoning")
    )

    # Return recommendation (NO EXECUTION)
    return bottleneck
```

### Future: Conditional Execution (Tier 2)

```python
async def execute_conditional(self, action: Action) -> ExecutionResult:
    """Execute action with approval for high-impact items (Tier 2)."""

    # Assess action risk
    if action.impact_score >= 7.0:
        # High impact - require approval
        approval = await self.request_approval(action)
        if not approval.granted:
            return ExecutionResult(status="rejected", reason=approval.reason)

    # Low impact or approved - execute
    result = await self._execute_action(action)

    # Log execution
    self.log_decision(
        decision_type="action_executed",
        decision_data={"action": action, "result": result}
    )

    return result
```

### Future: Full Autonomy (Tier 3)

```python
async def execute_autonomous(self, action: Action) -> ExecutionResult:
    """Execute action immediately (Tier 3)."""

    # Circuit breaker check
    if self.circuit_breaker.is_open():
        return ExecutionResult(status="circuit_open", reason="Too many recent failures")

    # Execute
    result = await self._execute_action(action)

    # Monitor for anomalies
    if self.anomaly_detector.is_anomalous(result):
        await self.trigger_alert(result)
        await self.rollback_action(action)

    return result
```

## Safety Guardrails

### Circuit Breakers
- Automatically disable agent after N consecutive failures
- Requires manual re-enable after investigation
- Prevents cascading failures

### Rollback Mechanisms
- All actions must be reversible or have compensating transactions
- Automatic rollback on detected anomalies
- Manual rollback available via UI

### Monitoring and Alerts
- Real-time execution monitoring
- Alert on unexpected outcomes
- Daily summary of autonomous actions

### Kill Switch
- Global disable for all autonomous execution
- Per-agent disable
- Emergency stop button in UI

## Future Enhancements

1. **Dynamic Tier Adjustment**
   - Real-time tier changes based on performance
   - Temporary tier elevation for urgent actions
   - Automatic demotion after errors

2. **User-Specific Trust Levels**
   - Power users can grant higher autonomy
   - New users start with conservative settings
   - Per-user agent preferences

3. **Action-Specific Policies**
   - Whitelist/blacklist specific action types
   - Custom approval workflows
   - Integration with corporate approval systems

4. **Explainable AI Dashboard**
   - Show why agent was promoted/demoted
   - Visualization of trust score trends
   - Audit log of autonomous actions

## References

- AI Safety: https://www.safe.ai/
- Autonomous Systems: https://arxiv.org/abs/2108.07258
- Human-in-the-Loop: https://hai.stanford.edu/

---

**Supersedes:** None
**Superseded By:** None
**Related:** ADR-004 (Agent Communication Protocol), ADR-006 (Security Architecture)
