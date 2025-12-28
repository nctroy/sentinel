-- Superset Dashboard SQL Queries for Sentinel
-- These queries power the business intelligence dashboards

-- ============================================
-- DASHBOARD 1: Job Search Executive View
-- ============================================

-- Query 1: Application Funnel
-- Shows progression from research to offer across all stages
SELECT
    CASE
        WHEN description ILIKE '%research%' THEN 'Researched'
        WHEN description ILIKE '%appli%' THEN 'Applied'
        WHEN description ILIKE '%interview%' THEN 'Interview'
        WHEN description ILIKE '%offer%' THEN 'Offer'
        ELSE 'Other'
    END as stage,
    COUNT(*) as count,
    AVG(confidence) as avg_confidence,
    AVG(impact_score) as avg_impact
FROM bottlenecks
WHERE agent_id LIKE 'job-%'
    AND identified_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY stage
ORDER BY
    CASE stage
        WHEN 'Researched' THEN 1
        WHEN 'Applied' THEN 2
        WHEN 'Interview' THEN 3
        WHEN 'Offer' THEN 4
        ELSE 5
    END;

-- Query 2: Response Rate Trends
-- Weekly response rates over time
SELECT
    DATE_TRUNC('week', identified_at) as week,
    COUNT(*) as total_applications,
    COUNT(*) FILTER (WHERE description ILIKE '%response%' OR description ILIKE '%reply%') as responses,
    ROUND(100.0 * COUNT(*) FILTER (WHERE description ILIKE '%response%' OR description ILIKE '%reply%') / NULLIF(COUNT(*), 0), 2) as response_rate_pct
FROM bottlenecks
WHERE agent_id LIKE 'job-%'
    AND identified_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY week
ORDER BY week;

-- Query 3: Interview Conversion Rate
-- Conversion from application to interview
SELECT
    DATE_TRUNC('month', identified_at) as month,
    COUNT(*) FILTER (WHERE description ILIKE '%appli%') as applications,
    COUNT(*) FILTER (WHERE description ILIKE '%interview%') as interviews,
    ROUND(100.0 * COUNT(*) FILTER (WHERE description ILIKE '%interview%') / NULLIF(COUNT(*) FILTER (WHERE description ILIKE '%appli%'), 0), 2) as conversion_rate_pct
FROM bottlenecks
WHERE agent_id LIKE 'job-%'
    AND identified_at >= CURRENT_DATE - INTERVAL '180 days'
GROUP BY month
ORDER BY month;

-- Query 4: Weekly Application Velocity
-- Applications submitted per week
SELECT
    DATE_TRUNC('week', identified_at) as week,
    COUNT(*) as applications_submitted,
    AVG(confidence) as avg_confidence,
    AVG(impact_score) as avg_impact_score
FROM bottlenecks
WHERE agent_id LIKE 'job-%'
    AND description ILIKE '%appli%'
    AND identified_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY week
ORDER BY week;

-- ============================================
-- DASHBOARD 2: 30-in-30 Challenge Tracker
-- ============================================

-- Query 5: Projects Launched vs Target
-- Track progress toward 30 projects in 30 days
SELECT
    COUNT(DISTINCT agent_id) as projects_launched,
    30 as target_projects,
    ROUND(100.0 * COUNT(DISTINCT agent_id) / 30, 2) as completion_pct,
    DATE_TRUNC('day', MIN(identified_at)) as challenge_start_date,
    CURRENT_DATE as current_date,
    EXTRACT(DAY FROM CURRENT_DATE - DATE_TRUNC('day', MIN(identified_at))) as days_elapsed
FROM bottlenecks
WHERE identified_at >= CURRENT_DATE - INTERVAL '30 days';

-- Query 6: Daily Progress Heatmap Data
-- Daily activity levels for heatmap visualization
SELECT
    DATE(identified_at) as date,
    COUNT(*) as bottlenecks_identified,
    COUNT(DISTINCT agent_id) as agents_active,
    AVG(impact_score) as avg_impact
FROM bottlenecks
WHERE identified_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(identified_at)
ORDER BY date;

-- Query 7: Success/Failure Ratio
-- Track resolution success rate
SELECT
    status,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
FROM bottlenecks
WHERE identified_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY status;

-- ============================================
-- DASHBOARD 3: Multi-Business Portfolio
-- ============================================

-- Query 8: Time Allocation Across Domains
-- How time is distributed across different business domains
SELECT
    CASE
        WHEN agent_id LIKE 'job-%' THEN 'Job Search'
        WHEN agent_id LIKE '%research%' THEN 'AI Research'
        WHEN agent_id LIKE '%github%' THEN 'Development'
        ELSE 'Other'
    END as domain,
    COUNT(*) as activities,
    AVG(impact_score) as avg_impact,
    AVG(confidence) as avg_confidence
FROM bottlenecks
WHERE identified_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY domain
ORDER BY activities DESC;

-- Query 9: Domain Performance Metrics
-- Performance metrics by business domain
SELECT
    CASE
        WHEN agent_id LIKE 'job-%' THEN 'Job Search'
        WHEN agent_id LIKE '%research%' THEN 'AI Research'
        WHEN agent_id LIKE '%github%' THEN 'Development'
        ELSE 'Other'
    END as domain,
    COUNT(*) as total_bottlenecks,
    COUNT(*) FILTER (WHERE status = 'resolved') as resolved,
    COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
    COUNT(*) FILTER (WHERE status = 'pending') as pending,
    AVG(impact_score) as avg_impact_score
FROM bottlenecks
WHERE identified_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY domain
ORDER BY total_bottlenecks DESC;

-- ============================================
-- DASHBOARD 4: Sentinel System Health
-- ============================================

-- Query 10: Agent Productivity Score
-- Measures agent effectiveness and activity
SELECT
    agent_id,
    COUNT(DISTINCT DATE(identified_at)) as active_days,
    COUNT(*) as bottlenecks_found,
    AVG(impact_score) as avg_impact,
    AVG(confidence) as avg_confidence,
    COUNT(*) FILTER (WHERE status = 'resolved') as resolved_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'resolved') / NULLIF(COUNT(*), 0), 2) as resolution_rate_pct
FROM bottlenecks
WHERE identified_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY agent_id
ORDER BY bottlenecks_found DESC;

-- Query 11: Bottlenecks Resolved vs Identified
-- System effectiveness tracking
SELECT
    DATE_TRUNC('week', identified_at) as week,
    COUNT(*) as identified,
    COUNT(*) FILTER (WHERE status = 'resolved') as resolved,
    COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
    COUNT(*) FILTER (WHERE status = 'pending') as pending
FROM bottlenecks
WHERE identified_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY week
ORDER BY week;

-- Query 12: System Uptime and Reliability
-- Agent execution reliability metrics
SELECT
    agent_id,
    COUNT(*) as total_executions,
    COUNT(*) FILTER (WHERE confidence > 0) as successful_executions,
    ROUND(100.0 * COUNT(*) FILTER (WHERE confidence > 0) / NULLIF(COUNT(*), 0), 2) as success_rate_pct,
    MAX(identified_at) as last_execution,
    EXTRACT(HOUR FROM NOW() - MAX(identified_at)) as hours_since_last_run
FROM bottlenecks
WHERE identified_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY agent_id
ORDER BY last_execution DESC;

-- Query 13: High Impact Bottlenecks
-- Critical issues requiring attention
SELECT
    agent_id,
    description,
    impact_score,
    confidence,
    status,
    identified_at,
    EXTRACT(DAY FROM NOW() - identified_at) as days_old
FROM bottlenecks
WHERE impact_score >= 8.0
    AND status != 'resolved'
    AND identified_at >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY impact_score DESC, identified_at ASC
LIMIT 20;

-- Query 14: Agent Activity Timeline
-- Recent agent execution history
SELECT
    agent_id,
    DATE(identified_at) as date,
    COUNT(*) as executions,
    AVG(confidence) as avg_confidence,
    AVG(impact_score) as avg_impact,
    STRING_AGG(DISTINCT status, ', ') as statuses
FROM bottlenecks
WHERE identified_at >= CURRENT_DATE - INTERVAL '14 days'
GROUP BY agent_id, DATE(identified_at)
ORDER BY date DESC, agent_id;
