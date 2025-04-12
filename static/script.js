// Converts structure JSON to markdown for admin preview
function structureToMarkdown(structure) {
    let md = '';

    for (const section in structure) {
        const sectionData = structure[section];
        md += `### ${section} (${sectionData.weight}%)\n`;

        if (sectionData.details) {
            sectionData.details.forEach(detail => {
                md += `- ${detail}\n`;
            });
        }

        if (sectionData.arguments) {
            sectionData.arguments.forEach(arg => {
                md += `#### ${arg.name} (${arg.weight}%)\n`;
                arg.details.forEach(detail => {
                    md += `- ${detail}\n`;
                });
            });
        }

        md += '\n';
    }

    return md.trim();
}

// DOM Elements
const generateBtn = document.getElementById("generate-btn");
const finalizeBtn = document.getElementById("finalize-structure");
const editBtn = document.getElementById("make-edit-btn");

const structureOutput = document.getElementById("structure-json");       // first structure (markdown)
const editInput = document.getElementById("edit-structure");             // optional edit input
const finalOutput = document.getElementById("final-structure");          // final JSON
const readablePreview = document.getElementById("final-structure-markdown"); // readable view

// === GENERATE STRUCTURE ===
generateBtn?.addEventListener("click", async (e) => {
    e.preventDefault();

    const topic = document.getElementById("topic").value.trim();
    const difficulty = document.getElementById("difficulty").value.trim();
    if (!topic || !difficulty) return alert("Enter topic and difficulty");

    const res = await fetch("/generate_structure", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, difficulty })
    });

    const data = await res.json();

    if (data.structure) {
        const markdown = structureToMarkdown(data.structure);
        const rawJson = JSON.stringify(data.structure, null, 2);

        structureOutput.value = markdown;
        finalOutput.value = rawJson;
        readablePreview.value = markdown;

        window.currentStructure = data.structure;
        alert("✅ Structure generated successfully!");
    } else {
        alert("❌ Failed to generate structure.");
    }
});

// === MAKE EDIT ===
editBtn?.addEventListener("click", async () => {
    const original = window.currentStructure;
    const current = JSON.parse(finalOutput.value);
    const suggestion = editInput.value.trim();

    if (!original || !suggestion) return alert("Missing original structure or suggestion.");

    const res = await fetch('/api/make_edit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            original_structure: original,
            current_structure: current,
            suggested_edit: suggestion
        })
    });

    const data = await res.json();
    if (data.success) {
        const updated = data.updated_structure;
        const updatedJSON = JSON.stringify(updated, null, 2);
        const updatedMarkdown = structureToMarkdown(updated);

        finalOutput.value = updatedJSON;
        readablePreview.value = updatedMarkdown;

        window.currentStructure = updated;
        alert("✅ Edit applied successfully.");
    } else {
        alert("❌ Edit failed: " + (data.error || "Unknown error"));
    }
});

// === FINALIZE STRUCTURE ===
finalizeBtn?.addEventListener("click", async () => {
    const topic = document.getElementById("topic").value.trim();
    const difficulty = document.getElementById("difficulty").value.trim();
    let finalStructure;

    try {
        finalStructure = JSON.parse(finalOutput.value);
    } catch (err) {
        return alert("❌ Invalid JSON in Final Structure box.");
    }

    const res = await fetch("/finalize_structure", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            topic,
            difficulty,
            structure: finalStructure
        })
    });

    const result = await res.json();
    if (res.ok) {
        alert("✅ Structure finalized and saved to DB!");
    } else {
        alert("❌ Finalization failed: " + (result?.error || "Unknown error"));
    }
});
