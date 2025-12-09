// script.js

document.addEventListener('DOMContentLoaded', (event) => {
    const terminalInput = document.getElementById('terminal-input');
    const terminalLog = document.getElementById('terminal-log');
    const cursor = document.getElementById('cursor');

    // Focus input when clicking anywhere on the terminal area
    terminalLog.addEventListener('click', () => {
        terminalInput.focus();
    });

    terminalInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const command = terminalInput.value.trim();
            if (command) {
                logOutput(`> ${command}`);
                handleCommand(command);
                terminalInput.value = '';
                // Scroll to the bottom
                terminalLog.scrollTop = terminalLog.scrollHeight;
            }
        }
    });

    function logOutput(message) {
        const p = document.createElement('p');
        // Use innerHTML to handle line breaks/formatting from server response
        p.innerHTML = message; 
        terminalLog.appendChild(p);
        terminalLog.scrollTop = terminalLog.scrollHeight;
    }

    async function handleCommand(command) {
        if (command.toLowerCase() === 'clear') {
            terminalLog.innerHTML = '';
            logOutput("Screen cleared.");
            return;
        }

        if (command.toLowerCase() === 'logout' || command.toLowerCase() === 'exit') {
            logOutput("Logging out... Redirecting.");
            // Redirect after a short delay
            setTimeout(() => {
                window.location.href = '/logout';
            }, 1000);
            return;
        }
        
        try {
            const response = await fetch('/api/terminal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command: command }),
            });

            if (response.ok) {
                const data = await response.json();
                logOutput(data.output);
            } else {
                logOutput(`Error: ${response.statusText}`);
            }
        } catch (error) {
            logOutput(`Network error: ${error.message}`);
        }
    }

    // Ensure input is focused on load
    terminalInput.focus();
});
