import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "./ui/react-accordian";

interface ColumnData {
  public_name: string,
  data_type: string
}

interface TableData {
  table_name: string,
  column_data: ColumnData[]
}

interface RenderTableColumnProps {
  data: TableData[];
}

const TableColumnAccordian: React.FC<RenderTableColumnProps> = ({data}) => {
  return (
    <Accordion type="multiple" className="w-full">
      {data.map((t_data: TableData, index) => (
        <AccordionItem value={index.toString()}>
          <AccordionTrigger className="text-cyan-500">{t_data['table_name']}</AccordionTrigger>
          <AccordionContent>
            {t_data.column_data.map((c_data: ColumnData, idx) => (
              <div key={idx.toString()} className="flex flex-row justify-between text-xs leading-5">
                <div className="text-gray-800">
                  {c_data['public_name']}
                </div>
                <div className="text-gray-400">
                  {c_data['data_type']}
                </div>
              </div>
            ))}
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  );
};

export default TableColumnAccordian;
