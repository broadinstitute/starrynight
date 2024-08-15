"use client";
import { SearchIcon } from "lucide-react";
import React from "react";
import { useDebounce } from "./utils";

export type TSearchProps = {
  /**
   * To set the initial value of search.
   */
  value: string;
  /**
   * Callback when search value changes.
   *
   ** Make sure to wrap this function in `useCallback` to prevent unnecessary re-renders.
   */
  onSearch: (value: string) => void;
};

let hasSearchKeywordChanged = false;

export default function Search(props: TSearchProps) {
  const { value: _value = "", onSearch } = props;

  const [value, setValue] = React.useState(_value);
  const [debouncedQuery] = useDebounce(value, 300);

  React.useEffect(() => {
    if (hasSearchKeywordChanged) {
      onSearch(debouncedQuery);
    }
  }, [debouncedQuery, onSearch]);

  React.useEffect(() => {
    return () => {
      hasSearchKeywordChanged = false;
    };
  }, []);

  return (
    <label className="flex border-slate-400 border rounded-sm p-3">
      <SearchIcon className="mr-4" />
      <input
        className="outline-none bg-transparent flex-1"
        type="text"
        placeholder="Search..."
        value={value}
        onChange={(e) => {
          setValue(e.target.value);
          hasSearchKeywordChanged = true;
        }}
      />
    </label>
  );
}
