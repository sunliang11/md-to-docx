const { execFile } = require("child_process");
const { Notice, Plugin } = require("obsidian");

class MdToDocxPlugin extends Plugin {
  async onload() {
    this.addCommand({
      id: "export-current",
      name: "Export to Professional Word",
      editorCallback: (editor, view) => {
        if (!this.isDesktop()) {
          new Notice("md-to-docx: desktop only");
          return;
        }
        const file = view.file;
        if (!file) {
          new Notice("No active file");
          return;
        }
        this.exportFile(file.path);
      },
    });

    this.addCommand({
      id: "export-folder",
      name: "Export folder to DOCX",
      checkCallback: (checking) => {
        const folder = this.app.vault.getRoot();
        if (!checking) {
          if (!this.isDesktop()) {
            new Notice("md-to-docx: desktop only");
            return;
          }
          this.exportFolder(folder.path);
        }
        return true;
      },
    });
  }

  isDesktop() {
    return typeof require("child_process").execFile === "function";
  }

  getCli() {
    return this.loadData().then((data) => (data && data.cli) || "md-to-docx");
  }

  getPreset() {
    return this.loadData().then((data) => (data && data.preset) || "technical");
  }

  getOutputDir() {
    return this.loadData().then((data) => (data && data.outputDir) || "");
  }

  exportFile(vaultPath) {
    const adapter = this.app.vault.adapter;
    const absPath = adapter.getFullPath(vaultPath);

    Promise.all([this.getCli(), this.getPreset(), this.getOutputDir()]).then(
      ([cli, preset, outputDir]) => {
        const args = [absPath, "--preset", preset];
        if (outputDir) {
          args.push("--output-dir", adapter.getFullPath(outputDir));
        }
        execFile(cli, args, (err, stdout, stderr) => {
          if (err) {
            const hint = (stderr || err.message || "").includes("ENOENT")
              ? " — install: pip install md2docx-compiler"
              : "";
            new Notice(`md-to-docx failed${hint}`);
            console.error(stderr || err);
            return;
          }
          new Notice(`Exported ${vaultPath.replace(/\.md$/i, ".docx")}`);
          if (stdout) console.log(stdout);
        });
      }
    );
  }

  exportFolder(vaultPath) {
    const adapter = this.app.vault.adapter;
    const absPath = adapter.getFullPath(vaultPath);

    Promise.all([this.getCli(), this.getPreset(), this.getOutputDir()]).then(
      ([cli, preset, outputDir]) => {
        const args = [absPath, "--preset", preset];
        if (outputDir) {
          args.push("--output-dir", adapter.getFullPath(outputDir));
        }
        execFile(cli, args, (err, stdout, stderr) => {
          if (err) {
            new Notice("md-to-docx folder export failed");
            console.error(stderr || err);
            return;
          }
          new Notice("Folder export complete");
          if (stdout) console.log(stdout);
        });
      }
    );
  }
}

module.exports = MdToDocxPlugin;
