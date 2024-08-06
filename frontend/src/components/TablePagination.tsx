import ReactPaginate from 'react-paginate';

interface PaginatedListProps {
  totalPages: number;
  onSelect: (value: number) => Promise<void>;
}

const PaginatedList: React.FC<PaginatedListProps> = ({ totalPages, onSelect }) => {
  const handlePageClick = (event: any) => {
    onSelect(event.selected+1);
  };

  return (
    <div className='w-full m-5 pb-10 flex flex-row justify-center items-center list-none'>
      <ReactPaginate
        previousLabel={'Previous'}
        nextLabel={'Next'}
        breakLabel={'...'}
        breakClassName={'break'}
        pageCount={Math.ceil(totalPages)}
        marginPagesDisplayed={2}
        pageRangeDisplayed={3}
        onPageChange={handlePageClick}
        containerClassName={'flex flex-row gap-5'}
        activeLinkClassName={'px-3 py-2 rounded border'}
        pageLinkClassName={'px-3 py-2 rounded hover:bg-slate-200'}
        previousLinkClassName={'px-3 py-2 rounded hover:bg-slate-200'}
        nextLinkClassName={'px-3 py-2 rounded hover:bg-slate-200'}
        renderOnZeroPageCount={null}
      />
    </div>
  );
};

export default PaginatedList;
