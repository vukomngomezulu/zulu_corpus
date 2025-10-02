//TTS FEATURE
function speakZuluText(text) {
    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'zu-ZA'; // Zulu language code
        
        // Find Zulu voice
        const voices = speechSynthesis.getVoices();
        const zuluVoice = voices.find(voice => 
            voice.lang === 'zu-ZA' || voice.lang.startsWith('zu')
        );
        
        if (zuluVoice) {
            utterance.voice = zuluVoice;
        }
        utterance.rate = 0.9;
        utterance.pitch = 1;
        
        window.speechSynthesis.speak(utterance);
    }
}

let voicesLoaded = false;
speechSynthesis.onvoiceschanged = function() {
    voicesLoaded = true;
};

// Chart instance storage
let chartInstance = null;


document.addEventListener('DOMContentLoaded', function() {
    
    document.querySelectorAll('.tts-btn').forEach(button => {
        button.addEventListener('click', function() {
            const text = this.getAttribute('data-text');
            
            if (!voicesLoaded) {
                const voices = speechSynthesis.getVoices();
                if (voices.length > 0) {
                    voicesLoaded = true;
                    speakZuluText(text);
                } else {
                    setTimeout(() => speakZuluText(text), 300);
                }
            } else {
                speakZuluText(text);
            }
        });
    });
    
    
    initializeTrendsChart();
});


function initializeTrendsChart() {
    const wordCtx = document.getElementById('wordFrequencyChart');
    if (!wordCtx) return;
    
    // Destroy existing chart instance if it exists
    if (chartInstance) {
        chartInstance.destroy();
        chartInstance = null;
    }
    
    // Get data from table
    const wordRows = document.querySelectorAll('.table tbody tr');
    const labels = [];
    const data = [];
    
    wordRows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 3) {
            const wordLink = cells[0].querySelector('a');
            const wordText = wordLink ? wordLink.textContent.trim() : cells[0].textContent.trim();
            const count = parseInt(cells[2].textContent.trim()) || 0;
            
            if (wordText && !isNaN(count)) {
                labels.push(wordText);
                data.push(count);
            }
        }
    });
    
    // Creating the chart 
    if (labels.length > 0 && data.length > 0 && typeof Chart !== 'undefined') {
        chartInstance = new Chart(wordCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Search Frequency',
                    data: data,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Search Count'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Words'
                        }
                    }
                }
            }
        });
    }
}

// Clean up 
window.addEventListener('beforeunload', function() {
    if (chartInstance) {
        chartInstance.destroy();
    }
});