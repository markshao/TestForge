import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { FileText, Play, CheckCircle, XCircle, Clock } from "lucide-react";

// Mock Data
const TASKS = [
  { id: "1", name: "Google Search Test", status: "finished", date: "2023-10-27 10:00" },
  { id: "2", name: "Baidu Search Test", status: "running", date: "2023-10-27 11:30" },
  { id: "3", name: "Login Flow", status: "error", date: "2023-10-26 15:45" },
];

export function TaskListPage() {
  return (
    <div className="container mx-auto p-8 max-w-5xl">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Tasks</h1>
          <p className="text-gray-500 mt-2">Manage and run your autonomous testing tasks.</p>
        </div>
        <Button>
          <Play className="mr-2 h-4 w-4" /> New Task
        </Button>
      </div>

      <div className="bg-white rounded-lg border shadow-sm">
        <div className="grid grid-cols-12 gap-4 p-4 border-b bg-gray-50 font-medium text-sm text-gray-500">
          <div className="col-span-6">Task Name</div>
          <div className="col-span-2">Status</div>
          <div className="col-span-3">Created At</div>
          <div className="col-span-1"></div>
        </div>
        
        {TASKS.map((task) => (
          <div key={task.id} className="grid grid-cols-12 gap-4 p-4 border-b last:border-0 items-center hover:bg-gray-50 transition-colors">
            <div className="col-span-6 flex items-center gap-3">
              <div className="p-2 bg-blue-50 text-blue-600 rounded">
                <FileText className="h-5 w-5" />
              </div>
              <span className="font-medium">{task.name}</span>
            </div>
            <div className="col-span-2">
              <StatusBadge status={task.status} />
            </div>
            <div className="col-span-3 text-sm text-gray-500">
              {task.date}
            </div>
            <div className="col-span-1 text-right">
              <Link to={`/tasks/${task.id}`}>
                <Button variant="ghost" size="sm">View</Button>
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  if (status === "finished") {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
        <CheckCircle className="h-3 w-3" /> Finished
      </span>
    );
  }
  if (status === "running") {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
        <Clock className="h-3 w-3 animate-spin" /> Running
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
      <XCircle className="h-3 w-3" /> Error
    </span>
  );
}
