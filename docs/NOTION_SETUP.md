# Notion Integration Setup

> [!CAUTION]
> **DEPRECATED:** As of December 2025, the Notion Integration has been deprecated in favor of the **Sentinel Command Center (Next.js Dashboard)**.
> This documentation is kept for historical traceability. The Notion integration requires a paid workspace for custom integrations, whereas the new GUI runs locally and provides real-time control.

## Overview
...

## Step 1: Create Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Fill in:
   - **Name**: Sentinel
   - **Logo**: (optional) Upload an icon
   - **Description**: Multi-agent orchestration dashboard
4. Under **Capabilities**, select:
   - ✅ Read content
   - ✅ Update content
   - ✅ Insert content
5. Click "Submit"

## Step 2: Get Your API Key

1. You'll see "Internal Integration Token" section
2. Click "Show" to reveal the token
3. **Copy the token** — this is your `NOTION_API_KEY`
4. Add it to `.env`:

```bash
NOTION_API_KEY=ntn_xxxxxxxxxxxxxxxxxxxxx
```

## Step 3: Share Your Workspace

1. In your Notion workspace, click the **share icon** (top right)
2. Click "Invite"
3. Search for "Sentinel" (the integration you created)
4. Click it to add
5. Grant **Edit** permissions

## Step 4: Get Your Workspace ID

Your workspace ID is already configured:

```bash
NOTION_WORKSPACE_ID=38d5edab-553a-4fe3-9a5a-fe188a4c210c
NOTION_WORKSPACE_NAME=superonyx
```

These are already set in `.env`.

## Step 5: Create Dashboard Database

Sentinel will automatically create the following databases in your Notion workspace:

### Agent Daily Reports Database
- **Fields:**
  - Agent ID (Title)
  - Domain (Select)
  - Bottleneck Description (Rich Text)
  - Confidence (Number)
  - Impact Score (Number)
  - Status (Select: Identified, In Progress, Resolved)
  - Timestamp (Date)

### Weekly Priorities Database
- **Fields:**
  - Week (Title)
  - Top Bottleneck (Rich Text)
  - Priority Ranking (Relation to Agent Reports)
  - Resource Allocation (JSON)
  - Status (Select: Planning, Executing, Complete)

### Decisions Database
- **Fields:**
  - Decision (Title)
  - Agent (Select)
  - Type (Select: Diagnosis, Execution, Escalation)
  - Confidence (Number)
  - Outcome (Rich Text)
  - Timestamp (Date)

## Step 6: Verify Connection

```bash
# Test Notion connection
python -c "from src.storage.notion_client import NotionClient; n = NotionClient(); print('✓ Notion connected')"
```

## Manual Dashboard Setup (Optional)

If you prefer manual setup, create these databases in Notion:

### 1. Agent Status Dashboard (Database)

**Template:**
- Agent Name (Title)
- Domain (Select: Job Search, AI Business, Photography, Personal Dev)
- Current Bottleneck (Rich Text)
- Confidence (%) (Number)
- Impact Score (Number)
- Last Updated (Date)
- Status (Select: Healthy, At Risk, Critical)

### 2. Weekly Priorities (Database)

**Template:**
- Week (Title, e.g. "Week of Dec 25")
- Top Bottleneck (Rich Text)
- Impact Score (Number)
- Assigned Domain (Relation to Agent Status)
- Action Items (Checkbox list)
- Status (Select: Planning, In Progress, Complete)
- Owner (Person)

### 3. Decision Log (Database)

**Template:**
- Decision (Title)
- Type (Select: Diagnosis, Action, Escalation)
- Agent (Relation to Agent Status)
- Reasoning (Rich Text)
- Confidence (Number %)
- Outcome (Rich Text)
- Date Made (Date)

## Testing the Integration

```bash
# Run a diagnostic cycle
python -m src.cli.cli run-cycle --mode diagnostic --verbose

# Check Notion — your workspace should now have:
# - Agent Daily Reports
# - Weekly Priorities
# - Decision Log

# All populated with today's data
```

## Troubleshooting

### "Invalid API Key"

1. Verify your integration still exists at https://www.notion.so/my-integrations
2. Copy the token again (it may have expired)
3. Update `.env` and test again

### "Workspace not shared"

1. Ensure the Sentinel integration has **Edit** permission
2. Workspace owner must approve integration
3. Try removing and re-adding the integration

### "Database not found"

1. Sentinel attempts to create databases automatically
2. If it fails, create them manually (instructions above)
3. Update `.env` with database IDs if needed

## Next Steps

1. ✅ Integration created and API key stored
2. ✅ Workspace shared with integration
3. ✅ Run first diagnostic cycle
4. ✅ View results in Notion dashboard
5. ✅ Customize databases as needed

## Resources

- [Notion API Documentation](https://developers.notion.com)
- [Notion SDK for Python](https://github.com/ramnes/notion-sdk-py)
- [API Reference](https://developers.notion.com/reference)
