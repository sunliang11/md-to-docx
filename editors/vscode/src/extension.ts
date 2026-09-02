import * as vscode from "vscode";
import { spawn } from "child_process";
import * as path from "path";

function getConfig() {
  const cfg = vscode.workspace.getConfiguration("md-to-docx");
  return {
    cli: cfg.get<string>("path", "md-to-docx"),
    preset: cfg.get<string>("preset", "technical"),
    extraArgs: cfg.get<string[]>("extraArgs", []),
    outputDir: cfg.get<string>("outputDir", ""),
  };
}

function runConvert(filePath: string): Promise<{ code: number; stderr: string }> {
  const { cli, preset, extraArgs, outputDir } = getConfig();
  const args = [filePath, "--preset", preset, ...extraArgs];
  if (outputDir) {
    args.push("--output-dir", outputDir);
  }

  const channel = vscode.window.createOutputChannel("md-to-docx");
  channel.show(true);
  channel.appendLine(`> ${cli} ${args.join(" ")}`);

  return new Promise((resolve) => {
    const proc = spawn(cli, args, { shell: true });
    let stderr = "";
    proc.stderr.on("data", (d) => {
      const text = d.toString();
      stderr += text;
      channel.append(text);
    });
    proc.stdout.on("data", (d) => channel.append(d.toString()));
    proc.on("close", (code) => resolve({ code: code ?? 1, stderr }));
  });
}

export function activate(context: vscode.ExtensionContext) {
  const disposable = vscode.commands.registerCommand("md-to-docx.export", async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== "markdown") {
      vscode.window.showWarningMessage("Open a Markdown file to export.");
      return;
    }

    const filePath = editor.document.uri.fsPath;
    if (editor.document.isDirty) {
      const saved = await editor.document.save();
      if (!saved) {
        return;
      }
    }

    const { code, stderr } = await runConvert(filePath);
    if (code !== 0) {
      const hint = stderr.includes("not found") || stderr.includes("ENOENT")
        ? " Install with: pip install md2docx-compiler"
        : "";
      vscode.window.showErrorMessage(`md-to-docx failed (exit ${code}).${hint}`);
      return;
    }

    const outDocx = getConfig().outputDir
      ? path.join(getConfig().outputDir, path.basename(filePath).replace(/\.md$/i, ".docx"))
      : filePath.replace(/\.md$/i, ".docx");

    const open = await vscode.window.showInformationMessage(
      `Exported ${path.basename(outDocx)}`,
      "Open DOCX"
    );
    if (open === "Open DOCX") {
      await vscode.env.openExternal(vscode.Uri.file(outDocx));
    }
  });

  context.subscriptions.push(disposable);
}

export function deactivate() {}
