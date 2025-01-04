import CSRFToken from "../utils/csrftoken";
import { FcGoogle } from "react-icons/fc";
import terno from "../assets/terno-ai.svg"
import { checkUserExists, login } from "../utils/api";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Response, ErrorResponse } from "../utils/types";

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [response, setResponse] = useState({ fetching: false, content: null as Response | ErrorResponse | null })
  const [formError, setFormError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [submitBtnText, setSubmitBtnText] = useState('Continue');
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

      const verifyEmailFlow = content.data?.flows?.find(
        flow => flow.id === 'verify_email' && flow.is_pending
      );

      if (verifyEmailFlow) {
        navigate('/accounts/verify-email');
      }
      else if (content.meta?.is_authenticated) {
        navigate('/');
      }
    }).catch((e) => {
      setFormError(e);
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } });
    })
  }

  const checkEmail = async () => {
    setFormError('');
    setResponse({ ...response, fetching: true });
    try {
      const content = await checkUserExists({'email': email})

      if (content['status'] == 'error') {
        setFormError('Please contact your organization administrator for access.');
        return;
      }

      setShowPassword(true);
      setSubmitBtnText('Login');
    } catch (e) {
      setFormError('An error occurred. Please try again.');
    } finally {
      setResponse((r) => ({ ...r, fetching: false }));
    }
  };

  const handleSubmit = () => {
    if (!showPassword) {
      checkEmail();
    } else {
      submitLogin();
    }
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
                    <div className="flex flex-row">
                      <form
                        method="post"
                        action="/_allauth/browser/v1/auth/provider/redirect?process=login&next=/"
                        className="w-full"
                      >
                        <CSRFToken />
                        <input name="provider" value={"google"} type="hidden" />
                        <input name="process" value={"login"} type="hidden" />
                        <input name="callback_url" value={"/accounts/provider/callback"} type="hidden" />
                        <button className="w-full flex flex-row justify-center items-center gap-2 px-4 py-2 border rounded-md shadow hover:bg-zinc-100 transition-colors">
                          <FcGoogle />
                          <span className="">Login with Google</span>
                        </button>
                      </form>
                    </div>
                    <div className="relative text-center text-sm after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t after:border-border">
                      <span className="bg-white relative z-10 bg-background px-2 text-muted-foreground">
                        Or continue with
                      </span>
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
                      {showPassword && (
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
                    )}
                      <div className="text-sm text-red-500">
                        {formError}
                      </div>
                      <button
                        onClick={handleSubmit}
                        className="w-full px-4 py-2 border rounded-md bg-slate-800 text-white hover:bg-slate-700 transition-colors"
                      >
                        {submitBtnText}
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
