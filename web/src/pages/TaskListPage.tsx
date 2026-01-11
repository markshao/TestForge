import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "../components/ui/button";
import { FileText, Play, CheckCircle, XCircle, Clock, Trash2 } from "lucide-react";
import { tasksApi, type TaskCreate } from "../lib/api";

export function TaskListPage() {
  const queryClient = useQueryClient();
  
  const { data: tasks, isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: tasksApi.list
  });

  const createTaskMutation = useMutation({
    mutationFn: tasksApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    }
  });

  const deleteTaskMutation = useMutation({
    mutationFn: tasksApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    }
  });

  const handleCreateTask = () => {
    // Mock creating a task for now
    const newTask: TaskCreate = {
      name: "New Test Task " + new Date().toLocaleTimeString(),
      description: "Created from web ui",
      yaml_content: `name: "Generated Test"
description: "Auto generated test case"
version: "1.0"
test-env:
  browser: "chromium"
steps:
  - id: 1
    type: action
    content: "Open Page"`
    };
    createTaskMutation.mutate(newTask);
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
        <Button onClick={handleCreateTask} disabled={createTaskMutation.isPending}>
          <Play className="mr-2 h-4 w-4" /> 
          {createTaskMutation.isPending ? "Creating..." : "New Task"}
        </Button>
      </div>

      <div className="bg-white rounded-lg border shadow-sm">
        <div className="grid grid-cols-12 gap-4 p-4 border-b bg-gray-50 font-medium text-sm text-gray-500">
          <div className="col-span-6">Task Name</div>
          <div className="col-span-2">Status</div>
          <div className="col-span-3">Created At</div>
          <div className="col-span-1"></div>
        </div>
        
        {tasks?.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            No tasks found. Create one to get started.
          </div>
        )}

        {tasks?.map((task) => (
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
              {new Date(task.created_at).toLocaleString()}
            </div>
            <div className="col-span-1 text-right flex items-center justify-end gap-2">
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
