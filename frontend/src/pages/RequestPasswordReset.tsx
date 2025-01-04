import { useState } from "react";
import { requestPasswordReset } from "../utils/api";
import { Link } from "react-router-dom";
import terno from "../assets/terno-ai.svg";
import { Response, ErrorResponse } from "../utils/types";

const RequestPasswordReset = () => {
  const [email, setEmail] = useState("");
  const [formError, setFormError] = useState("");
  const [resetLinkSent, setResetLinkSent] = useState(false);
  const [response, setResponse] = useState({
    fetching: false,
    content: null as Response | ErrorResponse | null,
  });

  function submit() {
    setResponse({ ...response, fetching: true });
    requestPasswordReset({'email': email})
      .then((content) => {
        setResponse((r) => {
          return { ...r, content };
        });
        setResetLinkSent(true);
      })
      .catch((e) => {
        setFormError(e);
      })
      .then(() => {
        setResponse((r) => {
          return { ...r, fetching: false };
        });
      });
  }

  return (
    <div className="w-screen h-screen bg-stone-100">
      <div className="flex min-h-svh flex-col items-center justify-center bg-muted p-6 md:p-10 overflow-scroll">
        <div className="w-full max-w-sm md:max-w-3xl">
          <div className="flex flex-col gap-6">
            <div className="rounded-xl border bg-white text-card-foreground shadow overflow-hidden">
              <div className="grid p-0 md:grid-cols-2">
                <div className="p-6 md:p-8">
                  <div className="flex flex-col gap-6">
                    <div className="flex flex-col items-center text-center">
                      <h1 className="text-2xl font-bold">Reset Password</h1>
                    </div>
                    {resetLinkSent ? (
                      <div className="flex flex-col gap-4 text-center">
                        Password reset sent.
                      </div>
                    ) : (
                      <div className="flex flex-col gap-4">
                        <div className="grid gap-2">
                          <label htmlFor="email">Email</label>
                          <input
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            type="email"
                            required
                            className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm"
                          />
                        </div>
                        <div className="text-sm text-red-500">{formError}</div>
                        <button
                          onClick={submit}
                          className="w-full px-4 py-2 border rounded-md bg-slate-800 text-white hover:bg-slate-700 transition-colors"
                        >
                          Submit
                        </button>
                      </div>
                    )}
                    <div className="text-center text-sm">
                      Remember your password?{" "}
                      <Link
                        to="/accounts/login"
                        className="underline underline-offset-4"
                      >
                        Back to login.
                      </Link>
                    </div>
                  </div>
                </div>
                <div className="hidden bg-zinc-800 md:flex flex-col justify-center items-center">
                  <img src={terno} alt="Image" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RequestPasswordReset;
