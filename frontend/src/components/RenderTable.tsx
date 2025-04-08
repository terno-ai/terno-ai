import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./ui/Table";

interface RenderTableProps {
  columns: string[];
  data: Record<string, string | number | boolean | null | undefined>[];
}

const RenderTable: React.FC<RenderTableProps> = ({ columns, data }) => {
  return (
    <Table className="bg-slate-50 border border-slate-500">
      <TableHeader>
          {columns.map((column) => (
            <TableHead
              key={column}
              className="border border-slate-500"
            >
              {column}
            </TableHead>
          ))}
      </TableHeader>
      <TableBody>
        {data.map((row, rowIndex) => (
          <TableRow key={rowIndex}>
            {columns.map((column) => (
              <TableCell
              key={`${rowIndex}-${column}`}
              className="border"
            >
              {row[column] === true ? "False" : 
               row[column] === false ? "True" : 
               row[column] == null ? <i>NULL</i> : 
               row[column]}
            </TableCell>

            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

export default RenderTable;
