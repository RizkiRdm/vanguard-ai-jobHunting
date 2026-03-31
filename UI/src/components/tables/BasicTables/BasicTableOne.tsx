import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "../../ui/table";
import Badge from "../../ui/badge/Badge";
import { useAgentStore } from "../../../store/useAgentStore";

export default function BasicTableOne() {
  const tasks = useAgentStore((state) => state.tasks);

  // Helper untuk menentukan warna badge berdasarkan status bot
  const getStatusColor = (status: string) => {
    switch (status) {
      case "RUNNING":
        return "success"; // Hijau
      case "AWAITING_USER":
        return "warning"; // Kuning
      case "FAILED":
        return "error"; // Merah
      default:
        return "light"; // Abu-abu
    }
  };

  return (
    <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-white/10 dark:bg-white/[0.03]">
      <div className="max-w-full overflow-x-auto">
        <Table>
          {/* Table Header sesuai dengan wireframe UX_doc.md */}
          <TableHeader className="border-b border-gray-100 dark:border-white/10">
            <TableRow>
              <TableCell isHeader className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400">
                Task ID
              </TableCell>
              <TableCell isHeader className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400">
                Type
              </TableCell>
              <TableCell isHeader className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400">
                Status
              </TableCell>
              <TableCell isHeader className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400">
                Action
              </TableCell>
            </TableRow>
          </TableHeader>

          {/* Table Body - Mapping dari Agent Store */}
          <TableBody className="divide-y divide-gray-100 dark:divide-white/10">
            {tasks.length > 0 ? (
              tasks.map((task) => (
                <TableRow key={task.id}>
                  <TableCell className="px-5 py-4 text-gray-500 text-start text-theme-sm dark:text-gray-400">
                    <span className="font-medium text-gray-800 dark:text-white/90">
                      {task.id.substring(0, 8)}...
                    </span>
                  </TableCell>
                  <TableCell className="px-5 py-4 text-gray-500 text-start text-theme-sm dark:text-gray-400">
                    {task.task_type}
                  </TableCell>
                  <TableCell className="px-5 py-4 text-start">
                    <Badge size="sm" color={getStatusColor(task.status)}>
                      {task.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="px-5 py-4 text-gray-500 text-start text-theme-sm dark:text-gray-400">
                    <button
                      className="text-primary hover:underline font-medium"
                      onClick={() => console.log("Opening stream for:", task.id)}
                    >
                      View Stream
                    </button>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell className="px-5 py-10 text-center text-gray-500 text-theme-sm">
                  No active tasks. Start a new job hunt from the dashboard.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}