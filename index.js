document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("redaction-form");
    const fileInput = document.getElementById("file-input");
    const dropzone = document.getElementById("file-dropzone");
    const fileBadge = document.getElementById("file-badge");
    const fileNameText = document.getElementById("file-name-text");
    const removeFileBtn = document.getElementById("remove-file-btn");
    const submitBtn = document.getElementById("submit-btn");
    
    const statusCard = document.getElementById("status-card");
    const statusSpinner = document.getElementById("status-spinner");
    const statusSuccessIcon = document.getElementById("status-success-icon");
    const statusTitle = document.getElementById("status-title");
    const statusMessage = document.getElementById("status-message");
    const downloadContainer = document.getElementById("download-container");
    const downloadLink = document.getElementById("download-link");
    
    const resultsCard = document.getElementById("results-card");
    const statsGrid = document.getElementById("stats-grid");

    let selectedFile = null;

    // Trigger file input click when clicking dropzone
    dropzone.addEventListener("click", (e) => {
        // Prevent click if we clicked the remove badge button
        if (e.target.closest("#file-badge")) return;
        fileInput.click();
    });

    // Handle Drag & Drop styles
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop', 'dragend'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
        }, false);
    });

    // Handle File Drop
    dropzone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // Handle standard File Selection
    fileInput.addEventListener("change", (e) => {
        if (fileInput.files.length > 0) {
            handleFileSelect(fileInput.files[0]);
        }
    });

    // File selection logic
    function handleFileSelect(file) {
        const ext = file.name.split('.').pop().toLowerCase();
        if (!['docx', 'txt', 'log'].includes(ext)) {
            alert("Unsupported file format! Please upload a .docx, .txt, or .log file.");
            clearFile();
            return;
        }

        selectedFile = file;
        fileNameText.textContent = file.name;
        fileBadge.classList.remove("hidden");
        submitBtn.disabled = false;
        
        // Hide previous results
        statusCard.classList.add("hidden");
        resultsCard.classList.add("hidden");
    }

    // Remove File
    removeFileBtn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        clearFile();
    });

    function clearFile() {
        selectedFile = null;
        fileInput.value = "";
        fileBadge.classList.add("hidden");
        submitBtn.disabled = true;
    }

    // Handle Form Submit
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!selectedFile) return;

        // Reset Status UI for processing
        statusCard.classList.remove("hidden");
        statusSpinner.classList.remove("hidden");
        statusSuccessIcon.classList.add("hidden");
        downloadContainer.classList.add("hidden");
        statusTitle.textContent = "Processing your document...";
        statusMessage.textContent = "Analyzing context, detecting names, and stripping PII...";
        resultsCard.classList.add("hidden");
        submitBtn.disabled = true;

        // Build request payload
        const formData = new FormData();
        formData.append("file", selectedFile);

        // Append PII types checkboxes
        const checkboxes = document.querySelectorAll('input[name="types"]:checked');
        checkboxes.forEach(cb => {
            formData.append("types", cb.value);
        });

        try {
            const response = await fetch("/api/redact", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || "Server processing failed.");
            }

            // Get the response file as a blob
            const blob = await response.blob();
            
            // Get stats from custom header 'X-Redaction-Stats'
            const statsHeader = response.headers.get("X-Redaction-Stats");
            displayStats(statsHeader);

            // Trigger file download
            const blobUrl = URL.createObjectURL(blob);
            downloadLink.href = blobUrl;
            downloadLink.download = `redacted_${selectedFile.name}`;
            
            // Update Status UI to Success
            statusSpinner.classList.add("hidden");
            statusSuccessIcon.classList.remove("hidden");
            statusTitle.textContent = "Redaction Complete!";
            statusMessage.textContent = "Your document has been fully anonymized.";
            downloadContainer.classList.remove("hidden");

        } catch (error) {
            console.error("Redaction error:", error);
            statusSpinner.classList.add("hidden");
            statusTitle.textContent = "Redaction Failed";
            statusMessage.textContent = error.message || "An unexpected error occurred during processing.";
        } finally {
            submitBtn.disabled = false;
        }
    });

    // Parse and display statistics
    function displayStats(statsStr) {
        statsGrid.innerHTML = "";
        if (!statsStr) return;

        // Format of statsStr is: "name:2;email:1;phone:0"
        const items = statsStr.split(";");
        let totalRedacted = 0;

        const displayNameMap = {
            "name": "Names",
            "email": "Emails",
            "phone": "Phone Numbers",
            "company": "Companies",
            "address": "Addresses",
            "ssn": "SSNs / IDs",
            "cc": "Credit Cards",
            "dob": "DOBs",
            "ip": "IP Addresses"
        };

        items.forEach(item => {
            const [key, val] = item.split(":");
            const count = parseInt(val) || 0;
            totalRedacted += count;

            const card = document.createElement("div");
            card.className = "stat-item-card";
            card.innerHTML = `
                <div class="stat-number">${count}</div>
                <div class="stat-name">${displayNameMap[key] || key}</div>
            `;
            statsGrid.appendChild(card);
        });

        if (totalRedacted > 0) {
            resultsCard.classList.remove("hidden");
        }
    }
});
