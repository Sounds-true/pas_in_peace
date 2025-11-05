"""Telegraph API client for letter editing."""

from typing import Dict, Any, Optional
import uuid
import secrets
import re

try:
    from telegraph import Telegraph
    TELEGRAPH_AVAILABLE = True
except ImportError:
    TELEGRAPH_AVAILABLE = False

from src.core.logger import get_logger


logger = get_logger(__name__)


class TelegraphClient:
    """
    Telegraph integration for beautiful letter editing.

    Features:
    - Create rich-text articles
    - Generate hard-to-guess URLs for privacy
    - Update existing articles
    - Track versions
    """

    def __init__(self, author_name: str = "PAS Bot"):
        """Initialize Telegraph client."""
        self.telegraph = None
        self.access_token = None
        self.author_name = author_name
        self.initialized = False

    async def initialize(self) -> bool:
        """Initialize Telegraph account."""
        if self.initialized:
            return True

        if not TELEGRAPH_AVAILABLE:
            logger.warning("telegraph_not_available",
                          message="Install: pip install telegraph")
            return False

        try:
            self.telegraph = Telegraph()

            # Create account for bot
            response = self.telegraph.create_account(
                short_name=self.author_name,
                author_name=self.author_name,
                author_url='https://t.me/pas_support_bot'  # TODO: Real bot URL
            )

            self.access_token = response['access_token']
            self.telegraph.access_token = self.access_token

            self.initialized = True
            logger.info("telegraph_initialized", author=self.author_name)
            return True

        except Exception as e:
            logger.error("telegraph_init_failed", error=str(e))
            return False

    def generate_secure_path(self) -> str:
        """
        Generate hard-to-guess Telegraph path.

        Returns:
            Path like: l-a8f3d92b4c1e7f5a-f8e4a1c3b7d9
        """
        # UUID4 = 128 bit randomness
        random_uuid = uuid.uuid4().hex[:16]

        # Additional random token
        random_token = secrets.token_hex(8)

        return f"l-{random_uuid}-{random_token}"

    async def create_letter(
        self,
        title: str,
        content: str,
        author_name: str = "Анонимный автор"
    ) -> Dict[str, str]:
        """
        Create Telegraph article for letter.

        Args:
            title: Letter title
            content: Letter content (plain text)
            author_name: Author display name

        Returns:
            {
                "url": "https://telegra.ph/...",
                "path": "l-...",
                "access_token": "..."
            }
        """
        if not self.initialized:
            await self.initialize()

        if not self.telegraph:
            raise RuntimeError("Telegraph not initialized")

        try:
            # Convert plain text to Telegraph HTML
            html_content = self._format_content(content)

            # Use pre-generated secure path (custom path not supported by library)
            # So we rely on Telegraph's random paths
            response = self.telegraph.create_page(
                title=title,
                author_name=author_name,
                html_content=html_content
            )

            logger.info("telegraph_letter_created",
                       url=response['url'],
                       path=response['path'])

            return {
                "url": response['url'],
                "path": response['path'],
                "access_token": self.access_token
            }

        except Exception as e:
            logger.error("telegraph_create_failed", error=str(e))
            raise

    async def update_letter(
        self,
        path: str,
        title: str,
        content: str
    ) -> str:
        """
        Update existing Telegraph article.

        Args:
            path: Telegraph path
            title: New title
            content: New content

        Returns:
            Updated URL
        """
        if not self.telegraph:
            raise RuntimeError("Telegraph not initialized")

        try:
            html_content = self._format_content(content)

            response = self.telegraph.edit_page(
                path=path,
                title=title,
                html_content=html_content
            )

            logger.info("telegraph_letter_updated", path=path)
            return response['url']

        except Exception as e:
            logger.error("telegraph_update_failed", path=path, error=str(e))
            raise

    async def get_letter(self, path: str) -> Dict[str, Any]:
        """
        Get Telegraph article content.

        Args:
            path: Telegraph path

        Returns:
            {
                "title": "...",
                "content": "...",  # Plain text
                "views": 123
            }
        """
        if not self.telegraph:
            raise RuntimeError("Telegraph not initialized")

        try:
            page = self.telegraph.get_page(path, return_content=True)

            content = self._extract_text(page.get('content', []))

            return {
                "title": page.get('title', ''),
                "content": content,
                "views": page.get('views', 0)
            }

        except Exception as e:
            logger.error("telegraph_get_failed", path=path, error=str(e))
            raise

    async def delete_letter(self, path: str) -> bool:
        """
        'Delete' letter by replacing content.

        Note: Telegraph API doesn't support deletion,
        so we replace content with "Deleted" message.

        Args:
            path: Telegraph path

        Returns:
            True if successful
        """
        try:
            self.telegraph.edit_page(
                path=path,
                title="Письмо удалено",
                html_content="<p>Это письмо было удалено автором.</p>"
            )

            logger.info("telegraph_letter_deleted", path=path)
            return True

        except Exception as e:
            logger.error("telegraph_delete_failed", path=path, error=str(e))
            return False

    def _format_content(self, text: str) -> str:
        """
        Convert plain text to Telegraph HTML.

        Supports:
        - Paragraphs
        - Bold (**text**)
        - Italic (*text*)
        - Line breaks
        """
        # Split into paragraphs
        paragraphs = text.split('\n\n')

        html_parts = []
        for para in paragraphs:
            if not para.strip():
                continue

            # Replace bold **text**
            para = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', para)

            # Replace italic *text*
            para = re.sub(r'\*(.+?)\*', r'<em>\1</em>', para)

            # Replace line breaks
            para = para.replace('\n', '<br>')

            html_parts.append(f'<p>{para}</p>')

        return ''.join(html_parts)

    def _extract_text(self, content: list) -> str:
        """
        Extract plain text from Telegraph JSON content.

        Telegraph content is a list of nodes like:
        [
            {'tag': 'p', 'children': ['text']},
            {'tag': 'p', 'children': [{'tag': 'strong', 'children': ['bold']}]}
        ]
        """
        def extract_node(node):
            if isinstance(node, str):
                return node
            elif isinstance(node, dict):
                children = node.get('children', [])
                return ''.join(extract_node(child) for child in children)
            elif isinstance(node, list):
                return ''.join(extract_node(item) for item in node)
            return ''

        text_parts = []
        for node in content:
            text = extract_node(node)
            if text:
                text_parts.append(text)

        return '\n\n'.join(text_parts)

    def is_available(self) -> bool:
        """Check if Telegraph is available."""
        return TELEGRAPH_AVAILABLE
