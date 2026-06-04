document.addEventListener('DOMContentLoaded', () => {
    // Set today as default date
    const dateInput = document.getElementById('date-input');
    const today = new Date();
    // Format to YYYY-MM-DD in local time
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    dateInput.value = `${yyyy}-${mm}-${dd}`;

    const form = document.getElementById('generate-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = document.getElementById('spinner');
    
    const resultSection = document.getElementById('result-section');
    const markdownResult = document.getElementById('markdown-result');
    const copyBtn = document.getElementById('copy-btn');
    
    let currentRawMarkdown = '';

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const date = dateInput.value;
        const topic = document.querySelector('input[name="topic"]:checked').value;
        
        // UI State: Loading
        btnText.textContent = 'Generating...';
        spinner.classList.remove('hidden');
        submitBtn.disabled = true;
        resultSection.classList.add('hidden');
        
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ date, topic })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Success
                currentRawMarkdown = data.content;
                markdownResult.innerHTML = marked.parse(data.content);
                resultSection.classList.remove('hidden');
            } else {
                // Error
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            console.error('Error generating post:', error);
            alert('An error occurred while communicating with the server.');
        } finally {
            // UI State: Reset
            btnText.textContent = 'Generate Post';
            spinner.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });

    copyBtn.addEventListener('click', () => {
        if (!currentRawMarkdown) return;
        
        navigator.clipboard.writeText(currentRawMarkdown).then(() => {
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        }).catch(err => {
            console.error('Could not copy text: ', err);
            alert('Failed to copy text.');
        });
    });
});
