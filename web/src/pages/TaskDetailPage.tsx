import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Terminal, PlayCircle, CheckCircle2, AlertCircle, FileText, Loader2 } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { cn } from "../lib/utils";
import { tasksApi } from "../lib/api";
import { useEffect } from "react";

export function TaskDetailPage() {
  const { id } = useParams();
  const queryClient = useQueryClient();

  const { data: task, isLoading: isTaskLoading } = useQuery({
    queryKey: ['task', id],
    queryFn: () => tasksApi.get(id!)
  });

  const { data: execution, isLoading: isExecutionLoading } = useQuery({
    queryKey: ['execution', id],
    queryFn: () => tasksApi.getExecution(id!),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'running' || status === 'pending' ? 1000 : false;
    },
    enabled: !!task
  });

  const startMutation = useMutation({
    mutationFn: tasksApi.start,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['task', id] });
      queryClient.invalidateQueries({ queryKey: ['execution', id] });
    }
  });

  if (isTaskLoading) return <div>Loading...</div>;
  if (!task) return <div>Task not found</div>;

  const isRunning = task.status === 'running' || task.status === 'pending';

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
            <h1 className="font-semibold text-sm">{task.name}</h1>
            <p className="text-xs text-gray-500">Task ID: {id}</p>
          </div>
          <StatusBadge status={task.status} />
        </div>
        <div className="flex items-center gap-2">
           {isRunning && <Button size="sm" variant="outline">Stop</Button>}
           <Button 
             size="sm" 
             onClick={() => startMutation.mutate(id!)}
             disabled={isRunning || startMutation.isPending}
           >
             {isRunning ? 'Running...' : 'Run Test'}
           </Button>
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
            <pre className="text-xs font-mono text-gray-600 whitespace-pre-wrap">{task.yaml_content}</pre>
          </div>
        </div>

        {/* Middle: Live Execution */}
        <div className="flex-1 flex flex-col min-w-[400px] bg-gray-50/50">
          <div className="px-4 py-3 border-b bg-white font-medium text-xs text-gray-500 uppercase tracking-wider flex items-center gap-2">
            <PlayCircle className="h-3 w-3" /> Live Execution
          </div>
          <div className="flex-1 overflow-auto p-6 space-y-4">
            {execution?.cells.length === 0 && (
               <div className="text-center text-gray-400 mt-20 text-sm">
                 Ready to start execution...
               </div>
            )}
            
            {execution?.cells.map((cell) => (
              <div key={cell.id} className="bg-white rounded-lg border shadow-sm overflow-hidden group">
                {/* Cell Header */}
                <div className="bg-gray-50 px-3 py-1.5 border-b flex items-center justify-between">
                  <span className="text-xs font-mono text-gray-500">In [{cell.id}]</span>
                  <CellStatus status={cell.status} />
                </div>
                
                {/* Code Block */}
                <div className="p-3 bg-white">
                  <pre className="text-sm font-mono text-gray-800 whitespace-pre-wrap">{cell.code}</pre>
                </div>

                {/* Output Block */}
                {cell.output && (
                  <div className="border-t bg-gray-50/50 p-3">
                    <pre className="text-xs font-mono text-gray-600 whitespace-pre-wrap">{cell.output}</pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Right: System Logs */}
        <div className="w-1/4 border-l bg-[#1e1e1e] flex flex-col min-w-[300px]">
          <div className="px-4 py-3 border-b border-gray-700 bg-[#252526] font-medium text-xs text-gray-400 uppercase tracking-wider flex items-center gap-2">
            <Terminal className="h-3 w-3" /> System Logs
          </div>
          <div className="flex-1 overflow-auto p-4 font-mono text-xs space-y-1">
             {execution?.logs.map((log, i) => (
               <div key={i} className="flex gap-2">
                 <span className="text-gray-500 shrink-0">
                   [{new Date(log.timestamp).toLocaleTimeString()}]
                 </span>
                 <span className={cn(
                   "break-all",
                   log.level === "INFO" && "text-blue-400",
                   log.level === "ERROR" && "text-red-400",
                   log.level === "WARNING" && "text-yellow-400"
                 )}>
                   {log.message}
                 </span>
               </div>
             ))}
             {execution?.logs.length === 0 && (
               <div className="text-gray-600 italic">Waiting for logs...</div>
             )}
          </div>
        </div>

      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  if (status === "completed") {
    return (
      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-100">
        <CheckCircle2 className="h-3 w-3" /> Finished
      </span>
    );
  }
  if (status === "running" || status === "pending") {
    return (
      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-100">
        <Loader2 className="h-3 w-3 animate-spin" /> {status === 'running' ? 'Running' : 'Pending'}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-100">
      <AlertCircle className="h-3 w-3" /> {status}
    </span>
  );
}

function CellStatus({ status }: { status: string }) {
  if (status === "success") return <CheckCircle2 className="h-3 w-3 text-green-500" />;
  if (status === "running") return <Loader2 className="h-3 w-3 text-blue-500 animate-spin" />;
  if (status === "error") return <AlertCircle className="h-3 w-3 text-red-500" />;
  return <div className="h-2 w-2 rounded-full bg-gray-300" />;
}
