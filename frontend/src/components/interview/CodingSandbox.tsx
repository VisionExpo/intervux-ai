import { useState, useCallback } from "react";
import Editor from "@monaco-editor/react";

interface TestCase {
  input: string;
  expectedOutput: string;
}

interface CodingSandboxProps {
  initialCode?: string;
  language?: string;
  problemDescription?: string;
  onRunCode?: (code: string, language: string) => Promise<{ output: string; success: boolean }>;
}

const LANGUAGE_OPTIONS = [
  { value: "python", label: "Python" },
  { value: "javascript", label: "JavaScript" },
  { value: "java", label: "Java" },
  { value: "cpp", label: "C++" },
  { value: "csharp", label: "C#" },
  { value: "go", label: "Go" },
  { value: "rust", label: "Rust" },
];

const DEFAULT_CODE: Record<string, string> = {
  python: `# Write your solution here
def two_sum(nums, target):
    """
    Find two numbers that add up to target.
    Return their indices (1-indexed).
    """
    pass

# Example:
# nums = [2, 7, 11, 15], target = 9
# Output: [1, 2]
`,
  javascript: `// Write your solution here
function twoSum(nums, target) {
    // Find two numbers that add up to target
    // Return their indices (1-indexed)
}

// Example:
// nums = [2, 7, 11, 15], target = 9
// Output: [1, 2]
`,
  java: `// Write your solution here
class Solution {
    public int[] twoSum(int[] nums, int target) {
        // Find two numbers that add up to target
        // Return their indices (1-indexed)
        return new int[]{};
    }
}
`,
  cpp: `// Write your solution here
#include <vector>
using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        // Find two numbers that add up to target
        // Return their indices (1-indexed)
        return {};
    }
};
`,
};

export default function CodingSandbox({
  initialCode = "",
  language: initialLanguage = "python",
  problemDescription = "Implement a function that finds two numbers that add up to a target.",
  onRunCode,
}: CodingSandboxProps) {
  const [language, setLanguage] = useState(initialLanguage);
  const [code, setCode] = useState(initialCode || DEFAULT_CODE[initialLanguage] || "");
  const [output, setOutput] = useState<string>("");
  const [isRunning, setIsRunning] = useState(false);
  const [showTestCases, setShowTestCases] = useState(false);

  const testCases: TestCase[] = [
    { input: "nums = [2, 7, 11, 15], target = 9", expectedOutput: "[1, 2]" },
    { input: "nums = [3, 2, 4], target = 6", expectedOutput: "[2, 3]" },
    { input: "nums = [3, 3], target = 6", expectedOutput: "[1, 2]" },
  ];

  const handleLanguageChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLang = e.target.value;
    setLanguage(newLang);
    if (!initialCode) {
      setCode(DEFAULT_CODE[newLang] || "");
    }
  }, [initialCode]);

  const handleRunCode = useCallback(async () => {
    setIsRunning(true);
    setOutput("Running...");

    try {
      if (onRunCode) {
        const result = await onRunCode(code, language);
        setOutput(result.output);
      } else {
        // Simulate running for demo purposes
        await new Promise((resolve) => setTimeout(resolve, 1000));
        setOutput("Code executed successfully!\n\nNote: Connect to a code execution backend to run actual code.");
      }
    } catch (error) {
      setOutput(`Error: ${error instanceof Error ? error.message : "Unknown error"}`);
    } finally {
      setIsRunning(false);
    }
  }, [code, language, onRunCode]);

  const getMonacoLanguage = () => {
    const langMap: Record<string, string> = {
      python: "python",
      javascript: "javascript",
      java: "java",
      cpp: "cpp",
      csharp: "csharp",
      go: "go",
      rust: "rust",
    };
    return langMap[language] || "plaintext";
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      {/* Toolbar */}
      <div className="coding-toolbar">
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <select
            value={language}
            onChange={handleLanguageChange}
            className="language-select"
          >
            {LANGUAGE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <button
            onClick={handleRunCode}
            disabled={isRunning}
            className="run-button"
          >
            {isRunning ? "Running..." : "▶ Run Code"}
          </button>
        </div>
        <button
          onClick={() => setShowTestCases(!showTestCases)}
          style={{
            background: "transparent",
            border: "1px solid #4b5563",
            color: "#e0e0e0",
            padding: "0.375rem 0.75rem",
            borderRadius: "6px",
            fontSize: "0.75rem",
            cursor: "pointer",
          }}
        >
          {showTestCases ? "Hide Test Cases" : "Show Test Cases"}
        </button>
      </div>

      {/* Problem Description */}
      <div
        style={{
          padding: "0.75rem 1rem",
          background: "#1e293b",
          borderBottom: "1px solid #334155",
          fontSize: "0.8rem",
          color: "#94a3b8",
        }}
      >
        <strong style={{ color: "#e2e8f0" }}>Problem: </strong>
        {problemDescription}
      </div>

      {/* Monaco Editor */}
      <div style={{ flex: 1, minHeight: "200px" }}>
        <Editor
          height="100%"
          language={getMonacoLanguage()}
          value={code}
          onChange={(value: string | undefined) => setCode(value || "")}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: "on",
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            wordWrap: "on",
            padding: { top: 10 },
          }}
        />
      </div>

      {/* Test Cases Panel */}
      {showTestCases && (
        <div
          style={{
            borderTop: "1px solid #334155",
            background: "#1e1e1e",
            maxHeight: "150px",
            overflow: "auto",
          }}
        >
          <div style={{ padding: "0.5rem 1rem", color: "#94a3b8", fontSize: "0.75rem", fontWeight: 600 }}>
            Test Cases
          </div>
          {testCases.map((tc, idx) => (
            <div
              key={idx}
              style={{
                padding: "0.5rem 1rem",
                borderBottom: "1px solid #2d2d2d",
                fontSize: "0.75rem",
                fontFamily: "monospace",
              }}
            >
              <div style={{ color: "#e2e8f0" }}>Input: {tc.input}</div>
              <div style={{ color: "#22c55e" }}>Expected: {tc.expectedOutput}</div>
            </div>
          ))}
        </div>
      )}

      {/* Output Panel */}
      <div
        style={{
          borderTop: "1px solid #334155",
          background: "#0f172a",
          padding: "0.75rem 1rem",
          fontSize: "0.8rem",
          fontFamily: "monospace",
          color: output.includes("Error") ? "#ef4444" : "#22c55e",
          whiteSpace: "pre-wrap",
          minHeight: "60px",
          maxHeight: "100px",
          overflow: "auto",
        }}
      >
        {output || "Output will appear here..."}
      </div>
    </div>
  );
}

