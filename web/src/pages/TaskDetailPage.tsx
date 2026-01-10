import { useParams } from "react-router-dom";
import { ArrowLeft, Terminal, PlayCircle, CheckCircle2, AlertCircle, FileText } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { cn } from "../lib/utils";

// Mock Data
const MOCK_TESTCASE = `name: "Google Search Test"
description: "Verify that Google search works correctly"
version: "1.0"

test-env:
  base_url: "https://www.google.com"
  browser: "chromium"
  viewport: { width: 1280, height: 720 }
  headless: false
  timeout: 30000

steps:
  - id: 1
    type: action
    content: "Open Home Page"

  - id: 2
    type: action
    content: "Search for 'Playwright'"
`;

const MOCK_LOGS = [
  "[10:00:01] INFO: Starting session...",
  "[10:00:02] INFO: Browser launched (chromium)",
  "[10:00:03] INFO: Navigating to https://www.google.com",
  "[10:00:05] INFO: Page loaded successfully",
  "[10:00:06] INFO: Finding search box...",
];

const MOCK_CELLS = [
  {
    id: "cell-1",
    status: "success",
    code: `from playwright.async_api import async_playwright
p = await async_playwright().start()
browser = await p.chromium.launch(headless=False)
page = await browser.new_page()`,
    output: "Browser launched successfully."
  },
  {
    id: "cell-2",
    status: "running",
    code: `await page.goto("https://www.google.com")
print(f"Navigated to {page.url}")`,
    output: ""
  },
  {
    id: "cell-3",
    status: "pending",
    code: `# Generating code for step 2...`,
    output: ""
  }
];

export function TaskDetailPage() {
  const { id } = useParams();

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b px-6 py-3 flex items-center justify-between shrink-0 h-14">
        <div className="flex items-center gap-4">
          <Link to="/" className="text-gray-500 hover:text-gray-900">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div className="h-6 w-px bg-gray-200" />
          <div>
            <h1 className="font-semibold text-sm">Google Search Test</h1>
            <p className="text-xs text-gray-500">Task ID: {id}</p>
          </div>
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-100">
            <PlayCircle className="h-3 w-3" /> Running
          </span>
        </div>
        <div className="flex items-center gap-2">
           <Button size="sm" variant="outline">Stop</Button>
           <Button size="sm">Rerun</Button>
        </div>
      </header>

      {/* Main Content - 3 Column Layout */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left: Test Case YAML */}
        <div className="w-1/4 border-r bg-white flex flex-col min-w-[300px]">
          <div className="px-4 py-3 border-b bg-gray-50 font-medium text-xs text-gray-500 uppercase tracking-wider flex items-center gap-2">
            <FileText className="h-3 w-3" /> Test Case
          </div>
          <div className="flex-1 overflow-auto p-4">
            <pre className="text-xs font-mono text-gray-600 whitespace-pre-wrap">{MOCK_TESTCASE}</pre>
          </div>
        </div>

        {/* Middle: Execution Notebook */}
        <div className="flex-1 flex flex-col bg-gray-50/50 min-w-[400px]">
           <div className="px-4 py-3 border-b bg-white font-medium text-xs text-gray-500 uppercase tracking-wider flex items-center gap-2">
            <Terminal className="h-3 w-3" /> Live Execution
          </div>
          <div className="flex-1 overflow-auto p-6 space-y-6">
            {MOCK_CELLS.map((cell) => (
              <div key={cell.id} className="bg-white rounded-lg border shadow-sm overflow-hidden">
                {/* Cell Header / Status */}
                <div className="px-3 py-2 border-b bg-gray-50/50 flex items-center justify-between">
                   <div className="flex items-center gap-2">
                      <div className={cn("w-2 h-2 rounded-full", {
                        "bg-green-500": cell.status === "success",
                        "bg-yellow-500 animate-pulse": cell.status === "running",
                        "bg-gray-300": cell.status === "pending"
                      })} />
                      <span className="text-xs font-medium text-gray-600 uppercase">{cell.status}</span>
                   </div>
                   <span className="text-xs font-mono text-gray-400">{cell.id}</span>
                </div>
                {/* Code Block */}
                <div className="p-4 bg-[#f8f9fa] border-b">
                  <pre className="text-sm font-mono text-gray-800 whitespace-pre-wrap">{cell.code}</pre>
                </div>
                {/* Output Block (if any) */}
                {(cell.output || cell.status === "success") && (
                  <div className="p-3 bg-white text-xs font-mono text-gray-600 border-l-4 border-gray-100 ml-0">
                    {cell.output}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Right: Logs */}
        <div className="w-1/4 border-l bg-white flex flex-col min-w-[250px]">
          <div className="px-4 py-3 border-b bg-gray-50 font-medium text-xs text-gray-500 uppercase tracking-wider flex items-center gap-2">
            <LogsIcon className="h-3 w-3" /> System Logs
          </div>
          <div className="flex-1 overflow-auto p-4 bg-[#1e1e1e]">
            {MOCK_LOGS.map((log, i) => (
              <div key={i} className="text-xs font-mono text-gray-300 mb-1 font-light">
                {log}
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}

function FileIcon({ className }: { className?: string }) {
  return (
    <svg className={className} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  )
}

function LogsIcon({ className }: { className?: string }) {
  return (
    <svg className={className} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  )
}
