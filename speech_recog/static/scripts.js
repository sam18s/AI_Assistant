const micElement = document.getElementById('mic');
const transcriptElement = document.getElementById('transcript');
const downloadBtn = document.getElementById('downloadTranscript');
const startRecordingBtn = document.getElementById('startRecording');
const stopRecordingBtn = document.getElementById('stopRecording');
const audioContainer = document.getElementById('audioContainer');
const audioPlayback = document.getElementById('audioPlayback');
const closeAudio = document.getElementById('closeAudio');

let finalTranscript = "";
let isListening = false;

// === Speech Recognition ===
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.continuous = true;
recognition.interimResults = true;
recognition.lang = 'en-US';

micElement.addEventListener('click', () => {
    if (isListening) {
        recognition.stop();
        micElement.classList.remove('active');
        isListening = false;
        console.log('Speech recognition stopped.');
    } else {
        micElement.classList.add('active');
        recognition.start();
        transcriptElement.textContent = "Listening...";
        finalTranscript = "";
        isListening = true;
        console.log('Speech recognition started.');
    }
});

recognition.onresult = (event) => {
    finalTranscript = Array.from(event.results)
        .map(result => result[0].transcript)
        .join(' ');
    transcriptElement.textContent = finalTranscript;
};

recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
};

recognition.onend = () => {
    if (isListening) {
        transcriptElement.textContent = "Final Transcript: " + finalTranscript;
    }
};

// === Download Transcript ===
downloadBtn.addEventListener('click', () => {
    if (finalTranscript.trim() === "") return alert("No transcript to download.");
    const blob = new Blob([finalTranscript], { type: 'text/plain' });
    const link = document.createElement('a');
    link.download = 'transcript.txt';
    link.href = URL.createObjectURL(blob);
    link.click();
});

// === Audio Recording ===
let mediaRecorder;
let audioChunks = [];

startRecordingBtn.addEventListener('click', async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            const audioUrl = URL.createObjectURL(audioBlob);
            audioPlayback.src = audioUrl;
            audioContainer.style.display = "block";
        };

        mediaRecorder.start();
        startRecordingBtn.disabled = true;
        stopRecordingBtn.disabled = false;
        console.log("Audio recording started.");
    } catch (err) {
        alert("Microphone permission denied.");
        console.error(err);
    }
});

stopRecordingBtn.addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        startRecordingBtn.disabled = false;
        stopRecordingBtn.disabled = true;
        console.log("Audio recording stopped.");
    }
});

closeAudio.addEventListener('click', () => {
    audioContainer.style.display = 'none';
    audioPlayback.pause();
    audioPlayback.src = '';
});
