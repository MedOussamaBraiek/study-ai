export default function Loading() {
  return (
    <div className="flex items-center justify-center h-screen bg-white">
      <div className="flex flex-col items-center gap-4">
        <div className="h-16 w-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-lg font-semibold text-gray-700">
          Analyzing your document...
        </p>
      </div>
    </div>
  );
}
