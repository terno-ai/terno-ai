import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "./ui/react-accordian";

interface RenderTableColumnProps {
  data: string[];
}

const TableColumnAccordian: React.FC<RenderTableColumnProps> = ({data}) => {
  return (
    <Accordion type="multiple" className="w-full">
      {data.map((row, rowIndex) => (
          <AccordionItem value={rowIndex.toString()}>
          <AccordionTrigger>{row}</AccordionTrigger>
          <AccordionContent>
            Yes. It adheres to the WAI-ARIA design pattern.
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  );
};

export default TableColumnAccordian;