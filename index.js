import http from 'http';
import { Innertube, UniversalCache } from 'youtubei.js';

const PORT = process.env.PORT || 3000;

let youtube;

async function getStreamUrl(videoId, lang, country) {
    if (!youtube) {
        youtube = await Innertube.create({ 
            client_type: 'WEB',
            lang: lang,
            location: country,
            cache: new UniversalCache(false) 
        });
    } else {
        if (lang) await youtube.session.setLang(lang);
        if (country) await youtube.session.setLocation(country);
    }
    
    const videoInfo = await youtube.getInfo(videoId);
    const streamingData = videoInfo.streaming_data;

    if (!streamingData) return null;

    if (streamingData.server_abr_streaming_url) {
        return streamingData.server_abr_streaming_url;
    }

    const formats = [
        ...(streamingData.formats || []),
        ...(streamingData.adaptive_formats || [])
    ];
    
    const format = formats.find(f => f.url);
    return format ? format.url : null;
}

const server = http.createServer(async (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.statusCode = 200;
        return res.end();
    }

    const baseURL = `http://${req.headers.host || 'localhost'}`;
    const parsedUrl = new URL(req.url, baseURL);
    
    if (parsedUrl.pathname.includes('/api/streams') && req.method === 'GET') {
        const videoId = parsedUrl.searchParams.get('videoId');
        const lang = parsedUrl.searchParams.get('lang');
        const country = parsedUrl.searchParams.get('country');

        if (!videoId) {
            res.statusCode = 400;
            return res.end(JSON.stringify({ error: "Missing videoId" }));
        }

        try {
            const streamUrl = await getStreamUrl(videoId, lang, country);

            if (!streamUrl) {
                res.statusCode = 404;
                return res.end(JSON.stringify({ error: "No stream found or video is restricted" }));
            }

            res.statusCode = 200;
            res.end(JSON.stringify({ url: streamUrl }));

        } catch (error) {
            res.statusCode = 500;
            res.end(JSON.stringify({ error: error.message }));
        }
    } else {
        res.statusCode = 404;
        res.end(JSON.stringify({ error: "Route not found. Use /api/streams?videoId=YOUR_ID" }));
    }
});

server.listen(PORT, () => {
    console.log(`NebulaTube Extractor corriendo en http://localhost:${PORT}`);
});