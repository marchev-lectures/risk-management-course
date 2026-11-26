# Някои идеи за риска

Local Quarto textbook based on slides 1–32 of the 222-slide PowerPoint. The index contains the opening slides. The two chapters follow the headings on slides 4 and 18. Original Bulgarian and English text appears alongside the slide images.

## Build and preview

With Quarto 1.11.9 installed, run `quarto render` in the repository root. The local installation is `.tools/quarto-1.11.9/bin/quarto`. Serve only the build directory with `python3 -m http.server 8743 --bind 127.0.0.1 --directory _book`, then open http://127.0.0.1:8743/.

## Source and maintenance

The Markdown and images are sufficient to render the reviewed baseline. To audit the import, see the local manifests/sources.json and reports/progress.md. Keep the original deck at its initial path. For regeneration use a fresh staging directory with the original checksum and empty chapter/image directories. With LibreOffice 24.2.7.2 export the original to extracted/ using Impress PDF export with ExportHiddenSlides enabled. Run scripts/import_baseline.py with Python 3 and Poppler pdftoppm. Compare the result before replacing reviewed material.

The project config selects Sol medium for development and offers the routine profile (Luna low) for small edits. Rendering and extraction use local tools. Create remotes, upload material and deploy only with the corresponding approval.
