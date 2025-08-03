document.addEventListener('DOMContentLoaded', () => {
    const dbUrlInput = document.getElementById('dbUrl');
    const promptInput = document.getElementById('prompt');
    const submitBtn = document.getElementById('submitBtn');
    const loader = document.getElementById('loader');
    const responseContainer = document.getElementById('response-container');

    submitBtn.addEventListener('click', async () => {
        const dbUrl = dbUrlInput.value.trim();
        const prompt = promptInput.value.trim();

        if (!dbUrl || !prompt) {
            alert('Please fill in both the Database URL and the Prompt.');
            return;
        }

        loader.style.display = 'block';
        responseContainer.innerHTML = '';

        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ database_url: dbUrl, prompt: prompt }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'An unknown error occurred.');
            }

            renderResponse(data);

        } catch (error) {
            responseContainer.innerHTML = `<div class="response-section"><h2>Error</h2><pre>${error.message}</pre></div>`;
        } finally {
            loader.style.display = 'none';
        }
    });

    function renderResponse(data) {
        responseContainer.innerHTML = ''; // Clear previous results

        if (data.email_status) {
            const emailSection = createSection('📧 Email Status', `<div class="status-message">${data.email_status}</div>`);
            responseContainer.appendChild(emailSection);
        }

        if (data.report) {
            const reportHtml = marked.parse(data.report);
            const reportSection = createSection('📊 Report', reportHtml);
            responseContainer.appendChild(reportSection);
        }

        if (data.visual) {
            const visualSection = createSection('📈 Visualization', '<canvas id="myChart"></canvas>');
            responseContainer.appendChild(visualSection);
            const ctx = document.getElementById('myChart').getContext('2d');
            new Chart(ctx, data.visual);
        }

        if (data.query_result) {
            const tableHtml = createTable(data.query_result);
            const resultSection = createSection('🔍 Query Result', tableHtml);
            responseContainer.appendChild(resultSection);
        }

        if (data.generated_query) {
            const querySyntax = typeof data.generated_query === 'object' ? JSON.stringify(data.generated_query, null, 2) : data.generated_query;
            const querySection = createSection('Generated Query', `<pre><code>${querySyntax}</code></pre>`);
            responseContainer.appendChild(querySection);
        }
    }

    function createSection(title, content) {
        const section = document.createElement('div');
        section.className = 'response-section';
        section.innerHTML = `<h2>${title}</h2>${content}`;
        return section;
    }

    function createTable(data) {
        if (!data || data.length === 0) {
            return '<p>No data returned from query.</p>';
        }

        const headers = Object.keys(data[0]);
        let table = '<table><thead><tr>';
        headers.forEach(header => table += `<th>${header}</th>`);
        table += '</tr></thead><tbody>';

        data.forEach(row => {
            table += '<tr>';
            headers.forEach(header => {
                const cellData = row[header] === null ? 'NULL' : row[header];
                table += `<td>${cellData}</td>`;
            });
            table += '</tr>';
        });

        table += '</tbody></table>';
        return table;
    }
});