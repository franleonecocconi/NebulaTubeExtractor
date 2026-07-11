const http = require('http');
const url = require('url');
const { Innertube, UniversalCache } = require('youtubei.js');

const PORT = process.env.PORT || 3000;

let youtube;

async function getStreamUrl(videoId) {
    if (!youtube) {
        youtube = await Innertube.create({ 
            client_type: 'WEB',
            cache: new UniversalCache(false) 
        });
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

    const parsedUrl = url.parse(req.url, true);
    
    if (parsedUrl.pathname === '/api/streams' && req.method === 'GET') {
        const { videoId } = parsedUrl.query;

        if (!videoId) {
            res.statusCode = 400;
            return res.end(JSON.stringify({ error: "Missing videoId" }));
        }

        try {
            const streamUrl = await getStreamUrl(videoId);

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
        res.end(JSON.stringify({ error: "Invalid route" }));
    }
});

server.listen(PORT, () => {
    console.log(`NebulaTube Extractor corriendo en http://localhost:${PORT}`);
});