import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "../components/ui/button";
import { FileText, Play, CheckCircle, XCircle, Clock, Trash2, Plus } from "lucide-react";
import { tasksApi, type TaskCreate } from "../lib/api";

export function TaskListPage() {
  const queryClient = useQueryClient();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newTaskName, setNewTaskName] = useState("");
  const [newTaskContent, setNewTaskContent] = useState(`name: "Baidu Search Test"
steps:
  - content: "Type 'test' in the search box"
  - content: "Click the search button"
test-env:
  base_url: "https://www.baidu.com"
  headless: false
`);

  const { data: tasks, isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: tasksApi.list
  });

  const createTaskMutation = useMutation({
    mutationFn: tasksApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      setIsCreateOpen(false);
      setNewTaskName("");
    }
  });

  const deleteTaskMutation = useMutation({
    mutationFn: tasksApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    }
  });

  const startTaskMutation = useMutation({
    mutationFn: tasksApi.start,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    }
  });

  const handleCreateTask = () => {
    if (!newTaskName || !newTaskContent) return;
    createTaskMutation.mutate({
      name: newTaskName,
      description: "Created via web UI",
      yaml_content: newTaskContent
    });
  };

  const handleTabKey = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const target = e.currentTarget;
      const start = target.selectionStart;
      const end = target.selectionEnd;
      const value = target.value;
      
      // Insert 2 spaces
      const newValue = value.substring(0, start) + "  " + value.substring(end);
      
      // Update state and cursor
      setNewTaskContent(newValue);
      
      // We need to set selection after render, but React state update is async.
      // A simple workaround for controlled inputs is to just update state.
      // To preserve cursor, we might need useEffect or use ref. 
      // But for simple case, let's try just updating state and manually setting cursor in next tick?
      // Actually, standard textarea tab handling in React is tricky.
      // Let's use a simpler approach: update state, and in next render, cursor jumps to end? No.
      // Let's just do the DOM manipulation which is what I did in previous thought, but better:
      
      // Update the value directly in the event to make it immediate (though React might override)
      // target.value = newValue; 
      // target.selectionStart = target.selectionEnd = start + 2;
      // setNewTaskContent(newValue);
      
      // Correct React way:
      setNewTaskContent(newValue);
      setTimeout(() => {
        target.selectionStart = target.selectionEnd = start + 2;
      }, 0);
    }
  };

  if (isLoading) {
    return <div className="p-8">Loading tasks...</div>;
  }

  return (
    <div className="container mx-auto p-8 max-w-5xl">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Tasks</h1>
          <p className="text-gray-500 mt-2">Manage and run your autonomous testing tasks.</p>
        </div>
        <Button onClick={() => setIsCreateOpen(true)}>
          <Plus className="mr-2 h-4 w-4" /> 
          New Task
        </Button>
      </div>

      <div className="bg-white rounded-lg border shadow-sm">
        <div className="grid grid-cols-12 gap-4 p-4 border-b bg-gray-50 font-medium text-sm text-gray-500">
          <div className="col-span-5">Task Name</div>
          <div className="col-span-2">Status</div>
          <div className="col-span-3">Created At</div>
          <div className="col-span-2"></div>
        </div>
        
        {tasks?.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            No tasks found. Create one to get started.
          </div>
        )}

        {tasks?.map((task) => (
          <div key={task.id} className="grid grid-cols-12 gap-4 p-4 border-b last:border-0 items-center hover:bg-gray-50 transition-colors">
            <div className="col-span-5 flex items-center gap-3">
              <div className="p-2 bg-blue-50 text-blue-600 rounded">
                <FileText className="h-5 w-5" />
              </div>
              <span className="font-medium truncate" title={task.name}>{task.name}</span>
            </div>
            <div className="col-span-2">
              <StatusBadge status={task.status} />
            </div>
            <div className="col-span-3 text-sm text-gray-500">
              {new Date(task.created_at).toLocaleString()}
            </div>
            <div className="col-span-2 text-right flex items-center justify-end gap-2">
              {task.status === 'pending' && (
                <Button 
                  variant="ghost" 
                  size="sm"
                  className="text-green-600 hover:text-green-700 hover:bg-green-50"
                  onClick={() => startTaskMutation.mutate(task.id)}
                  disabled={startTaskMutation.isPending}
                >
                  <Play className="h-4 w-4 mr-1" /> Start
                </Button>
              )}
              <Link to={`/tasks/${task.id}`}>
                <Button variant="ghost" size="sm">View</Button>
              </Link>
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-50"
                onClick={() => deleteTaskMutation.mutate(task.id)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        ))}
      </div>

      {/* Create Task Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl flex flex-col max-h-[90vh]">
            <div className="p-6 border-b">
              <h2 className="text-xl font-bold">Create New Task</h2>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1 space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Task Name</label>
                <input 
                  className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  placeholder="e.g. Baidu Search Test"
                  value={newTaskName}
                  onChange={e => setNewTaskName(e.target.value)}
                  autoFocus
                />
              </div>
              
              <div className="flex-1 flex flex-col">
                <label className="block text-sm font-medium mb-1 text-gray-700">Testcase Content (YAML)</label>
                <p className="text-xs text-gray-500 mb-2">Use 2 spaces for indentation. Press Tab to insert spaces.</p>
                <textarea 
                  className="w-full border rounded px-3 py-2 font-mono text-sm min-h-[300px] flex-1 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  value={newTaskContent}
                  onChange={e => setNewTaskContent(e.target.value)}
                  onKeyDown={handleTabKey}
                  spellCheck={false}
                />
              </div>
            </div>
            
            <div className="p-6 border-t bg-gray-50 flex justify-end gap-3 rounded-b-lg">
              <Button variant="ghost" onClick={() => setIsCreateOpen(false)}>Cancel</Button>
              <Button onClick={handleCreateTask} disabled={createTaskMutation.isPending || !newTaskName.trim()}>
                {createTaskMutation.isPending ? "Creating..." : "Create Task"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  if (status === "completed") {
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
  if (status === "pending") {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
        <Clock className="h-3 w-3" /> Pending
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
      <XCircle className="h-3 w-3" /> {status}
    </span>
  );
}
