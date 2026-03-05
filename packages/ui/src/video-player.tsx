import React from "react";

interface VideoPlayerProps {
    src: string;
    className?: string;
    poster?: string;
    autoPlay?: boolean;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({
    src,
    className = "",
    poster,
    autoPlay = true
}) => {
    // Check if the source is an HTML file (our generated "video")
    const isHtmlVideo = src?.endsWith(".html");

    if (isHtmlVideo) {
        return (
            <iframe
                src={src}
                className={`w-full h-full border-0 pointer-events-none ${className}`}
                title="Generated Content"
                allow="autoplay"
            />
        );
    }

    // Fallback to standard video tag for MP4s (or mock data)
    return (
        <video
            src={src}
            className={`w-full h-full object-cover ${className}`}
            autoPlay={autoPlay}
            loop
            muted
            playsInline
            poster={poster}
        />
    );
};
