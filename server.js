const express = require('express');
const WebSocket = require('ws');
const path = require('path');
const ffmpeg = require('fluent-ffmpeg');
const { SpeechClient } = require('@google-cloud/speech').v1p1beta1;

const app = express();
const port = 8080;

const wss = new WebSocket.Server({ noServer: true });

const speechClient = new SpeechClient();

const config = {
    encoding: 'LINEAR16',
    sampleRateHertz: 16000,
    languageCode: 'te-IN',
    enableAutomaticPunctuation: true,
    useEnhanced: true,
};

function setupTranscription(ws) {
    const recognizeStream = speechClient
        .streamingRecognize({
            config,
            interimResults: true,
        })
        .on('error', (error) => {
            console.error('API Error:', error);
            ws.send(JSON.stringify({ error: 'Google Cloud Speech-to-Text APIలో లోపం.' }));
            ws.close();
        })
        .on('data', (data) => {
            const result = data.results[0];
            if (result) {
                const transcript = result.alternatives[0].transcript;
                const isFinal = result.isFinal;
                ws.send(JSON.stringify({ transcript, isFinal }));
            }
        });

    return recognizeStream;
}

wss.on('connection', ws => {
    let recognizeStream;
    let ffmpegProcess = null;

    ws.on('message', message => {
        if (!recognizeStream) {
            recognizeStream = setupTranscription(ws);
            ffmpegProcess = ffmpeg({ source: '-' })
                .inputFormat('webm')
                .audioCodec('pcm_s16le')
                .audioChannels(1)
                .audioFrequency(16000)
                .format('s16le')
                .on('error', (err) => {
                    console.error('FFmpeg Error:', err.message);
                    ws.send(JSON.stringify({ error: 'ఆడియో మార్పిడిలో లోపం.' }));
                    ws.close();
                })
                .pipe(recognizeStream);
        }
        ffmpegProcess.write(message);
    });

    ws.on('close', () => {
        if (ffmpegProcess) {
            ffmpegProcess.end();
        }
        if (recognizeStream) {
            recognizeStream.end();
        }
        console.log('Client disconnected');
    });

    ws.on('error', error => {
        console.error('WebSocket Error:', error);
    });
});

const server = app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});

server.on('upgrade', (request, socket, head) => {
    wss.handleUpgrade(request, socket, head, ws => {
        wss.emit('connection', ws, request);
    });
});