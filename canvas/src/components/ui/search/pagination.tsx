import {
  Pagination as ShPagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/src/components/ui/pagination";

export type TPaginationProps = {
  onChange: (page: number) => void;
  totalPages: number;
};

export default function Pagination(props: TPaginationProps) {
  const { onChange, totalPages } = props;

  return (
    <ShPagination>
      <PaginationContent>
        {Array.from({ length: totalPages }).map((_, index) => (
          <PaginationItem key={index}>
            <PaginationLink onClick={() => onChange(index)}>
              {index}
            </PaginationLink>
          </PaginationItem>
        ))}
      </PaginationContent>
    </ShPagination>
  );
}
