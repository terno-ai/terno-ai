import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  }
from './ui/Table'

interface RenderTableProps {
    columns: string[];
    data: Record<string, string | number>[];
}

const RenderTable: React.FC<RenderTableProps> = ({columns, data}) => {
  return (
    <Table>
    <TableCaption>A list of your recent invoices.</TableCaption>
    <TableHeader>
        <TableRow>
        {columns.map((column) => (
            <TableHead key={column}>{column}</TableHead>
        ))}
        </TableRow>
    </TableHeader>
    <TableBody>
        {data.map((row, rowIndex) => (
          <TableRow key={rowIndex}>
            {columns.map((column) => (
              <TableCell key={`${rowIndex}-${column}`}>
                {row[column]}
              </TableCell>
            ))}
          </TableRow>
        ))}
    </TableBody>
    </Table>
  )
}

export default RenderTable