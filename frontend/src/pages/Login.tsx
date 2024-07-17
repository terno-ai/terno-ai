import CSRFToken from "../utils/csrftoken";

const Login = () => {
  return (
    <div className="flex flex-col justify-center items-center max-w-md w-full mx-auto my-auto p-4 border rounded-xl">
      <div className="text-xl font-bold">Login</div>
      <form method="post">
        <CSRFToken />
        <div className="flex justify-center items-center gap-5 m-3 flex-wrap">
          <label
            htmlFor="username"
            className="text-black dark:text-white leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            Username:
          </label>
          <div className="gap-5 px-5 rounded-full bg-slate-100 hover:drop-shadow-sm focus-within:ring-1 focus-within:ring-sky-500 focus-within:hover:drop-shadow-none">
            <input
              type="text"
              id="username"
              name="username"
              required
              className="flex-1 bg-transparent border-none outline-none p-2 text-lg focus:outline-none autofill:bg-none"
            />
          </div>
        </div>
        <div className="flex justify-center items-center gap-5 m-3 flex-wrap">
          <label
            htmlFor="password"
            className="text-black dark:text-white leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            Password:
          </label>
          <div className="gap-5 px-5 rounded-full bg-slate-100 hover:drop-shadow-sm focus-within:ring-1 focus-within:ring-sky-500 focus-within:hover:drop-shadow-none">
            <input
              type="password"
              id="password"
              name="password"
              required
              className="flex-1 bg-transparent border-none outline-none p-2 text-lg focus:outline-none"
            />
          </div>
        </div>
        <div className="flex justify-center items-center gap-5">
          <button
            className="text-right inline-flex h-10 items-center justify-center rounded-md border bg-cyan-500 hover:bg-cyan-600 mt-4 px-10 font-medium text-white transition-colors hover:opacity-80 focus:outline-none focus:ring-2 focus:ring-sky-400 focus:ring-offset-2 focus:ring-offset-slate-50"
            type="submit"
          >
            Login
          </button>
        </div>
      </form>
    </div>
  );
};

export default Login;
