const API_BASE = '/api';

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const selectedFileInfo = document.getElementById('selectedFileInfo');
const fileNameSpan = document.getElementById('fileName');
const fileSizeSpan = document.getElementById('fileSize');
const clearFileBtn = document.getElementById('clearFileBtn');
const uploadBtn = document.getElementById('uploadBtn');
const jobsTableBody = document.getElementById('jobsTableBody');
const statusFilter = document.getElementById('statusFilter');
const refreshBtn = document.getElementById('refreshBtn');

// Modal Elements
const inspectionModal = document.getElementById('inspectionModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const modalTitle = document.getElementById('modalTitle');
const modalMetadata = document.getElementById('modalMetadata');
const modalExtractedText = document.getElementById('modalExtractedText');
const copyTextBtn = document.getElementById('copyTextBtn');
const downloadTextBtn = document.getElementById('downloadTextBtn');

let selectedFile = null;
let currentViewingJob = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    fetchJobs();
    setInterval(fetchJobs, 3000); // Polling every 3 seconds for live job updates
});

function setupEventListeners() {
    // Dropzone Click
    dropZone.addEventListener('click', () => fileInput.click());

    // Drag & Drop
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) handleFileSelected(files[0]);
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFileSelected(e.target.files[0]);
    });

    clearFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearSelectedFile();
    });

    uploadBtn.addEventListener('click', handleUpload);
    refreshBtn.addEventListener('click', fetchJobs);
    statusFilter.addEventListener('change', fetchJobs);

    // Modal Events
    closeModalBtn.addEventListener('click', closeModal);
    copyTextBtn.addEventListener('click', copyTextToClipboard);
    downloadTextBtn.addEventListener('click', downloadExtractedText);
}

function handleFileSelected(file) {
    selectedFile = file;
    fileNameSpan.textContent = file.name;
    fileSizeSpan.textContent = formatBytes(file.size);
    selectedFileInfo.classList.remove('hidden');
    uploadBtn.disabled = false;
}

function clearSelectedFile() {
    selectedFile = null;
    fileInput.value = '';
    selectedFileInfo.classList.add('hidden');
    uploadBtn.disabled = true;
}

async function handleUpload() {
    if (!selectedFile) return;

    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span>Uploading Payload...</span>';

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch(`${API_BASE}/documents/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            alert(`Document queued successfully! Job ID: ${data.job_id}`);
            clearSelectedFile();
            fetchJobs();
        } else {
            alert(`Upload error: ${data.detail || 'Failed to upload document'}`);
        }
    } catch (err) {
        alert(`Network error during upload: ${err.message}`);
    } finally {
        uploadBtn.innerHTML = '<span>Push to Pipeline</span>';
    }
}

async function fetchJobs() {
    const filter = statusFilter.value;
    const url = filter ? `${API_BASE}/jobs?status=${filter}` : `${API_BASE}/jobs`;

    try {
        const response = await fetch(url);
        if (!response.ok) return;
        const jobs = await response.json();
        renderJobsTable(jobs);
    } catch (err) {
        console.error('Error fetching jobs:', err);
    }
}

function renderJobsTable(jobs) {
    if (!jobs || jobs.length === 0) {
        jobsTableBody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 2rem;">
                    No jobs found in queue.
                </td>
            </tr>
        `;
        return;
    }

    jobsTableBody.innerHTML = jobs.map(job => `
        <tr>
            <td><strong>${escapeHtml(job.filename)}</strong></td>
            <td><span class="status-chip">${job.file_format.toUpperCase()}</span></td>
            <td><span class="badge badge-${job.status}">${job.status}</span></td>
            <td>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: ${job.progress}%"></div>
                </div>
            </td>
            <td><small>${escapeHtml(job.parser_used || 'Pending')}</small></td>
            <td>
                <button class="btn btn-secondary btn-sm" onclick="inspectJob('${job.id}')">
                    ${job.status === 'COMPLETED' ? '👁 View Result' : 'ℹ️ Details'}
                </button>
            </td>
        </tr>
    `).join('');
}

async function inspectJob(jobId) {
    try {
        const response = await fetch(`${API_BASE}/jobs/${jobId}`);
        if (!response.ok) return alert('Failed to fetch job details');
        const job = await response.json();
        currentViewingJob = job;

        modalTitle.textContent = `Job Details: ${job.filename}`;
        renderMetadata(job);

        if (job.status === 'COMPLETED') {
            modalExtractedText.textContent = job.extracted_text || '(No text extracted)';
        } else if (job.status === 'FAILED') {
            modalExtractedText.textContent = `ERROR: ${job.error_message}`;
        } else {
            modalExtractedText.textContent = `Processing in progress (${job.progress}%)... Please refresh shortly.`;
        }

        inspectionModal.classList.remove('hidden');
    } catch (err) {
        alert(`Error opening job inspect modal: ${err.message}`);
    }
}

function renderMetadata(job) {
    const meta = job.metadata_json || {};
    let html = `
        <div class="meta-item">
            <span class="meta-label">Claim Check ID</span>
            <span class="meta-val">${job.claim_check_id.substring(0, 8)}...</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">File Size</span>
            <span class="meta-val">${formatBytes(job.file_size_bytes)}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">Parser Engine</span>
            <span class="meta-val">${escapeHtml(job.parser_used || 'N/A')}</span>
        </div>
    `;

    if (meta.page_count) {
        html += `<div class="meta-item"><span class="meta-label">Pages</span><span class="meta-val">${meta.page_count}</span></div>`;
    }
    if (meta.total_word_count || meta.word_count) {
        html += `<div class="meta-item"><span class="meta-label">Word Count</span><span class="meta-val">${meta.total_word_count || meta.word_count}</span></div>`;
    }
    if (meta.ocr_fallback_pages !== undefined) {
        html += `<div class="meta-item"><span class="meta-label">OCR Fallback Pages</span><span class="meta-val">${meta.ocr_fallback_pages}</span></div>`;
    }
    if (meta.detected_encoding) {
        html += `<div class="meta-item"><span class="meta-label">Encoding</span><span class="meta-val">${meta.detected_encoding}</span></div>`;
    }

    modalMetadata.innerHTML = html;
}

function closeModal() {
    inspectionModal.classList.add('hidden');
    currentViewingJob = null;
}

function copyTextToClipboard() {
    if (!modalExtractedText.textContent) return;
    navigator.clipboard.writeText(modalExtractedText.textContent);
    alert('Extracted text copied to clipboard!');
}

function downloadExtractedText() {
    if (!currentViewingJob || !currentViewingJob.id) return;
    window.open(`${API_BASE}/jobs/${currentViewingJob.id}/result`, '_blank');
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function escapeHtml(str) {
    return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
