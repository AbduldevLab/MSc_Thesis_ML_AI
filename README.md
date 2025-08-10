# 📚 LaTeX Thesis Template

This repository contains a structured LaTeX folder designed for writing academic theses, dissertations, or reports. It includes a modular setup with separate files for chapters, bibliography, and formatting, making it easy to manage large documents.

## 📁 Folder Structure


### 🛠️ Requirements (Local Setup)

To compile and work with LaTeX documents locally on macOS (or any OS), you need:

- **LaTeX distribution:**  
  - On macOS: [MacTeX](https://tug.org/mactex/) (full LaTeX distribution including TeX Live)  
  - On Windows: [MiKTeX](https://miktex.org/) or TeX Live  
  - On Linux: TeX Live via package manager (e.g., `sudo apt install texlive-full`)

- **Bibliography tool:**  
  - `bibtex` is included with MacTeX and MiKTeX  
  - Alternatively, use `biber` if your bibliography uses BibLaTeX

- **Editor:**  
  - Visual Studio Code (VS Code) — [Download here](https://code.visualstudio.com/)

- **VS Code extensions:**  
  - **LaTeX Workshop** (essential extension to compile, preview, and manage LaTeX projects)  
  - Optional: **LaTeX Utilities**, **Spell Right** (spell checking), etc.

### 🚀 Usage

#### Option 1: Overleaf (Online)

You can upload the entire folder to Overleaf for online editing and compilation. Overleaf supports collaborative writing and automatic PDF generation.

#### Option 2: Visual Studio Code (Local)

If you prefer working locally:

1. Install MacTeX on macOS from [https://tug.org/mactex/](https://tug.org/mactex/)  
   > This installs the full TeX Live distribution along with all necessary binaries.

2. Install Visual Studio Code: [https://code.visualstudio.com/](https://code.visualstudio.com/)

3. Open VS Code and install the **LaTeX Workshop** extension from the Extensions Marketplace.

4. Open this project folder in VS Code.

5. Compile your thesis by opening `thesis.tex` and pressing the LaTeX Workshop build command:  
   - macOS: `Cmd + Option + B`  
   - Windows/Linux: `Ctrl + Alt + B`

6. The PDF viewer will automatically display the compiled PDF.

> **Tip:** Make sure the MacTeX binaries (usually `/Library/TeX/texbin`) are in your system PATH. You can check this by running `which pdflatex` in your terminal. If not found, add it to your shell profile, e.g., in `.zshrc` or `.bash_profile`:

```bash
export PATH="/Library/TeX/texbin:$PATH"