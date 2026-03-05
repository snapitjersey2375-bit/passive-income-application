from .base import BaseAgent
from typing import Dict, Any
import os
import uuid

class VideoGenAgent(BaseAgent):
    """
    Agent responsible for creating HTML5 'Video' files (animations).
    Since ffmpeg is not available, we generate standalone HTML files 
    that play CSS animations with the content.
    """
    def __init__(self):
        super().__init__(name="VideoGenAgent")
        self.output_dir = "apps/web/public/generated_videos"
        os.makedirs(self.output_dir, exist_ok=True)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates an HTML file that acts as the video.
        """
        title = context.get("title", "Untitled")
        image_url = context.get("image_url", "https://source.unsplash.com/random/800x600")
        description = context.get("description", "")
        
        self.log(f"Generating HTML Video for: {title}")
        
        video_id = str(uuid.uuid4())
        filename = f"video_{video_id}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        # HTML5 Animation Template (Ken Burns Effect + Typewriter Text)
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #000; font-family: 'Inter', sans-serif; }}
        .container {{ position: relative; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }}
        
        /* Background Image with Ken Burns Effect */
        .bg-image {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: url('{image_url}');
            background-size: cover;
            background-position: center;
            opacity: 0.6;
            animation: kenburns 15s infinite alternate;
        }}
        
        @keyframes kenburns {{
            0% {{ transform: scale(1); }}
            100% {{ transform: scale(1.2) translate(2%, 2%); }}
        }}
        
        /* Overlay Text */
        .content {{
            position: relative;
            z-index: 10;
            color: white;
            text-align: center;
            max-width: 80%;
            text-shadow: 0 4px 10px rgba(0,0,0,0.8);
        }}
        
        h1 {{
            font-size: 3rem;
            margin-bottom: 1rem;
            opacity: 0;
            animation: fadeup 1s forwards 0.5s;
        }}
        
        p {{
            font-size: 1.5rem;
            opacity: 0;
            animation: fadeup 1s forwards 1.2s;
        }}
        
        @keyframes fadeup {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        /* Progress Bar to simulate video playback */
        .progress {{
            position: absolute;
            bottom: 0; left: 0; height: 5px; background: red;
            width: 0%;
            animation: play 10s linear forwards;
        }}
        @keyframes play {{ to {{ width: 100%; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="bg-image"></div>
        <div class="content">
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
        <div class="progress"></div>
    </div>
</body>
</html>
        """
        
        with open(filepath, "w") as f:
            f.write(html_content)
            
        public_url = f"/generated_videos/{filename}"
        
        self.log(f"Video generated at: {filepath}")
        
        return {
            "video_path": filepath,
            "video_url": public_url,
            "status": "success"
        }
