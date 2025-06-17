// Global variables
let currentResult = null

// DOM Elements
const uploadArea = document.getElementById("uploadArea")
const fileInput = document.getElementById("fileInput")
const uploadProgress = document.getElementById("uploadProgress")
const resultsSection = document.getElementById("results")

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  initializeUpload()
  loadStatistics()
  setupSmoothScrolling()
})

// Initialize upload functionality
function initializeUpload() {
  // Click to upload
  uploadArea.addEventListener("click", () => {
    fileInput.click()
  })

  // File input change
  fileInput.addEventListener("change", handleFileSelect)

  // Drag and drop
  uploadArea.addEventListener("dragover", handleDragOver)
  uploadArea.addEventListener("dragleave", handleDragLeave)
  uploadArea.addEventListener("drop", handleDrop)

  // Prevent default drag behaviors
  ;["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    uploadArea.addEventListener(eventName, preventDefaults, false)
    document.body.addEventListener(eventName, preventDefaults, false)
  })
}

function preventDefaults(e) {
  e.preventDefault()
  e.stopPropagation()
}

function handleDragOver(e) {
  uploadArea.classList.add("dragover")
}

function handleDragLeave(e) {
  uploadArea.classList.remove("dragover")
}

function handleDrop(e) {
  uploadArea.classList.remove("dragover")
  const files = e.dataTransfer.files
  if (files.length > 0) {
    handleFile(files[0])
  }
}

function handleFileSelect(e) {
  const file = e.target.files[0]
  if (file) {
    handleFile(file)
  }
}

function handleFile(file) {
  // Validate file type
  const allowedTypes = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/bmp", "image/tiff"]
  if (!allowedTypes.includes(file.type)) {
    showError("Please upload a valid image file (JPG, PNG, GIF, BMP, TIFF)")
    return
  }

  // Validate file size (16MB)
  if (file.size > 16 * 1024 * 1024) {
    showError("File size must be less than 16MB")
    return
  }

  uploadFile(file)
}

function uploadFile(file) {
  const formData = new FormData()
  formData.append("file", file)

  // Show progress
  showProgress()

  fetch("/upload", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      hideProgress()
      if (data.success) {
        displayResults(data)
      } else {
        showError(data.error || "An error occurred while processing the image")
      }
    })
    .catch((error) => {
      hideProgress()
      console.error("Error:", error)
      showError("Network error. Please try again.")
    })
}

function showProgress() {
  uploadArea.style.display = "none"
  uploadProgress.style.display = "block"
}

function hideProgress() {
  uploadArea.style.display = "block"
  uploadProgress.style.display = "none"
}

function displayResults(data) {
  currentResult = data
  const result = data.result

  // Update result image
  document.getElementById("resultImage").src = data.image

  // Update status
  const statusElement = document.getElementById("resultStatus")
  const isLegitimate = !result.is_fake

  statusElement.className = `result-status ${isLegitimate ? "legitimate" : "fake"}`
  statusElement.innerHTML = `
        <h2>
            <i class="fas fa-${isLegitimate ? "check-circle" : "times-circle"}"></i>
            ${isLegitimate ? "Legitimate Invoice" : "Fake Invoice Detected"}
        </h2>
        <p>${isLegitimate ? "This invoice appears to be authentic" : "This invoice may be fraudulent"}</p>
    `

  // Update details
  document.getElementById("confidence").textContent = `${(result.confidence * 100).toFixed(1)}%`
  document.getElementById("hashValue").textContent = result.hash || "N/A"
  document.getElementById("analysisReason").textContent = result.reason || "N/A"

  // Update metadata if available
  const metadataInfo = document.getElementById("metadataInfo")
  const sourceInfo = document.getElementById("sourceInfo")

  if (result.metadata) {
    metadataInfo.style.display = "flex"
    sourceInfo.textContent = `${result.metadata.source} (${result.metadata.split})`
  } else {
    metadataInfo.style.display = "none"
  }

  // Show results section
  resultsSection.style.display = "block"
  resultsSection.scrollIntoView({ behavior: "smooth" })
}

function resetUpload() {
  // Hide results
  resultsSection.style.display = "none"

  // Reset file input
  fileInput.value = ""

  // Scroll to upload area
  document.getElementById("home").scrollIntoView({ behavior: "smooth" })

  // Reset current result
  currentResult = null
}

function downloadReport() {
  if (!currentResult) return

  const result = currentResult.result
  const reportData = {
    filename: currentResult.filename,
    timestamp: new Date().toISOString(),
    status: result.is_fake ? "FAKE" : "LEGITIMATE",
    confidence: (result.confidence * 100).toFixed(1) + "%",
    hash: result.hash,
    reason: result.reason,
    metadata: result.metadata || null,
  }

  const reportText = `
INVOICE VERIFICATION REPORT
===========================

File: ${reportData.filename}
Date: ${new Date(reportData.timestamp).toLocaleString()}
Status: ${reportData.status}
Confidence: ${reportData.confidence}
Hash: ${reportData.hash}
Analysis: ${reportData.reason}

${reportData.metadata ? `Source: ${reportData.metadata.source}` : ""}

Generated by InvoiceGuard AI Detection System
    `.trim()

  const blob = new Blob([reportText], { type: "text/plain" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = `invoice-report-${Date.now()}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

function loadStatistics() {
  fetch("/stats")
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("total-invoices").textContent = data.total_legitimate_hashes || "0"
      document.getElementById("dbTotalHashes").textContent = data.total_legitimate_hashes || "0"
      document.getElementById("dbStatus").textContent = data.database_exists ? "Active" : "Inactive"
    })
    .catch((error) => {
      console.error("Error loading statistics:", error)
      document.getElementById("dbTotalHashes").textContent = "Error"
      document.getElementById("dbStatus").textContent = "Error"
    })
}

function setupSmoothScrolling() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault()
      const target = document.querySelector(this.getAttribute("href"))
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        })
      }
    })
  })
}

function showError(message) {
  // Create error notification
  const errorDiv = document.createElement("div")
  errorDiv.className = "error-notification"
  errorDiv.innerHTML = `
        <div class="error-content">
            <i class="fas fa-exclamation-triangle"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `

  // Add error styles
  errorDiv.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: linear-gradient(135deg, #e17055, #d63031);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `

  document.body.appendChild(errorDiv)

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (errorDiv.parentElement) {
      errorDiv.remove()
    }
  }, 5000)
}

// Add CSS for error notification animation
const style = document.createElement("style")
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .error-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .error-content button {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 0.25rem;
        margin-left: 0.5rem;
    }
`
document.head.appendChild(style)
