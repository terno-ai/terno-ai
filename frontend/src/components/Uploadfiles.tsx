import { useState } from "react";
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../components/ui/AlertDialog";
import CSRFToken from "../utils/csrftoken";
import { fileUpload } from "../utils/api";

const Uploadfiles = ({
  open,
  setOpen,
}: {
  open: boolean;
  setOpen: (open: boolean) => void;
}) => {
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    setFiles(selectedFiles);
  };

  const handleUpload = async () => {
    setOpen(true);
    setLoading(true);
    if (files) {
      const response = await fileUpload(files);
      if (response["status"] == "success") {
        console.log("done");
      } else {
        setError(response["error"]);
      }
    }
    setLoading(false);
  };

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogContent className="bg-white m-2">
        <AlertDialogHeader>
          <AlertDialogTitle className="text-center">
            Add CSV File
          </AlertDialogTitle>
          <AlertDialogDescription>
            <div className="w-[400px]">
              <form method="post">
                <CSRFToken />
                <div className="my-4">
                  <label
                    htmlFor="name"
                    className="my-4 text-black text-base font-semibold leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                  >
                    Choose CSV files to upload:
                  </label>
                  <div className="rounded-md bg-slate-100 hover:drop-shadow-sm focus-within:ring-1 focus-within:ring-sky-500 focus-within:hover:drop-shadow-none">
                    <input type="file" multiple onChange={handleFileInput} />
                  </div>
                </div>

                {error && (
                  <div className="text-red-500 text-sm mt-2">{error}</div>
                )}
                <div className="">
                  <AlertDialogFooter>
                    <AlertDialogCancel
                      onClick={() => setOpen(false)}
                      className="hover:bg-slate-100"
                    >
                      Cancel
                    </AlertDialogCancel>
                    <button
                      type="submit"
                      onClick={handleUpload}
                      className="btn px-4 py-1 text-white border rounded-md bg-slate-800 hover:bg-slate-700 transition-colors"
                    >
                      {loading ? "Submitting..." : "Upload"}
                    </button>
                  </AlertDialogFooter>
                </div>
              </form>
            </div>
          </AlertDialogDescription>
        </AlertDialogHeader>
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default Uploadfiles;
