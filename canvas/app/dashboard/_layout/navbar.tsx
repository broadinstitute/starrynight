export function Navbar() {
  return (
    <div className="px-0 py-4 md:p-4 flex justify-between">
      <div className="inline-flex flex-col">
        <div>
          <span className="font-black">Starrynight.</span>
          <sup className="text-[10px]">Beta</sup>
        </div>
        <span className="text-xs font-light">
          OPS image processing pipeline
        </span>
      </div>
    </div>
  );
}
