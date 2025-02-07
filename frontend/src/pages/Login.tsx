import terno from "../assets/terno-ai.svg"
import { login } from "../utils/api";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Response, ErrorResponse } from "../utils/types";

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [response, setResponse] = useState({ fetching: false, content: null as Response | ErrorResponse | null })
  const [formError, setFormError] = useState('');
  const navigate = useNavigate();

  const submitLogin = () => {
    setFormError('');
    setResponse({ ...response, fetching: true })
    login({ email, password }).then((content: Response | ErrorResponse) => {
      setResponse((r) => { return { ...r, content } })
      if ('errors' in content) {
        const errors = content.errors;
        if (errors && errors.length > 0) {
          setFormError(errors.map(err => err.message).join(', '));
        }
        return;
      }
      if (content.meta?.is_authenticated) {
        navigate('/');
      }
    }).catch((e) => {
      setFormError(e);
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } });
    })
  }

  const handleSubmit = () => {
      submitLogin();
  };

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
                      <h1 className="text-2xl font-bold">Welcome back</h1>
                      <p className="text-balance text-muted-foreground">
                        Login to your Terno App
                      </p>
                    </div>
                    <div
                      className="flex flex-col gap-6"
                    >
                      <div className="grid gap-2">
                        <label htmlFor="email">Email</label>
                        <input
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          type="email"
                          required
                          placeholder="terno@example.com"
                          className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm"
                        />
                      </div>
                      <div className="grid gap-2">
                        <div className="flex items-center">
                          <label htmlFor="password">Password</label>
                          <a
                            href="/accounts/password/reset"
                            className="ml-auto text-sm underline-offset-2 hover:underline"
                          >
                            Forgot your password?
                          </a>
                        </div>
                        <input
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          type="password"
                          required
                          className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm"
                        />
                      </div>
                      <div className="text-sm text-red-500">
                        {formError}
                      </div>
                      <button
                        onClick={handleSubmit}
                        className="w-full px-4 py-2 border rounded-md bg-slate-800 text-white hover:bg-slate-700 transition-colors"
                      >
                        Login
                      </button>
                    </div>
                  </div>
                </div>
                <div className="hidden bg-zinc-800 md:flex flex-col justify-center items-center">
                  <img src={terno} alt="Image"/>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
