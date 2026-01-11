import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Terminal, PlayCircle, CheckCircle2, AlertCircle, FileText, Loader2, Image as ImageIcon } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { cn } from "../lib/utils";
import { tasksApi } from "../lib/api";
import { useEffect } from "react";

// Assuming backend URL is http://localhost:8000, but in dev it might be proxied or direct
const API_BASE_URL = "http://localhost:8000";

export function TaskDetailPage() {
  const { id } = useParams();
  const queryClient = useQueryClient();

  const { data: task, isLoading: isTaskLoading } = useQuery({
    queryKey: ['task', id],
    queryFn: () => tasksApi.get(id!),
    refetchInterval: (query) => {
      // Also refetch task to update step status
      // We need to check the data status, not the query status
      const status = query.state.data?.status;
      return status === 'running' || status === 'pending' ? 1000 : false;
    }
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
        
        {/* Left: Test Case Steps */}
        <div className="w-1/4 border-r bg-white flex flex-col min-w-[300px]">
          <div className="px-4 py-3 border-b bg-gray-50 font-medium text-xs text-gray-500 uppercase tracking-wider flex items-center gap-2">
            <FileText className="h-3 w-3" /> Test Steps
          </div>
          <div className="flex-1 overflow-auto p-0">
             {task.steps && task.steps.length > 0 ? (
               <div className="divide-y">
                 {task.steps.map((step: any, index: number) => (
                   <div 
                    key={index} 
                    className={cn(
                      "p-4 text-sm transition-colors",
                      step.status === "running" && "bg-yellow-50",
                      step.status === "completed" && "bg-green-50",
                      step.status === "error" && "bg-red-50",
                    )}
                   >
                     <div className="flex items-start gap-3">
                       <div className={cn(
                         "flex items-center justify-center w-6 h-6 rounded-full text-xs font-medium shrink-0",
                         step.status === "completed" ? "bg-green-100 text-green-700" :
                         step.status === "running" ? "bg-yellow-100 text-yellow-700" :
                         step.status === "error" ? "bg-red-100 text-red-700" :
                         "bg-gray-100 text-gray-500"
                       )}>
                         {index + 1}
                       </div>
                       <div className="flex-1 space-y-1">
                         <p className={cn(
                           "leading-snug",
                           step.status === "completed" && "text-gray-900",
                           step.status === "pending" && "text-gray-500"
                         )}>
                           {step.content}
                         </p>
                         <div className="flex items-center gap-2">
                            <span className={cn(
                              "text-[10px] uppercase font-bold tracking-wider",
                              step.status === "completed" ? "text-green-600" :
                              step.status === "running" ? "text-yellow-600" :
                              step.status === "error" ? "text-red-600" :
                              "text-gray-400"
                            )}>
                              {step.status}
                            </span>
                            {step.screenshot && (
                              <span className="text-[10px] text-gray-400 flex items-center gap-1">
                                <ImageIcon className="h-3 w-3" /> Screenshot captured
                              </span>
                            )}
                         </div>
                       </div>
                     </div>
                   </div>
                 ))}
               </div>
             ) : (
                <div className="p-4">
                  <pre className="text-xs font-mono text-gray-600 whitespace-pre-wrap">{task.yaml_content}</pre>
                </div>
             )}
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
              <div 
                key={cell.id} 
                className={cn(
                  "rounded-lg border shadow-sm overflow-hidden group transition-colors",
                  cell.status === "running" && "bg-yellow-50 border-yellow-200",
                  cell.status === "success" && "bg-green-50 border-green-200",
                  cell.status === "error" && "bg-red-50 border-red-200",
                  !["running", "success", "error"].includes(cell.status) && "bg-white"
                )}
              >
                {/* Cell Header */}
                <div className={cn(
                  "px-3 py-1.5 border-b flex items-center justify-between",
                  cell.status === "running" ? "bg-yellow-100/50" :
                  cell.status === "success" ? "bg-green-100/50" :
                  cell.status === "error" ? "bg-red-100/50" : "bg-gray-50"
                )}>
                  <span className="text-xs font-mono text-gray-500">In [{cell.id}]</span>
                  <CellStatus status={cell.status} />
                </div>
                
                {/* Code Block */}
                <div className="p-3 bg-transparent">
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

        {/* Right: Step Screenshots (Replaces System Logs) */}
        <div className="w-1/4 border-l bg-gray-100 flex flex-col min-w-[300px]">
          <div className="px-4 py-3 border-b bg-white font-medium text-xs text-gray-500 uppercase tracking-wider flex items-center gap-2">
            <ImageIcon className="h-3 w-3" /> Execution Snapshots
          </div>
          <div className="flex-1 overflow-auto p-4 space-y-6">
             {task.steps && task.steps.filter((s: any) => s.screenshot).length > 0 ? (
               task.steps.filter((s: any) => s.screenshot).map((step: any, index: number) => (
                 <div key={index} className="space-y-2">
                   <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
                     <span className="flex items-center justify-center w-5 h-5 rounded-full bg-green-100 text-green-700 text-xs">
                       {step.index + 1}
                     </span>
                     <span className="truncate" title={step.content}>{step.content}</span>
                   </div>
                   <div className="rounded-lg border bg-white p-1 shadow-sm overflow-hidden hover:shadow-md transition-shadow cursor-pointer" onClick={() => window.open(API_BASE_URL + step.screenshot, '_blank')}>
                     <img 
                      src={API_BASE_URL + step.screenshot} 
                      alt={`Step ${step.index + 1} Screenshot`}
                      className="w-full h-auto rounded bg-gray-50"
                      loading="lazy"
                     />
                   </div>
                 </div>
               ))
             ) : (
               <div className="text-center text-gray-400 mt-20 text-sm italic">
                 Screenshots will appear here as steps complete...
               </div>
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
