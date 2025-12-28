"""
Notion client for managing dashboards and human-readable state.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from notion_client import Client

logger = logging.getLogger(__name__)


class NotionClient:
    """Client for Notion API operations"""

    def __init__(self):
        self.api_key = os.getenv("NOTION_API_KEY")
        self.workspace_id = os.getenv("NOTION_WORKSPACE_ID")
        self.workspace_name = os.getenv("NOTION_WORKSPACE_NAME", "superonyx")

        if not self.api_key:
            raise ValueError("NOTION_API_KEY not set in environment")

        self.client = Client(auth=self.api_key)
        logger.info(f"Initialized Notion client for {self.workspace_name}")

    def test_connection(self) -> Dict[str, Any]:
        """Test Notion API connection"""
        try:
            # List users to verify connection
            users = self.client.users.list()
            logger.info(f"Connected to Notion workspace: {self.workspace_name}")
            return {
                "connected": True,
                "workspace": self.workspace_name,
                "users_count": len(users.get("results", [])),
            }
        except Exception as e:
            logger.error(f"Failed to connect to Notion: {e}")
            raise

    def search_pages(self, query: str = "") -> list:
        """Search for pages in Notion"""
        try:
            results = self.client.search(query=query)
            return results.get("results", [])
        except Exception as e:
            logger.error(f"Failed to search pages: {e}")
            return []

    def create_bottleneck_page(
        self, parent_page_id: str, agent_id: str, bottleneck: Dict[str, Any]
    ) -> Optional[str]:
        """Create a page for a bottleneck"""
        try:
            page = self.client.pages.create(
                parent={"page_id": parent_page_id},
                properties={
                    "title": {
                        "title": [
                            {
                                "text": {
                                    "content": f"[{agent_id}] {bottleneck['description'][:100]}"
                                }
                            }
                        ]
                    }
                },
                children=[
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": "Bottleneck Details"},
                                }
                            ]
                        },
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": f"Agent: {agent_id}\n"},
                                    "annotations": {"bold": True},
                                },
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Impact Score: {bottleneck['impact_score']}/10\n"
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Confidence: {bottleneck['confidence']:.0%}\n"
                                    },
                                },
                            ]
                        },
                    },
                    {
                        "object": "block",
                        "type": "heading_3",
                        "heading_3": {
                            "rich_text": [
                                {"type": "text", "text": {"content": "Description"}}
                            ]
                        },
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": bottleneck["description"]},
                                }
                            ]
                        },
                    },
                    {
                        "object": "block",
                        "type": "heading_3",
                        "heading_3": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": "Recommended Action"},
                                }
                            ]
                        },
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": bottleneck.get(
                                            "recommended_action", "None specified"
                                        )
                                    },
                                }
                            ]
                        },
                    },
                    {"object": "block", "type": "divider", "divider": {}},
                    {
                        "object": "block",
                        "type": "callout",
                        "callout": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Created by Sentinel on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                                    },
                                }
                            ],
                            "icon": {"emoji": "🤖"},
                        },
                    },
                ],
            )

            logger.info(f"Created Notion page for {agent_id} bottleneck")
            return page["id"]

        except Exception as e:
            logger.error(f"Failed to create Notion page: {e}")
            return None

    def setup_dashboard(self, parent_page_id: str) -> Dict[str, str]:
        """Create the dashboard databases in Notion"""
        try:
            logger.info(f"Setting up dashboard on page {parent_page_id}")

            # 1. Create Agent Daily Reports Database
            reports_db = self._create_database(
                parent_page_id,
                "Agent Daily Reports",
                {
                    "Agent ID": {"title": {}},
                    "Domain": {
                        "select": {
                            "options": [
                                {"name": "Job Search", "color": "blue"},
                                {"name": "Business", "color": "green"},
                                {"name": "Personal", "color": "yellow"},
                            ]
                        }
                    },
                    "Bottleneck": {"rich_text": {}},
                    "Confidence": {"number": {"format": "percent"}},
                    "Impact Score": {"number": {"format": "number"}},
                    "Status": {
                        "select": {
                            "options": [
                                {"name": "Identified", "color": "red"},
                                {"name": "In Progress", "color": "yellow"},
                                {"name": "Resolved", "color": "green"},
                            ]
                        }
                    },
                    "Timestamp": {"date": {}},
                },
            )

            # 2. Create Weekly Priorities Database
            priorities_db = self._create_database(
                parent_page_id,
                "Weekly Priorities",
                {
                    "Week": {"title": {}},
                    "Top Bottleneck": {"rich_text": {}},
                    "Status": {
                        "select": {
                            "options": [
                                {"name": "Planning", "color": "gray"},
                                {"name": "Executing", "color": "blue"},
                                {"name": "Complete", "color": "green"},
                            ]
                        }
                    },
                    "Owner": {"people": {}},
                },
            )

            # 3. Create Decision Log Database
            decisions_db = self._create_database(
                parent_page_id,
                "Decision Log",
                {
                    "Decision": {"title": {}},
                    "Type": {
                        "select": {
                            "options": [
                                {"name": "Diagnosis", "color": "blue"},
                                {"name": "Action", "color": "green"},
                                {"name": "Escalation", "color": "red"},
                            ]
                        }
                    },
                    "Agent": {"rich_text": {}},
                    "Confidence": {"number": {"format": "percent"}},
                    "Outcome": {"rich_text": {}},
                    "Timestamp": {"date": {}},
                },
            )

            return {
                "reports_db": reports_db,
                "priorities_db": priorities_db,
                "decisions_db": decisions_db,
            }

        except Exception as e:
            logger.error(f"Failed to setup dashboard: {e}")
            raise

    def _create_database(
        self, parent_page_id: str, title: str, properties: Dict
    ) -> str:
        """Helper to create a database"""
        try:
            db = self.client.databases.create(
                parent={"page_id": parent_page_id},
                title=[{"type": "text", "text": {"content": title}}],
                properties=properties,
            )
            logger.info(f"Created database: {title}")
            return db["id"]
        except Exception as e:
            logger.error(f"Failed to create database '{title}': {e}")
            raise

    async def create_agent_database(self, agent_name: str) -> str:
        """Create a database for an agent (Deprecated)"""
        logger.warning(
            "create_agent_database is deprecated. Use setup_dashboard instead."
        )
        return ""

    async def write_daily_report(self, agent_id: str, report: Dict[str, Any]) -> None:
        """Write daily agent report to Notion"""
        # TODO: Implement writing to the created database
        logger.info(f"Writing report for {agent_id}")

    async def read_priorities(self) -> Dict[str, Any]:
        """Read current priorities from Notion"""
        # TODO: Implement reading from the created database
        logger.info("Reading priorities from Notion")
        return {}
