function highlightDiffs() {
  document.querySelectorAll(".highlight code").forEach((codeBlock) => {
    // Get the HTML content
    const content = codeBlock.innerHTML;

    // Split by newline while preserving HTML
    const lines = content.split("\n");

    // Process each line
    const wrappedContent = lines
      .map((line) => {
        if (!line.trim()) return ""; // Skip empty lines

        // Check if line contains our markers
        const isAdded = line.includes("//+");
        const isDeleted = line.includes("//-");

        // Remove the markers
        let cleanLine = line.replace("//+", "").replace("//-", "");

        // Create a wrapper with appropriate class
        const classes = ["wrapped-line"];
        if (isAdded) classes.push("highlight-added");
        if (isDeleted) classes.push("highlight-deleted");

        return `<span class="${classes.join(" ")}">${cleanLine}</span>`;
      })
      .join("\n");

    codeBlock.innerHTML = wrappedContent;
  });
}

document.addEventListener("DOMContentLoaded", highlightDiffs);
