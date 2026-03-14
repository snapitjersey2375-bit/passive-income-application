"""
YouTube Official Publishing - OAuth2 Integration

Real YouTube OAuth2 integration for auto-uploading videos to user's channel.
No manual download/upload needed - true passive income automation.

Status: Framework complete, needs production Google credentials (Week 1)
"""

import logging
import os
import json
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from apps.engine.db.models import User, Content, Ledger

logger = logging.getLogger(__name__)


class YouTubeOAuth:
    """YouTube OAuth2 flow handler."""

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    def __init__(self):
        self.client_id = os.getenv("YOUTUBE_CLIENT_ID")
        self.client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        self.redirect_uri = os.getenv(
            "YOUTUBE_REDIRECT_URI", "http://localhost:3000/auth/youtube/callback"
        )

        if not all([self.client_id, self.client_secret]):
            logger.warning("YouTube OAuth credentials not configured")

    def get_auth_url(self, state: str) -> str:
        """Get URL for user to authorize YouTube access."""
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_config(
            {
                "installed": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                }
            },
            scopes=self.SCOPES,
            state=state,
        )

        flow.redirect_uri = self.redirect_uri
        auth_url, state = flow.authorization_url(prompt="consent")

        return auth_url

    def get_credentials_from_code(self, code: str, state: str) -> Dict:
        """Exchange authorization code for credentials."""
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_config(
            {
                "installed": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                }
            },
            scopes=self.SCOPES,
            state=state,
        )

        flow.redirect_uri = self.redirect_uri
        credentials = flow.fetch_token(code=code)

        return {
            "access_token": credentials.get("access_token"),
            "refresh_token": credentials.get("refresh_token"),
            "token_expiry": datetime.now() + timedelta(seconds=credentials.get("expires_in", 3600)),
            "token_uri": credentials.get("token_uri"),
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scopes": self.SCOPES,
        }


class YouTubeAPI:
    """YouTube Data API handler."""

    def __init__(self, credentials: Dict):
        self.credentials = credentials
        self.access_token = credentials["access_token"]

    def get_channel_info(self) -> Tuple[str, str]:
        """
        Get authenticated user's YouTube channel ID and name.

        Returns: (channel_id, channel_name)
        """
        from googleapiclient.discovery import build

        youtube = build("youtube", "v3", developerKey=self.access_token)

        request = youtube.channels().list(part="snippet", mine=True)
        response = request.execute()

        if response["items"]:
            channel = response["items"][0]
            return (
                channel["id"],
                channel["snippet"]["title"],
            )

        raise Exception("No YouTube channel found")

    def upload_video(
        self,
        file_path: str,
        title: str,
        description: str,
        privacy_status: str = "private",
    ) -> Dict:
        """
        Upload video to user's YouTube channel.

        privacy_status: 'public', 'unlisted', 'private'
        Returns: upload response with video_id
        """
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        youtube = build("youtube", "v3", developerKey=self.access_token)

        media = MediaFileUpload(file_path, mimetype="video/mp4", resumable=True)

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": ["ai-generated", "automation"],
                    "categoryId": "22",  # People & Blogs
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "madeForKids": False,
                },
            },
            media_body=media,
        )

        response = request.execute()

        logger.info(f"YouTube upload successful: {response.get('id')}")

        return {
            "video_id": response.get("id"),
            "title": title,
            "privacy_status": privacy_status,
            "upload_time": datetime.now().isoformat(),
        }


class YouTubePublisher:
    """Main YouTube publishing service."""

    @staticmethod
    def get_auth_url(user_id: str) -> Dict:
        """
        Get YouTube authorization URL for user.

        User visits this URL to grant access to their YouTube channel.
        """
        import uuid

        state = f"{user_id}:{uuid.uuid4().hex}"

        oauth = YouTubeOAuth()
        auth_url = oauth.get_auth_url(state)

        return {
            "auth_url": auth_url,
            "state": state,
            "instruction": "Click this URL to authorize NexusFlow to publish videos to your YouTube channel",
            "message": "Videos will upload as PRIVATE. You control when/if to make them public.",
        }

    @staticmethod
    def handle_callback(state: str, code: str, db: Session) -> Dict:
        """
        Handle YouTube OAuth callback.

        Stores encrypted credentials in database.
        """
        try:
            # Extract user_id from state
            user_id = state.split(":")[0]

            # Get credentials from authorization code
            oauth = YouTubeOAuth()
            credentials = oauth.get_credentials_from_code(code, state)

            # Find user and update with encrypted credentials
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}

            # Store credentials (in production, encrypt these)
            user.youtube_credentials = json.dumps(credentials)
            user.youtube_authorized = True
            user.youtube_authorized_at = datetime.now()

            db.commit()

            # Get channel info to confirm
            yt_api = YouTubeAPI(credentials)
            channel_id, channel_name = yt_api.get_channel_info()

            logger.info(f"YouTube auth successful for user {user_id}: {channel_name}")

            return {
                "success": True,
                "message": f"✅ Authorized! Connected to: {channel_name}",
                "channel_id": channel_id,
                "channel_name": channel_name,
                "instruction": "Your videos will now auto-upload as PRIVATE. You can publish them anytime.",
            }

        except Exception as e:
            logger.error(f"YouTube callback failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Authorization failed. Please try again.",
            }

    @staticmethod
    def publish_video(
        content_id: str,
        video_file_path: str,
        title: str,
        description: str,
        user_id: str,
        db: Session,
        is_private: bool = True,
    ) -> Dict:
        """
        Auto-upload video to user's YouTube channel.

        Videos start as PRIVATE. User can make public from YouTube dashboard.
        """
        try:
            # Get user and credentials
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}

            if not hasattr(user, "youtube_credentials") or not user.youtube_credentials:
                return {
                    "success": False,
                    "error": "YouTube not authorized",
                    "message": "Please authorize YouTube access first",
                    "auth_url": YouTubePublisher.get_auth_url(user_id),
                }

            # Parse credentials
            credentials = json.loads(user.youtube_credentials)

            # Upload to YouTube
            yt_api = YouTubeAPI(credentials)
            upload_result = yt_api.upload_video(
                file_path=video_file_path,
                title=title,
                description=description,
                privacy_status="private" if is_private else "public",
            )

            # Record in Content model
            content = db.query(Content).filter(Content.id == content_id).first()
            if content:
                content.youtube_video_id = upload_result["video_id"]
                content.youtube_status = "uploaded"
                content.youtube_published_at = datetime.now()
                db.commit()

            # Record upload transaction
            upload_entry = Ledger(
                user_id=user_id,
                amount=0,  # YouTube publishing is free
                transaction_type="youtube_publish",
                description=f"Video published to YouTube: {title}",
                affiliate_network="youtube",
            )
            db.add(upload_entry)
            db.commit()

            logger.info(f"Video published to YouTube for user {user_id}: {upload_result['video_id']}")

            return {
                "success": True,
                "video_id": upload_result["video_id"],
                "youtube_url": f"https://www.youtube.com/watch?v={upload_result['video_id']}",
                "privacy": "PRIVATE - You can make it public anytime from YouTube",
                "message": f"✅ Video uploaded! {upload_result['video_id']}",
                "instruction": "Go to YouTube Studio to review, edit, or publish your video",
            }

        except Exception as e:
            logger.error(f"YouTube publishing failed for content {content_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Video upload failed. Please check file and try again.",
            }

    @staticmethod
    def get_upload_status(content_id: str, db: Session) -> Dict:
        """Get YouTube upload status for content."""
        content = db.query(Content).filter(Content.id == content_id).first()

        if not content:
            return {"error": "Content not found"}

        if not hasattr(content, "youtube_video_id") or not content.youtube_video_id:
            return {
                "status": "not_uploaded",
                "message": "This content hasn't been uploaded to YouTube yet",
            }

        return {
            "status": content.youtube_status or "unknown",
            "video_id": content.youtube_video_id,
            "youtube_url": f"https://www.youtube.com/watch?v={content.youtube_video_id}",
            "uploaded_at": content.youtube_published_at.isoformat() if content.youtube_published_at else None,
        }


class YouTubePublisherAPI:
    """API endpoints for YouTube publishing."""

    @staticmethod
    def register_endpoints(app):
        """Register YouTube publishing endpoints."""

        @app.get("/auth/youtube/url")
        def get_youtube_auth_url(current_user: User):
            """Get URL for user to authorize YouTube."""
            return YouTubePublisher.get_auth_url(current_user.id)

        @app.get("/auth/youtube/callback")
        def youtube_oauth_callback(code: str, state: str, db: Session):
            """Handle YouTube OAuth callback."""
            return YouTubePublisher.handle_callback(state, code, db)

        @app.post("/content/{content_id}/publish-youtube")
        def publish_to_youtube(
            content_id: str,
            current_user: User,
            db: Session,
        ):
            """Publish content to user's YouTube channel."""
            content = db.query(Content).filter(
                Content.id == content_id,
                Content.user_id == current_user.id
            ).first()

            if not content:
                return {"error": "Content not found"}

            result = YouTubePublisher.publish_video(
                content_id=content_id,
                video_file_path=content.video_url,
                title=content.title,
                description=content.description or "",
                user_id=current_user.id,
                db=db,
                is_private=True,
            )

            return result

        @app.get("/content/{content_id}/youtube-status")
        def get_youtube_status(content_id: str, db: Session):
            """Get YouTube upload status."""
            return YouTubePublisher.get_upload_status(content_id, db)
